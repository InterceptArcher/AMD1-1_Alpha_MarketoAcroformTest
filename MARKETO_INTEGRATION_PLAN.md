# Marketo Integration Plan

## Overview

This document outlines the integration between Adobe Marketo Engage and the AMD Ebook personalization backend. The flow enables:

1. User fills out a Marketo-hosted form
2. Marketo webhook triggers our FastAPI backend
3. Backend enriches data + generates personalized PDF
4. PDF URL sent back to Marketo
5. Marketo emails the user with download link

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MARKETO                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────┐    ┌──────────────────┐    ┌───────────────────┐    │
│   │  Marketo     │───►│  Smart Campaign  │───►│  Call Webhook     │    │
│   │  Form        │    │  (Fills Out Form)│    │  (POST to FastAPI)│    │
│   └──────────────┘    └──────────────────┘    └─────────┬─────────┘    │
│                                                          │              │
│   ┌──────────────────────────────────────────────────────┼──────────┐  │
│   │                      Response Mapping                 │          │  │
│   │   pdfUrl → Lead.Custom_PDF_URL                       │          │  │
│   │   status → Lead.Enrichment_Status                    ▼          │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS POST (JSON)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   POST /rad/marketo/webhook                                             │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ 1. Validate webhook (shared secret header)                      │   │
│   │ 2. Parse Marketo payload → EnrichmentRequest                    │   │
│   │ 3. Call RADOrchestrator.enrich() (PDL, Hunter, GNews, Apollo)   │   │
│   │ 4. Generate personalized PDF via PDFService                     │   │
│   │ 5. Upload PDF to Supabase Storage → get signed URL              │   │
│   │ 6. Return JSON: { pdfUrl, status, leadId }                      │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   Background (async):                                                    │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ 7. Update lead in Marketo via REST API (PDF URL, enriched data) │   │
│   │ 8. Trigger email campaign via Request Campaign API               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Marketo REST API (OAuth 2.0)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           MARKETO                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────┐    ┌──────────────────────────────────────────┐  │
│   │  Lead Updated    │───►│  Transactional Email Campaign            │  │
│   │  (PDF URL field) │    │  "Your personalized ebook is ready!"     │  │
│   └──────────────────┘    │  Download link: {{lead.Custom_PDF_URL}}  │  │
│                           └──────────────────────────────────────────┘  │
│                                        │                                 │
│                                        ▼                                 │
│                           ┌──────────────────────┐                      │
│                           │  User receives email │                      │
│                           │  with PDF download   │                      │
│                           └──────────────────────┘                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Marketo Configuration

### 1. Custom Lead Fields

Create these custom fields in Marketo (Admin → Field Management):

| Field Name | API Name | Type | Description |
|------------|----------|------|-------------|
| PDF Download URL | `Custom_PDF_URL` | String | Signed URL for personalized PDF |
| Enrichment Status | `Enrichment_Status` | String | completed/failed/pending |
| Enrichment Date | `Enrichment_Date` | DateTime | When enrichment completed |
| Company Size | `Company_Size__c` | Picklist | startup/small/midmarket/enterprise |
| Buyer Stage | `Buyer_Stage__c` | Picklist | awareness/consideration/decision |
| Job Function | `Job_Function__c` | Picklist | ceo/cto/ciso/vp_engineering/etc |

### 2. Marketo Form Fields

Map your form fields to these Marketo fields:

| Form Field | Marketo Field | Required |
|------------|---------------|----------|
| Email | Email Address | Yes |
| First Name | First Name | Yes |
| Last Name | Last Name | Yes |
| Company | Company Name | Yes |
| Industry | Industry | Yes |
| Job Title | Job Title | No |
| Company Size | Company_Size__c | No |
| What stage are you in? | Buyer_Stage__c | No |
| Your Role | Job_Function__c | No |

### 3. Webhook Configuration

**Admin → Webhooks → New Webhook**

| Setting | Value |
|---------|-------|
| Name | AMD Ebook Personalization |
| URL | `https://amd1-1-backend.onrender.com/rad/marketo/webhook` |
| Request Type | POST |
| Request Token Encoding | JSON |
| Response Type | JSON |

