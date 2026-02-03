"""
Tests for Marketo webhook integration.
Following TDD: Write failing tests first, then implement.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from fastapi.testclient import TestClient


class TestMarketoWebhookEndpoint:
    """Tests for POST /rad/marketo/webhook endpoint."""

    def test_webhook_rejects_missing_secret(self, client: TestClient):
        """Webhook should reject requests without X-Marketo-Secret header."""
        payload = {
            "leadId": "12345",
            "email": "test@example.com",
            "firstName": "John",
            "lastName": "Doe"
        }

        response = client.post("/rad/marketo/webhook", json=payload)

        assert response.status_code == 422  # Missing required header

    def test_webhook_rejects_invalid_secret(self, client: TestClient):
        """Webhook should reject requests with invalid secret."""
        payload = {
            "leadId": "12345",
            "email": "test@example.com",
            "firstName": "John",
            "lastName": "Doe"
        }

        response = client.post(
            "/rad/marketo/webhook",
            json=payload,
            headers={"X-Marketo-Secret": "wrong-secret"}
        )

        assert response.status_code == 401
        assert "Invalid webhook secret" in response.json().get("detail", "")

    def test_webhook_accepts_valid_request(self, client: TestClient, mock_enrichment):
        """Webhook should process valid requests with correct secret."""
        payload = {
            "leadId": "12345",
            "email": "john@acme.com",
            "firstName": "John",
            "lastName": "Doe",
            "company": "Acme Corp",
            "industry": "Technology",
            "buyerStage": "Evaluating Options"
        }

        response = client.post(
            "/rad/marketo/webhook",
            json=payload,
            headers={"X-Marketo-Secret": "test-webhook-secret"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["completed", "processing"]
        assert "pdfUrl" in data or data["status"] == "processing"

    def test_webhook_validates_email_required(self, client: TestClient):
        """Webhook should require email field."""
        payload = {
            "leadId": "12345",
            "firstName": "John"
        }

        response = client.post(
            "/rad/marketo/webhook",
            json=payload,
            headers={"X-Marketo-Secret": "test-webhook-secret"}
        )

        assert response.status_code == 422  # Validation error

    def test_webhook_validates_lead_id_required(self, client: TestClient):
        """Webhook should require leadId field."""
        payload = {
            "email": "test@example.com",
            "firstName": "John"
        }

        response = client.post(
            "/rad/marketo/webhook",
            json=payload,
            headers={"X-Marketo-Secret": "test-webhook-secret"}
        )

        assert response.status_code == 422  # Validation error

    def test_webhook_returns_pdf_url_on_success(self, client: TestClient, mock_enrichment, mock_pdf_service):
        """Webhook should return PDF URL on successful processing."""
        payload = {
            "leadId": "12345",
            "email": "john@acme.com",
            "firstName": "John",
            "lastName": "Doe",
            "company": "Acme Corp"
        }

        response = client.post(
            "/rad/marketo/webhook",
            json=payload,
            headers={"X-Marketo-Secret": "test-webhook-secret"}
        )

        assert response.status_code == 200
        data = response.json()
        if data["status"] == "completed":
            assert data["pdfUrl"] is not None
            assert data["pdfUrl"].startswith("https://")


class TestMarketoFieldMapping:
    """Tests for Marketo field mapping helpers."""

    def test_map_industry_known_value(self):
        """Should map known Marketo industry values."""
        from app.routes.marketo import _map_industry

        assert _map_industry("Healthcare") == "healthcare"
        assert _map_industry("Financial Services") == "financial_services"
        assert _map_industry("Technology") == "technology"

    def test_map_industry_unknown_value(self):
        """Should handle unknown industry values gracefully."""
        from app.routes.marketo import _map_industry

        result = _map_industry("Some Unknown Industry")
        assert result == "some_unknown_industry"

    def test_map_industry_none(self):
        """Should handle None industry."""
        from app.routes.marketo import _map_industry

        assert _map_industry(None) is None

    def test_map_persona_known_value(self):
        """Should map known job functions to personas."""
        from app.routes.marketo import _map_persona

        assert _map_persona("CEO/President") == "ceo"
        assert _map_persona("CTO/CIO") == "cto"
        assert _map_persona("CISO") == "ciso"

    def test_map_buyer_stage(self):
        """Should map buyer stages correctly."""
        from app.routes.marketo import _map_buyer_stage

        assert _map_buyer_stage("Just Learning") == "awareness"
        assert _map_buyer_stage("Evaluating Options") == "consideration"
        assert _map_buyer_stage("Ready to Buy") == "decision"

    def test_map_company_size(self):
        """Should map company size correctly."""
        from app.routes.marketo import _map_company_size

        assert _map_company_size("1-50") == "startup"
        assert _map_company_size("51-200") == "small"
        assert _map_company_size("201-1000") == "midmarket"
        assert _map_company_size("1001-5000") == "enterprise"
        assert _map_company_size("5000+") == "large_enterprise"


class TestMarketoService:
    """Tests for MarketoService API client."""

    @pytest.mark.asyncio
    async def test_get_access_token(self, mock_marketo_oauth):
        """Should fetch and cache OAuth token."""
        from app.services.marketo_service import MarketoService

        service = MarketoService()
        token = await service._get_access_token()

        assert token is not None
        assert token == "mock-access-token"

    @pytest.mark.asyncio
    async def test_update_lead(self, mock_marketo_api):
        """Should update lead record via API."""
        from app.services.marketo_service import MarketoService

        service = MarketoService()
        service._access_token = "mock-token"

        result = await service.update_lead("12345", {
            "Custom_PDF_URL": "https://example.com/pdf.pdf"
        })

        assert result is not None

    @pytest.mark.asyncio
    async def test_trigger_campaign(self, mock_marketo_api):
        """Should trigger campaign via API."""
        from app.services.marketo_service import MarketoService

        service = MarketoService()
        service._access_token = "mock-token"

        result = await service.trigger_campaign(
            campaign_id="1001",
            lead_id="12345",
            tokens={"pdfUrl": "https://example.com/pdf.pdf"}
        )

        assert result is not None


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Create test client with mocked dependencies."""
    import os
    os.environ["MOCK_SUPABASE"] = "true"
    os.environ["MARKETO_WEBHOOK_SECRET"] = "test-webhook-secret"
    os.environ["MARKETO_CLIENT_ID"] = "test-client-id"
    os.environ["MARKETO_CLIENT_SECRET"] = "test-client-secret"
    os.environ["MARKETO_BASE_URL"] = "https://test.mktorest.com"

    from app.main import app
    from fastapi.testclient import TestClient

    return TestClient(app)


