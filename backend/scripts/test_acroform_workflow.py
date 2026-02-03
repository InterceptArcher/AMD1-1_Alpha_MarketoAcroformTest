#!/usr/bin/env python3
"""
Test AcroForm Workflow

This script:
1. Creates a sample PDF with AcroForm text fields
2. Fills those fields with personalized content
3. Flattens the PDF
4. Validates the workflow works end-to-end

Run: python scripts/test_acroform_workflow.py
"""

import io
from pathlib import Path

# Check if pypdf is available
try:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject, TextStringObject
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    print("ERROR: pypdf not installed. Run: pip install pypdf")

# Check if reportlab is available (for creating test PDF with fields)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import black, white
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("WARNING: reportlab not installed. Cannot create test PDF.")


def create_test_pdf_with_fields() -> bytes:
    """
    Create a simple test PDF with AcroForm text fields.

    This simulates what the design team will deliver.
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab required to create test PDF")

    from reportlab.pdfbase import pdfform
    from reportlab.lib.colors import magenta, pink, blue, green

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pageSize=letter)

    # Page 1 - Cover with hook field
    c.setFillColor(black)
    c.rect(0, 0, 612, 792, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, 700, "AMD Enterprise AI Readiness")
    c.setFont("Helvetica", 12)
    c.drawString(50, 650, "Personalized for: [Your Company]")

    # Add a text field for the hook
    c.setFont("Helvetica", 10)
    c.drawString(50, 600, "Your personalized introduction:")

    # Create form field - this is the key part
    form = c.acroForm
    form.textfield(
        name='personalized_hook',
        x=50,
        y=450,
        width=500,
        height=120,
        fontName='Helvetica',
        fontSize=10,
        borderColor=blue,
        fillColor=white,
        textColor=black,
        forceBorder=True,
        value='',  # Empty - will be filled by backend
    )

    c.showPage()

    # Page 2 - Case Study with framing field
    c.setFillColor(white)
    c.rect(0, 0, 612, 792, fill=1)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 700, "Case Study: KT Cloud")

    c.setFont("Helvetica", 10)
    c.drawString(50, 650, "Context for your industry:")

    form.textfield(
        name='case_study_1_framing',
        x=50,
        y=550,
        width=500,
        height=80,
        fontName='Helvetica',
        fontSize=10,
        borderColor=green,
        fillColor=white,
        textColor=black,
        forceBorder=True,
        value='',
    )

    c.drawString(50, 500, "[Case study content would go here...]")

    c.showPage()

    # Page 3 - CTA page
    c.setFillColor(white)
    c.rect(0, 0, 612, 792, fill=1)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 700, "Your Next Steps")

    c.setFont("Helvetica", 10)
    c.drawString(50, 650, "Personalized call to action:")

    form.textfield(
        name='personalized_cta_footer',
        x=50,
        y=550,
        width=500,
        height=80,
        fontName='Helvetica',
        fontSize=10,
        borderColor=magenta,
        fillColor=white,
        textColor=black,
        forceBorder=True,
        value='',
    )

    c.save()
    buffer.seek(0)
    return buffer.read()


def inspect_pdf_fields(pdf_bytes: bytes) -> dict:
    """Inspect a PDF and return its form fields."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    fields = reader.get_fields()

    if not fields:
        return {"has_fields": False, "fields": []}

    field_info = []
    for name, field in fields.items():
        field_info.append({
            "name": name,
            "type": str(field.get("/FT", "Unknown")),
            "value": str(field.get("/V", "")),
        })

    return {"has_fields": True, "fields": field_info}


def fill_pdf_fields(pdf_bytes: bytes, field_values: dict) -> bytes:
    """Fill form fields in a PDF."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    # Clone the entire document (preserves AcroForm)
    writer.clone_document_from_reader(reader)

    # Fill form fields
    writer.update_page_form_field_values(
        writer.pages[0],
        field_values
    )

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.read()


def flatten_pdf(pdf_bytes: bytes) -> bytes:
    """Flatten PDF to make form fields static."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Remove AcroForm to flatten
    if "/AcroForm" in writer._root_object:
        del writer._root_object["/AcroForm"]

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.read()


def check_existing_template():
    """Check if the real AMD template has form fields."""
    template_path = Path(__file__).parent.parent / "assets" / "amdtemplate.pdf"
    template_with_fields_path = Path(__file__).parent.parent / "assets" / "amdtemplate_with_fields.pdf"

    print("\n" + "="*60)
    print("CHECKING EXISTING TEMPLATES")
    print("="*60)

    # Check original template
    if template_path.exists():
        print(f"\n[Original Template] {template_path}")
        with open(template_path, "rb") as f:
            pdf_bytes = f.read()

        reader = PdfReader(io.BytesIO(pdf_bytes))
        fields = reader.get_fields()

        print(f"  Pages: {len(reader.pages)}")
        if fields:
            print(f"  Form Fields: {len(fields)}")
            for name in fields.keys():
                print(f"    - {name}")
        else:
            print("  Form Fields: NONE (static PDF)")
            print("  Status: Needs AcroForm fields added by design team")
    else:
        print(f"\n[Original Template] NOT FOUND at {template_path}")

    # Check template with fields
    if template_with_fields_path.exists():
        print(f"\n[Template with Fields] {template_with_fields_path}")
        with open(template_with_fields_path, "rb") as f:
            pdf_bytes = f.read()

        reader = PdfReader(io.BytesIO(pdf_bytes))
        fields = reader.get_fields()

        print(f"  Pages: {len(reader.pages)}")
        if fields:
            print(f"  Form Fields: {len(fields)}")
            for name, field in fields.items():
                print(f"    - {name}: {field.get('/FT', 'Unknown')}")
        else:
            print("  Form Fields: NONE")
    else:
        print(f"\n[Template with Fields] NOT FOUND")
        print("  Status: Waiting for design team to deliver")


