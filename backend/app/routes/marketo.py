"""
Marketo webhook routes for form submission handling.

Endpoint: POST /rad/marketo/webhook
Flow:
  1. Receive form submission from Marketo webhook
  2. Validate shared secret header
  3. Enrich lead data via RADOrchestrator
  4. Generate personalized PDF
  5. Return PDF URL (for Marketo response mapping)
  6. Background: Update lead in Marketo + trigger email campaign
"""

import hmac
import time
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Header, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr, Field

from app.config import settings
from app.services.supabase_client import SupabaseClient, get_supabase_client
from app.services.rad_orchestrator import RADOrchestrator
from app.services.llm_service import LLMService
from app.services.pdf_service import PDFService
from app.services.marketo_service import MarketoService, get_marketo_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rad/marketo", tags=["marketo"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class MarketoWebhookPayload(BaseModel):
    """
    Payload sent by Marketo webhook on form submission.
    Fields are populated from Marketo lead tokens.
    """
    leadId: str = Field(..., description="Marketo lead ID")
    email: EmailStr = Field(..., description="Lead email address")
    firstName: Optional[str] = Field(None, description="Lead first name")
    lastName: Optional[str] = Field(None, description="Lead last name")
    company: Optional[str] = Field(None, description="Company name")
    industry: Optional[str] = Field(None, description="Industry vertical")
    jobTitle: Optional[str] = Field(None, description="Job title")
    companySize: Optional[str] = Field(None, description="Company size range")
    buyerStage: Optional[str] = Field(None, description="Buying stage")
    jobFunction: Optional[str] = Field(None, description="Job function/role")
    formName: Optional[str] = Field(None, description="Marketo form name")
    timestamp: Optional[str] = Field(None, description="Submission timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "leadId": "12345",
                "email": "john@acme.com",
                "firstName": "John",
                "lastName": "Doe",
                "company": "Acme Corp",
                "industry": "Technology",
                "buyerStage": "Evaluating Options"
            }
        }


class WebhookResponse(BaseModel):
    """
    Response returned to Marketo webhook.
    Marketo can map these fields to lead records via response mapping.
    """
    status: str = Field(..., description="Processing status: completed, processing, failed")
    pdfUrl: Optional[str] = Field(None, description="Signed URL for personalized PDF")
    message: Optional[str] = Field(None, description="Status message or error details")
    webhookId: Optional[str] = Field(None, description="Internal webhook tracking ID")


# ============================================================================
# FIELD MAPPING HELPERS
# ============================================================================

def _map_industry(marketo_industry: Optional[str]) -> Optional[str]:
    """
    Map Marketo industry picklist values to our schema.

    Args:
        marketo_industry: Industry value from Marketo

    Returns:
        Normalized industry string for our system
    """
    if not marketo_industry:
        return None

    mapping = {
        "Healthcare": "healthcare",
        "Healthcare/Life Sciences": "healthcare",
        "Financial Services": "financial_services",
        "Banking": "financial_services",
        "Insurance": "financial_services",
        "Manufacturing": "manufacturing",
        "Technology": "technology",
        "Software": "technology",
        "Retail": "retail",
        "E-commerce": "retail",
        "Education": "education",
        "Higher Education": "education",
        "Government": "government",
        "Public Sector": "government",
        "Energy": "energy",
        "Oil & Gas": "energy",
        "Utilities": "energy",
        "Telecommunications": "telecommunications",
        "Media": "media",
        "Entertainment": "media",
    }

    if marketo_industry in mapping:
        return mapping[marketo_industry]

    # Fallback: normalize unknown values
    return marketo_industry.lower().replace(" ", "_").replace("/", "_")


def _map_persona(job_function: Optional[str]) -> Optional[str]:
    """
    Map Marketo job function to our persona schema.

    Args:
        job_function: Job function from Marketo

    Returns:
        Normalized persona string
    """
    if not job_function:
        return None

    mapping = {
        "CEO/President": "ceo",
        "CEO": "ceo",
        "President": "ceo",
        "CTO/CIO": "cto",
        "CTO": "cto",
        "CIO": "cto",
        "Chief Technology Officer": "cto",
        "CISO": "ciso",
        "Chief Information Security Officer": "ciso",
        "CFO": "cfo",
        "Chief Financial Officer": "cfo",
        "VP Engineering": "vp_engineering",
        "VP of Engineering": "vp_engineering",
        "VP Technology": "vp_engineering",
        "IT Director": "it_director",
        "Director of IT": "it_director",
        "IT Manager": "it_manager",
        "Data Scientist": "data_scientist",
        "Data Engineer": "data_engineer",
        "ML Engineer": "ml_engineer",
        "Security Analyst": "security_analyst",
        "DevOps": "devops",
        "Developer": "developer",
        "Software Engineer": "developer",
    }

    if job_function in mapping:
        return mapping[job_function]

    return "other"


