"""Tests for bots/rental_cashflow_bot/tiers.py and bots/rental_cashflow_bot/rental_cashflow_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.rental_cashflow_bot.rental_cashflow_bot import RentalCashflowBot, RentalCashflowBotTierError
from bots.rental_cashflow_bot.tiers import BOT_FEATURES, get_bot_tier_info


class TestRentalCashflowBotInstantiation:
    def test_default_tier_is_free(self):
        bot = RentalCashflowBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = RentalCashflowBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = RentalCashflowBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = RentalCashflowBot()
        assert bot.config is not None

    def test_flow_initialized(self):
        bot = RentalCashflowBot()
        assert bot.flow is not None


class TestTiersModule:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_get_bot_tier_info_returns_dict(self):
        info = get_bot_tier_info(Tier.FREE)
        assert isinstance(info, dict)

    def test_get_bot_tier_info_has_required_keys(self):
        info = get_bot_tier_info(Tier.PRO)
        for key in ("tier", "name", "price_usd_monthly", "features", "support_level"):
            assert key in info

    def test_enterprise_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > len(BOT_FEATURES[Tier.FREE.value])


class TestAnalyzeProperty:
    def test_returns_dict(self):
        bot = RentalCashflowBot(tier=Tier.FREE)
        result = bot.analyze_property("RNT001")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = RentalCashflowBot(tier=Tier.FREE)
        result = bot.analyze_property("RNT001")
        for key in ("monthly_cashflow_usd", "cap_rate_pct", "gross_rent_multiplier",
                    "cash_on_cash_return_pct", "annual_noi_usd"):
            assert key in result

    def test_free_tier_portfolio_limit(self):
        bot = RentalCashflowBot(tier=Tier.FREE)
        bot.analyze_property("RNT001")
        with pytest.raises(RentalCashflowBotTierError):
            bot.analyze_property("RNT002")

    def test_pro_allows_10_properties(self):
        bot = RentalCashflowBot(tier=Tier.PRO)
        for pid in [f"RNT{i:03d}" for i in range(1, 11)]:
            result = bot.analyze_property(pid)
            assert isinstance(result, dict)

    def test_pro_includes_expense_breakdown(self):
        bot = RentalCashflowBot(tier=Tier.PRO)
        result = bot.analyze_property("RNT001")
        assert "expense_breakdown" in result
        assert isinstance(result["expense_breakdown"], dict)

    def test_pro_includes_investment_grade(self):
        bot = RentalCashflowBot(tier=Tier.PRO)
        result = bot.analyze_property("RNT001")
        assert "investment_grade" in result
        assert result["investment_grade"] in ("A", "B+", "B", "C+", "C")

    def test_enterprise_includes_10yr_projection(self):
        bot = RentalCashflowBot(tier=Tier.ENTERPRISE)
        result = bot.analyze_property("RNT001")
        assert "10_year_projection" in result

    def test_enterprise_includes_depreciation(self):
        bot = RentalCashflowBot(tier=Tier.ENTERPRISE)
        result = bot.analyze_property("RNT001")
        assert "depreciation_annual_usd" in result

    def test_mortgage_payment_positive(self):
        bot = RentalCashflowBot(tier=Tier.FREE)
        result = bot.analyze_property("RNT001")
        assert result["monthly_mortgage_usd"] > 0

    def test_cap_rate_positive_for_viable_property(self):
        bot = RentalCashflowBot(tier=Tier.FREE)
        result = bot.analyze_property("RNT001")
        assert result["cap_rate_pct"] > 0

    def test_address_lookup(self):
        bot = RentalCashflowBot(tier=Tier.FREE)
        result = bot.analyze_property("Austin")
        assert isinstance(result, dict)
        assert "monthly_cashflow_usd" in result


class TestGetPortfolioSummary:
    def test_free_tier_raises(self):
        bot = RentalCashflowBot(tier=Tier.FREE)
        with pytest.raises(RentalCashflowBotTierError):
            bot.get_portfolio_summary()

    def test_pro_returns_dict(self):
        bot = RentalCashflowBot(tier=Tier.PRO)
        result = bot.get_portfolio_summary()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = RentalCashflowBot(tier=Tier.PRO)
        result = bot.get_portfolio_summary()
        for key in ("portfolio_size", "total_monthly_cashflow_usd", "average_cap_rate_pct",
                    "average_cash_on_cash_pct"):
            assert key in result

    def test_enterprise_summary(self):
        bot = RentalCashflowBot(tier=Tier.ENTERPRISE)
        result = bot.get_portfolio_summary()
        assert isinstance(result, dict)
        assert result["portfolio_size"] > 0


class TestAddProperty:
    def test_add_custom_property(self):
        bot = RentalCashflowBot(tier=Tier.PRO)
        custom = {
            "address": "999 Test St, Testville",
            "purchase_price": 250000,
            "down_payment_pct": 0.20,
            "mortgage_rate_pct": 7.0,
            "mortgage_term_years": 30,
            "beds": 3, "baths": 2, "sqft": 1500,
            "type": "single_family",
            "monthly_rent": 2000,
            "year_built": 2000,
            "market": "austin",
            "property_tax_annual": 4000,
            "insurance_annual": 1200,
            "hoa_monthly": 0,
        }
        pid = bot.add_property(custom)
        assert pid.startswith("CUSTOM")

    def test_free_tier_add_limit(self):
        bot = RentalCashflowBot(tier=Tier.FREE)
        custom = {"purchase_price": 200000, "monthly_rent": 1800, "down_payment_pct": 0.20,
                  "mortgage_rate_pct": 7.0, "mortgage_term_years": 30,
                  "property_tax_annual": 3000, "insurance_annual": 1000, "hoa_monthly": 0}
        bot.add_property(custom)
        with pytest.raises(RentalCashflowBotTierError):
            bot.add_property(custom)


class TestProjectReturns:
    def test_free_tier_raises(self):
        bot = RentalCashflowBot(tier=Tier.FREE)
        with pytest.raises(RentalCashflowBotTierError):
            bot.project_returns("RNT001")

    def test_pro_returns_projection(self):
        bot = RentalCashflowBot(tier=Tier.PRO)
        result = bot.project_returns("RNT001", years=10)
        assert isinstance(result, dict)
        assert "yearly_breakdown" in result
        assert len(result["yearly_breakdown"]) == 10

    def test_property_value_increases_over_time(self):
        bot = RentalCashflowBot(tier=Tier.ENTERPRISE)
        result = bot.project_returns("RNT001", years=5)
        values = [y["property_value_usd"] for y in result["yearly_breakdown"]]
        assert values[-1] > values[0]

    def test_irr_estimate_present(self):
        bot = RentalCashflowBot(tier=Tier.PRO)
        result = bot.project_returns("RNT001", years=10)
        assert "estimated_irr_pct" in result


class TestDescribeTier:
    def test_returns_string(self):
        bot = RentalCashflowBot(tier=Tier.FREE)
        result = bot.describe_tier()
        assert isinstance(result, str)

    def test_contains_tier_name(self):
        bot = RentalCashflowBot(tier=Tier.ENTERPRISE)
        result = bot.describe_tier()
        assert "Enterprise" in result


class TestRunPipeline:
    def test_run_returns_dict(self):
        bot = RentalCashflowBot(tier=Tier.FREE)
        result = bot.run()
        assert isinstance(result, dict)

    def test_run_pro_tier(self):
        bot = RentalCashflowBot(tier=Tier.PRO)
        result = bot.run()
        assert isinstance(result, dict)
