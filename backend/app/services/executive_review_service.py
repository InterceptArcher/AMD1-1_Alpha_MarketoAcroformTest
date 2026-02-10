"""
Executive Review Service for AMD 2-page assessment generation.
Generates personalized content based on Stage, Industry, Segment, Persona, Priority, and Challenge.
"""

import logging
import json
from typing import Optional
from anthropic import Anthropic

from app.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# MAPPING FUNCTIONS
# =============================================================================

def map_company_size_to_segment(company_size: str) -> str:
    """Map company size to AMD segment (Enterprise/Mid-Market/SMB)."""
    mapping = {
        "startup": "SMB",
        "small": "SMB",
        "midmarket": "Mid-Market",
        "enterprise": "Enterprise",
        "large_enterprise": "Enterprise",
    }
    return mapping.get(company_size, "Enterprise")


def map_role_to_persona(role: str) -> str:
    """Map detailed role to AMD persona (BDM or ITDM)."""
    # Technical roles -> ITDM (IT Decision Maker)
    itdm_roles = {
        "cto", "cio", "ciso", "cdo",
        "vp_engineering", "vp_it", "vp_data", "vp_security",
        "eng_manager", "it_manager", "data_manager", "security_manager",
        "senior_engineer", "engineer", "sysadmin"
    }
    # Business roles -> BDM (Business Decision Maker)
    bdm_roles = {
        "ceo", "coo", "cfo", "c_suite_other",
        "vp_ops", "vp_finance",
        "ops_manager", "finance_manager", "procurement"
    }

    if role in itdm_roles:
        return "ITDM"
    elif role in bdm_roles:
        return "BDM"
    else:
        return "BDM"  # Default to BDM


def map_it_environment_to_stage(it_environment: str) -> str:
    """Map IT environment selection to modernization stage."""
    mapping = {
        "traditional": "Observer",
        "modernizing": "Challenger",
        "modern": "Leader",
    }
    return mapping.get(it_environment, "Challenger")


def get_stage_sidebar(stage: str) -> str:
    """Get the sidebar statistic for a stage."""
    sidebars = {
        "Observer": "9% of Observers plan to modernize within the next two years.",
        "Challenger": "58% of Challengers are currently undertaking modernization initiatives.",
        "Leader": "33% of Leaders have fully modernized in the past two years.",
    }
    return sidebars.get(stage, "")


def map_priority_display(priority: str) -> str:
    """Map priority code to display text."""
    mapping = {
        "reducing_cost": "Reducing cost",
        "improving_performance": "Improving workload performance",
        "preparing_ai": "Preparing for AI adoption",
    }
    return mapping.get(priority, priority)


def map_challenge_display(challenge: str) -> str:
    """Map challenge code to display text."""
    mapping = {
        "legacy_systems": "Legacy systems",
        "integration_friction": "Integration friction",
        "resource_constraints": "Resource constraints",
        "skills_gap": "Skills gap",
        "data_governance": "Data governance and compliance",
    }
    return mapping.get(challenge, challenge)


def map_industry_display(industry: str) -> str:
    """Map industry code to display text."""
    mapping = {
        "technology": "Technology",
        "financial_services": "Financial Services",
        "healthcare": "Healthcare",
        "manufacturing": "Manufacturing",
        "retail": "Retail",
        "energy": "Energy",
        "telecommunications": "Telecommunications",
        "media": "Media",
        "government": "Government",
        "education": "Education",
        "professional_services": "Professional Services",
        "other": "Other",
    }
    return mapping.get(industry, industry)


# =============================================================================
# CASE STUDY SELECTION
# =============================================================================

CASE_STUDIES = {
    "kt_cloud": {
        "name": "KT Cloud Expands AI Power with AMD Instinct Accelerators",
        "description": "KT Cloud built a scalable AI cloud service using AMD Instinct MI250 accelerators, increasing performance and reducing GPU service costs by up to 70%.",
    },
    "smurfit_westrock": {
        "name": "Smurfit Westrock Saves AWS Costs for Innovation with AMD",
        "description": "Smurfit Westrock cut cloud costs by 25% and lowered its carbon footprint by 10% by transitioning to AWS instances powered by AMD EPYC CPUs.",
    },
    "pqr": {
        "name": "PQR Offers Next-Gen IT Services with AMD Pensando DPUs",
        "description": "PQR created a next-generation data center service emphasizing stronger security and operational simplicity using AMD Pensando DPU-enabled infrastructure.",
    },
}