**Payload Template:**
```json
{
  "leadId": "{{lead.Id}}",
  "email": "{{lead.Email Address}}",
  "firstName": "{{lead.First Name}}",
  "lastName": "{{lead.Last Name}}",
  "company": "{{company.Company Name}}",
  "industry": "{{lead.Industry}}",
  "jobTitle": "{{lead.Job Title}}",
  "companySize": "{{lead.Company_Size__c}}",
  "buyerStage": "{{lead.Buyer_Stage__c}}",
  "jobFunction": "{{lead.Job_Function__c}}",
  "formName": "{{trigger.Name}}",
  "timestamp": "{{system.dateTime}}"
}
```

**Custom Headers:**
```
Content-Type: application/json
X-Marketo-Secret: <shared-secret-from-env>
```

**Response Mappings:**

| Response Attribute | Marketo Field |
|-------------------|---------------|
| pdfUrl | Custom_PDF_URL |
| status | Enrichment_Status |

### 4. Smart Campaign Setup

**Campaign: "AMD Ebook - Form Fill Handler"**

**Smart List (Trigger):**
- Fills Out Form
  - Form: AMD Ebook Request Form
  - Web Page: (any)

**Flow:**
1. Call Webhook: "AMD Ebook Personalization"
2. Wait: 1 minute (allows async processing)
3. Send Email: "Your Personalized AMD Ebook"
   - Constraint: Custom_PDF_URL is not empty

**Schedule:**
- Qualification Rules: Each lead can run through every time

### 5. Email Template

**Subject:** `{{lead.First Name}}, your personalized AI readiness ebook is ready`

**Body:**
```html
<p>Hi {{lead.First Name}},</p>

<p>Thank you for your interest in enterprise AI readiness. We've created a
personalized ebook tailored to {{lead.Company Name}}'s needs in the
{{lead.Industry}} industry.</p>

<p style="text-align: center; margin: 30px 0;">
  <a href="{{lead.Custom_PDF_URL}}"
     style="background: #ED1C24; color: white; padding: 15px 30px;
            text-decoration: none; border-radius: 5px; font-weight: bold;">
    Download Your Personalized Ebook
  </a>
</p>

<p>This link expires in 7 days. If you have any questions, reply to this email.</p>

<p>Best regards,<br>
The AMD Enterprise AI Team</p>
```

---

## Backend Implementation

### 1. New Files to Create

```
backend/app/
├── routes/
│   └── marketo.py              # Webhook endpoint
├── services/
│   └── marketo_service.py      # Marketo API client
└── models/
    └── marketo_schemas.py      # Request/response models
```

### 2. Database Schema

**New migration: `supabase/migrations/20260203_add_marketo_tables.sql`**

```sql
-- Track incoming webhooks
CREATE TABLE marketo_webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'received',
    pdf_url TEXT,
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_marketo_webhooks_email ON marketo_webhooks(email);
CREATE INDEX idx_marketo_webhooks_lead_id ON marketo_webhooks(lead_id);
CREATE INDEX idx_marketo_webhooks_status ON marketo_webhooks(status);

-- Track API calls back to Marketo
CREATE TABLE marketo_api_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES marketo_webhooks(id),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_body JSONB,
    response_status INTEGER,
    response_body JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. Environment Variables

Add to Render (backend):

```bash
# Marketo API Credentials
MARKETO_CLIENT_ID=<from-marketo-admin>
MARKETO_CLIENT_SECRET=<from-marketo-admin>
MARKETO_BASE_URL=https://<munchkin-id>.mktorest.com
MARKETO_IDENTITY_URL=https://<munchkin-id>.mktorest.com/identity

# Webhook Security
MARKETO_WEBHOOK_SECRET=<generate-random-string>

# Email Campaign ID (for triggering transactional emails)
MARKETO_EMAIL_CAMPAIGN_ID=<campaign-id>
```

### 4. Marketo Service Implementation

**`backend/app/services/marketo_service.py`**

```python
import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from ..config import settings

