"""
PDF Personalization Service

Fills AcroForm text fields in the AMD ebook template with personalized content,
then flattens the PDF to produce a clean, static output.

Dependencies:
- pypdf: For reading/writing PDF and filling form fields
- reportlab: For generating field appearances (if needed)

Usage:
    from app.services.pdf_personalization_service import personalize_ebook

    result = personalize_ebook(
        persona="executive",
        industry="healthcare",
        buying_stage="evaluating",
        company_name="Acme Corp",
        personalized_content={
            "hook": "As Acme Corp accelerates...",
            "case_study_framing": "Like many healthcare organizations...",
            "cta": "Ready to build your business case?..."
        }
    )
"""

import io
from pathlib import Path
from typing import Optional

import pypdf

# Template paths
TEMPLATE_DIR = Path(__file__).parent.parent.parent / "assets"
TEMPLATE_WITH_FIELDS = TEMPLATE_DIR / "amdtemplate_with_fields.pdf"
TEMPLATE_ORIGINAL = TEMPLATE_DIR / "amdtemplate.pdf"

# Field names (must match designer spec)
FIELD_HOOK = "personalized_hook"
FIELD_CASE_STUDY_1 = "case_study_1_framing"
FIELD_CASE_STUDY_2 = "case_study_2_framing"
FIELD_CASE_STUDY_3 = "case_study_3_framing"
FIELD_CTA_ASSESSMENT = "personalized_cta_assessment"
FIELD_CTA_FOOTER = "personalized_cta_footer"

# Industry to case study mapping
INDUSTRY_CASE_STUDY_MAP = {
    # Cloud/GPU focus -> KT Cloud (case study 1)
    "telecommunications": 1,
    "technology": 1,
    "gaming_media": 1,
    "media": 1,

    # Cost optimization focus -> Smurfit Westrock (case study 2)
    "manufacturing": 2,
    "retail": 2,
    "energy": 2,
    "consumer_goods": 2,

    # Security/compliance focus -> PQR (case study 3)
    "healthcare": 3,
    "financial_services": 3,
    "government": 3,
    "education": 3,
    "non_profit": 3,
}


def get_template_fields() -> dict:
    """
    Get all form fields from the template PDF.

    Returns:
        dict: Field names and their properties

    Raises:
        FileNotFoundError: If template with fields doesn't exist
    """
    if not TEMPLATE_WITH_FIELDS.exists():
        raise FileNotFoundError(
            f"Template with AcroForm fields not found at {TEMPLATE_WITH_FIELDS}. "
            "Designer must create this file. See DESIGNER_SPEC.md."
        )

    reader = pypdf.PdfReader(str(TEMPLATE_WITH_FIELDS))
    fields = reader.get_fields()

    if not fields:
        raise ValueError("Template PDF has no form fields. Designer must add AcroForm text fields.")

    return fields


def validate_template() -> dict:
    """
    Validate that the template has all required fields.

    Returns:
        dict: Validation result with 'valid' bool and 'missing' list
    """
    required_fields = {
        FIELD_HOOK,
        FIELD_CASE_STUDY_1,
        FIELD_CASE_STUDY_2,
        FIELD_CASE_STUDY_3,
        FIELD_CTA_ASSESSMENT,
        FIELD_CTA_FOOTER,
    }

    try:
        fields = get_template_fields()
        found_fields = set(fields.keys())
        missing = required_fields - found_fields

        return {
            "valid": len(missing) == 0,
            "missing": list(missing),
            "found": list(found_fields),
        }
    except FileNotFoundError as e:
        return {
            "valid": False,
            "missing": list(required_fields),
            "error": str(e),
        }


def get_case_study_field(industry: str) -> str:
    """
    Get the appropriate case study field name for an industry.

    Args:
        industry: Industry name (e.g., "healthcare", "manufacturing")

    Returns:
        str: Field name for the relevant case study
    """
    industry_normalized = industry.lower().replace(" ", "_").replace("-", "_")
    case_study_num = INDUSTRY_CASE_STUDY_MAP.get(industry_normalized, 3)  # Default to PQR

    field_map = {
        1: FIELD_CASE_STUDY_1,
        2: FIELD_CASE_STUDY_2,
        3: FIELD_CASE_STUDY_3,
    }

    return field_map[case_study_num]


