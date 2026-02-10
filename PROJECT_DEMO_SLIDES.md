# AMD AI Readiness Ebook - Project Demo Slides

---

## TABLE OF CONTENTS

| Section | Condensed (1 slide) | Expanded (multiple) |
|---------|---------------------|---------------------|
| Title + Problem | [Slide 1-2](#slides-1-2-title--problem) | Same |
| **Architecture** | [Option A](#architecture-option-a-condensed-1-slide) | [Option B](#architecture-option-b-expanded-4-slides) |
| **Dynamic Changes** | [Option A](#dynamic-changes-option-a-condensed-1-slide) | [Option B](#dynamic-changes-option-b-expanded-6-slides) |
| Completed Tasks | [Slide](#completed-tasks) | Same |
| **Next Steps** | [Option A](#next-steps-option-a-condensed-1-slide) | [Option B](#next-steps-option-b-expanded-3-slides) |
| Summary | [Slide](#summary--demo) | Same |

---

## HOW TO USE

```
OPTION A (Condensed) = Everything on ONE slide
  → Use for: Executive summary, short demos, time-limited presentations

OPTION B (Expanded) = Multiple detailed slides
  → Use for: Technical deep-dives, stakeholder education, full demos
```

---
---
---

# SLIDES 1-2: Title + Problem

---

## SLIDE 1: Title

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│                   AMD PERSONALIZED EBOOK GENERATOR                       │
│                                                                          │
│           From Generic Marketing to 1:1 Personalized Experiences         │
│                                                                          │
│                                                                          │
│                  Project: AMD1-1_Alpha                                   │
│                  Status:  Alpha Complete                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE 2: The Problem

```
┌─────────────────────────────────────────────────────────────────────────┐
│  WHY GENERIC EBOOKS FAIL                                                 │
│                                                                          │
│  ┌─────────────────────────┬──────────────────────────────────────────┐ │
│  │ Problem                 │ Impact                                   │ │
│  ├─────────────────────────┼──────────────────────────────────────────┤ │
│  │ Same content for all    │ Low relevance, high bounce              │ │
│  │ No company context      │ Missed connection opportunity           │ │
│  │ Static CTAs             │ Poor conversion across stages           │ │
│  │ Manual personalization  │ Doesn't scale                           │ │
│  └─────────────────────────┴──────────────────────────────────────────┘ │
│                                                                          │
│  WHAT BUYERS WANT                                                        │
│                                                                          │
│  • Content that names THEIR COMPANY                                      │
│  • References THEIR RECENT NEWS                                          │
│  • Speaks to THEIR ROLE and priorities                                   │
│  • Matches THEIR BUYING STAGE                                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---
---
---

# ARCHITECTURE: Option A (Condensed - 1 Slide)

---

## SLIDE: System Architecture (ALL-IN-ONE)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SYSTEM ARCHITECTURE                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ FRONTEND (Vercel)          Next.js 14 • Form • Polling UI         │  │
│  └───────────────────────────────────┬───────────────────────────────┘  │
│                                      ▼                                   │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ BACKEND (Render)                  FastAPI                         │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
│  │  │RADOrchestrator│  │  LLMService  │  │  PDFService  │            │  │
│  │  │ 5+1 API calls │  │ Claude + fallback│ │ WeasyPrint │            │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │  │
│  └───────────────────────────────────┬───────────────────────────────┘  │
│            │                         │                     │             │
│            ▼                         ▼                     ▼             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │ 5+1 Enrich APIs │  │ Claude (LLM)     │  │ Supabase         │      │
│  │ Apollo, PDL,      │  │ OpenAI fallback  │  │ PostgreSQL +     │      │
│  │ Hunter, GNews,    │  │ Gemini fallback  │  │ PDF Storage      │      │
│  │ ZoomInfo          │  │                  │  │                  │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  PIPELINE: Form → Enrich (5+1 APIs) → LLM → Compliance → PDF → Deliver │
│  TIMING:   ~45 seconds end-to-end                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

**Speaker Notes:**
- Frontend on Vercel handles form + polling
- Backend on Render runs 3 core services
- 5 APIs called in parallel + 1 sequential for enrichment
- Claude generates personalized content with fallbacks
- Supabase stores data + PDFs
- Total time under 60 seconds

---
---
---

# ARCHITECTURE: Option B (Expanded - 4 Slides)

---

## SLIDE B1: System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SYSTEM OVERVIEW                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      FRONTEND (Vercel)                            │  │
│  │                                                                   │  │
│  │              Next.js 14  •  Form UI  •  Polling                   │  │
│  └───────────────────────────────────┬───────────────────────────────┘  │
│                                      │                                   │
│                                      ▼                                   │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      BACKEND (Render)                             │  │
│  │                                                                   │  │
│  │                          FastAPI                                  │  │
│  │   RADOrchestrator  •  LLMService  •  PDFService  •  Compliance   │  │
│  └───────────────────────────────────┬───────────────────────────────┘  │
│                                      │                                   │
│                    ┌─────────────────┼─────────────────┐                │
│                    ▼                 ▼                 ▼                │
│             ┌───────────┐     ┌───────────┐     ┌───────────┐          │
│             │ 5+1 APIs  │     │  Claude   │     │ Supabase  │          │
│             │ (Enrich)  │     │  (LLM)    │     │ (Data+PDF)│          │
│             └───────────┘     └───────────┘     └───────────┘          │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Three-tier architecture: Frontend → Backend → External Services        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE B2: Tech Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TECH STACK                                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┬────────────────────┬─────────────────────────────┐ │
│  │ Layer           │ Technology         │ Why                         │ │
│  ├─────────────────┼────────────────────┼─────────────────────────────┤ │
│  │ Frontend        │ Next.js 14         │ Modern React, fast, SSR     │ │
│  │ Hosting         │ Vercel             │ Auto-deploy, global CDN     │ │
│  ├─────────────────┼────────────────────┼─────────────────────────────┤ │
│  │ Backend         │ FastAPI (Python)   │ Async, fast, ML-friendly    │ │
│  │ Hosting         │ Render             │ Easy Python deploy          │ │
│  ├─────────────────┼────────────────────┼─────────────────────────────┤ │
│  │ Database        │ Supabase Postgres  │ Managed, real-time          │ │
│  │ File Storage    │ Supabase Storage   │ Signed URLs, integrated     │ │
│  ├─────────────────┼────────────────────┼─────────────────────────────┤ │
│  │ PDF Engine      │ WeasyPrint         │ HTML→PDF with CSS support   │ │
│  │ LLM             │ Claude 3.5 Haiku   │ Fast, high-quality          │ │
│  └─────────────────┴────────────────────┴─────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE B3: Backend Services

```
┌─────────────────────────────────────────────────────────────────────────┐
│  BACKEND SERVICES                                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  RADOrchestrator                                                 │    │
│  │  • Calls 5 APIs in PARALLEL + 1 sequential                                      │    │
│  │  • Merges data with priority rules                               │    │
│  │  • Calculates quality score (0-1.0)                              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  LLMService                                                      │    │
│  │  • Sends 50+ data points to Claude                               │    │
│  │  • Generates 3 personalized sections                             │    │
│  │  • Fallback: Claude → OpenAI → Gemini                            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  PDFService                                                      │    │
│  │  • HTML template + variable substitution                         │    │
│  │  • WeasyPrint renders to PDF                                     │    │
│  │  • Uploads to Supabase, returns signed URL                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ComplianceService                                               │    │
│  │  • Checks for banned terms ("guaranteed", "best")                │    │
│  │  • Auto-corrects or uses safe fallback                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE B4: Data Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│  DATA PIPELINE FLOW                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ① USER INPUT ─────────────────────────────────────────────── ~0 sec    │
│     Name, Company, Industry, Role, Buying Stage                          │
│                         │                                                │
│                         ▼                                                │
│  ② ENRICHMENT (5 APIs parallel + 1 sequential) ─────────────────────── 5-15 sec    │
│     Apollo │ PDL │ PDL Company │ Hunter │ GNews │ ZoomInfo              │
│                         │                                                │
│                         ▼                                                │
│  ③ RESOLUTION ─────────────────────────────────────────────── ~0 sec    │
│     Priority-based merge → Quality score                                 │
│                         │                                                │
│                         ▼                                                │
│  ④ LLM PERSONALIZATION ────────────────────────────────────  3-8 sec    │
│     Claude generates: hook, case study framing, CTA                      │
│                         │                                                │
│                         ▼                                                │
│  ⑤ COMPLIANCE CHECK ───────────────────────────────────────── ~0 sec    │
│     Banned terms → Auto-correct                                          │
│                         │                                                │
│                         ▼                                                │
│  ⑥ PDF GENERATION ───────────────────────────────────────── 5-10 sec    │
│     HTML → WeasyPrint → Upload → Signed URL                              │
│                         │                                                │
│                         ▼                                                │
│  ⑦ DELIVERY                                                              │
│     Download link OR email                                               │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  TOTAL TIME: ~45 seconds                                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---
---
---

# DYNAMIC CHANGES: Option A (Condensed - 1 Slide)

---

## SLIDE: Dynamic Personalization (ALL-IN-ONE)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  DYNAMIC PERSONALIZATION                                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  WHAT CHANGES PER USER                                                   │
│  ┌────────────────┬──────────────────────────────────────────────────┐  │
│  │ Input          │ What Adapts                                      │  │
│  ├────────────────┼──────────────────────────────────────────────────┤  │
│  │ Industry       │ Case study selection (PQR / Smurfit / KT Cloud) │  │
│  │ Role           │ Hook angle, priorities, technical depth          │  │
│  │ Buying Stage   │ CTA urgency (educational → action-oriented)      │  │
│  │ Company Name   │ Direct references throughout                     │  │
│  │ Company News   │ Hook references actual recent events             │  │
│  └────────────────┴──────────────────────────────────────────────────┘  │
│                                                                          │
│  5+1 APIs → PRIORITY MERGE            CASE STUDY MAPPING                 │
│  PARALLEL:                            ┌─────────────┬─────────────────┐ │
│  ┌────────────┬──────────┐            │ Healthcare  │ PQR             │ │
│  │ Apollo     │ Priority 5│            │ Financial   │ PQR             │ │
│  │ PDL Person │ Priority 3│            │ Manufacturing│ Smurfit Westrock│ │
│  │ Hunter     │ Priority 2│            │ Technology  │ KT Cloud        │ │
│  │ GNews      │ Priority 1│            │ Government  │ PQR General     │ │
│  │ ZoomInfo   │ Priority 4│            └─────────────┴─────────────────┘ │
│  └────────────┴──────────┘                                               │
│  SEQUENTIAL:                                                             │
│  ┌────────────┬──────────┐                                               │
│  │ PDL Company│ Priority 4│                                               │
│  └────────────┴──────────┘                                               │
│                                                                          │
│  3 PERSONALIZED SECTIONS                                                 │
│  • Hook: "As [Company] expands AI after your $50M funding..."           │
│  • Case Study Framing: "Like your HIPAA challenges, PQR faced..."       │
│  • CTA: "Request a custom TCO analysis for [Company]'s needs."          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Speaker Notes:**
- Every PDF is unique - not mail merge, actual context-aware content
- 5 APIs run in parallel + 1 sequential, merged by priority (Apollo wins ties)
- Industry selection drives case study (Healthcare→PQR, Tech→KT Cloud)
- Buying stage changes CTA tone (AWARENESS=educational, DECISION=action)
- Company news from GNews feeds directly into the hook

---
---
---

# DYNAMIC CHANGES: Option B (Expanded - 6 Slides)

---

## SLIDE B1: What Changes Per User

```
┌─────────────────────────────────────────────────────────────────────────┐
│  WHAT CHANGES PER USER                                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Every PDF is UNIQUE. Here's what adapts:                               │
│                                                                          │
│  ┌────────────────────┬──────────────────────────────────────────────┐  │
│  │ User Input         │ What Adapts in the PDF                       │  │
│  ├────────────────────┼──────────────────────────────────────────────┤  │
│  │ INDUSTRY           │ Case study selection, challenge framing      │  │
│  │ ROLE / PERSONA     │ Hook angle, priorities, technical depth      │  │
│  │ BUYING STAGE       │ CTA urgency, recommended next steps          │  │
│  │ COMPANY NAME       │ Direct references throughout PDF             │  │
│  │ COMPANY NEWS       │ Hook references actual recent events         │  │
│  │ COMPANY SIZE       │ Segment-appropriate examples and metrics     │  │
│  └────────────────────┴──────────────────────────────────────────────┘  │
│                                                                          │
│  THREE PERSONALIZED SECTIONS:                                            │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ PAGE 1: Personalized Hook                                        │    │
│  │ "As [Company] expands its AI capabilities following your         │    │
│  │  recent $50M funding round..."                                   │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │ PAGE 8-9: Case Study Framing                                     │    │
│  │ "Like your work in healthcare compliance, PQR faced similar..."  │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │ FINAL PAGE: Personalized CTA                                     │    │
│  │ "Request a custom TCO analysis for [Company]'s requirements."    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE B2: Multi-API Enrichment

```
┌─────────────────────────────────────────────────────────────────────────┐
│  MULTI-API ENRICHMENT ENGINE                                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PHASE 1: 5 APIs IN PARALLEL                                             │
│                                                                          │
│                           ┌─────────────────────┐                        │
│                      ┌───►│ Apollo              │ Person data    [P: 5] │
│                      │    └─────────────────────┘                        │
│                      │    ┌─────────────────────┐                        │
│                      ├───►│ PDL (Person)        │ Skills, career [P: 3] │
│                      │    └─────────────────────┘                        │
│  Email submitted ────┼───►│ Hunter              │ Email verify   [P: 2] │
│                      │    └─────────────────────┘                        │
│                      │    ┌─────────────────────┐                        │
│                      ├───►│ GNews               │ Company news   [P: 1] │
│                      │    └─────────────────────┘                        │
│                      │    ┌─────────────────────┐                        │
│                      └───►│ ZoomInfo            │ Company data   [P: 4] │
│                           └─────────────────────┘                        │
│                                                                          │
│  PHASE 2: 1 API SEQUENTIAL (after Phase 1)                               │
│                           ┌─────────────────────┐                        │
│                      ────►│ PDL (Company)       │ Funding, size  [P: 4] │
│                           └─────────────────────┘                        │
│                                                                          │
│  PRIORITY RESOLUTION:                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Field: "company_name"                                            │    │
│  │                                                                  │    │
│  │   Apollo:   "Acme Corp"         (Priority 5)  ✓ WINS            │    │
│  │   ZoomInfo: "Acme"              (Priority 4)                     │    │
│  │   PDL:      "ACME Corporation"  (Priority 3)                     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  → Higher priority source wins. No single API has complete data.        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE B3: News Intelligence

```
┌─────────────────────────────────────────────────────────────────────────┐
│  NEWS INTELLIGENCE SYSTEM                                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  5 PARALLEL NEWS QUERIES (covers different angles)                       │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Query 1:  "[Company Name]"                    → Exact match     │    │
│  │ Query 2:  "[Company] AI artificial intelligence" → AI angle     │    │
│  │ Query 3:  "[Company] technology innovation"     → Tech angle    │    │
│  │ Query 4:  "[Company] strategy leadership CEO"   → Leadership    │    │
│  │ Query 5:  "[Company] expansion growth"          → Growth angle  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  PROCESSING PIPELINE:                                                    │
│                                                                          │
│      25 articles (5 per query)                                           │
│              │                                                           │
│              ▼                                                           │
│      Deduplicate by URL                                                  │
│              │                                                           │
│              ▼                                                           │
│      Categorize (AI, Leadership, Growth, General)                        │
│              │                                                           │
│              ▼                                                           │
│      Extract themes + Analyze sentiment                                  │
│              │                                                           │
│              ▼                                                           │
│      Top 10 unique articles                                              │
│                                                                          │
│  OUTPUT:                                                                 │
│  ┌────────────────┬──────────────────────────────────────────────────┐  │
│  │ Themes         │ "AI adoption", "Cloud transformation"            │  │
│  │ Sentiment      │ Positive (5), Negative (0), Neutral (2)          │  │
│  │ Categories     │ ai_technology, leadership, growth, general       │  │
│  └────────────────┴──────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE B4: LLM Personalization

```
┌─────────────────────────────────────────────────────────────────────────┐
│  LLM PERSONALIZATION                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  WHAT GOES INTO THE LLM (50+ data points):                              │
│                                                                          │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐   │
│  │ PERSON PROFILE              │  │ COMPANY PROFILE                 │   │
│  │ • Name: John Smith          │  │ • Company: Acme Corp            │   │
│  │ • Title: CISO               │  │ • Industry: Healthcare          │   │
│  │ • Skills: kubernetes,       │  │ • Employees: 2,547              │   │
│  │   cloud security, zero trust│  │ • Funding: Series C, $125M     │   │
│  │ • Career history            │  │ • Growth rate: 18%              │   │
│  └─────────────────────────────┘  └─────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐   │
│  │ BUYER CONTEXT               │  │ COMPANY NEWS                    │   │
│  │ • Stage: DECISION           │  │ • Themes: AI adoption, Cloud    │   │
│  │ • Persona: CISO             │  │ • Sentiment: POSITIVE           │   │
│  │ • Segment: ENTERPRISE       │  │ • "Acme launches AI platform"   │   │
│  └─────────────────────────────┘  └─────────────────────────────────┘   │
│                                                                          │
│  LLM MUST REFERENCE:                                                     │
│  ✓ Company name exactly    ✓ Recent news headline    ✓ Their title     │
│  ✓ Employee count/funding  ✓ Buying stage context    ✓ Case study metric│
│                                                                          │
│  OUTPUT:                                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Hook: "As Acme Corp expands AI following your $125M Series C..."│    │
│  │ Framing: "Like your HIPAA challenges, PQR faced similar..."     │    │
│  │ CTA: "Request a custom TCO analysis for Acme's requirements."   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE B5: Case Study Selection

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CASE STUDY SELECTION LOGIC                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  INDUSTRY → CASE STUDY MAPPING:                                          │
│                                                                          │
│  ┌─────────────────────────┬─────────────────────┬────────────────────┐ │
│  │ User Selects            │ Gets Case Study     │ Key Metric         │ │
│  ├─────────────────────────┼─────────────────────┼────────────────────┤ │
│  │ Healthcare              │ PQR Healthcare      │ 40% faster threat  │ │
│  │ Life Sciences           │                     │ detection, HIPAA   │ │
│  ├─────────────────────────┼─────────────────────┼────────────────────┤ │
│  │ Financial Services      │ PQR Financial       │ Regulatory         │ │
│  │                         │                     │ compliance         │ │
│  ├─────────────────────────┼─────────────────────┼────────────────────┤ │
│  │ Manufacturing           │ Smurfit Westrock    │ 25% cost reduction │ │
│  │ Retail / Energy         │                     │ 30% emissions cut  │ │
│  ├─────────────────────────┼─────────────────────┼────────────────────┤ │
│  │ Technology / Telecom    │ KT Cloud            │ Massive GPU scale  │ │
│  │ Gaming / Media          │                     │ AI infrastructure  │ │
│  ├─────────────────────────┼─────────────────────┼────────────────────┤ │
│  │ Government / Education  │ PQR General         │ 40% efficiency     │ │
│  └─────────────────────────┴─────────────────────┴────────────────────┘ │
│                                                                          │
│  SELECTION PRIORITY:                                                     │
│                                                                          │
│      User's form selection     API-detected industry     Default         │
│             │                         │                     │            │
│             ▼                         ▼                     ▼            │
│          HIGHEST ─────────────────► FALLBACK ───────────► LAST RESORT   │
│                                                           (PQR General)  │
│                                                                          │
│  → User's explicit choice is ALWAYS trusted over API data               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE B6: Buying Stage Adaptation

```
┌─────────────────────────────────────────────────────────────────────────┐
│  BUYING STAGE ADAPTATION                                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  FOUR BUYING STAGES:                                                     │
│                                                                          │
│  ┌─────────────────┬─────────────────────┬─────────────────────────┐    │
│  │ Stage           │ User Mindset        │ Content Tone            │    │
│  ├─────────────────┼─────────────────────┼─────────────────────────┤    │
│  │ AWARENESS       │ "I'm just learning" │ Educational, non-pushy  │    │
│  │ CONSIDERATION   │ "I'm comparing"     │ Comparative, features   │    │
│  │ DECISION        │ "I'm ready to choose"│ Confident, ROI-focused │    │
│  │ IMPLEMENTATION  │ "I'm already deploying"│ Partnership, optimize│    │
│  └─────────────────┴─────────────────────┴─────────────────────────┘    │
│                                                                          │
│  HOOK ADAPTATION:                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ AWARENESS:      "Understanding where [Company] stands..."       │    │
│  │ CONSIDERATION:  "As you evaluate AI options for [Company]..."   │    │
│  │ DECISION:       "You're ready to decide on [Company]'s AI..."   │    │
│  │ IMPLEMENTATION: "With [Company] already implementing..."        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  CTA ADAPTATION:                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ AWARENESS:      "Download the full guide to explore..."         │    │
│  │ CONSIDERATION:  "See how these capabilities compare..."         │    │
│  │ DECISION:       "Request a custom TCO analysis..."              │    │
│  │ IMPLEMENTATION: "Connect with our architects..."                │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  → CTA urgency INCREASES as buyer progresses through stages             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---
---
---

# COMPLETED TASKS

---

## SLIDE: What We've Completed

```
┌─────────────────────────────────────────────────────────────────────────┐
│  WHAT WE'VE COMPLETED (Alpha Phase)                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────┬────────┬───────────────────────────────┐  │
│  │ Component                │ Status │ Notes                         │  │
│  ├──────────────────────────┼────────┼───────────────────────────────┤  │
│  │ Frontend (Next.js)       │   ✅   │ Form, polling, download UI    │  │
│  │ Backend (FastAPI)        │   ✅   │ All /rad/* endpoints          │  │
│  │ 5+1 API Enrichment         │   ✅   │ Parallel + priority merge     │  │
│  │ LLM Service              │   ✅   │ Claude + OpenAI + Gemini      │  │
│  │ Compliance Layer         │   ✅   │ Banned terms, auto-correct    │  │
│  │ PDF Service              │   ✅   │ WeasyPrint, AMD branding      │  │
│  │ Database                 │   ✅   │ Supabase tables + storage     │  │
│  │ Deployment               │   ✅   │ Vercel + Render               │  │
│  └──────────────────────────┴────────┴───────────────────────────────┘  │
│                                                                          │
│  LIVE ENDPOINTS:                                                         │
│  ┌─────────────────────────────┬────────────────────────────────────┐   │
│  │ POST /rad/enrich            │ Full enrichment + personalization  │   │
│  │ GET  /rad/profile/{email}   │ Retrieve stored profile            │   │
│  │ GET  /rad/download/{email}  │ Download generated PDF             │   │
│  │ POST /rad/deliver/{email}   │ Email PDF delivery                 │   │
│  └─────────────────────────────┴────────────────────────────────────┘   │
│                                                                          │
│  LIVE URLS:                                                              │
│  • Frontend: https://amd1-1-alpha.vercel.app                            │
│  • Backend:  https://amd1-1-backend.onrender.com                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---
---
---

# NEXT STEPS: Option A (Condensed - 1 Slide)

---

## SLIDE: Next Steps (ALL-IN-ONE)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  NEXT STEPS                                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ 1. MARKETO INTEGRATION                               Priority: HIGH│  │
│  ├───────────────────────────────────────────────────────────────────┤  │
│  │                                                                   │  │
│  │  Marketo Form → Webhook POST → Enrich → PDF → Return URL         │  │
│  │                                 │                                 │  │
│  │  Marketo stores URL on lead → Sends email with download link     │  │
│  │                                                                   │  │
│  │  ⚠️ Constraint: 30-second webhook timeout                        │  │
│  │  Why: Lead ownership, email deliverability, CRM sync             │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ 2. ACROFORM PDF APPROACH                             Priority: HIGH│  │
│  ├───────────────────────────────────────────────────────────────────┤  │
│  │                                                                   │  │
│  │  Designer PDF template with 6 text fields                        │  │
│  │       → Backend fills fields → Flatten → Pixel-perfect PDF       │  │
│  │                                                                   │  │
│  │  Fields: personalized_hook, case_study_1/2/3_framing, cta x2     │  │
│  │  Status: Waiting on design team template                          │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ 3. OTHER ITEMS                                                    │  │
│  ├───────────────────────────────────────────────────────────────────┤  │
│  │  • Email delivery (add RESEND_API_KEY)              Medium        │  │
│  │  • Test suite updates                               Medium        │  │
│  │  • Rate limiting + circuit breakers                 Medium        │  │
│  │  • A/B testing for LLM prompts                      Low           │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Speaker Notes:**
- Marketo = enterprise marketing automation, enables lead nurturing
- 30-second timeout means we need fast processing, background updates
- AcroForm = design team creates pixel-perfect PDF, we just fill fields
- 6 fields: hook on page 1, 3 case study framings, 2 CTAs
- Currently waiting on design team to deliver the template

---
---
---

# NEXT STEPS: Option B (Expanded - 3 Slides)

---

## SLIDE B1: Marketo Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│  NEXT: MARKETO INTEGRATION                              Priority: HIGH  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  WHY MARKETO?                                                            │
│  ┌────────────────────┬──────────────────────────────────────────────┐  │
│  │ Benefit            │ Value                                        │  │
│  ├────────────────────┼──────────────────────────────────────────────┤  │
│  │ Lead Ownership     │ Marketo captures leads for nurturing         │  │
│  │ Email Deliverability│ Proper authentication, better inbox rates  │  │
│  │ Campaign Analytics │ Track opens, clicks, conversions             │  │
│  │ CRM Sync           │ Auto-sync to Salesforce                      │  │
│  └────────────────────┴──────────────────────────────────────────────┘  │
│                                                                          │
│  INTEGRATION FLOW:                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ MARKETO                                                          │    │
│  │ User fills form → Smart Campaign → Webhook POST                  │    │
│  └────────────────────────────────────────┬────────────────────────┘    │
│                                           │                              │
│                                           ▼                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ BACKEND: POST /rad/marketo/webhook                               │    │
│  │ 1. Validate secret header                                        │    │
│  │ 2. Enrich via 5+1 APIs                                             │    │
│  │ 3. Generate PDF                                                  │    │
│  │ 4. Return { pdfUrl, status }                                     │    │
│  └────────────────────────────────────────┬────────────────────────┘    │
│                                           │                              │
│                                           ▼                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Marketo stores pdfUrl → Sends email with download link          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ⚠️  KEY CONSTRAINT: 30-second webhook timeout                          │
│      Solution: Return URL immediately, update lead in background        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE B2: AcroForm PDF Approach

```
┌─────────────────────────────────────────────────────────────────────────┐
│  NEXT: ACROFORM PDF APPROACH                            Priority: HIGH  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CURRENT VS. ACROFORM:                                                   │
│  ┌─────────────────┬─────────────────────┬─────────────────────────┐    │
│  │ Aspect          │ Current (HTML→PDF)  │ AcroForm (Designer PDF) │    │
│  ├─────────────────┼─────────────────────┼─────────────────────────┤    │
│  │ Design Fidelity │ Good                │ PIXEL-PERFECT           │    │
│  │ Font Control    │ Web fonts           │ EMBEDDED BRAND FONTS    │    │
│  │ Ownership       │ Engineering         │ DESIGN TEAM             │    │
│  │ Brand Match     │ Approximate         │ EXACT                   │    │
│  └─────────────────┴─────────────────────┴─────────────────────────┘    │
│                                                                          │
│  HOW IT WORKS:                                                           │
│                                                                          │
│      Designer creates PDF with 6 editable text fields                    │
│                          │                                               │
│                          ▼                                               │
│      Backend fills fields with LLM-generated content                     │
│                          │                                               │
│                          ▼                                               │
│      Backend FLATTENS PDF (fields → static text)                         │
│                          │                                               │
│                          ▼                                               │
│      Result: Pixel-perfect branded PDF with personalization              │
│                                                                          │
│  THE 6 FIELDS:                                                           │
│  ┌──────────────────────────────┬────────┬───────────────────────────┐  │
│  │ Field Name                   │ Page   │ Content                   │  │
│  ├──────────────────────────────┼────────┼───────────────────────────┤  │
│  │ personalized_hook            │ 1      │ Opening paragraph         │  │
│  │ case_study_1_framing         │ 11     │ KT Cloud framing          │  │
│  │ case_study_2_framing         │ 12     │ Smurfit framing           │  │
│  │ case_study_3_framing         │ 13     │ PQR framing               │  │
│  │ personalized_cta_assessment  │ 14     │ Assessment CTA            │  │
│  │ personalized_cta_footer      │ 16     │ Final CTA                 │  │
│  └──────────────────────────────┴────────┴───────────────────────────┘  │
│                                                                          │
│  STATUS: Waiting on design team to deliver template                      │
│          Spec provided in: /backend/assets/DESIGNER_SPEC.md             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE B3: Roadmap & Priorities

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ROADMAP & PRIORITIES                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PHASE 2: BETA                                                           │
│  ┌──────────────────────────────────┬──────────┬─────────────────────┐  │
│  │ Task                             │ Priority │ Status              │  │
│  ├──────────────────────────────────┼──────────┼─────────────────────┤  │
│  │ Marketo webhook integration      │ HIGH     │ Planned             │  │
│  │ AcroForm PDF support             │ HIGH     │ Waiting on design   │  │
│  │ Email delivery (Resend API key)  │ MEDIUM   │ Ready to configure  │  │
│  │ Test suite updates               │ MEDIUM   │ Needs work          │  │
│  │ Rate limiting + circuit breakers │ MEDIUM   │ Planned             │  │
│  └──────────────────────────────────┴──────────┴─────────────────────┘  │
│                                                                          │
│  PHASE 3: PRODUCTION                                                     │
│  ┌──────────────────────────────────┬──────────┐                        │
│  │ Task                             │ Priority │                        │
│  ├──────────────────────────────────┼──────────┤                        │
│  │ A/B testing for LLM prompts      │ Medium   │                        │
│  │ Multi-language support           │ Medium   │                        │
│  │ Multiple PDF templates           │ Low      │                        │
│  │ Cost optimization dashboard      │ Low      │                        │
│  └──────────────────────────────────┴──────────┘                        │
│                                                                          │
│  ENVIRONMENT VARIABLES NEEDED:                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ FOR EMAIL:                                                       │    │
│  │   RESEND_API_KEY=re_...  OR  SENDGRID_API_KEY=SG...             │    │
│  │                                                                  │    │
│  │ FOR MARKETO:                                                     │    │
│  │   MARKETO_CLIENT_ID, MARKETO_CLIENT_SECRET                       │    │
│  │   MARKETO_BASE_URL, MARKETO_WEBHOOK_SECRET                       │    │
│  │   MARKETO_EMAIL_CAMPAIGN_ID                                      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---
---
---

# SUMMARY & DEMO

---

## SLIDE: Summary & Demo

```
┌─────────────────────────────────────────────────────────────────────────┐
│  KEY TAKEAWAYS                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ 1. TRUE 1:1 PERSONALIZATION                                      │    │
│  │    Not mail-merge — actual context-aware content                 │    │
│  │                                                                  │    │
│  │ 2. MULTI-SOURCE INTELLIGENCE                                     │    │
│  │    5+1 APIs provide rich, verified data                            │    │
│  │                                                                  │    │
│  │ 3. REAL-TIME GENERATION                                          │    │
│  │    Under 60 seconds end-to-end                                   │    │
│  │                                                                  │    │
│  │ 4. COMPLIANCE-SAFE                                               │    │
│  │    Auto-validation catches marketing overreach                   │    │
│  │                                                                  │    │
│  │ 5. SCALABLE                                                      │    │
│  │    Serverless, async, no manual steps                            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  DEMO FLOW                                                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ① Show form with dropdowns (industry, role, buying stage)              │
│  ② Submit → Show loading state                                          │
│  ③ Download PDF → Point out personalized sections                       │
│  ④ Submit again with DIFFERENT industry                                 │
│  ⑤ Show different case study in new PDF                                 │
│  ⑥ Highlight: company name + news reference in hook                     │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  METRICS                                                                 │
│  ┌─────────────────────────┬─────────────┬─────────────┐                │
│  │ Metric                  │ Current     │ Target      │                │
│  ├─────────────────────────┼─────────────┼─────────────┤                │
│  │ End-to-end latency      │ ~45 sec     │ < 60 sec    │                │
│  │ Data quality score      │ 0.7-0.9     │ > 0.7       │                │
│  │ API success rate        │ ~95%        │ > 99%       │                │
│  └─────────────────────────┴─────────────┴─────────────┘                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---
---
---

# QUICK REFERENCE

---

## Slide Count Summary

| Presentation Type | Total Slides |
|-------------------|--------------|
| **Condensed** (Option A for all) | 7 slides |
| **Expanded** (Option B for all) | 17 slides |
| **Hybrid** (mix and match) | 7-17 slides |

---

## Recommended Combinations

**5-minute pitch:**
- Title (1) + Problem (1) + Architecture A (1) + Dynamic A (1) + Next Steps A (1) + Summary (1)
- **Total: 6 slides**

**15-minute demo:**
- Title (1) + Problem (1) + Architecture B (4) + Dynamic A (1) + Completed (1) + Next Steps A (1) + Summary (1)
- **Total: 10 slides**

**30-minute deep dive:**
- Title (1) + Problem (1) + Architecture B (4) + Dynamic B (6) + Completed (1) + Next Steps B (3) + Summary (1)
- **Total: 17 slides**

---

## Live URLs

```
Frontend:     https://amd1-1-alpha.vercel.app
Backend:      https://amd1-1-backend.onrender.com
Health Check: https://amd1-1-backend.onrender.com/rad/status
```

---

*Document generated for AMD AI Readiness Ebook project demo*
