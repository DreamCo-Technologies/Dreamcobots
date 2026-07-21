"""Tests for bots/real_estate_bot/tiers.py and bots/real_estate_bot/real_estate_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.real_estate_bot.real_estate_bot import RealEstateBot, RealEstateBotTierError


class TestRealEstateBotInstantiation:
    def test_default_tier_is_free(self):
        bot = RealEstateBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = RealEstateBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = RealEstateBot()
        assert bot.config is not None


class TestSearchDeals:
    def test_returns_list(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.search_deals("austin", 500000)
        assert isinstance(result, list)

    def test_results_under_budget(self):
        bot = RealEstateBot(tier=Tier.FREE)
        budget = 350000
        results = bot.search_deals("austin", budget)
        for prop in results:
            assert prop["price"] <= budget

    def test_free_location_limit_enforced(self):
        bot = RealEstateBot(tier=Tier.FREE)
        bot.search_deals("austin", 500000)
        with pytest.raises(RealEstateBotTierError):
            bot.search_deals("phoenix", 500000)

    def test_pro_allows_10_locations(self):
        bot = RealEstateBot(tier=Tier.PRO)
        locations = ["austin", "phoenix", "nashville", "denver", "tampa",
                     "charlotte", "atlanta", "dallas", "houston", "las_vegas"]
        for loc in locations:
            result = bot.search_deals(loc, 500000)
            assert isinstance(result, list)

    def test_enterprise_unlimited_locations(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        locations = ["austin", "phoenix", "nashville", "denver", "tampa",
                     "charlotte", "atlanta", "dallas", "houston", "las_vegas"]
        for loc in locations:
            result = bot.search_deals(loc, 500000)
            assert isinstance(result, list)


class TestEvaluateProperty:
    def test_returns_dict(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.evaluate_property("1204 Oak Blvd, Austin TX")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.evaluate_property("1204 Oak Blvd, Austin TX")
        for key in ("price", "cap_rate_pct", "monthly_cashflow_usd", "roi_estimate_pct"):
            assert key in result

    def test_enterprise_has_ai_valuation(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.evaluate_property("1204 Oak Blvd, Austin TX")
        assert "ai_valuation" in result


class TestEstimateROI:
    def test_returns_float(self):
        bot = RealEstateBot(tier=Tier.FREE)
        prop = {"price": 300000, "monthly_rent": 2200}
        result = bot.estimate_roi(prop)
        assert isinstance(result, float)

    def test_positive_roi_for_good_property(self):
        bot = RealEstateBot(tier=Tier.FREE)
        prop = {"price": 200000, "monthly_rent": 2000}
        result = bot.estimate_roi(prop)
        assert result > 0


class TestGetMarketTrends:
    def test_pro_returns_dict(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.get_market_trends("austin")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.get_market_trends("austin")
        for key in ("avg_price_change_pct_yoy", "inventory_months_supply", "avg_days_on_market"):
            assert key in result

    def test_free_tier_raises(self):
        bot = RealEstateBot(tier=Tier.FREE)
        with pytest.raises(RealEstateBotTierError):
            bot.get_market_trends("austin")

    def test_enterprise_has_predictive_analytics(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.get_market_trends("austin")
        assert "predictive_analytics" in result


# ------------------------------------------------------------------ #
# Housing + Gov Contract Bot Tests                                     #
# ------------------------------------------------------------------ #

class TestFindDistressedProperties:
    def test_free_returns_list(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.find_distressed_properties()
        assert isinstance(result, list)

    def test_free_limited_to_three_results(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.find_distressed_properties()
        assert len(result) <= 3

    def test_returns_equity_fields(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.find_distressed_properties()
        for prop in result:
            assert "equity_spread" in prop
            assert "equity_pct" in prop

    def test_pro_filter_by_state(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.find_distressed_properties(state="MI")
        for prop in result:
            assert prop["state"] == "MI"

    def test_pro_filter_by_max_price(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.find_distressed_properties(max_price=20000)
        for prop in result:
            assert prop["price"] <= 20000

    def test_pro_filter_by_type(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.find_distressed_properties(property_type="foreclosure")
        for prop in result:
            assert prop["type"] == "foreclosure"

    def test_enterprise_returns_more_than_free(self):
        free_bot = RealEstateBot(tier=Tier.FREE)
        ent_bot = RealEstateBot(tier=Tier.ENTERPRISE)
        assert len(ent_bot.find_distressed_properties()) > len(free_bot.find_distressed_properties())


class TestFindGovHousingPrograms:
    def test_free_tier_raises(self):
        bot = RealEstateBot(tier=Tier.FREE)
        with pytest.raises(RealEstateBotTierError):
            bot.find_gov_housing_programs()

    def test_pro_returns_list(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.find_gov_housing_programs()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_pro_limited_to_five(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.find_gov_housing_programs()
        assert len(result) <= 5

    def test_enterprise_no_result_cap(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.find_gov_housing_programs()
        assert len(result) > 5

    def test_filter_by_state(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.find_gov_housing_programs(state="WI")
        for prog in result:
            assert "all" in prog["states"] or "WI" in prog["states"]

    def test_filter_by_category(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.find_gov_housing_programs(category="emergency_housing")
        for prog in result:
            assert prog["category"] == "emergency_housing"

    def test_filter_by_portal(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.find_gov_housing_programs(portal="sam.gov")
        for prog in result:
            assert prog["portal"].lower() == "sam.gov"

    def test_result_has_required_keys(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.find_gov_housing_programs()
        for prog in result:
            for key in ("id", "name", "agency", "portal", "payment_per_person_monthly"):
                assert key in prog


class TestCalculateHousingRevenue:
    FLOATING_POINT_TOLERANCE = 0.01
    def test_free_tier_returns_dict(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.calculate_housing_revenue(beds=3)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.calculate_housing_revenue(beds=3)
        for key in ("monthly_gross_usd", "monthly_net_usd", "annual_net_usd", "tenants"):
            assert key in result

    def test_five_bed_revenue(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.calculate_housing_revenue(beds=5)
        assert result["tenants"] == 5
        assert result["monthly_gross_usd"] == 5 * 750

    def test_pro_uses_program_rate(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.calculate_housing_revenue(beds=3, program_id="GHP003")
        assert result["rate_per_person_usd"] == 1100

    def test_net_less_than_gross(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.calculate_housing_revenue(beds=4)
        assert result["monthly_net_usd"] < result["monthly_gross_usd"]

    def test_annual_is_twelve_times_monthly(self):
        bot = RealEstateBot(tier=Tier.FREE)
        result = bot.calculate_housing_revenue(beds=2)
        assert abs(result["annual_net_usd"] - result["monthly_net_usd"] * 12) < self.FLOATING_POINT_TOLERANCE


class TestMatchPropertyToProgram:
    def test_free_tier_raises(self):
        bot = RealEstateBot(tier=Tier.FREE)
        with pytest.raises(RealEstateBotTierError):
            bot.match_property_to_program("DP001")

    def test_pro_returns_dict(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.match_property_to_program("DP001")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.match_property_to_program("DP001")
        for key in ("address", "matched_program", "monthly_net_usd", "payback_months"):
            assert key in result

    def test_payback_months_positive(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.match_property_to_program("DP001")
        assert result["payback_months"] > 0

    def test_enterprise_includes_all_programs(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.match_property_to_program("DP001")
        assert "all_matching_programs" in result
        assert isinstance(result["all_matching_programs"], list)

    def test_enterprise_has_strategy(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.match_property_to_program("DP001")
        assert "strategy_recommendation" in result

    def test_invalid_property_raises(self):
        bot = RealEstateBot(tier=Tier.PRO)
        with pytest.raises(ValueError):
            bot.match_property_to_program("INVALID_ID")


class TestSendOutreach:
    def test_free_tier_raises(self):
        bot = RealEstateBot(tier=Tier.FREE)
        with pytest.raises(RealEstateBotTierError):
            bot.send_outreach("property_owner", "123 Main St")

    def test_pro_returns_message(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.send_outreach("property_owner", "123 Main St")
        assert isinstance(result, dict)
        assert "message" in result
        assert "123 Main St" in result["message"]

    def test_pro_not_auto_sent(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.send_outreach("property_owner", "123 Main St")
        assert result["sent"] is False

    def test_enterprise_auto_sent(self):
        bot = RealEstateBot(tier=Tier.ENTERPRISE)
        result = bot.send_outreach("property_owner", "123 Main St")
        assert result["sent"] is True

    def test_housing_department_contact_type(self):
        bot = RealEstateBot(tier=Tier.PRO)
        result = bot.send_outreach(
            "housing_department",
            "456 Oak Ave",
            program_name="HUD Emergency Voucher",
            unit_count=3,
            beds=4,
        )
        assert "HUD Emergency Voucher" in result["message"]

    def test_invalid_contact_type_raises(self):
        bot = RealEstateBot(tier=Tier.PRO)
        with pytest.raises(ValueError):
            bot.send_outreach("unknown_type", "789 Elm St")
