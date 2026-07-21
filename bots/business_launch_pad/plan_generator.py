# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""Business Plan Generator module for Business Launch Pad."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class BusinessPlan:
    plan_id: str
    business_name: str
    industry: str
    executive_summary: str
    target_market: str
    revenue_model: str
    financial_projections: dict  # year1..year5 revenue
    tam_usd: float
    created_at: str


_TAM_BY_INDUSTRY: dict[str, float] = {
    "technology": 5_000_000_000_000.0,
    "healthcare": 4_200_000_000_000.0,
    "finance": 3_800_000_000_000.0,
    "retail": 6_000_000_000_000.0,
    "education": 7_300_000_000_000.0,
    "real estate": 3_700_000_000_000.0,
    "food & beverage": 2_900_000_000_000.0,
    "manufacturing": 8_500_000_000_000.0,
    "transportation": 2_100_000_000_000.0,
    "entertainment": 2_400_000_000_000.0,
    "consulting": 1_300_000_000_000.0,
    "e-commerce": 5_700_000_000_000.0,
}

_DEFAULT_TAM = 1_000_000_000_000.0  # $1T fallback


class PlanGenerator:
    """Generates AI-powered business plans with financial projections and TAM analysis."""

    def __init__(self) -> None:
        self._plans: list[BusinessPlan] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_plan(self, business_name: str, industry: str, description: str) -> BusinessPlan:
        """Generate a complete business plan."""
        base_revenue = 100_000.0
        growth_rate = 0.35
        projections = self.generate_financial_projections(base_revenue, growth_rate)
        tam = self.calculate_tam(industry)
        summary = self.generate_executive_summary(business_name, industry, description)
        plan = BusinessPlan(
            plan_id=str(uuid.uuid4()),
            business_name=business_name,
            industry=industry,
            executive_summary=summary,
            target_market=f"Primary customers in the {industry} sector seeking innovative solutions",
            revenue_model="Subscription-based recurring revenue with one-time setup fees",
            financial_projections=projections,
            tam_usd=tam,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._plans.append(plan)
        return plan

    def generate_financial_projections(self, base_revenue: float, growth_rate: float) -> dict:
        """Project revenue for years 1-5 given a base and annual growth rate."""
        projections = {}
        revenue = base_revenue
        for year in range(1, 6):
            projections[f"year{year}"] = round(revenue, 2)
            revenue *= 1 + growth_rate
        return projections

    def calculate_tam(self, industry: str) -> float:
        """Return total addressable market estimate in USD for the given industry."""
        return _TAM_BY_INDUSTRY.get(industry.lower(), _DEFAULT_TAM)

    def generate_executive_summary(self, business_name: str, industry: str, description: str) -> str:
        """Generate an executive summary paragraph."""
        return (
            f"{business_name} is an innovative company operating in the {industry} industry. "
            f"{description} "
            f"The company is positioned to capture significant market share through differentiated "
            f"products and services, a customer-centric approach, and scalable operations. "
            f"With a strong founding team and clear go-to-market strategy, {business_name} aims "
            f"to become a leading player in the {industry} space within five years."
        )

    def export_pitch_deck(self, plan: BusinessPlan) -> dict:
        """Return structured pitch deck data derived from a business plan."""
        return {
            "title_slide": {
                "company": plan.business_name,
                "tagline": f"Transforming the {plan.industry} industry",
            },
            "problem": f"Key pain points in the {plan.industry} market remain unaddressed.",
            "solution": plan.executive_summary,
            "market_opportunity": {
                "tam_usd": plan.tam_usd,
                "target_segment": plan.target_market,
            },
            "business_model": plan.revenue_model,
            "financials": plan.financial_projections,
            "team": "Experienced founding team with domain expertise in " + plan.industry,
            "ask": "Seeking seed funding to accelerate growth and product development.",
        }

    def list_plans(self) -> list[BusinessPlan]:
        """Return all generated plans."""
        return list(self._plans)

    def get_plan(self, plan_id: str) -> BusinessPlan:
        """Retrieve a plan by ID; raises KeyError if not found."""
        for plan in self._plans:
            if plan.plan_id == plan_id:
                return plan
        raise KeyError(f"Plan '{plan_id}' not found")
