#!/usr/bin/env python3
"""
Quick test script to generate a sample PDF using the HTML template approach.
Run: python scripts/test_pdf_generation.py
Output: test_output.pdf
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pdf_service import PDFService
from app.services.ebook_content import (
    get_case_study_for_industry,
    load_industry_content,
    get_industry_key_insights,
)


async def main():
    # Test data
    profile = {
        "email": "john.smith@acme.com",
        "first_name": "John",
        "last_name": "Smith",
        "title": "VP of Infrastructure",
        "company_name": "Acme Healthcare Systems",
        "industry": "Healthcare",
    }

    user_context = {
        "goal": "evaluating",
        "persona": "it_infrastructure",
        "industry_input": "healthcare",
    }

    personalization = {
        "personalized_hook": (
            "As Acme Healthcare Systems continues to navigate the complex intersection of "
            "patient data security and AI innovation, your infrastructure decisions become "
            "increasingly critical. For IT leaders like yourself managing healthcare systems, "
            "understanding where you stand on the modernization curve isn't just about "
            "technology—it's about enabling better patient outcomes while maintaining the "
            "highest standards of data protection and regulatory compliance."
        ),
        "case_study_framing": (
            "Like many organizations in the healthcare sector, your infrastructure decisions "
            "directly impact both patient care quality and regulatory compliance. Here's how "
            "a similar challenge around security, scalability, and operational efficiency "
            "was addressed using AMD solutions."
        ),
        "personalized_cta": (
            "Ready to explore how AMD can help Acme Healthcare Systems modernize its data center "
            "infrastructure while maintaining HIPAA compliance? Our healthcare-specialized team "
            "can provide a custom assessment of your current environment and identify the most "
            "cost-effective path to AI readiness. Schedule a confidential consultation today."
        ),
    }

    print("=" * 60)
    print("PDF Generation Test")
    print("=" * 60)

    # Test content loading
    print("\n1. Testing content file loading...")
    industry_content = load_industry_content("healthcare")
    if industry_content:
        print(f"   ✓ Loaded healthcare content: {len(industry_content):,} chars")
    else:
        print("   ✗ Failed to load healthcare content")

    insights = get_industry_key_insights("healthcare")
    print(f"   ✓ Extracted insights: {len(insights['trends'])} trends, {len(insights['priorities'])} priorities")

    # Test case study mapping
    print("\n2. Testing case study mapping...")
    case_study = get_case_study_for_industry("healthcare")
    print(f"   ✓ Healthcare -> {case_study['company']} ({case_study['industry']})")

    case_study = get_case_study_for_industry("manufacturing")
    print(f"   ✓ Manufacturing -> {case_study['company']} ({case_study['industry']})")

    case_study = get_case_study_for_industry("telecommunications")
    print(f"   ✓ Telecommunications -> {case_study['company']} ({case_study['industry']})")

    # Generate PDF
    print("\n3. Generating PDF...")
    service = PDFService(supabase_client=None)

    try:
        result = await service.generate_amd_ebook(
            job_id=12345,
            profile=profile,
            personalization=personalization,
            user_context=user_context,
        )

        print(f"   ✓ Generated PDF: {result['file_size_bytes']:,} bytes")
        print(f"   ✓ Case study used: {result['case_study_used']}")

        # Save to file for inspection
        if result["pdf_url"].startswith("data:"):
            import base64
            pdf_data = result["pdf_url"].split(",")[1]
            pdf_bytes = base64.b64decode(pdf_data)

            output_path = Path(__file__).parent.parent / "test_output.pdf"
            output_path.write_bytes(pdf_bytes)
            print(f"\n   → Saved to: {output_path}")
            print(f"   → Open it to verify the layout!")
        else:
            print(f"   → URL: {result['pdf_url']}")

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
