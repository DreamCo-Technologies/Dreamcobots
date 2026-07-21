"""
Tests for divisions/revenue_simulator.py

Run with:
    python -m pytest tests/test_revenue_simulator.py -v
"""
# GLOBAL AI SOURCES FLOW

import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from divisions.revenue_simulator import RevenueSimulator, BUNDLE_TIERS


# ---------------------------------------------------------------------------
# RevenueSimulator.simulate()
# ---------------------------------------------------------------------------


class TestRevenueSimulatorSimulate:
    def setup_method(self):
        self.sim = RevenueSimulator()

    def test_returns_dict(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10)
        assert isinstance(result, dict)

    def test_has_projections(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10)
        assert "projections" in result

    def test_has_summary(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10)
        assert "summary" in result

    def test_projections_length_default(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10)
        assert len(result["projections"]) == 12

    def test_projections_length_custom(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10, months=24)
        assert len(result["projections"]) == 24

    def test_summary_has_arr(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10)
        assert "arr_usd" in result["summary"]

    def test_summary_has_final_mrr(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10)
        assert "final_mrr_usd" in result["summary"]

    def test_summary_has_total_revenue(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10)
        assert "total_revenue_usd" in result["summary"]

    def test_summary_has_growth_multiplier(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10)
        assert "growth_multiplier" in result["summary"]

    def test_arr_equals_final_mrr_times_12(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10)
        expected_arr = round(result["summary"]["final_mrr_usd"] * 12, 2)
        assert result["summary"]["arr_usd"] == expected_arr

    def test_mrr_grows_with_net_positive_growth(self):
        result = self.sim.simulate(
            starting_mrr=10000, growth_rate=0.20, churn_rate=0.02, months=6
        )
        assert result["projections"][-1]["mrr_usd"] > 10000

    def test_mrr_declines_when_churn_exceeds_growth(self):
        result = self.sim.simulate(
            starting_mrr=10000, growth_rate=0.02, churn_rate=0.15, months=6
        )
        assert result["projections"][-1]["mrr_usd"] < 10000

    def test_zero_growth_zero_churn_stable_mrr(self):
        result = self.sim.simulate(
            starting_mrr=10000, growth_rate=0.0, churn_rate=0.0, months=3
        )
        for p in result["projections"]:
            assert p["mrr_usd"] == pytest.approx(10000.0, rel=1e-3)

    def test_zero_starting_mrr(self):
        result = self.sim.simulate(starting_mrr=0, growth_rate=0.10)
        assert result["summary"]["final_mrr_usd"] == 0.0
        assert result["summary"]["growth_multiplier"] == 0.0

    def test_projection_months_are_sequential(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10, months=5)
        months = [p["month"] for p in result["projections"]]
        assert months == [1, 2, 3, 4, 5]

    def test_invalid_months_raises(self):
        with pytest.raises(ValueError):
            self.sim.simulate(starting_mrr=10000, growth_rate=0.10, months=0)

    def test_invalid_churn_above_one_raises(self):
        with pytest.raises(ValueError):
            self.sim.simulate(starting_mrr=10000, growth_rate=0.10, churn_rate=1.5)

    def test_invalid_churn_exactly_one_raises(self):
        with pytest.raises(ValueError):
            self.sim.simulate(starting_mrr=10000, growth_rate=0.10, churn_rate=1.0)

    def test_negative_starting_mrr_raises(self):
        with pytest.raises(ValueError):
            self.sim.simulate(starting_mrr=-100, growth_rate=0.10)

    def test_division_label_preserved(self):
        result = self.sim.simulate(
            starting_mrr=5000, growth_rate=0.10, division="DreamSalesPro"
        )
        assert result["division"] == "DreamSalesPro"

    def test_tier_label_preserved(self):
        result = self.sim.simulate(
            starting_mrr=5000, growth_rate=0.10, tier="Enterprise"
        )
        assert result["tier"] == "Enterprise"

    def test_has_timestamp(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10)
        assert "timestamp" in result

    def test_simulation_type_label(self):
        result = self.sim.simulate(starting_mrr=10000, growth_rate=0.10)
        assert result["simulation"] == "mrr_arr_growth"


# ---------------------------------------------------------------------------
# RevenueSimulator.break_even()
# ---------------------------------------------------------------------------


class TestRevenueSimulatorBreakEven:
    def setup_method(self):
        self.sim = RevenueSimulator()

    def test_returns_dict(self):
        result = self.sim.break_even(
            fixed_costs_usd=10000,
            variable_cost_pct=0.20,
            price_per_unit_usd=199.0,
        )
        assert isinstance(result, dict)

    def test_has_break_even_units(self):
        result = self.sim.break_even(10000, 0.20, 199.0)
        assert "break_even_units" in result

    def test_has_break_even_revenue(self):
        result = self.sim.break_even(10000, 0.20, 199.0)
        assert "break_even_revenue_usd" in result

    def test_has_contribution_margin(self):
        result = self.sim.break_even(10000, 0.20, 199.0)
        assert "contribution_margin_usd" in result

    def test_has_gross_margin_pct(self):
        result = self.sim.break_even(10000, 0.20, 199.0)
        assert "gross_margin_pct" in result

    def test_break_even_units_positive(self):
        result = self.sim.break_even(10000, 0.20, 199.0)
        assert result["break_even_units"] > 0

    def test_break_even_revenue_positive(self):
        result = self.sim.break_even(10000, 0.20, 199.0)
        assert result["break_even_revenue_usd"] > 0

    def test_gross_margin_correct(self):
        result = self.sim.break_even(10000, 0.25, 200.0)
        assert result["gross_margin_pct"] == pytest.approx(75.0, rel=1e-3)

    def test_contribution_margin_correct(self):
        result = self.sim.break_even(10000, 0.25, 200.0)
        assert result["contribution_margin_usd"] == pytest.approx(150.0, rel=1e-3)

    def test_variable_cost_above_one_raises(self):
        with pytest.raises(ValueError):
            self.sim.break_even(10000, 1.5, 199.0)

    def test_variable_cost_exactly_one_raises(self):
        with pytest.raises(ValueError):
            self.sim.break_even(10000, 1.0, 199.0)

    def test_zero_price_raises(self):
        with pytest.raises(ValueError):
            self.sim.break_even(10000, 0.20, 0.0)

    def test_simulation_type_label(self):
        result = self.sim.break_even(10000, 0.20, 199.0)
        assert result["simulation"] == "break_even"