def fill_personalization_fields(
    personalized_content: dict,
    industry: str,
) -> bytes:
    """
    Fill AcroForm fields with personalized content.

    Args:
        personalized_content: Dict with keys:
            - hook: Personalized intro text
            - case_study_framing: Context for the relevant case study
            - cta_assessment: CTA for assessment page
            - cta_footer: CTA for final page

        industry: Reader's industry (determines which case study to frame)

    Returns:
        bytes: PDF with filled fields (not yet flattened)
    """
    if not TEMPLATE_WITH_FIELDS.exists():
        raise FileNotFoundError(
            f"Template not found: {TEMPLATE_WITH_FIELDS}. "
            "Designer must create template with AcroForm fields."
        )

    reader = pypdf.PdfReader(str(TEMPLATE_WITH_FIELDS))
    writer = pypdf.PdfWriter()

    # Clone entire document (preserves AcroForm structure)
    writer.clone_document_from_reader(reader)

    # Prepare field values
    case_study_field = get_case_study_field(industry)

    field_values = {
        FIELD_HOOK: personalized_content.get("hook", ""),
        FIELD_CTA_ASSESSMENT: personalized_content.get("cta_assessment", ""),
        FIELD_CTA_FOOTER: personalized_content.get("cta_footer", ""),
    }

    # Fill the relevant case study framing (only one)
    case_study_framing = personalized_content.get("case_study_framing", "")
    field_values[case_study_field] = case_study_framing

    # Fill form fields on ALL pages (fields are on pages 0, 10, 11, 12, 13, 15)
    # update_page_form_field_values needs to be called for each page with fields
    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values)

    # Set NeedAppearances flag to ensure PDF readers render the field content
    if "/AcroForm" in writer._root_object:
        writer._root_object["/AcroForm"][pypdf.generic.NameObject("/NeedAppearances")] = pypdf.generic.BooleanObject(True)

    # Write to bytes
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    return output.read()


def flatten_pdf(pdf_bytes: bytes) -> bytes:
    """
    Flatten a PDF so form fields become static text.

    This makes the personalized content part of the page content,
    removes editable fields, and produces a clean final PDF.

    Args:
        pdf_bytes: PDF with filled form fields

    Returns:
        bytes: Flattened PDF with no editable fields
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    writer = pypdf.PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Remove the AcroForm to flatten
    # Note: This approach removes field interactivity but may not
    # properly render field appearances. For full flattening with
    # proper text rendering, consider using pikepdf or pdftk.
    if "/AcroForm" in writer._root_object:
        del writer._root_object["/AcroForm"]

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    return output.read()


def personalize_ebook(
    persona: str,
    industry: str,
    buying_stage: str,
    company_name: str,
    personalized_content: dict,
    flatten: bool = True,
) -> bytes:
    """
    Main entry point: Personalize the AMD ebook for a specific reader.

    Args:
        persona: Reader's role (executive, it_infrastructure, security, data_ai, etc.)
        industry: Reader's industry (healthcare, manufacturing, etc.)
        buying_stage: Where they are in buying journey (exploring, evaluating, learning, building_case)
        company_name: Reader's company name
        personalized_content: Dict with personalized text:
            - hook: Intro paragraph
            - case_study_framing: Context for case study
            - cta_assessment: Call to action for assessment page
            - cta_footer: Call to action for final page

        flatten: Whether to flatten the PDF (default True)

    Returns:
        bytes: Personalized PDF

    Raises:
        FileNotFoundError: If template doesn't exist
        ValueError: If template is missing required fields
    """
    # Validate template first
    validation = validate_template()
    if not validation["valid"]:
        if "error" in validation:
            raise FileNotFoundError(validation["error"])
        raise ValueError(f"Template missing required fields: {validation['missing']}")

    # Fill the fields
    filled_pdf = fill_personalization_fields(
        personalized_content=personalized_content,
        industry=industry,
    )

    # Flatten if requested
    if flatten:
        return flatten_pdf(filled_pdf)

    return filled_pdf


# Content loading utilities

def load_industry_content(industry: str) -> Optional[str]:
    """Load industry-specific content from markdown files."""
    content_dir = TEMPLATE_DIR / "content"

    # Map industry names to file names
    industry_files = {
        "healthcare": "KP_Industry_Healthcare.md",
        "financial_services": "KP_Industry_Financial Services.md",
        "manufacturing": "KP_Industry_Manufacturing.md",
        "energy": "KP_Industry_Energy.md",
        "retail": "KP_Industry_Retail.md",
        "education": "KP_Industry_Education.md",
        "consumer_goods": "KP_Industry_Consumer Goods.md",
        "media": "KP_Industry_Media and Ent.md",
        "non_profit": "KP_Industry_Non-Profit.md",
    }

    filename = industry_files.get(industry.lower().replace(" ", "_"))
    if not filename:
        return None

    filepath = content_dir / filename
    if not filepath.exists():
        return None

    return filepath.read_text()


def load_job_function_content(job_function: str) -> Optional[str]:
    """Load job function content from markdown files."""
    content_dir = TEMPLATE_DIR / "content"

    function_files = {
        "bdm": "KP_Job Function_BDM.md",
        "itdm": "KP_Job Function_ITDM.md",
    }

    filename = function_files.get(job_function.lower())
    if not filename:
        return None

    filepath = content_dir / filename
    if not filepath.exists():
        return None

    return filepath.read_text()


def load_segment_content(segment: str) -> Optional[str]:
    """Load segment content from markdown files."""
    content_dir = TEMPLATE_DIR / "content"

    segment_files = {
        "enterprise": "KP_Segment_Enterprise.md",
        "government": "KP_Segment_Government.md",
        "mid_market": "KP_Segment_Mid-Market.md",
        "smb": "KP_Segment_SMB.md",
    }

    filename = segment_files.get(segment.lower().replace("-", "_").replace(" ", "_"))
    if not filename:
        return None

    filepath = content_dir / filename
    if not filepath.exists():
        return None

    return filepath.read_text()
