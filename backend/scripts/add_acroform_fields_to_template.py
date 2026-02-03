#!/usr/bin/env python3
"""
Add AcroForm Text Fields to AMD Template

This script takes the existing amdtemplate.pdf and adds the required
text fields for personalization, producing amdtemplate_with_fields.pdf.

No Adobe required - uses pypdf and reportlab.

Usage:
    python scripts/add_acroform_fields_to_template.py

The script will:
1. Read the existing amdtemplate.pdf
2. Add text fields at specified locations on specific pages
3. Save as amdtemplate_with_fields.pdf

You can adjust FIELD_POSITIONS to fine-tune field placement.
"""

import io
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    DictionaryObject,
    ArrayObject,
    NameObject,
    NumberObject,
    TextStringObject,
    IndirectObject,
)
from pypdf.annotations import FreeText

# Paths
ASSETS_DIR = Path(__file__).parent.parent / "assets"
INPUT_PDF = ASSETS_DIR / "amdtemplate.pdf"
OUTPUT_PDF = ASSETS_DIR / "amdtemplate_with_fields.pdf"

# Field definitions with positions
# Format: (field_name, page_number (0-indexed), x, y, width, height)
# Note: PDF coordinates start from bottom-left
# Standard US Letter page is 612 x 792 points

FIELD_POSITIONS = [
    # Page 1 (Cover) - Personalized hook below the title
    {
        "name": "personalized_hook",
        "page": 0,  # Page 1 (0-indexed)
        "x": 50,
        "y": 100,  # Near bottom of page
        "width": 400,
        "height": 80,
        "font_size": 10,
        "description": "Personalized intro paragraph (500-800 chars)",
    },
    # Page 11 (KT Cloud case study) - Framing at top
    {
        "name": "case_study_1_framing",
        "page": 10,  # Page 11 (0-indexed)
        "x": 50,
        "y": 700,  # Near top
        "width": 500,
        "height": 50,
        "font_size": 9,
        "description": "KT Cloud case study context (200-300 chars)",
    },
    # Page 12 (Smurfit Westrock case study) - Framing at top
    {
        "name": "case_study_2_framing",
        "page": 11,  # Page 12 (0-indexed)
        "x": 50,
        "y": 700,
        "width": 500,
        "height": 50,
        "font_size": 9,
        "description": "Smurfit Westrock case study context (200-300 chars)",
    },
    # Page 13 (PQR case study) - Framing at top
    {
        "name": "case_study_3_framing",
        "page": 12,  # Page 13 (0-indexed)
        "x": 50,
        "y": 700,
        "width": 500,
        "height": 50,
        "font_size": 9,
        "description": "PQR case study context (200-300 chars)",
    },
    # Page 14 (Assessment) - CTA below questions
    {
        "name": "personalized_cta_assessment",
        "page": 13,  # Page 14 (0-indexed)
        "x": 50,
        "y": 100,
        "width": 500,
        "height": 60,
        "font_size": 10,
        "description": "Assessment page CTA (300-500 chars)",
    },
    # Page 16 (Final page) - Footer CTA
    {
        "name": "personalized_cta_footer",
        "page": 15,  # Page 16 (0-indexed)
        "x": 50,
        "y": 150,
        "width": 500,
        "height": 60,
        "font_size": 10,
        "description": "Final page CTA (300-500 chars)",
    },
]


def create_text_field_widget(
    field_name: str,
    x: float,
    y: float,
    width: float,
    height: float,
    font_size: int = 10,
) -> DictionaryObject:
    """
    Create a text field widget annotation dictionary.

    This creates the visual representation of the form field on the page.
    """
    # Field rectangle: [x1, y1, x2, y2] (bottom-left to top-right)
    rect = ArrayObject([
        NumberObject(x),
        NumberObject(y),
        NumberObject(x + width),
        NumberObject(y + height),
    ])

    # Create the widget annotation
    widget = DictionaryObject({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/FT"): NameObject("/Tx"),  # Text field
        NameObject("/T"): TextStringObject(field_name),  # Field name
        NameObject("/Rect"): rect,
        NameObject("/F"): NumberObject(4),  # Print flag
        NameObject("/Ff"): NumberObject(0),  # Field flags (0 = editable)
        # Default appearance string
        NameObject("/DA"): TextStringObject(f"/Helv {font_size} Tf 0 g"),
        # Border style
        NameObject("/BS"): DictionaryObject({
            NameObject("/Type"): NameObject("/Border"),
            NameObject("/W"): NumberObject(1),
            NameObject("/S"): NameObject("/S"),  # Solid
        }),
        # Appearance characteristics
        NameObject("/MK"): DictionaryObject({
            NameObject("/BC"): ArrayObject([NumberObject(0.8), NumberObject(0.8), NumberObject(0.8)]),  # Border color (gray)
            NameObject("/BG"): ArrayObject([NumberObject(1), NumberObject(1), NumberObject(1)]),  # Background (white)
        }),
    })

    return widget


