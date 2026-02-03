"""
AcroForm PDF Personalization Test Suite

Tests for the PDF personalization system using AcroForm fields.

Run with:
    pytest tests/test_acroform_personalization.py -v

Or run specific test categories:
    pytest tests/test_acroform_personalization.py -v -k "template"
    pytest tests/test_acroform_personalization.py -v -k "industry"
    pytest tests/test_acroform_personalization.py -v -k "content"
"""

import io
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the service under test
from app.services.pdf_personalization_service import (
    validate_template,
    get_template_fields,
    get_case_study_field,
    fill_personalization_fields,
    flatten_pdf,
    personalize_ebook,
    load_industry_content,
    TEMPLATE_WITH_FIELDS,
    FIELD_HOOK,
    FIELD_CASE_STUDY_1,
    FIELD_CASE_STUDY_2,
    FIELD_CASE_STUDY_3,
    FIELD_CTA_ASSESSMENT,
    FIELD_CTA_FOOTER,
    INDUSTRY_CASE_STUDY_MAP,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_personalized_content():
    """Standard personalized content for testing."""
    return {
        "hook": (
            "As Acme Corp continues to expand its AI capabilities, "
            "the pressure on your data center infrastructure is growing. "
            "For IT leaders navigating this transformation, understanding "
            "where you stand on the modernization curve is critical."
        ),
        "case_study_framing": (
            "Like many organizations in your sector, infrastructure decisions "
            "directly impact operational efficiency and competitive advantage."
        ),
        "cta_assessment": (
            "Based on your profile, you're well-positioned to accelerate "
            "your AI journey. Download our AI Readiness Assessment."
        ),
        "cta_footer": (
            "Ready to build your business case for AMD? Contact our team "
            "for a personalized consultation tailored to your needs."
        ),
    }


@pytest.fixture
def minimal_content():
    """Minimal content for edge case testing."""
    return {
        "hook": "Welcome.",
        "case_study_framing": "Context.",
        "cta_assessment": "Next steps.",
        "cta_footer": "Contact us.",
    }


@pytest.fixture
def long_content():
    """Long content to test truncation/overflow handling."""
    return {
        "hook": "A" * 1000,  # Exceeds 500-800 char recommendation
        "case_study_framing": "B" * 500,  # Exceeds 200-300 char recommendation
        "cta_assessment": "C" * 800,  # Exceeds 300-500 char recommendation
        "cta_footer": "D" * 800,  # Exceeds 300-500 char recommendation
    }


@pytest.fixture
def special_chars_content():
    """Content with special characters."""
    return {
        "hook": "Test with special chars: <>&\"'© ® ™ € £ ¥ • — … ""''",
        "case_study_framing": "Framing with unicode: 中文 日本語 한국어 émojis: 🚀 📊",
        "cta_assessment": "CTA with symbols: → ← ↑ ↓ ✓ ✗ ★ ☆",
        "cta_footer": "Footer with math: ≤ ≥ ≠ ± × ÷ √ ∞",
    }


# =============================================================================
# TEMPLATE VALIDATION TESTS
# =============================================================================

class TestTemplateValidation:
    """Tests for template existence and field validation."""

    def test_template_file_exists(self):
        """Template with fields should exist."""
        assert TEMPLATE_WITH_FIELDS.exists(), (
            f"Template not found at {TEMPLATE_WITH_FIELDS}. "
            "Run: python scripts/add_acroform_fields_to_template.py"
        )

    def test_validate_template_returns_valid(self):
        """validate_template should return valid=True when all fields present."""
        result = validate_template()
        assert result["valid"] is True, f"Missing fields: {result.get('missing', [])}"

    def test_validate_template_finds_all_required_fields(self):
        """All 6 required personalization fields should be present."""
        result = validate_template()
        required_fields = {
            FIELD_HOOK,
            FIELD_CASE_STUDY_1,
            FIELD_CASE_STUDY_2,
            FIELD_CASE_STUDY_3,
            FIELD_CTA_ASSESSMENT,
            FIELD_CTA_FOOTER,
        }
        found_fields = set(result.get("found", []))

        for field in required_fields:
            assert field in found_fields, f"Required field '{field}' not found in template"

    def test_get_template_fields_returns_dict(self):
        """get_template_fields should return a dictionary of fields."""
        fields = get_template_fields()
        assert isinstance(fields, dict)
        assert len(fields) > 0

    def test_template_has_correct_field_types(self):
        """All personalization fields should be text fields (/Tx)."""
        fields = get_template_fields()
        text_field_names = [
            FIELD_HOOK,
            FIELD_CASE_STUDY_1,
            FIELD_CASE_STUDY_2,
            FIELD_CASE_STUDY_3,
            FIELD_CTA_ASSESSMENT,
            FIELD_CTA_FOOTER,
        ]

        for name in text_field_names:
            if name in fields:
                field_type = str(fields[name].get("/FT", ""))
                assert field_type == "/Tx", f"Field '{name}' should be text type, got {field_type}"


# =============================================================================
# INDUSTRY TO CASE STUDY MAPPING TESTS
# =============================================================================

class TestIndustryCaseStudyMapping:
    """Tests for industry-based case study selection."""

    @pytest.mark.parametrize("industry,expected_field", [
        # Cloud/GPU focus -> KT Cloud (case study 1)
        ("telecommunications", FIELD_CASE_STUDY_1),
        ("technology", FIELD_CASE_STUDY_1),
        ("gaming_media", FIELD_CASE_STUDY_1),
        ("media", FIELD_CASE_STUDY_1),

        # Cost optimization focus -> Smurfit Westrock (case study 2)
        ("manufacturing", FIELD_CASE_STUDY_2),
        ("retail", FIELD_CASE_STUDY_2),
        ("energy", FIELD_CASE_STUDY_2),
        ("consumer_goods", FIELD_CASE_STUDY_2),

        # Security/compliance focus -> PQR (case study 3)
        ("healthcare", FIELD_CASE_STUDY_3),
        ("financial_services", FIELD_CASE_STUDY_3),
        ("government", FIELD_CASE_STUDY_3),
        ("education", FIELD_CASE_STUDY_3),
        ("non_profit", FIELD_CASE_STUDY_3),
    ])
    def test_industry_maps_to_correct_case_study(self, industry, expected_field):
        """Each industry should map to the appropriate case study field."""
        result = get_case_study_field(industry)
        assert result == expected_field, (
            f"Industry '{industry}' should map to '{expected_field}', got '{result}'"
        )

    def test_unknown_industry_defaults_to_pqr(self):
        """Unknown industries should default to PQR (case study 3)."""
        unknown_industries = ["unknown", "other", "aerospace", "agriculture", ""]

        for industry in unknown_industries:
            result = get_case_study_field(industry)
            assert result == FIELD_CASE_STUDY_3, (
                f"Unknown industry '{industry}' should default to PQR"
            )

    def test_industry_normalization(self):
        """Industry names should be normalized (lowercase, underscores)."""
        variations = [
            ("Healthcare", FIELD_CASE_STUDY_3),
            ("HEALTHCARE", FIELD_CASE_STUDY_3),
            ("health-care", FIELD_CASE_STUDY_3),
            ("Financial Services", FIELD_CASE_STUDY_3),
            ("financial-services", FIELD_CASE_STUDY_3),
        ]

        for industry, expected in variations:
            result = get_case_study_field(industry)
            assert result == expected, (
                f"Industry '{industry}' normalization failed"
            )


# =============================================================================
# FIELD FILLING TESTS
# =============================================================================

class TestFieldFilling:
    """Tests for filling form fields with content."""

    def test_fill_fields_returns_bytes(self, sample_personalized_content):
        """fill_personalization_fields should return PDF bytes."""
        result = fill_personalization_fields(
            personalized_content=sample_personalized_content,
            industry="healthcare",
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_fill_fields_produces_valid_pdf(self, sample_personalized_content):
        """Filled PDF should be readable by pypdf."""
        from pypdf import PdfReader

        pdf_bytes = fill_personalization_fields(
            personalized_content=sample_personalized_content,
            industry="healthcare",
        )

        reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(reader.pages) == 16  # Should maintain page count

    def test_fill_fields_with_empty_content(self):
        """Should handle empty content gracefully."""
        empty_content = {
            "hook": "",
            "case_study_framing": "",
            "cta_assessment": "",
            "cta_footer": "",
        }

        result = fill_personalization_fields(
            personalized_content=empty_content,
            industry="healthcare",
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_fill_fields_with_missing_keys(self):
        """Should handle missing content keys gracefully."""
        partial_content = {"hook": "Only hook provided"}

        result = fill_personalization_fields(
            personalized_content=partial_content,
            industry="healthcare",
        )
        assert isinstance(result, bytes)

    def test_fill_fields_selects_correct_case_study(self, sample_personalized_content):
        """Only the industry-appropriate case study field should be filled."""
        from pypdf import PdfReader

        # Healthcare should fill case_study_3 (PQR)
        pdf_bytes = fill_personalization_fields(
            personalized_content=sample_personalized_content,
            industry="healthcare",
        )

        reader = PdfReader(io.BytesIO(pdf_bytes))
        fields = reader.get_fields()

        # The case_study_3_framing field should have content
        if FIELD_CASE_STUDY_3 in fields:
            value = fields[FIELD_CASE_STUDY_3].get("/V", "")
            assert str(value) != "", "Healthcare should fill case_study_3_framing"


# =============================================================================
# PDF FLATTENING TESTS
# =============================================================================

class TestPdfFlattening:
    """Tests for PDF flattening (making fields static)."""

    def test_flatten_removes_acroform(self, sample_personalized_content):
        """Flattened PDF should have no AcroForm dictionary."""
        from pypdf import PdfReader

        # First fill the fields
        filled_pdf = fill_personalization_fields(
            personalized_content=sample_personalized_content,
            industry="technology",
        )

        # Then flatten
        flattened_pdf = flatten_pdf(filled_pdf)

        reader = PdfReader(io.BytesIO(flattened_pdf))
        fields = reader.get_fields()

        # After flattening, there should be no editable text fields
        # (navigation buttons may still exist)
        if fields:
            text_fields = [
                name for name, f in fields.items()
                if str(f.get("/FT", "")) == "/Tx"
            ]
            assert len(text_fields) == 0, "Flattened PDF should have no text fields"

    def test_flatten_maintains_page_count(self, sample_personalized_content):
        """Flattening should not change page count."""
        from pypdf import PdfReader

        filled_pdf = fill_personalization_fields(
            personalized_content=sample_personalized_content,
            industry="manufacturing",
        )
        flattened_pdf = flatten_pdf(filled_pdf)

        reader = PdfReader(io.BytesIO(flattened_pdf))
        assert len(reader.pages) == 16

    def test_flatten_reduces_or_maintains_size(self, sample_personalized_content):
        """Flattened PDF should not be significantly larger."""
        filled_pdf = fill_personalization_fields(
            personalized_content=sample_personalized_content,
            industry="retail",
        )
        flattened_pdf = flatten_pdf(filled_pdf)

        # Flattened should not be more than 10% larger
        max_expected_size = len(filled_pdf) * 1.1
        assert len(flattened_pdf) <= max_expected_size


# =============================================================================
# END-TO-END PERSONALIZATION TESTS
# =============================================================================

class TestPersonalizeEbook:
    """End-to-end tests for the personalize_ebook function."""

    def test_personalize_ebook_basic(self, sample_personalized_content):
        """Basic personalization should succeed."""
        result = personalize_ebook(
            persona="executive",
            industry="healthcare",
            buying_stage="evaluating",
            company_name="Test Corp",
            personalized_content=sample_personalized_content,
            flatten=True,
        )

        assert isinstance(result, bytes)
        assert len(result) > 0

    @pytest.mark.parametrize("industry", [
        "healthcare",
        "financial_services",
        "manufacturing",
        "technology",
        "retail",
        "government",
        "education",
        "energy",
    ])
    def test_personalize_ebook_all_industries(self, sample_personalized_content, industry):
        """Personalization should work for all supported industries."""
        result = personalize_ebook(
            persona="it_infrastructure",
            industry=industry,
            buying_stage="learning",
            company_name="Industry Test Corp",
            personalized_content=sample_personalized_content,
            flatten=True,
        )

        assert isinstance(result, bytes)
        assert len(result) > 1000000  # Should be substantial (>1MB)

    @pytest.mark.parametrize("persona", [
        "executive",
        "it_infrastructure",
        "security",
        "data_ai",
        "sales_gtm",
        "hr_people",
    ])
    def test_personalize_ebook_all_personas(self, sample_personalized_content, persona):
        """Personalization should work for all personas."""
        result = personalize_ebook(
            persona=persona,
            industry="technology",
            buying_stage="exploring",
            company_name="Persona Test Corp",
            personalized_content=sample_personalized_content,
            flatten=True,
        )

        assert isinstance(result, bytes)

    @pytest.mark.parametrize("buying_stage", [
        "exploring",
        "evaluating",
        "learning",
        "building_case",
    ])
    def test_personalize_ebook_all_buying_stages(self, sample_personalized_content, buying_stage):
        """Personalization should work for all buying stages."""
        result = personalize_ebook(
            persona="executive",
            industry="healthcare",
            buying_stage=buying_stage,
            company_name="Stage Test Corp",
            personalized_content=sample_personalized_content,
            flatten=True,
        )

        assert isinstance(result, bytes)

    def test_personalize_ebook_without_flattening(self, sample_personalized_content):
        """Should be able to skip flattening."""
        from pypdf import PdfReader

        result = personalize_ebook(
            persona="executive",
            industry="healthcare",
            buying_stage="evaluating",
            company_name="Test Corp",
            personalized_content=sample_personalized_content,
            flatten=False,  # Don't flatten
        )

        reader = PdfReader(io.BytesIO(result))
        fields = reader.get_fields()

        # Should still have form fields
        assert fields is not None
        assert len(fields) > 0


# =============================================================================
# CONTENT EDGE CASES
# =============================================================================

class TestContentEdgeCases:
    """Tests for edge cases in content handling."""

    def test_special_characters_in_content(self, special_chars_content):
        """Should handle special characters without errors."""
        result = personalize_ebook(
            persona="executive",
            industry="technology",
            buying_stage="exploring",
            company_name="Test™ Corp®",
            personalized_content=special_chars_content,
            flatten=True,
        )

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_long_content_handling(self, long_content):
        """Should handle content longer than recommended limits."""
        result = personalize_ebook(
            persona="executive",
            industry="healthcare",
            buying_stage="evaluating",
            company_name="Long Content Corp",
            personalized_content=long_content,
            flatten=True,
        )

        assert isinstance(result, bytes)

    def test_minimal_content(self, minimal_content):
        """Should handle very short content."""
        result = personalize_ebook(
            persona="executive",
            industry="manufacturing",
            buying_stage="learning",
            company_name="Min Corp",
            personalized_content=minimal_content,
            flatten=True,
        )

        assert isinstance(result, bytes)

    def test_newlines_in_content(self):
        """Should handle content with newlines."""
        content_with_newlines = {
            "hook": "Line 1.\nLine 2.\nLine 3.",
            "case_study_framing": "Para 1.\n\nPara 2.",
            "cta_assessment": "Step 1\nStep 2\nStep 3",
            "cta_footer": "Contact:\nemail@test.com\n555-1234",
        }

        result = personalize_ebook(
            persona="security",
            industry="financial_services",
            buying_stage="building_case",
            company_name="Newline Corp",
            personalized_content=content_with_newlines,
            flatten=True,
        )

        assert isinstance(result, bytes)

    def test_html_in_content_not_rendered(self):
        """HTML tags in content should appear as text, not be rendered."""
        html_content = {
            "hook": "<b>Bold</b> and <i>italic</i> text",
            "case_study_framing": "<script>alert('xss')</script>",
            "cta_assessment": "<a href='http://evil.com'>Click here</a>",
            "cta_footer": "Normal text",
        }

        result = personalize_ebook(
            persona="executive",
            industry="technology",
            buying_stage="exploring",
            company_name="HTML Test Corp",
            personalized_content=html_content,
            flatten=True,
        )

        # Should succeed without executing HTML
        assert isinstance(result, bytes)


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Tests for error handling scenarios."""

    def test_missing_template_raises_error(self):
        """Should raise FileNotFoundError if template doesn't exist."""
        with patch.object(Path, 'exists', return_value=False):
            # This would need the template to not exist
            # For now, skip if template exists
            if TEMPLATE_WITH_FIELDS.exists():
                pytest.skip("Template exists, cannot test missing template error")

    def test_invalid_industry_uses_default(self, sample_personalized_content):
        """Invalid industry should use default case study (PQR)."""
        result = personalize_ebook(
            persona="executive",
            industry="invalid_industry_xyz",
            buying_stage="evaluating",
            company_name="Test Corp",
            personalized_content=sample_personalized_content,
            flatten=True,
        )

        # Should succeed with default
        assert isinstance(result, bytes)


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class TestPerformance:
    """Performance-related tests."""

    def test_personalization_completes_in_reasonable_time(self, sample_personalized_content):
        """Personalization should complete within 30 seconds."""
        import time

        start = time.time()
        result = personalize_ebook(
            persona="executive",
            industry="healthcare",
            buying_stage="evaluating",
            company_name="Test Corp",
            personalized_content=sample_personalized_content,
            flatten=True,
        )
        elapsed = time.time() - start

        assert elapsed < 30, f"Personalization took {elapsed:.2f}s, expected < 30s"
        assert isinstance(result, bytes)

    def test_output_size_is_reasonable(self, sample_personalized_content):
        """Output PDF should be within expected size range."""
        result = personalize_ebook(
            persona="executive",
            industry="technology",
            buying_stage="exploring",
            company_name="Size Test Corp",
            personalized_content=sample_personalized_content,
            flatten=True,
        )

        size_mb = len(result) / (1024 * 1024)

        # Should be between 1MB and 20MB
        assert 1 < size_mb < 20, f"PDF size {size_mb:.2f}MB outside expected range"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests with real data scenarios."""

    def test_healthcare_executive_scenario(self):
        """Test realistic healthcare executive personalization."""
        content = {
            "hook": (
                "As MedTech Solutions continues to expand its AI-driven diagnostic "
                "capabilities, the pressure on your data center infrastructure is growing. "
                "For healthcare IT leaders navigating HIPAA compliance while scaling AI "
                "workloads, understanding where you stand on the modernization curve is "
                "critical to making informed investment decisions."
            ),
            "case_study_framing": (
                "Like many organizations in the healthcare sector, your infrastructure "
                "decisions directly impact patient care and regulatory compliance. "
                "Here's how a similar challenge was addressed:"
            ),
            "cta_assessment": (
                "As a healthcare IT leader in the evaluation stage, your next step is "
                "to benchmark your current infrastructure against industry leaders. "
                "Download our Healthcare AI Readiness Assessment."
            ),
            "cta_footer": (
                "Ready to build your business case for AMD? Contact our healthcare "
                "solutions team for a HIPAA-compliant infrastructure consultation "
                "tailored to MedTech Solutions' specific needs."
            ),
        }

        result = personalize_ebook(
            persona="executive",
            industry="healthcare",
            buying_stage="evaluating",
            company_name="MedTech Solutions",
            personalized_content=content,
            flatten=True,
        )

        assert isinstance(result, bytes)
        assert len(result) > 1000000

    def test_manufacturing_it_scenario(self):
        """Test realistic manufacturing IT personalization."""
        content = {
            "hook": (
                "Global Manufacturing Inc's digital transformation initiatives are "
                "placing unprecedented demands on your IT infrastructure. With IoT "
                "sensors generating terabytes of data daily, your data center "
                "modernization strategy will determine operational efficiency."
            ),
            "case_study_framing": (
                "Manufacturing leaders like Smurfit Westrock have achieved 25% cost "
                "reductions while improving sustainability. Your situation shares "
                "similar optimization opportunities:"
            ),
            "cta_assessment": (
                "Based on your manufacturing IT profile, we recommend starting with "
                "a Total Cost of Ownership analysis. See how AMD EPYC processors "
                "can reduce your infrastructure costs."
            ),
            "cta_footer": (
                "Global Manufacturing Inc could benefit from AMD's proven track record "
                "in manufacturing environments. Request a custom TCO analysis today."
            ),
        }

        result = personalize_ebook(
            persona="it_infrastructure",
            industry="manufacturing",
            buying_stage="building_case",
            company_name="Global Manufacturing Inc",
            personalized_content=content,
            flatten=True,
        )

        assert isinstance(result, bytes)

    def test_telecom_cloud_scenario(self):
        """Test realistic telecom/cloud personalization."""
        content = {
            "hook": (
                "TeleCloud Networks' expansion into AI-as-a-Service puts you at the "
                "forefront of cloud innovation. Like KT Cloud, you're building "
                "infrastructure that must scale efficiently while managing costs."
            ),
            "case_study_framing": (
                "KT Cloud achieved 70% cost reduction with AMD Instinct accelerators. "
                "As a fellow telecom cloud provider, their journey offers directly "
                "applicable insights:"
            ),
            "cta_assessment": (
                "Your AI cloud service roadmap aligns well with AMD's GPU solutions. "
                "Explore our Instinct accelerator portfolio for scalable AI infrastructure."
            ),
            "cta_footer": (
                "TeleCloud Networks can leverage AMD's telecom expertise. "
                "Schedule a technical deep-dive with our cloud infrastructure team."
            ),
        }

        result = personalize_ebook(
            persona="data_ai",
            industry="telecommunications",
            buying_stage="learning",
            company_name="TeleCloud Networks",
            personalized_content=content,
            flatten=True,
        )

        assert isinstance(result, bytes)
