import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)

TOOL_DIR = os.path.join(REPO_ROOT, 'analytics-elites', 'loyalty_program_impact_simulator')
sys.path.insert(0, TOOL_DIR)

import pytest
from loyalty_program_impact_simulator import LoyaltyProgramImpactSimulator

BASE_PARAMS = {
    "customer_count": 1000,
    "avg_annual_spend": 500.0,
    "enrollment_rate": 0.30,
    "spend_lift_pct": 0.10,
    "program_cost_per_member": 20.0,
}


class TestLoyaltySimulatorInstantiation:
    def test_default_tier_is_free(self):
        sim = LoyaltyProgramImpactSimulator()
        assert sim.tier == "free"

    def test_pro_tier(self):
        sim = LoyaltyProgramImpactSimulator(tier="pro")
        assert sim.tier == "pro"


class TestSimulateROI:
    def test_returns_dict(self):
        sim = LoyaltyProgramImpactSimulator()
        result = sim.simulate_roi(BASE_PARAMS)
        assert isinstance(result, dict)

    def test_enrolled_members_correct(self):
        sim = LoyaltyProgramImpactSimulator()
        result = sim.simulate_roi(BASE_PARAMS)
        assert result["enrolled_members"] == 300

    def test_positive_net_benefit(self):
        sim = LoyaltyProgramImpactSimulator()
        result = sim.simulate_roi(BASE_PARAMS)
        assert result["net_benefit"] > 0

    def test_roi_pct_positive(self):
        sim = LoyaltyProgramImpactSimulator()
        result = sim.simulate_roi(BASE_PARAMS)
        assert result["roi_pct"] > 0

    def test_free_tier_scenario_limit(self):
        sim = LoyaltyProgramImpactSimulator(tier="free")
        for _ in range(3):
            sim.simulate_roi(BASE_PARAMS)
        with pytest.raises(PermissionError):
            sim.simulate_roi(BASE_PARAMS)

    def test_pro_has_no_limit(self):
        sim = LoyaltyProgramImpactSimulator(tier="pro")
        for _ in range(10):
            result = sim.simulate_roi(BASE_PARAMS)
        assert isinstance(result, dict)


class TestModelCLV:
    def test_free_tier_raises_permission(self):
        sim = LoyaltyProgramImpactSimulator(tier="free")
        with pytest.raises(PermissionError):
            sim.model_clv(BASE_PARAMS)

    def test_clv_with_loyalty_higher(self):
        sim = LoyaltyProgramImpactSimulator(tier="pro")
        result = sim.model_clv({
            "avg_annual_spend": 500,
            "retention_rate": 0.70,
            "discount_rate": 0.10,
            "loyalty_retention_lift": 0.05,
        })
        assert result["clv_with_loyalty"] > result["clv_without_loyalty"]

    def test_clv_lift_positive(self):
        sim = LoyaltyProgramImpactSimulator(tier="pro")
        result = sim.model_clv({
            "avg_annual_spend": 500,
            "retention_rate": 0.70,
            "discount_rate": 0.10,
            "loyalty_retention_lift": 0.05,
        })
        assert result["clv_lift"] > 0


class TestEstimateChurnReduction:
    def test_free_tier_raises_permission(self):
        sim = LoyaltyProgramImpactSimulator(tier="free")
        with pytest.raises(PermissionError):
            sim.estimate_churn_reduction(BASE_PARAMS)

    def test_customers_retained_positive(self):
        sim = LoyaltyProgramImpactSimulator(tier="pro")
        result = sim.estimate_churn_reduction({
            "base_churn_rate": 0.25,
            "loyalty_churn_reduction": 0.05,
            "customer_count": 1000,
            "avg_annual_spend": 500.0,
        })
        assert result["customers_retained"] == 50

    def test_new_churn_lower(self):
        sim = LoyaltyProgramImpactSimulator(tier="pro")
        result = sim.estimate_churn_reduction({
            "base_churn_rate": 0.25,
            "loyalty_churn_reduction": 0.05,
            "customer_count": 1000,
            "avg_annual_spend": 500.0,
        })
        assert result["new_churn_rate"] < result["base_churn_rate"]