class MarketoService:
    """Client for Marketo REST API."""

    def __init__(self):
        self.base_url = settings.MARKETO_BASE_URL
        self.identity_url = settings.MARKETO_IDENTITY_URL
        self.client_id = settings.MARKETO_CLIENT_ID
        self.client_secret = settings.MARKETO_CLIENT_SECRET
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def _get_access_token(self) -> str:
        """Get or refresh OAuth access token."""
        if self._access_token and self._token_expires_at:
            if datetime.utcnow() < self._token_expires_at - timedelta(minutes=5):
                return self._access_token

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.identity_url}/oauth/token",
                params={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            )
            response.raise_for_status()
            data = response.json()

            self._access_token = data["access_token"]
            # Tokens typically expire in 3600 seconds
            self._token_expires_at = datetime.utcnow() + timedelta(
                seconds=data.get("expires_in", 3600)
            )
            return self._access_token

    async def update_lead(self, lead_id: str, fields: dict) -> dict:
        """Update lead record with enrichment data."""
        token = await self._get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rest/v1/leads.json",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json={
                    "action": "updateOnly",
                    "lookupField": "id",
                    "input": [{
                        "id": int(lead_id),
                        **fields
                    }]
                }
            )
            response.raise_for_status()
            return response.json()

    async def trigger_campaign(
        self,
        campaign_id: str,
        lead_id: str,
        tokens: dict = None
    ) -> dict:
        """Trigger a smart campaign for a lead."""
        token = await self._get_access_token()

        payload = {
            "input": {
                "leads": [{"id": int(lead_id)}]
            }
        }

        if tokens:
            payload["input"]["tokens"] = [
                {"name": f"{{{{my.{k}}}}}", "value": v}
                for k, v in tokens.items()
            ]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rest/v1/campaigns/{campaign_id}/trigger.json",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            return response.json()
```

### 5. Webhook Endpoint Implementation

**`backend/app/routes/marketo.py`**

```python
import time
import hmac
import hashlib
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..config import settings
from ..services.rad_orchestrator import RADOrchestrator
from ..services.pdf_service import PDFService
from ..services.marketo_service import MarketoService
from ..services.supabase_client import get_supabase_client

router = APIRouter(prefix="/rad/marketo", tags=["marketo"])

class MarketoWebhookPayload(BaseModel):
    leadId: str
    email: EmailStr
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    jobTitle: Optional[str] = None
    companySize: Optional[str] = None
    buyerStage: Optional[str] = None
    jobFunction: Optional[str] = None
    formName: Optional[str] = None
    timestamp: Optional[str] = None

class WebhookResponse(BaseModel):
    status: str
    pdfUrl: Optional[str] = None
    message: Optional[str] = None

def verify_webhook_secret(x_marketo_secret: str = Header(...)) -> bool:
    """Verify the shared secret from Marketo."""
    expected = settings.MARKETO_WEBHOOK_SECRET
    if not hmac.compare_digest(x_marketo_secret, expected):
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    return True

@router.post("/webhook", response_model=WebhookResponse)
async def handle_marketo_webhook(
    payload: MarketoWebhookPayload,
    background_tasks: BackgroundTasks,
    x_marketo_secret: str = Header(...)
):
    """
    Handle incoming Marketo form submission webhook.

    Flow:
    1. Validate webhook secret
    2. Enrich lead data via RADOrchestrator
    3. Generate personalized PDF
    4. Return PDF URL for response mapping
    5. (Background) Update lead in Marketo + trigger email
    """
    start_time = time.time()

    # Verify webhook authenticity
    verify_webhook_secret(x_marketo_secret)

    supabase = get_supabase_client()

    # Log incoming webhook
    webhook_record = await supabase.table("marketo_webhooks").insert({
        "lead_id": payload.leadId,
        "email": payload.email,
        "payload": payload.model_dump(),
        "status": "processing"
    }).execute()
    webhook_id = webhook_record.data[0]["id"]

    try:
        # Map Marketo fields to our enrichment request format
        enrichment_request = {
            "email": payload.email,
            "firstName": payload.firstName,
            "lastName": payload.lastName,
            "company": payload.company,
            "industry": _map_industry(payload.industry),
            "persona": _map_persona(payload.jobFunction),
            "goal": _map_buyer_stage(payload.buyerStage),
            "companySize": _map_company_size(payload.companySize),
            "force_refresh": False
        }

        # Enrich the lead data
        orchestrator = RADOrchestrator()
        enrichment_result = await orchestrator.enrich(enrichment_request)

        # Generate personalized PDF
        pdf_service = PDFService()
        pdf_url = await pdf_service.generate_and_store(
            email=payload.email,
            profile=enrichment_result.get("profile"),
            personalization=enrichment_result.get("personalization")
        )

        processing_time = int((time.time() - start_time) * 1000)

        # Update webhook record
        await supabase.table("marketo_webhooks").update({
            "status": "completed",
            "pdf_url": pdf_url,
            "processing_time_ms": processing_time,
            "completed_at": "now()"
        }).eq("id", webhook_id).execute()

        # Queue background task to update Marketo
        background_tasks.add_task(
            update_marketo_lead,
            payload.leadId,
            pdf_url,
            enrichment_result,
            webhook_id
        )

        return WebhookResponse(
            status="completed",
            pdfUrl=pdf_url,
            message="PDF generated successfully"
        )

    except Exception as e:
        # Log error
        await supabase.table("marketo_webhooks").update({
            "status": "failed",
            "error_message": str(e),
            "completed_at": "now()"
        }).eq("id", webhook_id).execute()

        # Return error (Marketo will see this in response mapping)
        return WebhookResponse(
            status="failed",
            message=str(e)
        )