@pytest.fixture
def mock_enrichment():
    """Mock the enrichment orchestrator."""
    with patch("app.routes.marketo.RADOrchestrator") as mock:
        mock_instance = MagicMock()
        mock_instance.enrich = AsyncMock(return_value={
            "email": "john@acme.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "Acme Corp",
            "data_quality_score": 0.8
        })
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_pdf_service():
    """Mock PDF generation service."""
    with patch("app.routes.marketo.PDFService") as mock:
        mock_instance = MagicMock()
        mock_instance.generate_amd_ebook = AsyncMock(
            return_value={
                "pdf_url": "https://storage.example.com/pdfs/test.pdf",
                "storage_path": "personalized-pdfs/test.pdf",
                "file_size_bytes": 12345
            }
        )
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_marketo_oauth():
    """Mock Marketo OAuth endpoint."""
    with patch("httpx.AsyncClient.get") as mock:
        mock.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "access_token": "mock-access-token",
                "expires_in": 3600
            },
            raise_for_status=lambda: None
        )
        yield mock


@pytest.fixture
def mock_marketo_api():
    """Mock Marketo API endpoints."""
    with patch("httpx.AsyncClient.post") as mock:
        mock.return_value = MagicMock(
            status_code=200,
            json=lambda: {"success": True, "result": [{"id": "12345"}]},
            raise_for_status=lambda: None
        )
        yield mock
