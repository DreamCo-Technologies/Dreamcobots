"""
analytics.py – Company-profile analytics, partner recruitment, and
AI-ecosystem directory for the Dreamcobots Premium tier.

Key capabilities
----------------
* AI Company Profile  – generate a rich profile for any organisation.
* Partner Recruitment – score potential partners and produce outreach plans.
* AI Ecosystem Directory – maintain a curated list of top AI organisations.
* OnSite Signup Flow  – personalised developer / enterprise signup journeys.
* Usage Analytics     – aggregate chatbot and platform usage stats.

All features except ``usage_summary`` require the Premium tier.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .tiers import Tier, require_feature


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CompanyProfile:
    """Enriched profile for an organisation in the AI ecosystem."""

    company_id: str
    name: str
    industry: str
    focus_areas: List[str]
    headquarters: str
    website: str
    description: str
    partnership_potential_score: float = 0.0  # 0.0 – 1.0
    contact_email: str = ""
    developer_portal_url: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class PartnerRecruitmentResult:
    """Output of the partner-recruitment analysis engine."""

    run_id: str
    generated_at: str
    requester_company: str
    candidates: List[Dict]          # ranked list of CompanyProfile dicts
    recommended_outreach: List[str] # action-item strings
    estimated_reach: int            # total developer community size


@dataclass
class UsageStat:
    date: str
    total_messages: int
    active_users: int
    tier_breakdown: Dict[str, int]


# ---------------------------------------------------------------------------
# Seed data – curated AI ecosystem organisations
# ---------------------------------------------------------------------------

_AI_ECOSYSTEM_SEED: List[CompanyProfile] = [
    CompanyProfile(
        company_id="org_001",
        name="OpenAI",
        industry="AI Research & Products",
        focus_areas=["large language models", "safety", "AGI research"],
        headquarters="San Francisco, CA, USA",
        website="https://openai.com",
        description="Creator of GPT-4, DALL-E, and the ChatGPT platform.",
        partnership_potential_score=0.92,
        contact_email="partnerships@openai.com",
        developer_portal_url="https://platform.openai.com",
        tags=["llm", "api", "enterprise", "research"],
    ),
    CompanyProfile(
        company_id="org_002",
        name="Anthropic",
        industry="AI Safety & Research",
        focus_areas=["constitutional AI", "alignment", "enterprise LLMs"],
        headquarters="San Francisco, CA, USA",
        website="https://anthropic.com",
        description="Developer of the Claude AI assistant family.",
        partnership_potential_score=0.88,
        contact_email="partnerships@anthropic.com",
        developer_portal_url="https://console.anthropic.com",
        tags=["llm", "safety", "enterprise"],
    ),
    CompanyProfile(
        company_id="org_003",
        name="Moonshot AI (KimiK)",
        industry="AI Products",
        focus_areas=["long-context LLMs", "Chinese-English bilingual AI", "enterprise chatbots"],
        headquarters="Beijing, China",
        website="https://moonshot.cn",
        description="Developer of Kimi, a long-context AI assistant with 128k-token context.",
        partnership_potential_score=0.94,
        contact_email="bd@moonshot.cn",
        developer_portal_url="https://platform.moonshot.cn",
        tags=["kimi-k", "long-context", "enterprise", "bilingual"],
    ),
    CompanyProfile(
        company_id="org_004",
        name="Hugging Face",
        industry="AI Tooling & Community",
        focus_areas=["model hub", "open-source AI", "datasets", "inference APIs"],
        headquarters="New York, NY, USA",
        website="https://huggingface.co",
        description="The leading open-source AI community and model hub.",
        partnership_potential_score=0.85,
        contact_email="enterprise@huggingface.co",
        developer_portal_url="https://huggingface.co/docs",
        tags=["open-source", "hub", "api", "community"],
    ),
    CompanyProfile(
        company_id="org_005",
        name="Google DeepMind",
        industry="AI Research",
        focus_areas=["reinforcement learning", "Gemini models", "scientific AI"],
        headquarters="London, UK",
        website="https://deepmind.google",
        description="World-leading AI research lab and creator of the Gemini model family.",
        partnership_potential_score=0.90,
        contact_email="research-partnerships@google.com",
        developer_portal_url="https://ai.google.dev",
        tags=["research", "gemini", "enterprise", "science"],
    ),
    CompanyProfile(
        company_id="org_006",
        name="Mistral AI",
        industry="Open-weight LLMs",
        focus_areas=["efficient LLMs", "open weights", "European AI"],
        headquarters="Paris, France",
        website="https://mistral.ai",
        description="Creator of Mistral 7B and Mixtral, champion of open-weight AI.",
        partnership_potential_score=0.80,
        contact_email="partnerships@mistral.ai",
        developer_portal_url="https://docs.mistral.ai",
        tags=["open-source", "llm", "efficient", "european"],
    ),
    CompanyProfile(
        company_id="org_007",
        name="Cohere",
        industry="Enterprise AI",
        focus_areas=["RAG", "embeddings", "enterprise search", "command models"],
        headquarters="Toronto, Canada",
        website="https://cohere.com",
        description="Enterprise AI platform specialising in retrieval-augmented generation.",
        partnership_potential_score=0.83,
        contact_email="partnerships@cohere.com",
        developer_portal_url="https://docs.cohere.com",
        tags=["rag", "embeddings", "enterprise", "search"],
    ),
]


# ---------------------------------------------------------------------------
# Analytics engine
# ---------------------------------------------------------------------------

class AnalyticsEngine:
    """
    Provides company analytics, partner-recruitment, and ecosystem-directory
    features for the Dreamcobots platform.
    """

    def __init__(self, tier: Tier = Tier.PREMIUM) -> None:
        self.tier = tier
        self._ecosystem: Dict[str, CompanyProfile] = {
            org.company_id: org for org in _AI_ECOSYSTEM_SEED
        }
        self._usage_history: List[UsageStat] = []

    # ------------------------------------------------------------------
    # Company Profile (Premium)
    # ------------------------------------------------------------------

    def get_company_profile(self, company_id: str) -> Optional[CompanyProfile]:
        """Return a company profile by ID (Premium only)."""
        require_feature(self.tier, "ai_ecosystem_directory")
        return self._ecosystem.get(company_id)

    def search_companies(
        self,
        query: str = "",
        tags: Optional[List[str]] = None,
        min_score: float = 0.0,
    ) -> List[CompanyProfile]:
        """
        Search the AI ecosystem directory.

        Parameters
        ----------
        query : str
            Case-insensitive substring match against name or description.
        tags : list[str]
            Filter to companies having at least one of these tags.
        min_score : float
            Minimum partnership_potential_score (0.0 – 1.0).
        """
        require_feature(self.tier, "ai_ecosystem_directory")
        results = list(self._ecosystem.values())

        if query:
            q = query.lower()
            results = [
                c for c in results
                if q in c.name.lower() or q in c.description.lower()
            ]
        if tags:
            tag_set = set(tags)
            results = [c for c in results if tag_set.intersection(c.tags)]
        results = [c for c in results if c.partnership_potential_score >= min_score]

        return sorted(results, key=lambda c: c.partnership_potential_score, reverse=True)

    def add_company(self, profile: CompanyProfile) -> None:
        """Add or update a company in the ecosystem directory (Premium only)."""
        require_feature(self.tier, "ai_ecosystem_directory")
        self._ecosystem[profile.company_id] = profile

    # ------------------------------------------------------------------
    # Partner Recruitment (Premium)
    # ------------------------------------------------------------------

    def run_partner_recruitment(
        self,
        requester_name: str,
        focus_areas: List[str],
        top_n: int = 5,
    ) -> PartnerRecruitmentResult:
        """
        Identify and rank the best partner candidates for *requester_name*.

        Scoring combines:
        * base partnership_potential_score
        * focus-area overlap with the requester
        """
        require_feature(self.tier, "partner_recruitment")

        candidates = list(self._ecosystem.values())

        # Score each candidate based on focus-area overlap
        def _score(company: CompanyProfile) -> float:
            overlap = len(set(focus_areas) & set(company.focus_areas))
            bonus = min(overlap * 0.05, 0.20)
            return round(min(company.partnership_potential_score + bonus, 1.0), 3)

        ranked = sorted(candidates, key=_score, reverse=True)[:top_n]

        candidate_dicts = []
        for company in ranked:
            candidate_dicts.append({
                "company_id": company.company_id,
                "name": company.name,
                "score": _score(company),
                "focus_areas": company.focus_areas,
                "website": company.website,
                "contact_email": company.contact_email,
                "developer_portal_url": company.developer_portal_url,
            })

        outreach_actions = [
            f"Send personalised introduction to {c['name']} via {c['contact_email']}"
            for c in candidate_dicts[:3]
        ] + [
            "Invite top partners to Dreamcobots OnSite developer portal",
            "Schedule joint webinar with top-ranked ecosystem partner",
            "Share co-marketing materials via Marketing Doc Manager",
        ]

        total_reach = sum(
            {"OpenAI": 2_500_000, "Google DeepMind": 1_800_000}.get(c["name"], 100_000)
            for c in candidate_dicts
        )

        return PartnerRecruitmentResult(
            run_id=f"pr_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}",
            generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            requester_company=requester_name,
            candidates=candidate_dicts,
            recommended_outreach=outreach_actions,
            estimated_reach=total_reach,
        )

    # ------------------------------------------------------------------
    # OnSite Signup Flow (Premium)
    # ------------------------------------------------------------------

    def generate_onsite_signup_flow(
        self, user_type: str = "developer"
    ) -> Dict:
        """
        Generate a personalised OnSite signup/developer flow config.

        user_type : "developer" | "enterprise" | "partner"
        """
        require_feature(self.tier, "partner_recruitment")

        flows = {
            "developer": {
                "steps": [
                    "Register with GitHub OAuth or email",
                    "Choose AI model tier (Free / Intermediate / Premium)",
                    "Complete API key setup wizard",
                    "Explore the chatbot playground",
                    "Read Quickstart guide & sample integrations",
                ],
                "cta": "Start building with Dreamcobots AI",
                "resources": ["API Docs", "SDK Download", "Community Forum"],
            },
            "enterprise": {
                "steps": [
                    "Book a live demo with our solutions team",
                    "Custom tier configuration & SLA discussion",
                    "SSO / SAML integration setup",
                    "Dedicated onboarding manager assigned",
                    "Go-live review and load-test",
                ],
                "cta": "Schedule your Enterprise Demo",
                "resources": ["Enterprise Brochure", "Security Whitepaper", "Case Studies"],
            },
            "partner": {
                "steps": [
                    "Submit partner application via the AI Ecosystem Directory",
                    "Review mutual integration opportunities",
                    "Sign partner agreement and access co-marketing assets",
                    "List joint offering in Dreamcobots Marketplace",
                    "Attend partner enablement webinar",
                ],
                "cta": "Apply to the Dreamcobots Partner Programme",
                "resources": ["Partner Guide", "Co-Marketing Toolkit", "Technical Integration Docs"],
            },
        }

        return flows.get(user_type, flows["developer"])

    # ------------------------------------------------------------------
    # Usage Analytics (available from Intermediate tier)
    # ------------------------------------------------------------------

    def record_usage(
        self,
        total_messages: int,
        active_users: int,
        tier_breakdown: Optional[Dict[str, int]] = None,
    ) -> None:
        """Record a daily usage snapshot."""
        require_feature(self.tier, "analytics_dashboard")
        stat = UsageStat(
            date=datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
            total_messages=total_messages,
            active_users=active_users,
            tier_breakdown=tier_breakdown or {},
        )
        self._usage_history.append(stat)

    def usage_summary(self) -> Dict:
        """Return aggregated usage metrics."""
        require_feature(self.tier, "analytics_dashboard")
        if not self._usage_history:
            return {"message": "No usage data recorded yet."}

        total_msgs = sum(s.total_messages for s in self._usage_history)
        avg_users = sum(s.active_users for s in self._usage_history) / len(self._usage_history)
        return {
            "days_recorded": len(self._usage_history),
            "total_messages": total_msgs,
            "average_daily_active_users": round(avg_users, 1),
            "latest_date": self._usage_history[-1].date,
        }