def select_case_study(stage: str, priority: str, industry: str) -> tuple[str, str]:
    """
    Select the most relevant case study based on stage, priority, and industry.
    Returns (case_study_name, case_study_description).
    """
    # Priority-based selection
    if priority == "reducing_cost":
        cs = CASE_STUDIES["smurfit_westrock"]
        return cs["name"], cs["description"]

    if priority == "preparing_ai" or stage == "Leader":
        cs = CASE_STUDIES["kt_cloud"]
        return cs["name"], cs["description"]

    # Industry-based selection
    if industry in ["healthcare", "financial_services", "government"]:
        # Security/compliance focused
        cs = CASE_STUDIES["pqr"]
        return cs["name"], cs["description"]

    if industry in ["technology", "telecommunications"]:
        # Scale/AI focused
        cs = CASE_STUDIES["kt_cloud"]
        return cs["name"], cs["description"]

    if industry in ["manufacturing", "retail", "energy"]:
        # Cost focused
        cs = CASE_STUDIES["smurfit_westrock"]
        return cs["name"], cs["description"]

    # Default based on stage
    if stage == "Observer":
        cs = CASE_STUDIES["smurfit_westrock"]
    elif stage == "Challenger":
        cs = CASE_STUDIES["kt_cloud"]
    else:
        cs = CASE_STUDIES["pqr"]

    return cs["name"], cs["description"]


# =============================================================================
# FEW-SHOT EXAMPLES
# =============================================================================