def _map_buyer_stage(stage: Optional[str]) -> Optional[str]:
    """
    Map Marketo buyer stage to our goal schema.

    Args:
        stage: Buyer stage from Marketo

    Returns:
        Normalized goal/stage string
    """
    if not stage:
        return "awareness"

    mapping = {
        "Just Learning": "awareness",
        "Awareness": "awareness",
        "Learning": "awareness",
        "Evaluating Options": "consideration",
        "Consideration": "consideration",
        "Comparing": "consideration",
        "Ready to Buy": "decision",
        "Decision": "decision",
        "Purchasing": "decision",
        "Already Implementing": "implementation",
        "Implementation": "implementation",
        "Deployed": "implementation",
    }

    if stage in mapping:
        return mapping[stage]

    return "awareness"


def _map_company_size(size: Optional[str]) -> Optional[str]:
    """
    Map Marketo company size to our schema.

    Args:
        size: Company size range from Marketo

    Returns:
        Normalized company size string
    """
    if not size:
        return None

    mapping = {
        "1-50": "startup",
        "1-10": "startup",
        "11-50": "startup",
        "51-200": "small",
        "51-100": "small",
        "101-200": "small",
        "201-1000": "midmarket",
        "201-500": "midmarket",
        "501-1000": "midmarket",
        "1001-5000": "enterprise",
        "1000-5000": "enterprise",
        "5000+": "large_enterprise",
        "5001-10000": "large_enterprise",
        "10000+": "large_enterprise",
    }

    if size in mapping:
        return mapping[size]

    return "midmarket"


# ============================================================================
# WEBHOOK ENDPOINT
# ============================================================================

def verify_webhook_secret(x_marketo_secret: str = Header(..., alias="X-Marketo-Secret")) -> bool:
    """
    Verify the shared secret header from Marketo.

    Args:
        x_marketo_secret: Secret from X-Marketo-Secret header

    Returns:
        True if valid

    Raises:
        HTTPException: 401 if secret is invalid
    """
    expected = settings.MARKETO_WEBHOOK_SECRET
    if not expected:
        logger.warning("MARKETO_WEBHOOK_SECRET not configured, rejecting request")
        raise HTTPException(
            status_code=401,
            detail="Webhook secret not configured"
        )

    if not hmac.compare_digest(x_marketo_secret, expected):
        logger.warning("Invalid Marketo webhook secret received")
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook secret"
        )

    return True