# ---------------------------------------------------------------------------
# RevenueSimulator.model_bundle_revenue()
# ---------------------------------------------------------------------------


class TestRevenueSimulatorBundleRevenue:
    def setup_method(self):
        self.sim = RevenueSimulator()

    def test_returns_dict(self):
        result = self.sim.model_bundle_revenue(
            bundle_name="Starter+", subscriber_count=100
        )
        assert isinstance(result, dict)

    def test_has_projections(self):
        result = self.sim.model_bundle_revenue("Growth+", 50)
        assert "projections" in result

    def test_has_bundle_key(self):
        result = self.sim.model_bundle_revenue("Starter+", 100)
        assert "bundle" in result

    def test_bundle_name_preserved(self):
        result = self.sim.model_bundle_revenue("Growth+", 50)
        assert result["bundle"]["name"] == "Growth+"

    def test_starting_subscribers_preserved(self):
        result = self.sim.model_bundle_revenue("Empire", 10)
        assert result["bundle"]["starting_subscribers"] == 10

    def test_simulation_type_label(self):
        result = self.sim.model_bundle_revenue("Starter+", 100)
        assert result["simulation"] == "bundle_revenue"

    def test_unknown_bundle_raises(self):
        with pytest.raises(KeyError):
            self.sim.model_bundle_revenue("UnknownBundle", 100)

    def test_all_bundles_available(self):
        for bundle_name in BUNDLE_TIERS:
            result = self.sim.model_bundle_revenue(bundle_name, 10)
            assert "projections" in result

    def test_projections_length(self):
        result = self.sim.model_bundle_revenue("Starter+", 100, months=6)
        assert len(result["projections"]) == 6


# ---------------------------------------------------------------------------
# RevenueSimulator.model_enterprise_revenue()
# ---------------------------------------------------------------------------


class TestRevenueSimulatorEnterpriseRevenue:
    def setup_method(self):
        self.sim = RevenueSimulator()

    def test_returns_dict(self):
        result = self.sim.model_enterprise_revenue(
            division="DreamRealEstate", license_count=10
        )
        assert isinstance(result, dict)

    def test_has_projections(self):
        result = self.sim.model_enterprise_revenue("DreamSalesPro", 5)
        assert "projections" in result

    def test_has_license_info(self):
        result = self.sim.model_enterprise_revenue("DreamRealEstate", 10)
        assert "license_info" in result

    def test_division_in_license_info(self):
        result = self.sim.model_enterprise_revenue("DreamSalesPro", 5)
        assert result["license_info"]["division"] == "DreamSalesPro"

    def test_starting_licenses_preserved(self):
        result = self.sim.model_enterprise_revenue("DreamRealEstate", 7)
        assert result["license_info"]["starting_licenses"] == 7

    def test_simulation_type_label(self):
        result = self.sim.model_enterprise_revenue("DreamRealEstate", 5)
        assert result["simulation"] == "enterprise_license_revenue"

    def test_unknown_division_uses_default_price(self):
        result = self.sim.model_enterprise_revenue("UnknownDivision", 1)
        assert result["license_info"]["price_per_license_usd"] == 499.0

    def test_projections_length(self):
        result = self.sim.model_enterprise_revenue(
            "DreamRealEstate", 5, months=3
        )
        assert len(result["projections"]) == 3

    def test_tier_label_is_enterprise(self):
        result = self.sim.model_enterprise_revenue("DreamRealEstate", 5)
        assert result["tier"] == "Enterprise"


# ---------------------------------------------------------------------------
# BUNDLE_TIERS constant
# ---------------------------------------------------------------------------


class TestBundleTiersConstant:
    def test_starter_plus_exists(self):
        assert "Starter+" in BUNDLE_TIERS

    def test_growth_plus_exists(self):
        assert "Growth+" in BUNDLE_TIERS

    def test_empire_exists(self):
        assert "Empire" in BUNDLE_TIERS

    def test_each_has_price(self):
        for name, info in BUNDLE_TIERS.items():
            assert info["price_usd"] > 0, f"{name} missing price"

    def test_each_has_description(self):
        for name, info in BUNDLE_TIERS.items():
            assert info["description"], f"{name} missing description"

    def test_starter_cheaper_than_growth(self):
        assert BUNDLE_TIERS["Starter+"]["price_usd"] < BUNDLE_TIERS["Growth+"]["price_usd"]

    def test_growth_cheaper_than_empire(self):
        assert BUNDLE_TIERS["Growth+"]["price_usd"] < BUNDLE_TIERS["Empire"]["price_usd"]