FEW_SHOT_EXAMPLES = {
    "Observer": {
        "profile": {
            "company": "AECOM",
            "industry": "AEC",
            "segment": "Enterprise",
            "persona": "ITDM",
            "stage": "Observer",
            "priority": "Reducing cost",
            "challenge": "Legacy systems"
        },
        "output": {
            "advantages": [
                {
                    "headline": "Cost savings from reducing legacy system overhead",
                    "description": "Retiring aging on-prem systems lowers operating costs and reduces the maintenance burden across AECOM's globally distributed project teams."
                },
                {
                    "headline": "Efficiency gains through basic standardization",
                    "description": "Unifying fragmented BIM, CAD, and project data environments creates quick workflow efficiencies without requiring major architectural change."
                }
            ],
            "risks": [
                {
                    "headline": "High total cost of ownership from legacy infrastructure",
                    "description": "Running large, outdated systems at enterprise scale drives rising support, licensing, and hardware costs that conflict with cost-reduction goals."
                },
                {
                    "headline": "Integration gaps that add avoidable project costs",
                    "description": "Siloed tools and limited interoperability across field, design, and ERP systems increase rework risk and make secure integration harder for IT."
                }
            ],
            "recommendations": [
                {
                    "title": "Modernize high-impact legacy workloads first",
                    "description": "Target the most cost-intensive on-prem systems, such as storage and compute tied to BIM and CAD, to reduce maintenance overhead and improve stability for distributed project teams."
                },
                {
                    "title": "Standardize core infrastructure to reduce fragmentation",
                    "description": "Adopt consistent tooling and platform standards across regions to lower integration effort for ITDM teams and eliminate duplicated spend across project sites."
                },
                {
                    "title": "Build a scalable foundation for future AI workloads",
                    "description": "Upgrade underlying compute and storage so the organization can support emerging AI-driven design and planning tools without incurring higher costs from repeated rework."
                }
            ],
            "case_study": "Smurfit Westrock"
        }
    },
    "Challenger": {
        "profile": {
            "company": "Target",
            "industry": "Retail",
            "segment": "Enterprise",
            "persona": "BDM",
            "stage": "Challenger",
            "priority": "Improving workload performance",
            "challenge": "Integration friction"
        },
        "output": {
            "advantages": [
                {
                    "headline": "Performance gains from upgrading core systems",
                    "description": "Modernizing high-volume retail workloads improves responsiveness across POS, ecommerce, and supply chain operations."
                },
                {
                    "headline": "Faster throughput by reducing integration friction",
                    "description": "Improving data flow between merchandising, inventory, and digital platforms enables more consistent performance for customer-facing processes."
                }
            ],
            "risks": [
                {
                    "headline": "Persistent slowdowns from legacy system connections",
                    "description": "If integration issues remain unresolved, performance bottlenecks will continue to affect revenue, customer experience, and store operations."
                },
                {
                    "headline": "Competitors advance with more unified retail platforms",
                    "description": "Delays in improving system performance allow faster, better-integrated retailers to gain an advantage in speed and reliability."
                }
            ],
            "recommendations": [
                {
                    "title": "Prioritize performance upgrades for high-volume retail systems",
                    "description": "Focus modernization on the transactional workloads that power POS, ecommerce, and inventory to improve speed and reduce friction during peak demand."
                },
                {
                    "title": "Strengthen integration across core retail platforms",
                    "description": "Improve data consistency and flow between store, digital, and supply chain systems to eliminate performance delays that impact customer experience and revenue."
                },
                {
                    "title": "Adopt scalable infrastructure to support unified commerce",
                    "description": "Move toward more flexible compute and storage environments so Target can handle growing performance demands across omnichannel operations without added complexity."
                }
            ],
            "case_study": "KT Cloud"
        }
    },
    "Leader": {
        "profile": {
            "company": "HCA Healthcare",
            "industry": "Healthcare",
            "segment": "Enterprise",
            "persona": "ITDM",
            "stage": "Leader",
            "priority": "Preparing for AI adoption",
            "challenge": "Data governance and compliance"
        },
        "output": {
            "advantages": [
                {
                    "headline": "Stronger readiness for advanced AI workloads",
                    "description": "HCA's modern, scalable infrastructure gives IT teams the foundation to support clinical AI models that require high performance and reliable data access at enterprise scale."
                },
                {
                    "headline": "Tighter governance that accelerates compliant AI adoption",
                    "description": "With established data controls across EHR, imaging, and operational systems, HCA can evaluate and deploy AI use cases more confidently within strict regulatory boundaries."
                }
            ],
            "risks": [
                {
                    "headline": "AI accuracy and safety depend on high-quality, well-governed data",
                    "description": "If interoperability or data quality gaps persist across clinical and administrative systems, AI models may underperform or increase compliance risk for IT."
                },
                {
                    "headline": "Regulatory complexity can slow enterprise AI deployment",
                    "description": "Highly regulated environments like healthcare require rigorous validation and documentation, which may extend timelines for IT to operationalize AI at scale."
                }
            ],
            "recommendations": [
                {
                    "title": "Strengthen data foundations for clinical AI",
                    "description": "Improve data quality and interoperability across EHR, imaging, and operational systems to ensure AI models are accurate, reliable, and compliant."
                },
                {
                    "title": "Expand governance frameworks to support safe AI use",
                    "description": "Enhance validation, documentation, and audit controls so IT teams can deploy AI tools that meet strict healthcare regulatory requirements."
                },
                {
                    "title": "Scale infrastructure to support high-performance AI workloads",
                    "description": "Increase compute and storage capacity to run demanding AI models consistently across clinical and administrative environments."
                }
            ],
            "case_study": "PQR"
        }
    }
}


# =============================================================================
# EXECUTIVE REVIEW GENERATION
# =============================================================================