def main():
    print("="*60)
    print("ACROFORM WORKFLOW TEST")
    print("="*60)

    if not PYPDF_AVAILABLE:
        print("\nERROR: pypdf is required. Install with: pip install pypdf")
        return

    # First, check existing templates
    check_existing_template()

    if not REPORTLAB_AVAILABLE:
        print("\n" + "="*60)
        print("SKIPPING TEST PDF CREATION (reportlab not installed)")
        print("="*60)
        print("\nTo run full test, install reportlab: pip install reportlab")
        return

    print("\n" + "="*60)
    print("CREATING TEST PDF WITH ACROFORM FIELDS")
    print("="*60)

    # Step 1: Create test PDF with fields
    print("\n[Step 1] Creating test PDF with form fields...")
    test_pdf = create_test_pdf_with_fields()
    print(f"  Created PDF: {len(test_pdf)} bytes")

    # Step 2: Inspect fields
    print("\n[Step 2] Inspecting form fields...")
    field_info = inspect_pdf_fields(test_pdf)
    if field_info["has_fields"]:
        print(f"  Found {len(field_info['fields'])} fields:")
        for f in field_info["fields"]:
            print(f"    - {f['name']} ({f['type']})")
    else:
        print("  ERROR: No fields found!")
        return

    # Step 3: Fill fields with personalized content
    print("\n[Step 3] Filling fields with personalized content...")
    personalized_content = {
        "personalized_hook": (
            "As Acme Healthcare continues to expand its AI-driven diagnostic capabilities, "
            "the pressure on your data center infrastructure is growing rapidly. For IT leaders "
            "like yourself navigating HIPAA compliance while scaling AI workloads, understanding "
            "where you stand on the modernization curve is critical to making informed investment decisions."
        ),
        "case_study_1_framing": (
            "Like many organizations in the healthcare sector, your infrastructure decisions "
            "directly impact patient care and regulatory compliance. Here's how a similar "
            "challenge was addressed:"
        ),
        "personalized_cta_footer": (
            "Ready to build your business case for AMD? As a healthcare IT leader in the "
            "evaluation stage, we recommend starting with our HIPAA-compliant AI infrastructure "
            "assessment. Contact our healthcare solutions team for a personalized consultation."
        ),
    }

    filled_pdf = fill_pdf_fields(test_pdf, personalized_content)
    print(f"  Filled PDF: {len(filled_pdf)} bytes")

    # Step 4: Verify fields were filled
    print("\n[Step 4] Verifying filled content...")
    filled_info = inspect_pdf_fields(filled_pdf)
    for f in filled_info["fields"]:
        value_preview = f["value"][:50] + "..." if len(f["value"]) > 50 else f["value"]
        print(f"    - {f['name']}: {value_preview}")

    # Step 5: Flatten PDF
    print("\n[Step 5] Flattening PDF (making fields static)...")
    flattened_pdf = flatten_pdf(filled_pdf)
    print(f"  Flattened PDF: {len(flattened_pdf)} bytes")

    # Step 6: Verify flattening
    print("\n[Step 6] Verifying flattening...")
    flattened_info = inspect_pdf_fields(flattened_pdf)
    if flattened_info["has_fields"]:
        print("  WARNING: PDF still has form fields (partial flattening)")
    else:
        print("  SUCCESS: PDF is now static (no editable fields)")

    # Save test outputs
    output_dir = Path(__file__).parent.parent / "test_outputs"
    output_dir.mkdir(exist_ok=True)

    (output_dir / "test_template_with_fields.pdf").write_bytes(test_pdf)
    (output_dir / "test_filled.pdf").write_bytes(filled_pdf)
    (output_dir / "test_flattened.pdf").write_bytes(flattened_pdf)

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print(f"\nTest files saved to: {output_dir}")
    print("  - test_template_with_fields.pdf (empty form)")
    print("  - test_filled.pdf (with personalized content)")
    print("  - test_flattened.pdf (static, no editable fields)")

    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Design team creates 'amdtemplate_with_fields.pdf' with:
   - personalized_hook (Page 1)
   - case_study_1_framing (Page 11)
   - case_study_2_framing (Page 12)
   - case_study_3_framing (Page 13)
   - personalized_cta_assessment (Page 14)
   - personalized_cta_footer (Page 16)

2. Place template at: backend/assets/amdtemplate_with_fields.pdf

3. Run validation:
   python -c "from app.services.pdf_personalization_service import validate_template; print(validate_template())"

4. Integration is already built in pdf_personalization_service.py
""")


if __name__ == "__main__":
    main()