@router.post("/webhook", response_model=WebhookResponse)
async def handle_marketo_webhook(
    payload: MarketoWebhookPayload,
    background_tasks: BackgroundTasks,
    x_marketo_secret: str = Header(..., alias="X-Marketo-Secret"),
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> WebhookResponse:
    """
    Handle incoming Marketo form submission webhook.

    Flow:
    1. Validate webhook secret
    2. Log webhook to database
    3. Enrich lead data via RADOrchestrator
    4. Generate personalized PDF
    5. Return PDF URL for Marketo response mapping
    6. (Background) Update lead in Marketo + trigger email campaign

    Args:
        payload: Marketo webhook payload with lead data
        background_tasks: FastAPI background tasks
        x_marketo_secret: Shared secret header
        supabase: Database client

    Returns:
        WebhookResponse with status and PDF URL

    Note:
        Must complete within 30 seconds (Marketo timeout)
    """
    start_time = time.time()
    webhook_id = str(uuid.uuid4())

    # Verify webhook authenticity
    verify_webhook_secret(x_marketo_secret)

    logger.info(f"[{webhook_id}] Marketo webhook received for lead {payload.leadId} ({payload.email})")

    # Log incoming webhook to database
    try:
        webhook_record = _log_webhook(supabase, webhook_id, payload, "processing")
    except Exception as e:
        logger.error(f"[{webhook_id}] Failed to log webhook: {e}")
        # Continue processing even if logging fails

    try:
        # Map Marketo fields to our enrichment request format
        email = payload.email.lower().strip()
        domain = email.split("@")[1]

        enrichment_data = {
            "email": email,
            "domain": domain,
            "firstName": payload.firstName,
            "lastName": payload.lastName,
            "company": payload.company,
            "industry": _map_industry(payload.industry),
            "persona": _map_persona(payload.jobFunction),
            "goal": _map_buyer_stage(payload.buyerStage),
            "companySize": _map_company_size(payload.companySize),
        }

        # Initialize services
        orchestrator = RADOrchestrator(supabase)
        llm_service = LLMService()

        # Run enrichment
        logger.info(f"[{webhook_id}] Starting enrichment for {email}")
        finalized = await orchestrator.enrich(email, domain)

        # Override with user-provided data (more reliable)
        if payload.firstName:
            finalized["first_name"] = payload.firstName
        if payload.lastName:
            finalized["last_name"] = payload.lastName
        if payload.company:
            finalized["company_name"] = payload.company
        if enrichment_data["industry"]:
            finalized["industry"] = enrichment_data["industry"]

        # Build user context for LLM
        user_context = {
            "goal": enrichment_data["goal"],
            "persona": enrichment_data["persona"],
            "industry_input": enrichment_data["industry"],
            "company": payload.company,
            "company_size": enrichment_data["companySize"],
            "first_name": payload.firstName,
            "last_name": payload.lastName,
        }

        # Generate ebook personalization
        logger.info(f"[{webhook_id}] Generating personalization for {email}")
        company_news = finalized.get("company_context", "")

        ebook_personalization = await llm_service.generate_ebook_personalization(
            profile=finalized,
            user_context=user_context,
            company_news=company_news
        )

        # Generate legacy personalization for PDF
        personalization = await llm_service.generate_personalization(
            finalized,
            use_opus=False,  # Use Haiku for speed (30s timeout)
            user_context=user_context
        )

        # Store personalization in finalized data
        finalized["ebook_personalization"] = ebook_personalization
        finalized["user_context"] = user_context

        # Update finalize_data with personalization
        supabase.upsert_finalize_data(
            email=email,
            normalized_data=finalized,
            intro=personalization.get("intro_hook", ""),
            cta=personalization.get("cta", "")
        )

        # Generate PDF
        logger.info(f"[{webhook_id}] Generating PDF for {email}")
        pdf_service = PDFService(supabase_client=supabase)

        # Use AMD ebook generation with full personalization
        pdf_result = await pdf_service.generate_amd_ebook(
            job_id=hash(webhook_id) % 1000000,  # Generate numeric job ID from webhook ID
            profile=finalized,
            personalization=ebook_personalization,
            user_context=user_context
        )
        pdf_url = pdf_result.get("pdf_url", "")

        processing_time = int((time.time() - start_time) * 1000)
        logger.info(f"[{webhook_id}] Completed in {processing_time}ms, PDF URL: {pdf_url[:50]}...")

        # Update webhook record
        _update_webhook(supabase, webhook_id, "completed", pdf_url, processing_time)

        # Queue background task to update Marketo
        if settings.is_marketo_configured():
            background_tasks.add_task(
                _update_marketo_lead_background,
                payload.leadId,
                pdf_url,
                finalized,
                webhook_id,
                supabase
            )

        return WebhookResponse(
            status="completed",
            pdfUrl=pdf_url,
            message="PDF generated successfully",
            webhookId=webhook_id
        )

    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        logger.error(f"[{webhook_id}] Webhook processing failed after {processing_time}ms: {e}")

        # Update webhook record with error
        _update_webhook(supabase, webhook_id, "failed", None, processing_time, str(e))

        # Return error response (Marketo will see this via response mapping)
        return WebhookResponse(
            status="failed",
            pdfUrl=None,
            message=f"Processing failed: {str(e)}",
            webhookId=webhook_id
        )


@router.get("/status")
async def marketo_status():
    """Check Marketo integration status."""
    return {
        "configured": settings.is_marketo_configured(),
        "webhook_secret_set": bool(settings.MARKETO_WEBHOOK_SECRET),
        "base_url": settings.MARKETO_BASE_URL[:30] + "..." if settings.MARKETO_BASE_URL else None,
        "email_campaign_id": settings.MARKETO_EMAIL_CAMPAIGN_ID
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _log_webhook(
    supabase: SupabaseClient,
    webhook_id: str,
    payload: MarketoWebhookPayload,
    status: str
) -> dict:
    """Log incoming webhook to database."""
    if supabase.mock_mode:
        return {"id": webhook_id}

    try:
        data = {
            "id": webhook_id,
            "lead_id": payload.leadId,
            "email": payload.email,
            "payload": payload.model_dump(),
            "status": status,
            "created_at": datetime.utcnow().isoformat()
        }
        result = supabase.client.table("marketo_webhooks").insert(data).execute()
        return result.data[0] if result.data else data
    except Exception as e:
        logger.error(f"Failed to log webhook: {e}")
        return {"id": webhook_id}


def _update_webhook(
    supabase: SupabaseClient,
    webhook_id: str,
    status: str,
    pdf_url: Optional[str],
    processing_time_ms: int,
    error_message: Optional[str] = None
):
    """Update webhook record with result."""
    if supabase.mock_mode:
        return

    try:
        data = {
            "status": status,
            "pdf_url": pdf_url,
            "processing_time_ms": processing_time_ms,
            "completed_at": datetime.utcnow().isoformat()
        }
        if error_message:
            data["error_message"] = error_message

        supabase.client.table("marketo_webhooks").update(data).eq("id", webhook_id).execute()
    except Exception as e:
        logger.error(f"Failed to update webhook record: {e}")


async def _update_marketo_lead_background(
    lead_id: str,
    pdf_url: str,
    enrichment_result: dict,
    webhook_id: str,
    supabase: SupabaseClient
):
    """
    Background task to update lead in Marketo and trigger email campaign.

    This runs after the webhook response is sent, so it doesn't block
    the 30-second timeout.
    """
    marketo = get_marketo_service()

    try:
        # Update lead with PDF URL
        logger.info(f"[{webhook_id}] Updating Marketo lead {lead_id} with PDF URL")

        await marketo.update_lead(lead_id, {
            "Custom_PDF_URL": pdf_url,
            "Enrichment_Status": "completed",
            "Enrichment_Date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        })

        # Log API call
        _log_marketo_api_call(
            supabase, webhook_id,
            "/rest/v1/leads.json", "POST",
            {"lead_id": lead_id, "fields": ["Custom_PDF_URL", "Enrichment_Status"]},
            200, {"success": True}
        )

        # Trigger email campaign if configured
        if settings.MARKETO_EMAIL_CAMPAIGN_ID:
            logger.info(f"[{webhook_id}] Triggering email campaign for lead {lead_id}")

            await marketo.trigger_campaign(
                settings.MARKETO_EMAIL_CAMPAIGN_ID,
                lead_id,
                tokens={"pdfUrl": pdf_url}
            )

            _log_marketo_api_call(
                supabase, webhook_id,
                f"/rest/v1/campaigns/{settings.MARKETO_EMAIL_CAMPAIGN_ID}/trigger.json",
                "POST",
                {"lead_id": lead_id},
                200, {"success": True}
            )

        logger.info(f"[{webhook_id}] Marketo background tasks completed for lead {lead_id}")

    except Exception as e:
        logger.error(f"[{webhook_id}] Marketo background task failed: {e}")

        _log_marketo_api_call(
            supabase, webhook_id,
            "error", "N/A",
            {"error": str(e)},
            500, {"error": str(e)}
        )


def _log_marketo_api_call(
    supabase: SupabaseClient,
    webhook_id: str,
    endpoint: str,
    method: str,
    request_body: dict,
    response_status: int,
    response_body: dict
):
    """Log Marketo API call for debugging."""
    if supabase.mock_mode:
        return

    try:
        supabase.client.table("marketo_api_calls").insert({
            "id": str(uuid.uuid4()),
            "webhook_id": webhook_id,
            "endpoint": endpoint,
            "method": method,
            "request_body": request_body,
            "response_status": response_status,
            "response_body": response_body,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        logger.error(f"Failed to log Marketo API call: {e}")
