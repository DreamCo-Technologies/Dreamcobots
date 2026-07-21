# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""Market Research module for Business Launch Pad."""

import uuid
from dataclasses import dataclass, field


@dataclass
class Competitor:
    name: str
    market_share: float  # 0.0 – 1.0
    strengths: list[str]
    weaknesses: list[str]


@dataclass
class CustomerPersona:
    name: str
    age_range: str
    pain_points: list[str]
    goals: list[str]
    channels: list[str]


@dataclass
class MarketReport:
    report_id: str
    industry: str
    competitors: list  # list[Competitor]
    personas: list    # list[CustomerPersona]
    swot: dict
    trends: list[str]


_INDUSTRY_COMPETITORS: dict[str, list[dict]] = {
    "technology": [
        {"name": "TechGiant Corp", "market_share": 0.32, "strengths": ["brand recognition", "R&D budget"], "weaknesses": ["slow innovation", "high prices"]},
        {"name": "Innovate Inc", "market_share": 0.18, "strengths": ["agile team", "modern UX"], "weaknesses": ["limited support", "small market"]},
        {"name": "Digital Solutions LLC", "market_share": 0.12, "strengths": ["enterprise clients", "integrations"], "weaknesses": ["legacy codebase", "complex onboarding"]},
    ],
    "retail": [
        {"name": "MegaMart", "market_share": 0.28, "strengths": ["supply chain", "low prices"], "weaknesses": ["poor service", "thin margins"]},
        {"name": "StyleHub", "market_share": 0.15, "strengths": ["brand loyalty", "curated products"], "weaknesses": ["high cost", "limited SKUs"]},
        {"name": "QuickShop Online", "market_share": 0.10, "strengths": ["fast delivery", "mobile app"], "weaknesses": ["returns policy", "product quality"]},
    ],
    "healthcare": [
        {"name": "HealthFirst Group", "market_share": 0.25, "strengths": ["network size", "trust"], "weaknesses": ["bureaucratic", "slow tech adoption"]},
        {"name": "MedConnect", "market_share": 0.14, "strengths": ["telehealth platform", "NPS"], "weaknesses": ["rural coverage", "data privacy concerns"]},
        {"name": "WellnessAI", "market_share": 0.08, "strengths": ["AI diagnostics", "cost efficiency"], "weaknesses": ["regulatory risk", "nascent brand"]},
    ],
}

_DEFAULT_COMPETITORS = [
    {"name": "Market Leader A", "market_share": 0.30, "strengths": ["established brand", "resources"], "weaknesses": ["innovation lag", "high cost"]},
    {"name": "Challenger B", "market_share": 0.15, "strengths": ["agile", "pricing"], "weaknesses": ["limited reach", "support gaps"]},
    {"name": "Niche Player C", "market_share": 0.08, "strengths": ["specialization", "community"], "weaknesses": ["scale", "feature gaps"]},
]

_INDUSTRY_TRENDS: dict[str, list[str]] = {
    "technology": ["AI/ML adoption accelerating", "Edge computing growth", "Zero-trust security models", "Low-code/no-code platforms", "Sustainability in tech", "API-first architecture"],
    "retail": ["Social commerce expansion", "Buy-now-pay-later growth", "Omnichannel experiences", "Sustainable packaging", "AR try-on tools", "Hyper-personalization"],
    "healthcare": ["Telehealth normalization", "AI-assisted diagnostics", "Value-based care models", "Wearable health devices", "Mental health awareness", "Genomic medicine"],
    "education": ["Micro-credentialing rise", "AI tutoring adoption", "Gamified learning", "Corporate upskilling demand", "Global online platforms", "Competency-based education"],
    "finance": ["Embedded finance growth", "DeFi maturation", "ESG investing", "Real-time payments", "Open banking APIs", "RegTech automation"],
}

_DEFAULT_TRENDS = [
    "Digital transformation acceleration",
    "Data-driven decision making",
    "Sustainability and ESG focus",
    "Remote-first work models",
    "Customer experience personalization",
    "Automation and AI integration",
]


class MarketResearch:
    """Provides competitor mapping, persona building, SWOT analysis, and trend reports."""

    def __init__(self) -> None:
        self._reports: list[MarketReport] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_report(self, industry: str) -> MarketReport:
        """Generate a complete market research report for an industry."""
        competitors = self.map_competitors(industry)
        personas = self.build_personas(industry)
        swot = self.generate_swot("Our Company", industry)
        trends = self.get_trends(industry)
        report = MarketReport(
            report_id=str(uuid.uuid4()),
            industry=industry,
            competitors=competitors,
            personas=personas,
            swot=swot,
            trends=trends,
        )
        self._reports.append(report)
        return report

    def map_competitors(self, industry: str) -> list[Competitor]:
        """Return a list of mapped competitors for the given industry."""
        raw = _INDUSTRY_COMPETITORS.get(industry.lower(), _DEFAULT_COMPETITORS)
        return [Competitor(**c) for c in raw]

    def build_personas(self, industry: str) -> list[CustomerPersona]:
        """Build customer personas for the given industry."""
        personas = [
            CustomerPersona(
                name="Early Adopter Alex",
                age_range="25-35",
                pain_points=[f"High cost of existing {industry} solutions", "Lack of integration", "Poor support"],
                goals=["Save time", "Reduce costs", "Grow business"],
                channels=["LinkedIn", "Twitter", "Podcasts"],
            ),
            CustomerPersona(
                name="Pragmatic Pat",
                age_range="35-50",
                pain_points=[f"Complexity in {industry} tools", "Training burden", "Vendor lock-in"],
                goals=["Reliability", "ROI proof", "Easy onboarding"],
                channels=["Industry blogs", "Email newsletters", "Referrals"],
            ),
            CustomerPersona(
                name="Enterprise Emma",
                age_range="40-55",
                pain_points=["Compliance requirements", "Scalability concerns", "Security gaps"],
                goals=["Enterprise-grade security", "Compliance automation", "Strategic partnerships"],
                channels=["Analyst reports", "Conferences", "Direct sales"],
            ),
        ]
        return personas

    def generate_swot(self, business_name: str, industry: str) -> dict:
        """Generate a SWOT analysis dict with four lists of items."""
        return {
            "strengths": [
                f"Innovative approach in {industry}",
                "Experienced founding team",
                "Strong customer focus",
                "Agile development process",
            ],
            "weaknesses": [
                "Limited brand awareness",
                "Early-stage funding constraints",
                "Small team size",
                "No established distribution channels",
            ],
            "opportunities": [
                f"Rapidly growing {industry} market",
                "Underserved customer segments",
                "Technology disruption potential",
                "Partnership and integration opportunities",
            ],
            "threats": [
                "Well-funded incumbents",
                "Regulatory changes",
                "Economic downturn risk",
                "Rapid competitive imitation",
            ],
        }

    def get_trends(self, industry: str) -> list[str]:
        """Return 5+ market trends for the given industry."""
        return _INDUSTRY_TRENDS.get(industry.lower(), _DEFAULT_TRENDS)

    def list_reports(self) -> list[MarketReport]:
        """Return all generated market reports."""
        return list(self._reports)
