# GLOBAL AI SOURCES FLOW
"""Loyalty Program Impact Simulator - model the financial impact of loyalty programs."""
import sys
import os
import importlib.util
_TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_TOOL_DIR, '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
# Load local tiers.py by path to avoid sys.modules conflicts with other tiers modules
_tiers_spec = importlib.util.spec_from_file_location('_local_tiers', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS


class LoyaltyProgramImpactSimulator:
    """Simulate the revenue and retention impact of loyalty programs."""

    def __init__(self, tier: str = "free"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["free"])
        self._scenario_count = 0
        self._scenario_limit = 3 if tier == "free" else None

    def _check_limit(self):
        if self._scenario_limit and self._scenario_count >= self._scenario_limit:
            raise PermissionError(f"Scenario limit ({self._scenario_limit}) reached. Upgrade to Pro.")

    def simulate_roi(self, params: dict) -> dict:
        """
        Simulate loyalty program ROI.

        params keys:
          - customer_count: int
          - avg_annual_spend: float
          - enrollment_rate: float (0-1)
          - spend_lift_pct: float  (e.g. 0.10 for 10%)
          - program_cost_per_member: float
        """
        self._check_limit()
        count = params.get("customer_count", 1000)
        avg_spend = params.get("avg_annual_spend", 500.0)
        enrollment_rate = params.get("enrollment_rate", 0.30)
        spend_lift = params.get("spend_lift_pct", 0.10)
        cost_per_member = params.get("program_cost_per_member", 20.0)

        enrolled = int(count * enrollment_rate)
        baseline_revenue = count * avg_spend
        incremental_revenue = enrolled * avg_spend * spend_lift
        program_cost = enrolled * cost_per_member
        net_benefit = incremental_revenue - program_cost
        roi_pct = round((net_benefit / program_cost) * 100, 2) if program_cost else 0.0

        self._scenario_count += 1
        return {
            "enrolled_members": enrolled,
            "baseline_revenue": round(baseline_revenue, 2),
            "incremental_revenue": round(incremental_revenue, 2),
            "program_cost": round(program_cost, 2),
            "net_benefit": round(net_benefit, 2),
            "roi_pct": roi_pct,
            "tier": self.tier,
        }

    def model_clv(self, params: dict) -> dict:
        """Model Customer Lifetime Value impact (Pro+ only)."""
        if self.tier == "free":
            raise PermissionError("CLV modeling requires Pro tier or higher.")
        avg_spend = params.get("avg_annual_spend", 500.0)
        retention_rate = params.get("retention_rate", 0.70)
        discount_rate = params.get("discount_rate", 0.10)
        loyalty_retention_lift = params.get("loyalty_retention_lift", 0.05)

        clv_base = avg_spend * (retention_rate / (1 + discount_rate - retention_rate))
        new_retention = min(0.99, retention_rate + loyalty_retention_lift)
        clv_loyalty = avg_spend * (new_retention / (1 + discount_rate - new_retention))

        return {
            "clv_without_loyalty": round(clv_base, 2),
            "clv_with_loyalty": round(clv_loyalty, 2),
            "clv_lift": round(clv_loyalty - clv_base, 2),
            "clv_lift_pct": round(((clv_loyalty - clv_base) / clv_base) * 100, 2) if clv_base else 0.0,
        }

    def estimate_churn_reduction(self, params: dict) -> dict:
        """Estimate churn reduction from loyalty program (Pro+ only)."""
        if self.tier == "free":
            raise PermissionError("Churn impact analysis requires Pro tier or higher.")
        base_churn = params.get("base_churn_rate", 0.25)
        loyalty_churn_reduction = params.get("loyalty_churn_reduction", 0.05)
        customer_count = params.get("customer_count", 1000)
        avg_spend = params.get("avg_annual_spend", 500.0)

        new_churn = max(0, base_churn - loyalty_churn_reduction)
        customers_retained = int(customer_count * loyalty_churn_reduction)
        revenue_saved = customers_retained * avg_spend

        return {
            "base_churn_rate": base_churn,
            "new_churn_rate": new_churn,
            "customers_retained": customers_retained,
            "revenue_saved": round(revenue_saved, 2),
        }
