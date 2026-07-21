"""Smart City Government AI Services — tax, census, and policy modeling."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from framework import GlobalAISourcesFlow  # noqa: F401

_flow = GlobalAISourcesFlow(bot_name="SmartCityGovernmentAI")


class GovernmentAIError(Exception):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Tax System AI
# ---------------------------------------------------------------------------

class TaxSystemAI:
    """Tier-aware AI-powered tax calculation and policy optimization."""

    TAX_BRACKETS = [
        {"min": 0,       "max": 20000,  "rate": 0.10},
        {"min": 20001,   "max": 50000,  "rate": 0.20},
        {"min": 50001,   "max": 100000, "rate": 0.28},
        {"min": 100001,  "max": 250000, "rate": 0.35},
        {"min": 250001,  "max": None,   "rate": 0.42},
    ]

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)

    def calculate_tax(self, citizen_data: dict) -> dict:
        """Calculate tax liability for a citizen based on their income data."""
        income = citizen_data.get("annual_income", 0)
        deductions = citizen_data.get("deductions", 0) if self.tier in (Tier.PRO, Tier.ENTERPRISE) else 0
        taxable_income = max(0, income - deductions)

        tax_owed = 0.0
        breakdown = []
        for bracket in self.TAX_BRACKETS:
            if taxable_income <= 0:
                break
            lower = bracket["min"]
            upper = bracket["max"] if bracket["max"] else float("inf")
            amount_in_bracket = min(taxable_income - max(0, lower - 1), upper - lower + 1)
            if amount_in_bracket <= 0:
                continue
            bracket_tax = amount_in_bracket * bracket["rate"]
            tax_owed += bracket_tax
            if self.tier in (Tier.PRO, Tier.ENTERPRISE):
                upper_label = "inf" if bracket["max"] is None else str(bracket["max"])
                breakdown.append({
                    "bracket": f"${lower}-{upper_label}",
                    "rate_pct": bracket["rate"] * 100,
                    "amount_taxed": round(amount_in_bracket, 2),
                    "tax": round(bracket_tax, 2),
                })

        effective_rate = round(tax_owed / income * 100, 2) if income > 0 else 0.0

        result = {
            "citizen_id": citizen_data.get("citizen_id", "unknown"),
            "annual_income": income,
            "taxable_income": taxable_income,
            "tax_owed": round(tax_owed, 2),
            "effective_rate_pct": effective_rate,
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["deductions_applied"] = deductions
            result["bracket_breakdown"] = breakdown

        if self.tier == Tier.ENTERPRISE:
            result["optimization_opportunities"] = self._find_optimizations(citizen_data)

        return result

    def _find_optimizations(self, citizen_data: dict) -> list:
        income = citizen_data.get("annual_income", 0)
        opps = []
        if citizen_data.get("retirement_contributions", 0) < income * 0.15:
            opps.append("Increase retirement contributions for tax deferral")
        if not citizen_data.get("hsa_enrolled", False):
            opps.append("Enroll in HSA for pre-tax health savings")
        if income > 100000 and not citizen_data.get("municipal_bonds", False):
            opps.append("Consider tax-exempt municipal bonds")
        return opps

    def optimize_tax_policy(self, policy_data: dict) -> dict:
        """Analyze and optimize a tax policy for efficiency and equity."""
        if self.tier == Tier.FREE:
            raise GovernmentAIError(
                "Tax policy optimization requires PRO or ENTERPRISE tier."
            )
        population = policy_data.get("population", 100000)
        current_revenue = policy_data.get("current_revenue_usd", 500_000_000)
        target_revenue = policy_data.get("target_revenue_usd", current_revenue * 1.05)

        gap = target_revenue - current_revenue
        adjustment_pct = round(gap / current_revenue * 100, 2)

        result = {
            "policy_name": policy_data.get("policy_name", "unnamed"),
            "population_affected": population,
            "current_revenue_usd": current_revenue,
            "target_revenue_usd": target_revenue,
            "revenue_gap_usd": round(gap, 2),
            "recommended_rate_adjustment_pct": adjustment_pct,
            "efficiency_score": round(85 - abs(adjustment_pct) * 0.5, 1),
        }

        if self.tier == Tier.ENTERPRISE:
            result["equity_index"] = 0.72
            result["ai_recommendation"] = (
                "Broaden base and reduce top marginal rate by 2% to improve compliance."
            )

        return result

    def generate_tax_report(self, period: str) -> dict:
        """Generate a tax collection summary report for a fiscal period."""
        if self.tier == Tier.FREE:
            raise GovernmentAIError(
                "Tax report generation requires PRO or ENTERPRISE tier."
            )
        result = {
            "period": period,
            "total_filers": 124_500,
            "total_revenue_collected_usd": 842_000_000,
            "compliance_rate_pct": 94.2,
            "average_tax_usd": 6763,
            "tier": self.tier.value,
        }

        if self.tier == Tier.ENTERPRISE:
            result["top_bracket_contribution_pct"] = 38.5
            result["evasion_risk_flagged"] = 312
            result["audit_recommendations"] = 45

        return result


# ---------------------------------------------------------------------------
# Census Collector
# ---------------------------------------------------------------------------

class CensusCollector:
    """Tier-aware AI-powered census data collection and demographics analysis."""

    REGION_DATA = {
        "city_center":  {"population": 85000,  "households": 34000, "median_age": 32, "avg_income": 68000},
        "north_district": {"population": 62000, "households": 24800, "median_age": 38, "avg_income": 82000},
        "south_district": {"population": 74000, "households": 29600, "median_age": 29, "avg_income": 51000},
        "east_district":  {"population": 48000, "households": 19200, "median_age": 44, "avg_income": 95000},
        "west_district":  {"population": 53000, "households": 21200, "median_age": 35, "avg_income": 61000},
        "suburbs":        {"population": 112000,"households": 44800, "median_age": 41, "avg_income": 87000},
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)

    def collect_census(self, region: str) -> dict:
        """Collect and return census data for a region."""
        data = self.REGION_DATA.get(region, self.REGION_DATA["city_center"])

        result = {
            "region": region,
            "population": data["population"],
            "households": data["households"],
            "collection_date": "2024-01-15",
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["median_age"] = data["median_age"]
            result["avg_household_income_usd"] = data["avg_income"]
            result["response_rate_pct"] = 87.3

        if self.tier == Tier.ENTERPRISE:
            result["data_quality_score"] = 96.5
            result["anomalies_detected"] = 0
            result["api_endpoint"] = f"/api/v1/census/{region}"

        return result

    def analyze_demographics(self, region: str) -> dict:
        """Analyze demographic breakdown for a region."""
        if self.tier == Tier.FREE:
            raise GovernmentAIError(
                "Demographic analysis requires PRO or ENTERPRISE tier."
            )
        data = self.REGION_DATA.get(region, self.REGION_DATA["city_center"])

        result = {
            "region": region,
            "total_population": data["population"],
            "age_distribution": {
                "under_18": round(data["population"] * 0.22),
                "18_to_35": round(data["population"] * 0.28),
                "36_to_55": round(data["population"] * 0.30),
                "over_55":  round(data["population"] * 0.20),
            },
            "employment_rate_pct": 92.4,
            "education": {
                "high_school_pct": 85.2,
                "bachelors_pct": 48.1,
                "graduate_pct": 22.3,
            },
        }

        if self.tier == Tier.ENTERPRISE:
            result["income_quintiles"] = {
                "Q1_avg_usd": round(data["avg_income"] * 0.3),
                "Q2_avg_usd": round(data["avg_income"] * 0.6),
                "Q3_avg_usd": round(data["avg_income"] * 1.0),
                "Q4_avg_usd": round(data["avg_income"] * 1.5),
                "Q5_avg_usd": round(data["avg_income"] * 3.0),
            }
            result["diversity_index"] = 0.68

        return result

    def project_population(self, region: str, years: int) -> dict:
        """Project population growth for a region over the given number of years."""
        if self.tier == Tier.FREE:
            raise GovernmentAIError(
                "Population projection requires PRO or ENTERPRISE tier."
            )
        data = self.REGION_DATA.get(region, self.REGION_DATA["city_center"])
        growth_rate = 0.012  # 1.2% annual growth
        projected = round(data["population"] * ((1 + growth_rate) ** years))

        result = {
            "region": region,
            "current_population": data["population"],
            "projection_years": years,
            "projected_population": projected,
            "annual_growth_rate_pct": growth_rate * 100,
            "confidence_interval": {
                "low": round(projected * 0.95),
                "high": round(projected * 1.05),
            },
        }

        if self.tier == Tier.ENTERPRISE:
            result["migration_factor"] = 0.8
            result["model_version"] = "census-proj-v2"
            result["scenarios"] = {
                "optimistic": round(projected * 1.08),
                "baseline": projected,
                "pessimistic": round(projected * 0.92),
            }

        return result


# ---------------------------------------------------------------------------
# Policy Modeling Bot
# ---------------------------------------------------------------------------

class PolicyModelingBot:
    """Tier-aware AI-driven policy modeling and simulation."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)

    def model_policy(self, policy_data: dict) -> dict:
        """Create a structured model of a proposed policy."""
        name = policy_data.get("name", "Unnamed Policy")
        domain = policy_data.get("domain", "general")
        budget_usd = policy_data.get("budget_usd", 1_000_000)

        result = {
            "policy_name": name,
            "domain": domain,
            "budget_usd": budget_usd,
            "complexity_score": min(len(name) * 2, 100),
            "feasibility": "high" if budget_usd < 10_000_000 else "medium",
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["stakeholders_affected"] = policy_data.get("stakeholders", ["citizens", "businesses"])
            result["implementation_phases"] = 3 if budget_usd > 5_000_000 else 2
            result["risk_level"] = "low" if budget_usd < 5_000_000 else "medium"

        if self.tier == Tier.ENTERPRISE:
            result["ai_model_used"] = "policy-gpt-v4"
            result["cross_policy_conflicts"] = []

        return result

    def simulate_impact(self, policy: dict, population: int) -> dict:
        """Simulate the impact of a policy on a given population size."""
        if self.tier == Tier.FREE:
            raise GovernmentAIError(
                "Policy impact simulation requires PRO or ENTERPRISE tier."
            )
        budget = policy.get("budget_usd", 1_000_000)
        cost_per_person = round(budget / max(population, 1), 2)
        benefit_multiplier = 1.8 if self.tier == Tier.ENTERPRISE else 1.4

        result = {
            "policy_name": policy.get("name", "Unnamed"),
            "population_affected": population,
            "cost_per_person_usd": cost_per_person,
            "estimated_benefit_usd": round(budget * benefit_multiplier),
            "roi_pct": round((benefit_multiplier - 1) * 100, 1),
            "time_to_impact_months": 18 if budget > 5_000_000 else 9,
        }

        if self.tier == Tier.ENTERPRISE:
            result["gdp_impact_pct"] = round(budget / 10_000_000_000 * 100, 4)
            result["confidence_interval_pct"] = {"low": result["roi_pct"] * 0.8, "high": result["roi_pct"] * 1.2}
            result["simulation_runs"] = 10000

        return result

    def recommend_policy(self, domain: str) -> dict:
        """Recommend policy actions for a given governance domain."""
        if self.tier == Tier.FREE:
            raise GovernmentAIError(
                "Policy recommendation requires PRO or ENTERPRISE tier."
            )
        recommendations = {
            "transportation": ["Expand public transit", "Build cycling infrastructure", "Congestion pricing"],
            "housing":        ["Increase affordable housing units", "Streamline permits", "Anti-speculation tax"],
            "education":      ["Universal pre-K", "STEM curriculum update", "Teacher salary increase"],
            "healthcare":     ["Expand community clinics", "Mental health funding", "Preventive care programs"],
            "environment":    ["Green energy subsidies", "EV charging network", "Tree canopy expansion"],
        }

        items = recommendations.get(domain, ["Conduct stakeholder analysis", "Commission feasibility study"])

        result = {
            "domain": domain,
            "top_recommendations": items[:2] if self.tier == Tier.PRO else items,
            "priority": "high" if domain in ("healthcare", "environment") else "medium",
            "tier": self.tier.value,
        }

        if self.tier == Tier.ENTERPRISE:
            result["cost_estimate_usd"] = len(items) * 2_500_000
            result["public_approval_prediction_pct"] = 72.5
            result["similar_cities_adopted"] = ["Amsterdam", "Singapore", "Barcelona"]

        return result