def add_acroform_to_pdf(input_path: Path, output_path: Path, fields: list) -> dict:
    """
    Add AcroForm text fields to an existing PDF.

    Args:
        input_path: Path to source PDF
        output_path: Path for output PDF with fields
        fields: List of field definitions

    Returns:
        dict with status and field info
    """
    print(f"Reading: {input_path}")
    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    # Clone the document
    writer.clone_document_from_reader(reader)

    print(f"Pages: {len(writer.pages)}")

    # Track fields added
    fields_added = []
    field_references = []

    # Add fields to their respective pages
    for field_def in fields:
        page_num = field_def["page"]

        if page_num >= len(writer.pages):
            print(f"  WARNING: Page {page_num + 1} doesn't exist, skipping {field_def['name']}")
            continue

        page = writer.pages[page_num]

        # Create the text field widget
        widget = create_text_field_widget(
            field_name=field_def["name"],
            x=field_def["x"],
            y=field_def["y"],
            width=field_def["width"],
            height=field_def["height"],
            font_size=field_def.get("font_size", 10),
        )

        # Add page reference to widget
        widget[NameObject("/P")] = page.indirect_reference

        # Add widget as an indirect object
        widget_ref = writer._add_object(widget)
        field_references.append(widget_ref)

        # Add to page annotations
        if "/Annots" not in page:
            page[NameObject("/Annots")] = ArrayObject()
        page["/Annots"].append(widget_ref)

        fields_added.append({
            "name": field_def["name"],
            "page": page_num + 1,
            "position": f"({field_def['x']}, {field_def['y']})",
            "size": f"{field_def['width']}x{field_def['height']}",
        })

        print(f"  Added: {field_def['name']} on page {page_num + 1}")

    # Create or update the AcroForm dictionary
    if "/AcroForm" not in writer._root_object:
        writer._root_object[NameObject("/AcroForm")] = DictionaryObject()

    acroform = writer._root_object["/AcroForm"]

    # Set up the AcroForm
    if "/Fields" not in acroform:
        acroform[NameObject("/Fields")] = ArrayObject()

    # Add field references to AcroForm
    for ref in field_references:
        acroform["/Fields"].append(ref)

    # Add default resources for text rendering
    acroform[NameObject("/NeedAppearances")] = NameObject("/true")
    acroform[NameObject("/DA")] = TextStringObject("/Helv 10 Tf 0 g")

    # Add font resources if not present
    if "/DR" not in acroform:
        acroform[NameObject("/DR")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({
                NameObject("/Helv"): DictionaryObject({
                    NameObject("/Type"): NameObject("/Font"),
                    NameObject("/Subtype"): NameObject("/Type1"),
                    NameObject("/BaseFont"): NameObject("/Helvetica"),
                }),
            }),
        })

    # Write output
    print(f"\nWriting: {output_path}")
    with open(output_path, "wb") as f:
        writer.write(f)

    return {
        "success": True,
        "input": str(input_path),
        "output": str(output_path),
        "fields_added": fields_added,
        "total_pages": len(writer.pages),
    }


def verify_fields(pdf_path: Path) -> dict:
    """Verify that fields were added correctly."""
    reader = PdfReader(str(pdf_path))
    fields = reader.get_fields()

    if not fields:
        return {"has_fields": False, "fields": []}

    field_list = []
    for name, field in fields.items():
        field_type = str(field.get("/FT", "Unknown"))
        field_list.append({
            "name": name,
            "type": "Text" if field_type == "/Tx" else field_type,
        })

    return {"has_fields": True, "fields": field_list}


def main():
    print("=" * 60)
    print("ADD ACROFORM FIELDS TO AMD TEMPLATE")
    print("=" * 60)

    # Check input exists
    if not INPUT_PDF.exists():
        print(f"\nERROR: Input file not found: {INPUT_PDF}")
        print("Make sure amdtemplate.pdf exists in backend/assets/")
        return

    print(f"\nInput:  {INPUT_PDF}")
    print(f"Output: {OUTPUT_PDF}")
    print(f"\nFields to add: {len(FIELD_POSITIONS)}")
    for f in FIELD_POSITIONS:
        print(f"  - {f['name']} (Page {f['page'] + 1}): {f['description']}")

    print("\n" + "-" * 60)
    print("ADDING FIELDS")
    print("-" * 60)

    # Add fields
    result = add_acroform_to_pdf(INPUT_PDF, OUTPUT_PDF, FIELD_POSITIONS)

    print("\n" + "-" * 60)
    print("VERIFYING RESULT")
    print("-" * 60)

    # Verify
    verification = verify_fields(OUTPUT_PDF)

    if verification["has_fields"]:
        print(f"\nFound {len(verification['fields'])} fields in output:")

        # Separate text fields from buttons
        text_fields = [f for f in verification["fields"] if f["type"] == "Text"]
        button_fields = [f for f in verification["fields"] if f["type"] != "Text"]

        print(f"\n  TEXT FIELDS (for personalization): {len(text_fields)}")
        for f in text_fields:
            print(f"    ✓ {f['name']}")

        if button_fields:
            print(f"\n  BUTTON FIELDS (navigation, pre-existing): {len(button_fields)}")
    else:
        print("\nWARNING: No fields found in output PDF")

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    print(f"\nOutput saved to: {OUTPUT_PDF}")
    print("\nNext steps:")
    print("1. Open the PDF to verify field positions visually")
    print("2. Adjust FIELD_POSITIONS in this script if needed")
    print("3. Run the validation:")
    print('   python -c "from app.services.pdf_personalization_service import validate_template; print(validate_template())"')

    # Also create a position guide
    print("\n" + "-" * 60)
    print("FIELD POSITION GUIDE")
    print("-" * 60)
    print("""
To adjust field positions, edit FIELD_POSITIONS in this script:

- x: Distance from LEFT edge (0-612 for US Letter)
- y: Distance from BOTTOM edge (0-792 for US Letter)
- width: Field width in points
- height: Field height in points

Common positions:
- Top of page: y = 700-750
- Middle of page: y = 350-400
- Bottom of page: y = 50-150
- Left margin: x = 50
- Full width: width = 500
""")


if __name__ == "__main__":
    main()
