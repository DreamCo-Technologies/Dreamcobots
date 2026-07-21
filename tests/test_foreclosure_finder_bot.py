"""Tests for bots/foreclosure_finder_bot/tiers.py and bots/foreclosure_finder_bot/foreclosure_finder_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.foreclosure_finder_bot.foreclosure_finder_bot import ForeclosureFinderBot, ForeclosureFinderBotTierError
from bots.foreclosure_finder_bot.tiers import BOT_FEATURES, get_bot_tier_info


class TestForeclosureFinderBotInstantiation:
    def test_default_tier_is_free(self):
        bot = ForeclosureFinderBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = ForeclosureFinderBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = ForeclosureFinderBot()
        assert bot.config is not None

    def test_flow_initialized(self):
        bot = ForeclosureFinderBot()
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


class TestSearchForeclosures:
    def test_returns_list(self):
        bot = ForeclosureFinderBot(tier=Tier.FREE)
        result = bot.search_foreclosures("cook")
        assert isinstance(result, list)

    def test_free_tier_max_5_results(self):
        bot = ForeclosureFinderBot(tier=Tier.FREE)
        # Use a county with many entries or fallback
        result = bot.search_foreclosures("cook")
        assert len(result) <= 5

    def test_free_tier_county_limit(self):
        bot = ForeclosureFinderBot(tier=Tier.FREE)
        bot.search_foreclosures("cook")
        with pytest.raises(ForeclosureFinderBotTierError):
            bot.search_foreclosures("maricopa")

    def test_pro_allows_5_counties(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        counties = ["cook", "maricopa", "harris", "wayne", "hillsborough"]
        for county in counties:
            result = bot.search_foreclosures(county)
            assert isinstance(result, list)

    def test_pro_max_25_results(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        result = bot.search_foreclosures("cook")
        assert len(result) <= 25

    def test_enterprise_unlimited_counties(self):
        bot = ForeclosureFinderBot(tier=Tier.ENTERPRISE)
        counties = ["cook", "maricopa", "harris", "wayne", "hillsborough",
                    "mecklenburg", "cuyahoga", "clark"]
        for county in counties:
            result = bot.search_foreclosures(county)
            assert isinstance(result, list)

    def test_results_include_discount_pct(self):
        bot = ForeclosureFinderBot(tier=Tier.FREE)
        results = bot.search_foreclosures("cook")
        for r in results:
            assert "discount_pct" in r
            assert r["discount_pct"] >= 0

    def test_max_price_filter(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        max_price = 100000
        results = bot.search_foreclosures("cook", max_price=max_price)
        for r in results:
            assert r["listing_price_usd"] <= max_price

    def test_pro_results_include_risk_level(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        results = bot.search_foreclosures("cook")
        for r in results:
            assert "risk_level" in r
            assert r["risk_level"] in ("LOW", "MEDIUM", "HIGH", "VERY HIGH")

    def test_free_results_no_lien_info(self):
        bot = ForeclosureFinderBot(tier=Tier.FREE)
        results = bot.search_foreclosures("cook")
        for r in results:
            assert "liens_count" not in r


class TestEvaluateForeclosure:
    def test_returns_dict(self):
        bot = ForeclosureFinderBot(tier=Tier.FREE)
        result = bot.evaluate_foreclosure("FC001")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = ForeclosureFinderBot(tier=Tier.FREE)
        result = bot.evaluate_foreclosure("FC001")
        for key in ("listing_price_usd", "market_value_usd", "discount_from_market_pct",
                    "potential_gross_profit_usd", "risk_level"):
            assert key in result

    def test_discount_calculation_correct(self):
        bot = ForeclosureFinderBot(tier=Tier.FREE)
        result = bot.evaluate_foreclosure("FC001")
        expected = round((1 - 98000 / 148000) * 100, 1)
        assert result["discount_from_market_pct"] == expected

    def test_pro_includes_lien_summary(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        result = bot.evaluate_foreclosure("FC001")
        assert "lien_summary" in result
        assert "liens_count" in result["lien_summary"]

    def test_pro_includes_net_profit_after_liens(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        result = bot.evaluate_foreclosure("FC001")
        assert "net_profit_after_liens_usd" in result

    def test_enterprise_includes_title_risks(self):
        bot = ForeclosureFinderBot(tier=Tier.ENTERPRISE)
        result = bot.evaluate_foreclosure("FC001")
        assert "title_risks" in result

    def test_enterprise_includes_predictive_alert(self):
        bot = ForeclosureFinderBot(tier=Tier.ENTERPRISE)
        result = bot.evaluate_foreclosure("FC001")
        assert "predictive_alert" in result


class TestGetAuctionCalendar:
    def test_free_tier_raises(self):
        bot = ForeclosureFinderBot(tier=Tier.FREE)
        with pytest.raises(ForeclosureFinderBotTierError):
            bot.get_auction_calendar()

    def test_pro_returns_list(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        result = bot.get_auction_calendar()
        assert isinstance(result, list)

    def test_all_results_have_auction_date(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        result = bot.get_auction_calendar()
        for r in result:
            assert "auction_date" in r
            assert r["auction_date"] is not None

    def test_results_sorted_by_date(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        result = bot.get_auction_calendar()
        dates = [r["auction_date"] for r in result]
        assert dates == sorted(dates)

    def test_county_filter(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        result = bot.get_auction_calendar(county="maricopa")
        for r in result:
            assert r["county"] == "maricopa"

    def test_enterprise_includes_risk_level(self):
        bot = ForeclosureFinderBot(tier=Tier.ENTERPRISE)
        result = bot.get_auction_calendar()
        for r in result:
            assert "risk_level" in r


class TestCheckTitleRisks:
    def test_free_tier_raises(self):
        bot = ForeclosureFinderBot(tier=Tier.FREE)
        with pytest.raises(ForeclosureFinderBotTierError):
            bot.check_title_risks("FC001")

    def test_pro_returns_dict(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        result = bot.check_title_risks("FC001")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        result = bot.check_title_risks("FC001")
        for key in ("overall_title_risk", "liens_count", "risk_factors", "estimated_title_clearance_cost_usd"):
            assert key in result

    def test_risk_factors_is_list(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        result = bot.check_title_risks("FC001")
        assert isinstance(result["risk_factors"], list)

    def test_clearance_cost_positive_with_liens(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        result = bot.check_title_risks("FC001")  # FC001 has 2 liens
        assert result["estimated_title_clearance_cost_usd"] > 0


class TestDescribeTier:
    def test_returns_string(self):
        bot = ForeclosureFinderBot(tier=Tier.FREE)
        result = bot.describe_tier()
        assert isinstance(result, str)

    def test_contains_tier_name(self):
        bot = ForeclosureFinderBot(tier=Tier.PRO)
        result = bot.describe_tier()
        assert "Pro" in result


class TestRunPipeline:
    def test_run_returns_dict(self):
        bot = ForeclosureFinderBot(tier=Tier.FREE)
        result = bot.run()
        assert isinstance(result, dict)

    def test_run_enterprise_tier(self):
        bot = ForeclosureFinderBot(tier=Tier.ENTERPRISE)
        result = bot.run()
        assert isinstance(result, dict)