async def update_marketo_lead(
    lead_id: str,
    pdf_url: str,
    enrichment_result: dict,
    webhook_id: str
):
    """Background task to update lead in Marketo."""
    marketo = MarketoService()
    supabase = get_supabase_client()

    try:
        # Update lead with PDF URL and enrichment data
        update_response = await marketo.update_lead(lead_id, {
            "Custom_PDF_URL": pdf_url,
            "Enrichment_Status": "completed",
            "Enrichment_Date": datetime.utcnow().isoformat()
        })

        # Log API call
        await supabase.table("marketo_api_calls").insert({
            "webhook_id": webhook_id,
            "endpoint": "/rest/v1/leads.json",
            "method": "POST",
            "response_status": 200,
            "response_body": update_response
        }).execute()

        # Optionally trigger email campaign
        if settings.MARKETO_EMAIL_CAMPAIGN_ID:
            campaign_response = await marketo.trigger_campaign(
                settings.MARKETO_EMAIL_CAMPAIGN_ID,
                lead_id,
                tokens={"pdfUrl": pdf_url}
            )

            await supabase.table("marketo_api_calls").insert({
                "webhook_id": webhook_id,
                "endpoint": f"/rest/v1/campaigns/{settings.MARKETO_EMAIL_CAMPAIGN_ID}/trigger.json",
                "method": "POST",
                "response_status": 200,
                "response_body": campaign_response
            }).execute()

    except Exception as e:
        await supabase.table("marketo_api_calls").insert({
            "webhook_id": webhook_id,
            "endpoint": "error",
            "method": "N/A",
            "response_body": {"error": str(e)}
        }).execute()

# Field mapping helpers
def _map_industry(marketo_industry: Optional[str]) -> Optional[str]:
    """Map Marketo industry values to our schema."""
    if not marketo_industry:
        return None
    mapping = {
        "Healthcare": "healthcare",
        "Financial Services": "financial_services",
        "Manufacturing": "manufacturing",
        "Technology": "technology",
        "Retail": "retail",
        "Education": "education",
        "Government": "government",
        # Add more mappings as needed
    }
    return mapping.get(marketo_industry, marketo_industry.lower().replace(" ", "_"))

def _map_persona(job_function: Optional[str]) -> Optional[str]:
    """Map Marketo job function to our persona schema."""
    if not job_function:
        return None
    mapping = {
        "CEO/President": "ceo",
        "CTO/CIO": "cto",
        "CISO": "ciso",
        "VP Engineering": "vp_engineering",
        "IT Director": "it_director",
        "Data Scientist": "data_scientist",
        # Add more mappings
    }
    return mapping.get(job_function, "other")

def _map_buyer_stage(stage: Optional[str]) -> Optional[str]:
    """Map Marketo buyer stage to our goal schema."""
    if not stage:
        return "awareness"
    mapping = {
        "Just Learning": "awareness",
        "Evaluating Options": "consideration",
        "Ready to Buy": "decision",
        "Already Implementing": "implementation"
    }
    return mapping.get(stage, "awareness")

