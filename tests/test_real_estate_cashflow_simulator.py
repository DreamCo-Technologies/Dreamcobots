import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)

TOOL_DIR = os.path.join(REPO_ROOT, 'real-estate-tools', 'real_estate_cashflow_simulator')
sys.path.insert(0, TOOL_DIR)

import pytest
from real_estate_cashflow_simulator import RealEstateCashflowSimulator

PROPERTY = {
    "purchase_price": 250000,
    "down_payment_pct": 0.20,
    "interest_rate": 0.065,
    "loan_term_years": 30,
    "monthly_rent": 1800,
    "vacancy_rate": 0.05,
    "monthly_expenses": 450,
    "property_management_pct": 0.08,
}


class TestRealEstateCashflowSimulatorInstantiation:
    def test_default_tier_is_free(self):
        sim = RealEstateCashflowSimulator()
        assert sim.tier == "free"

    def test_pro_tier(self):
        sim = RealEstateCashflowSimulator(tier="pro")
        assert sim.tier == "pro"


class TestSimulateCashflow:
    def test_returns_dict(self):
        sim = RealEstateCashflowSimulator()
        result = sim.simulate_cashflow(PROPERTY)
        assert isinstance(result, dict)

    def test_loan_amount_correct(self):
        sim = RealEstateCashflowSimulator()
        result = sim.simulate_cashflow(PROPERTY)
        assert abs(result["loan_amount"] - 200000) < 1

    def test_cap_rate_positive(self):
        sim = RealEstateCashflowSimulator()
        result = sim.simulate_cashflow(PROPERTY)
        assert result["cap_rate_pct"] > 0

    def test_cash_on_cash_present(self):
        sim = RealEstateCashflowSimulator()
        result = sim.simulate_cashflow(PROPERTY)
        assert "cash_on_cash_return_pct" in result

    def test_monthly_mortgage_positive(self):
        sim = RealEstateCashflowSimulator()
        result = sim.simulate_cashflow(PROPERTY)
        assert result["monthly_mortgage"] > 0

    def test_noi_positive(self):
        sim = RealEstateCashflowSimulator()
        result = sim.simulate_cashflow(PROPERTY)
        assert result["noi"] > 0


class TestGenerateAmortization:
    def test_free_tier_raises_permission(self):
        sim = RealEstateCashflowSimulator(tier="free")
        with pytest.raises(PermissionError):
            sim.generate_amortization(PROPERTY)

    def test_returns_correct_years(self):
        sim = RealEstateCashflowSimulator(tier="pro")
        schedule = sim.generate_amortization(PROPERTY, years=5)
        assert len(schedule) == 5

    def test_balance_decreases(self):
        sim = RealEstateCashflowSimulator(tier="pro")
        schedule = sim.generate_amortization(PROPERTY, years=5)
        balances = [row["remaining_balance"] for row in schedule]
        assert balances[0] > balances[-1]

    def test_year_numbers_sequential(self):
        sim = RealEstateCashflowSimulator(tier="pro")
        schedule = sim.generate_amortization(PROPERTY, years=3)
        assert [row["year"] for row in schedule] == [1, 2, 3]


class TestPortfolioSummary:
    def test_free_tier_raises_permission(self):
        sim = RealEstateCashflowSimulator(tier="free")
        with pytest.raises(PermissionError):
            sim.portfolio_summary([PROPERTY])

    def test_property_count_correct(self):
        sim = RealEstateCashflowSimulator(tier="pro")
        result = sim.portfolio_summary([PROPERTY, PROPERTY])
        assert result["property_count"] == 2

    def test_total_cashflow_sum(self):
        sim = RealEstateCashflowSimulator(tier="pro")
        single = sim.simulate_cashflow(PROPERTY)
        portfolio = sim.portfolio_summary([PROPERTY, PROPERTY])
        assert abs(portfolio["total_annual_cashflow"] - single["annual_cashflow"] * 2) < 1
