#!/usr/bin/env python3
"""
Full End-to-End Personalization Test

This script tests the complete workflow:
1. Load the template with fields
2. Fill with sample personalized content
3. Flatten the PDF
4. Save the result

Run: python scripts/test_full_personalization.py
"""

from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pdf_personalization_service import (
    personalize_ebook,
    validate_template,
    TEMPLATE_WITH_FIELDS,
)


def main():
    print("=" * 60)
    print("FULL PERSONALIZATION TEST")
    print("=" * 60)

    # Step 1: Validate template
    print("\n[Step 1] Validating template...")
    validation = validate_template()

    if not validation["valid"]:
        print(f"  ERROR: Template validation failed")
        print(f"  Missing: {validation.get('missing', [])}")
        return

    print(f"  ✓ Template valid with {len(validation['found'])} fields")

    # Step 2: Prepare personalized content
    print("\n[Step 2] Preparing personalized content...")

    # Sample content for a Healthcare IT Executive in the Evaluating stage
    personalized_content = {
        "hook": (
            "As Acme Healthcare continues to expand its AI-driven diagnostic capabilities, "
            "the pressure on your data center infrastructure is growing rapidly. For IT leaders "
            "like yourself navigating HIPAA compliance while scaling AI workloads, understanding "
            "where you stand on the modernization curve is critical to making informed investment "
            "decisions that protect both patient data and your organization's competitive edge."
        ),
        "case_study_framing": (
            "Like many organizations in the healthcare sector, your infrastructure decisions "
            "directly impact patient care, data security, and regulatory compliance. Here's how "
            "a similar challenge was addressed with AMD technology:"
        ),
        "cta_assessment": (
            "Based on your responses, you're well-positioned to accelerate your AI journey. "
            "As Acme Healthcare's IT leader, your next step is to benchmark your current "
            "infrastructure against industry leaders. Download our Healthcare AI Readiness "
            "Assessment to identify specific optimization opportunities."
        ),
        "cta_footer": (
            "Ready to build your business case for AMD? As a healthcare IT leader in the "
            "evaluation stage, we recommend starting with our HIPAA-compliant AI infrastructure "
            "assessment. Contact our healthcare solutions team at enterprise@amd.com for a "
            "personalized consultation tailored to Acme Healthcare's specific needs."
        ),
    }

    print(f"  Hook: {len(personalized_content['hook'])} chars")
    print(f"  Case Study: {len(personalized_content['case_study_framing'])} chars")
    print(f"  CTA Assessment: {len(personalized_content['cta_assessment'])} chars")
    print(f"  CTA Footer: {len(personalized_content['cta_footer'])} chars")

    # Step 3: Generate personalized PDF
    print("\n[Step 3] Generating personalized PDF...")

    try:
        pdf_bytes = personalize_ebook(
            persona="executive",
            industry="healthcare",
            buying_stage="evaluating",
            company_name="Acme Healthcare",
            personalized_content=personalized_content,
            flatten=True,
        )

        print(f"  ✓ Generated PDF: {len(pdf_bytes):,} bytes")

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 4: Save output
    print("\n[Step 4] Saving output...")

    output_dir = Path(__file__).parent.parent / "test_outputs"
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "personalized_ebook_healthcare_executive.pdf"
    output_path.write_bytes(pdf_bytes)

    print(f"  ✓ Saved to: {output_path}")

    # Step 5: Verify output
    print("\n[Step 5] Verifying output...")

    from pypdf import PdfReader
    import io

    reader = PdfReader(io.BytesIO(pdf_bytes))
    fields = reader.get_fields()

    print(f"  Pages: {len(reader.pages)}")

    if fields:
        text_fields = [name for name, f in fields.items() if str(f.get("/FT", "")) == "/Tx"]
        print(f"  Form fields remaining: {len(text_fields)} text fields")
        print("  WARNING: PDF may not be fully flattened")
    else:
        print("  ✓ No editable form fields (properly flattened)")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print(f"\nPersonalized PDF saved to:")
    print(f"  {output_path}")
    print("\nOpen this file to verify:")
    print("  - Page 1: Personalized hook appears")
    print("  - Page 13: PQR case study has healthcare framing")
    print("  - Page 14: Assessment CTA appears")
    print("  - Page 16: Footer CTA appears")


if __name__ == "__main__":
    main()
