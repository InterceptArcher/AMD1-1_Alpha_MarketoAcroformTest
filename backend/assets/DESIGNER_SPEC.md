# PDF Template Specification for Dynamic Personalization

## Overview

The Intercept content team needs to create **one PDF template** with editable AcroForm text fields in specific locations. The backend will fill these fields with personalized content, then flatten the PDF so fields become static text.

---

## Current PDF Structure (16 pages)

| Page | Content | Personalization Needed |
|------|---------|------------------------|
| 1 | Cover + Intro | **YES - HOOK FIELD** |
| 2 | Table of Contents | No |
| 3 | Redefining the Data Center | No |
| 4 | Three Stages of Modernization | No |
| 5 | Data Center Leaders | No |
| 6 | Data Center Challengers | No |
| 7 | Data Center Observers | No |
| 8 | Path to Leadership | No |
| 9 | Modernization Models | No |
| 10 | Customer Success Snapshots Intro | No |
| 11 | Case Study 1 (KT Cloud) | **YES - CASE STUDY FRAMING** |
| 12 | Case Study 2 (Smurfit Westrock) | **YES - CASE STUDY FRAMING** |
| 13 | Case Study 3 (PQR) | **YES - CASE STUDY FRAMING** |
| 14 | Assessment Questions | **YES - CTA FIELD** |
| 15 | Why AMD | No |
| 16 | AI PCs + Footer | **YES - CTA FIELD** |

---

## Required AcroForm Text Fields

### 1. HOOK FIELD (Page 1)

**Field Name:** `personalized_hook`

**Location:** Below the title "FROM OBSERVERS TO LEADERS" or in the intro section area

**Purpose:** A personalized opening paragraph that addresses the reader directly based on their:
- Role/persona (Executive, IT Infrastructure, Security, Data/AI, etc.)
- Company context (recent news, industry challenges)
- Buying stage (Exploring, Evaluating, Learning, Building Case)

**Specifications:**
- **Type:** Multi-line text field
- **Max Characters:** ~500-800 characters (2-3 sentences)
- **Font:** Match surrounding body text (should match existing intro font)
- **Size:** Approximately 3-4 lines of text
- **Appearance:** No visible border when flattened

**Example Content:**
> "As [Company Name] continues to expand its AI capabilities in the healthcare sector, the pressure on your data center infrastructure is only growing. For IT leaders like yourself navigating this transformation, understanding where you stand on the modernization curve is critical to making informed investment decisions."

---

### 2. CASE STUDY FRAMING FIELDS (Pages 11, 12, 13)

**Field Names:**
- `case_study_1_framing` (Page 11 - KT Cloud)
- `case_study_2_framing` (Page 12 - Smurfit Westrock)
- `case_study_3_framing` (Page 13 - PQR)

**Location:** At the TOP of each case study page, before the case study title

**Purpose:** A brief intro sentence that connects the case study to the reader's industry/situation

**Specifications:**
- **Type:** Single or multi-line text field
- **Max Characters:** ~200-300 characters (1-2 sentences)
- **Font:** Italicized or slightly different style to distinguish from case study content
- **Size:** 1-2 lines
- **Appearance:** No visible border when flattened

**Example Content:**
> "Like many organizations in the financial services sector, your infrastructure decisions directly impact security and compliance. Here's how a similar challenge was addressed:"

**Note:** Only ONE case study framing will be filled based on the reader's industry. The other two will be left empty or filled with generic text.

---

### 3. CTA FIELDS (Pages 14 and 16)

**Field Names:**
- `personalized_cta_assessment` (Page 14 - Assessment Questions page)
- `personalized_cta_footer` (Page 16 - Final page)

**Location:**
- Page 14: Below the assessment questions or in a call-out box
- Page 16: In the footer area or as a final call-to-action block

**Purpose:** Personalized next-step recommendation based on the reader's buying stage

**Specifications:**
- **Type:** Multi-line text field
- **Max Characters:** ~300-500 characters
- **Font:** Match CTA styling (may be bold or in a colored box)
- **Appearance:** No visible border when flattened

**Example Content (for "Building Case" stage):**
> "Ready to build your business case for AMD? Download our ROI Calculator and Executive Brief to quantify the impact of data center modernization for [Company Name]. Our team can also provide a custom TCO analysis for your specific infrastructure."

---

## Technical Requirements for Designer

### AcroForm Field Settings

1. **Field Type:** Text Field (not button, checkbox, etc.)
2. **Multi-line:** Enable for all fields except short framings
3. **Font Embedding:** Ensure all fonts used are embedded in the PDF
4. **Default Value:** Leave empty or use placeholder like `{{personalized_hook}}`
5. **Field Appearance:**
   - Border: None (or very subtle)
   - Background: Transparent or matching page background
   - Text color: Match surrounding text
6. **Read-Only:** Do NOT set as read-only (we need to fill them)
7. **Required:** Not required

### Naming Convention

Use these exact field names (case-sensitive):
```
personalized_hook
case_study_1_framing
case_study_2_framing
case_study_3_framing
personalized_cta_assessment
personalized_cta_footer
```

### Font Considerations

- Use fonts that are embeddable and commonly available
- If using custom AMD brand fonts, ensure they're embedded
- The backend will use the font defined in the field appearance

---

## Delivery

Please deliver:
1. **One PDF file** with all 6 AcroForm text fields configured
2. **Field names** exactly as specified above
3. **Embedded fonts** for all text that may appear in fields

Save as: `amdtemplate_with_fields.pdf` in `/backend/assets/`

---

## Questions?

Contact the engineering team if you need clarification on:
- Field positioning
- Character limits
- Font specifications
- Any technical constraints

---

## Appendix: Industry → Case Study Mapping

The backend will select the most relevant case study based on the reader's industry:

| Reader's Industry | Primary Case Study | Reason |
|-------------------|-------------------|--------|
| Telecommunications, Technology, Gaming/Media | KT Cloud (Page 11) | Cloud/GPU focus |
| Manufacturing, Retail, Energy | Smurfit Westrock (Page 12) | Cost optimization focus |
| Healthcare, Financial Services, Government | PQR (Page 13) | Security/compliance focus |