def _map_company_size(size: Optional[str]) -> Optional[str]:
    """Map Marketo company size to our schema."""
    if not size:
        return None
    mapping = {
        "1-50": "startup",
        "51-200": "small",
        "201-1000": "midmarket",
        "1001-5000": "enterprise",
        "5000+": "large_enterprise"
    }
    return mapping.get(size, "midmarket")
```

### 6. Register Routes

**Update `backend/app/main.py`:**

```python
from .routes import enrichment, marketo

app.include_router(enrichment.router)
app.include_router(marketo.router)  # Add this line
```

---

## Implementation Checklist

### Phase 1: Backend Setup
- [ ] Create `marketo_service.py` with OAuth + API methods
- [ ] Create `marketo.py` routes with webhook endpoint
- [ ] Add Marketo schemas to `marketo_schemas.py`
- [ ] Create database migration for webhook tracking tables
- [ ] Add Marketo env vars to Render
- [ ] Register routes in `main.py`
- [ ] Deploy and test endpoint manually

### Phase 2: Marketo Configuration
- [ ] Create custom lead fields in Marketo
- [ ] Create/update form with required fields
- [ ] Create webhook pointing to backend
- [ ] Set up response mappings (pdfUrl → Custom_PDF_URL)
- [ ] Create Smart Campaign with form trigger
- [ ] Create email template with download link
- [ ] Test with sample lead

### Phase 3: Testing & Validation
- [ ] Test webhook with Postman/curl
- [ ] Verify PDF generation completes < 30 seconds
- [ ] Test response mapping updates lead correctly
- [ ] Verify email sends with correct PDF link
- [ ] Test error handling (invalid email, API failures)
- [ ] Load test with multiple concurrent submissions

### Phase 4: Monitoring & Optimization
- [ ] Add webhook dashboard in Supabase
- [ ] Set up alerts for failed webhooks
- [ ] Monitor PDF generation latency
- [ ] Implement retry logic for transient failures
- [ ] Add Marketo API rate limit handling

---

## Key Constraints & Notes

### Marketo Limitations
1. **30-second webhook timeout** - PDF generation must complete quickly
2. **No email attachments** - Must use download links instead
3. **No native webhook signing** - Use shared secret header
4. **100 calls/20 seconds API rate limit** - Implement backoff

### Recommendations
1. **Pre-warm PDF generation** - Cache templates, fonts
2. **Async Marketo updates** - Return webhook response immediately
3. **Idempotency** - Handle duplicate webhook calls gracefully
4. **Monitoring** - Log all webhook events for debugging

### Security
1. Validate `X-Marketo-Secret` header on every request
2. Store Marketo credentials in environment variables only
3. Use HTTPS for all endpoints
4. Consider IP allowlisting if Marketo publishes webhook IPs

---

## Testing the Integration

### Manual Webhook Test

```bash
curl -X POST https://amd1-1-backend.onrender.com/rad/marketo/webhook \
  -H "Content-Type: application/json" \
  -H "X-Marketo-Secret: your-secret-here" \
  -d '{
    "leadId": "12345",
    "email": "test@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "company": "Acme Corp",
    "industry": "Technology",
    "buyerStage": "Evaluating Options"
  }'
```

### Expected Response

```json
{
  "status": "completed",
  "pdfUrl": "https://xxx.supabase.co/storage/v1/object/sign/personalized-pdfs/...",
  "message": "PDF generated successfully"
}
```

---

## Estimated Timeline

| Phase | Tasks | Duration |
|-------|-------|----------|
| Phase 1 | Backend implementation | 1-2 days |
| Phase 2 | Marketo configuration | 1 day |
| Phase 3 | Testing & validation | 1-2 days |
| Phase 4 | Monitoring setup | 1 day |

**Total: 4-6 days**

---

## Questions for Stakeholders

1. **Form fields**: Which fields are required vs optional on the Marketo form?
2. **Email timing**: Should email send immediately or after a delay?
3. **Error handling**: What should happen if PDF generation fails? Retry? Notify ops?
4. **Existing leads**: Should we process leads who already have a PDF URL?
5. **Campaign ID**: What is the Marketo campaign ID for the transactional email?