class ExecutiveReviewService:
    """Service for generating AMD Executive Review content."""

    def __init__(self):
        self.client = None
        if settings.ANTHROPIC_API_KEY:
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_executive_review(
        self,
        company_name: str,
        industry: str,
        segment: str,
        persona: str,
        stage: str,
        priority: str,
        challenge: str,
    ) -> dict:
        """
        Generate executive review content using few-shot prompting.

        Args:
            company_name: Company name
            industry: Industry (display text)
            segment: Segment (Enterprise/Mid-Market/SMB)
            persona: Persona (BDM/ITDM)
            stage: Modernization stage (Observer/Challenger/Leader)
            priority: Business priority (display text)
            challenge: Challenge (display text)

        Returns:
            Dict with stage, advantages, risks, recommendations, case_study
        """
        if not self.client:
            logger.warning("No Anthropic client - returning mock executive review")
            return self._get_mock_response(company_name, stage, priority, industry)

        # Get the matching few-shot example
        example = FEW_SHOT_EXAMPLES.get(stage, FEW_SHOT_EXAMPLES["Challenger"])

        # Build the prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            company_name=company_name,
            industry=industry,
            segment=segment,
            persona=persona,
            stage=stage,
            priority=priority,
            challenge=challenge,
            example=example
        )

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                system=system_prompt
            )

            # Parse the response
            content = response.content[0].text
            return self._parse_response(content, company_name, stage, priority, industry)

        except Exception as e:
            logger.error(f"Executive review generation failed: {e}")
            return self._get_mock_response(company_name, stage, priority, industry)

    def _build_system_prompt(self) -> str:
        """Build the system prompt with AMD content rules."""
        return """You are an expert business strategist creating personalized executive reviews for AMD's Data Center Modernization program.

Your output must follow these strict rules:

CONTENT STRUCTURE:
- Headlines: 4-8 words, imperative or benefit-driven, no colons
- Descriptions: One single sentence, 22-30 words, human and professional tone
- No jargon, buzzwords, hype, or filler phrases like "in today's landscape"
- No em dashes, no exclamation marks, no emojis

COMPANY NAME RULES:
- Use the company name exactly ONCE in each section (advantages, risks, recommendations)
- The name should appear in the FIRST item of each section
- After first mention, use pronouns: "their environment", "the company", "the organization", "their teams"
- Never repeat the company name across every line (this is an AI tell)

STAGE-SPECIFIC FOCUS:
- Observer: low-lift, cost-saving steps, foundational efficiency
- Challenger: performance, integration, scalability steps
- Leader: governance, optimization, AI readiness steps

OUTPUT FORMAT:
Return valid JSON only, no markdown, no explanation. Match the exact structure shown in the example."""

    def _build_user_prompt(
        self,
        company_name: str,
        industry: str,
        segment: str,
        persona: str,
        stage: str,
        priority: str,
        challenge: str,
        example: dict
    ) -> str:
        """Build the user prompt with few-shot example."""
        return f"""Generate an executive review for this profile:

Company: {company_name}
Industry: {industry}
Segment: {segment}
Persona: {persona}
Stage: {stage}
Business Priority: {priority}
Challenge: {challenge}

Here is an example of excellent output for a {stage} stage company:

INPUT:
{json.dumps(example["profile"], indent=2)}

OUTPUT:
{json.dumps(example["output"], indent=2)}

Now generate the executive review for {company_name}. Return ONLY valid JSON matching the output structure above."""

    def _parse_response(self, content: str, company_name: str, stage: str, priority: str, industry: str) -> dict:
        """Parse the LLM response into structured output."""
        try:
            # Try to extract JSON from the response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            data = json.loads(content)

            # Get case study
            case_study_name, case_study_desc = select_case_study(stage, priority, industry)

            return {
                "company_name": company_name,
                "stage": stage,
                "stage_sidebar": get_stage_sidebar(stage),
                "advantages": data.get("advantages", []),
                "risks": data.get("risks", []),
                "recommendations": data.get("recommendations", []),
                "case_study": case_study_name,
                "case_study_description": case_study_desc,
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse executive review JSON: {e}")
            return self._get_mock_response(company_name, stage, priority, industry)

    def _get_mock_response(self, company_name: str, stage: str, priority: str, industry: str) -> dict:
        """Return a mock response when LLM is unavailable."""
        example = FEW_SHOT_EXAMPLES.get(stage, FEW_SHOT_EXAMPLES["Challenger"])
        case_study_name, case_study_desc = select_case_study(stage, priority, industry)

        return {
            "company_name": company_name,
            "stage": stage,
            "stage_sidebar": get_stage_sidebar(stage),
            "advantages": example["output"]["advantages"],
            "risks": example["output"]["risks"],
            "recommendations": example["output"]["recommendations"],
            "case_study": case_study_name,
            "case_study_description": case_study_desc,
        }
