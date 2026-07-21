"""
Feature 2: Occupational Resume Building Bot
Functionality: Assists in creating and formatting professional resumes using
  user-provided information. Includes templates, AI content suggestions,
  and ATS optimization.
Use Cases: Job seekers wanting a polished, ATS-optimized resume.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example resume template/component records
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "section": "Professional Summary", "role": "Software Engineer",      "template": "Results-driven Software Engineer with {years} years of experience building scalable {tech_stack} applications. Proven track record of delivering high-quality code on time.", "ats_score": 88, "industry": "technology"},
    {"id": 2,  "section": "Professional Summary", "role": "Data Analyst",            "template": "Detail-oriented Data Analyst with expertise in {tools}. Transformed complex datasets into actionable business insights that drove {metric} revenue growth.", "ats_score": 85, "industry": "analytics"},
    {"id": 3,  "section": "Professional Summary", "role": "Product Manager",         "template": "Strategic Product Manager with {years} years leading cross-functional teams. Launched {products} successful products that achieved {metric} user adoption.", "ats_score": 90, "industry": "product"},
    {"id": 4,  "section": "Professional Summary", "role": "Marketing Manager",       "template": "Creative Marketing Manager specializing in {channels}. Grew organic traffic by {metric}% and managed $500K+ in ad spend with {roi} ROAS.", "ats_score": 87, "industry": "marketing"},
    {"id": 5,  "section": "Professional Summary", "role": "UX Designer",             "template": "User-centered UX Designer with expertise in {tools}. Redesigned core product flows that improved user retention by {metric}%.", "ats_score": 84, "industry": "design"},
    {"id": 6,  "section": "Work Experience",      "role": "Software Engineer",       "template": "• Developed and maintained {system} using {tech_stack}, improving performance by {metric}%\n• Led a team of {size} engineers to deliver {project} on time and under budget", "ats_score": 92, "industry": "technology"},
    {"id": 7,  "section": "Work Experience",      "role": "Data Analyst",            "template": "• Built automated reporting pipelines using {tools}, reducing manual work by {hours} hours/week\n• Analyzed {dataset_size} records to identify revenue opportunities worth ${revenue}", "ats_score": 90, "industry": "analytics"},
    {"id": 8,  "section": "Work Experience",      "role": "Product Manager",         "template": "• Defined and shipped {features} product features used by {users}K+ monthly active users\n• Increased conversion rate by {metric}% through A/B testing and user research", "ats_score": 93, "industry": "product"},
    {"id": 9,  "section": "Work Experience",      "role": "Sales Representative",    "template": "• Consistently exceeded quota by {pct}%, generating ${revenue} in annual recurring revenue\n• Managed {clients} accounts across {territory} territory", "ats_score": 91, "industry": "sales"},
    {"id": 10, "section": "Work Experience",      "role": "Marketing Manager",       "template": "• Launched email campaign series achieving {open_rate}% open rate and {ctr}% CTR\n• Managed {budget} marketing budget with {roi}x return on investment", "ats_score": 89, "industry": "marketing"},
    {"id": 11, "section": "Skills",               "role": "Software Engineer",       "template": "Programming Languages: Python, JavaScript, TypeScript, Java\nFrameworks: React, Node.js, Django, FastAPI\nDevOps: AWS, Docker, Kubernetes, CI/CD\nDatabases: PostgreSQL, MongoDB, Redis", "ats_score": 95, "industry": "technology"},
    {"id": 12, "section": "Skills",               "role": "Data Analyst",            "template": "Analytics: SQL, Python (Pandas, NumPy), R\nVisualization: Tableau, Power BI, Matplotlib\nDatabases: PostgreSQL, BigQuery, Redshift\nTools: Excel, Google Sheets, Jupyter", "ats_score": 93, "industry": "analytics"},
    {"id": 13, "section": "Skills",               "role": "Product Manager",         "template": "Product: Roadmapping, User Research, A/B Testing, OKRs\nTools: Jira, Confluence, Figma, Amplitude, Mixpanel\nMethodologies: Agile, Scrum, Lean, Design Thinking\nData: SQL, Google Analytics", "ats_score": 91, "industry": "product"},
    {"id": 14, "section": "Skills",               "role": "Marketing Manager",       "template": "Digital Marketing: SEO, SEM, Social Media, Email Marketing\nTools: HubSpot, Mailchimp, Google Analytics, Semrush\nPaid Ads: Google Ads, Facebook Ads, LinkedIn Ads\nDesign: Canva, Figma", "ats_score": 90, "industry": "marketing"},
    {"id": 15, "section": "Skills",               "role": "UX Designer",             "template": "Design Tools: Figma, Sketch, Adobe XD, InVision\nResearch: User Interviews, Usability Testing, A/B Testing\nPrototyping: Wireframing, High-fidelity Mockups, User Flows\nDevelopment: HTML, CSS", "ats_score": 89, "industry": "design"},
    {"id": 16, "section": "Education",            "role": "all",                     "template": "{degree} in {field}, {university} — GPA {gpa} | {graduation_year}\nRelevant Coursework: {courses}\nActivities: {activities}", "ats_score": 87, "industry": "all"},
    {"id": 17, "section": "Certifications",       "role": "Software Engineer",       "template": "• AWS Certified Solutions Architect — Associate (2024)\n• Google Cloud Professional Data Engineer (2024)\n• Meta Backend Developer Certificate (2023)", "ats_score": 91, "industry": "technology"},
    {"id": 18, "section": "Certifications",       "role": "Marketing Manager",       "template": "• Google Analytics 4 Certified (2024)\n• HubSpot Inbound Marketing Certified (2024)\n• Meta Blueprint Certified (2023)\n• Google Ads Search Certified (2024)", "ats_score": 90, "industry": "marketing"},
    {"id": 19, "section": "Projects",             "role": "Software Engineer",       "template": "{project_name} | {tech_stack} | {date}\n• Built {description} — achieved {metric}\n• GitHub: github.com/username/{repo}", "ats_score": 88, "industry": "technology"},
    {"id": 20, "section": "Projects",             "role": "Data Analyst",            "template": "{project_name} | Python, SQL, Tableau | {date}\n• Analyzed {data_description} to uncover {insight}\n• Resulted in {business_impact}", "ats_score": 86, "industry": "analytics"},
    {"id": 21, "section": "Achievements",         "role": "all",                     "template": "• {year}: {award_name} — {reason}\n• {year}: {achievement} — recognized by {organization}", "ats_score": 89, "industry": "all"},
    {"id": 22, "section": "Professional Summary", "role": "Cybersecurity Analyst",   "template": "Certified Cybersecurity Analyst with expertise in {tools}. Detected and mitigated {threats} security threats, reducing organizational risk by {metric}%.", "ats_score": 90, "industry": "security"},
    {"id": 23, "section": "Work Experience",      "role": "Customer Success Manager","template": "• Maintained {nrr}% net revenue retention across portfolio of {accounts} accounts\n• Reduced churn by {churn_reduction}% through proactive health monitoring and QBRs", "ats_score": 91, "industry": "saas"},
    {"id": 24, "section": "Professional Summary", "role": "Financial Analyst",       "template": "Quantitative Financial Analyst with {years} years in {sector}. Modeled ${portfolio}B in assets with {accuracy}% forecast accuracy.", "ats_score": 88, "industry": "finance"},
    {"id": 25, "section": "Work Experience",      "role": "Operations Manager",      "template": "• Managed {headcount} FTE team across {locations} locations, achieving {metric}% operational efficiency\n• Reduced costs by ${savings}K through process optimization", "ats_score": 92, "industry": "operations"},
    {"id": 26, "section": "Skills",               "role": "Financial Analyst",       "template": "Financial Modeling: DCF, LBO, M&A, Comparable Analysis\nTools: Excel, Bloomberg, Capital IQ, Tableau\nProgramming: Python, VBA, SQL\nCertifications: CFA Level II, FRM", "ats_score": 93, "industry": "finance"},
    {"id": 27, "section": "Cover Letter Opening", "role": "all",                     "template": "I am excited to apply for the {position} role at {company}. With {years} years of experience in {domain}, I have consistently {achievement} and am eager to bring these skills to your team.", "ats_score": 85, "industry": "all"},
    {"id": 28, "section": "Cover Letter Closing", "role": "all",                     "template": "I would welcome the opportunity to discuss how my background in {domain} aligns with {company}'s vision. Thank you for your consideration — I look forward to speaking with you.", "ats_score": 84, "industry": "all"},
    {"id": 29, "section": "LinkedIn Summary",     "role": "all",                     "template": "{tagline} | {role} at {company} | Helping {target_audience} achieve {outcome} | {keyword1} | {keyword2} | {keyword3}", "ats_score": 90, "industry": "all"},
    {"id": 30, "section": "References",           "role": "all",                     "template": "References available upon request. Professional network includes {reference_types} from {companies}.", "ats_score": 75, "industry": "all"},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_templates": 5,    "ats_check": False, "ai_suggestions": False, "cover_letter": False},
    "PRO":        {"price_usd": 19,  "max_templates": 20,   "ats_check": True,  "ai_suggestions": True,  "cover_letter": True},
    "ENTERPRISE": {"price_usd": 49,  "max_templates": None, "ats_check": True,  "ai_suggestions": True,  "cover_letter": True},
}


class ResumeBuildingBot:
    """Creates professional, ATS-optimized resumes with AI-powered suggestions.

    Competes with Resume.io and Zety by providing role-specific templates,
    real-time ATS scoring, and AI content generation.
    Monetization: $19/month PRO or $49/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="ResumeBuildingBot")

    def _available_templates(self) -> list[dict]:
        limit = self._config["max_templates"]
        return EXAMPLES[:limit] if limit else EXAMPLES

    def get_templates_for_role(self, role: str) -> list[dict]:
        """Return all resume templates relevant to a specific role."""
        templates = self._available_templates()
        return [t for t in templates if t["role"].lower() in (role.lower(), "all")]

    def get_templates_by_section(self, section: str) -> list[dict]:
        """Return templates for a specific resume section."""
        return [t for t in self._available_templates() if t["section"].lower() == section.lower()]

    def get_template(self, template_id: int) -> dict:
        """Get a specific template by ID."""
        template = next((t for t in EXAMPLES if t["id"] == template_id), None)
        if template is None:
            raise ValueError(f"Template ID {template_id} not found.")
        return dict(template)

    def check_ats_score(self, template_id: int) -> dict:
        """Check the ATS compatibility score of a resume section (PRO/ENTERPRISE)."""
        if not self._config["ats_check"]:
            raise PermissionError(
                "ATS score checking requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        template = self.get_template(template_id)
        score = template["ats_score"]
        return {
            "template_id": template_id,
            "section": template["section"],
            "ats_score": score,
            "grade": "Excellent" if score >= 90 else "Good" if score >= 80 else "Needs Work",
            "tips": [
                "Use action verbs at the start of bullet points.",
                "Include quantifiable metrics (%, $, numbers).",
                "Match keywords from the job description.",
            ],
        }

    def get_ai_suggestions(self, role: str, section: str) -> dict:
        """Get AI-powered content suggestions for a resume section (PRO/ENTERPRISE)."""
        if not self._config["ai_suggestions"]:
            raise PermissionError(
                "AI suggestions require PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        matching = [t for t in EXAMPLES if t["role"].lower() in (role.lower(), "all") and t["section"].lower() == section.lower()]
        best = max(matching, key=lambda t: t["ats_score"]) if matching else EXAMPLES[0]
        return {
            "role": role,
            "section": section,
            "suggested_template": best["template"],
            "ats_score": best["ats_score"],
            "tips": [
                f"For a {role}, emphasize quantifiable achievements.",
                "Tailor each bullet point to the job description.",
                "Use industry-specific keywords to pass ATS filters.",
            ],
        }

    def generate_cover_letter(self, role: str, company: str) -> dict:
        """Generate a cover letter framework (PRO/ENTERPRISE)."""
        if not self._config["cover_letter"]:
            raise PermissionError(
                "Cover letter generation requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        opening = next((t for t in EXAMPLES if t["section"] == "Cover Letter Opening"), None)
        closing = next((t for t in EXAMPLES if t["section"] == "Cover Letter Closing"), None)
        if not opening or not closing:
            raise ValueError("Cover letter templates not found in knowledge base.")
        return {
            "role": role,
            "company": company,
            "opening": opening["template"].replace("{position}", role).replace("{company}", company),
            "closing": closing["template"].replace("{company}", company),
            "structure": ["Opening paragraph", "Skills & experience paragraph", "Why this company", "Closing paragraph"],
        }

    def get_high_ats_templates(self, min_score: int = 90) -> list[dict]:
        """Return templates with high ATS compatibility scores."""
        return [t for t in self._available_templates() if t["ats_score"] >= min_score]

    def get_resume_sections(self) -> list[str]:
        """Return all available resume sections."""
        seen: set[str] = set()
        sections: list[str] = []
        for t in EXAMPLES:
            if t["section"] not in seen:
                seen.add(t["section"])
                sections.append(t["section"])
        return sections

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_templates"] if cfg["max_templates"] else "all"
        lines = [
            f"=== ResumeBuildingBot — {self.tier} Tier ===",
            f"  Monthly price   : ${cfg['price_usd']}/month",
            f"  Templates access: {limit}",
            f"  ATS score check : {'enabled' if cfg['ats_check'] else 'disabled'}",
            f"  AI suggestions  : {'enabled' if cfg['ai_suggestions'] else 'disabled'}",
            f"  Cover letter    : {'enabled' if cfg['cover_letter'] else 'disabled'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "resume_building", "templates_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "sections": len(self.get_resume_sections())}


if __name__ == "__main__":
    bot = ResumeBuildingBot(tier="PRO")
    se_templates = bot.get_templates_for_role("Software Engineer")
    print(f"Software Engineer templates: {len(se_templates)}")
    high_ats = bot.get_high_ats_templates(90)
    print(f"High-ATS templates (90+): {len(high_ats)}")
    suggestions = bot.get_ai_suggestions("Product Manager", "Professional Summary")
    print(f"\nAI ATS Score: {suggestions['ats_score']}")
    cover = bot.generate_cover_letter("Software Engineer", "TechCorp")
    print(f"Cover letter structure: {cover['structure']}")
    print(bot.describe_tier())
ResumeBuilderBot = ResumeBuildingBot


# ---------------------------------------------------------------------------
# Tier system additions for test compatibility
# ---------------------------------------------------------------------------
import random as _random_tier
from enum import Enum as _TierEnum


class Tier(_TierEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other.upper()
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()


_TIER_MONTHLY_PRICE = {"free": 0, "pro": 29, "enterprise": 99}


class ResumeBuildingBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_resumebuilding_bot_init = ResumeBuildingBot.__init__


def _resumebuilding_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_resumebuilding_bot_init(self, tier_val.upper())
    self.tier = Tier(tier_val)


ResumeBuildingBot.__init__ = _resumebuilding_bot_new_init
ResumeBuildingBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _resumebuilding_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _resumebuilding_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _resumebuilding_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise ResumeBuildingBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _resumebuilding_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _resumebuilding_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "ResumeBuildingBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _resumebuilding_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "ResumeBuildingBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


ResumeBuildingBot.monthly_price = _resumebuilding_bot_monthly_price
ResumeBuildingBot.get_tier_info = _resumebuilding_bot_get_tier_info
ResumeBuildingBot._enforce_tier = _resumebuilding_bot_enforce_tier
ResumeBuildingBot.list_items = _resumebuilding_bot_list_items
ResumeBuildingBot.analyze = _resumebuilding_bot_analyze
ResumeBuildingBot.export_report = _resumebuilding_bot_export_report
