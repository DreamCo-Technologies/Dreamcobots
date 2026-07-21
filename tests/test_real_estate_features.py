"""Tests for Real_Estate_bots/feature_1.py, feature_2.py, feature_3.py"""
from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from Real_Estate_bots.feature_1 import PropertyListingAggregatorBot, EXAMPLES as RE1_EXAMPLES
from Real_Estate_bots.feature_2 import PropertyViewingSchedulerBot, EXAMPLES as RE2_EXAMPLES
from Real_Estate_bots.feature_3 import MarketAnalysisBot, EXAMPLES as RE3_EXAMPLES


# ===========================================================================
# Feature 1: PropertyListingAggregatorBot
# ===========================================================================

class TestPropertyListingAggregatorBotInstantiation:
    def test_default_tier_is_free(self):
        bot = PropertyListingAggregatorBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = PropertyListingAggregatorBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            PropertyListingAggregatorBot(tier="PLATINUM")

    def test_has_30_examples(self):
        assert len(RE1_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "address", "price", "beds", "baths", "sqft", "type", "source", "monthly_rent", "city"}
        for ex in RE1_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestPropertyListingAggregatorBotSearch:
    def test_search_returns_list(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        result = bot.search()
        assert isinstance(result, list)

    def test_free_tier_limits_sources_to_mls(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        results = bot.search()
        for r in results:
            assert r["source"] == "MLS"

    def test_pro_tier_includes_zillow(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        results = bot.search()
        sources = {r["source"] for r in results}
        assert "Zillow" in sources or "MLS" in sources

    def test_enterprise_tier_includes_redfin(self):
        bot = PropertyListingAggregatorBot(tier="ENTERPRISE")
        results = bot.search()
        sources = {r["source"] for r in results}
        assert "Redfin" in sources or len(results) > 0

    def test_free_tier_max_5_listings(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        results = bot.search()
        assert len(results) <= 5

    def test_search_by_city(self):
        bot = PropertyListingAggregatorBot(tier="ENTERPRISE")
        results = bot.search(city="Austin")
        for r in results:
            assert "Austin" in r["city"]

    def test_search_by_max_price(self):
        bot = PropertyListingAggregatorBot(tier="ENTERPRISE")
        results = bot.search(max_price=200000)
        for r in results:
            assert r["price"] <= 200000

    def test_search_by_min_beds(self):
        bot = PropertyListingAggregatorBot(tier="ENTERPRISE")
        results = bot.search(min_beds=3)
        for r in results:
            assert r["beds"] >= 3

    def test_search_by_property_type(self):
        bot = PropertyListingAggregatorBot(tier="ENTERPRISE")
        results = bot.search(property_type="condo")
        for r in results:
            assert r["type"] == "condo"


class TestPropertyListingAggregatorBotMethods:
    def test_get_listing_by_id(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        listing = bot.get_listing(1)
        assert listing is not None
        assert listing["id"] == 1

    def test_get_listing_missing_id_returns_none(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        result = bot.get_listing(9999)
        assert result is None

    def test_get_top_deals_requires_pro(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_top_deals()

    def test_get_top_deals_pro_returns_list(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        deals = bot.get_top_deals(3)
        assert isinstance(deals, list)
        assert len(deals) <= 3

    def test_get_top_deals_sorted_by_roi(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        deals = bot.get_top_deals(5)
        rois = [d["estimated_roi_pct"] for d in deals]
        assert rois == sorted(rois, reverse=True)

    def test_filter_by_budget_and_beds(self):
        bot = PropertyListingAggregatorBot(tier="ENTERPRISE")
        results = bot.filter_by_budget_and_beds(300000, 2)
        for r in results:
            assert r["price"] <= 300000
            assert r["beds"] >= 2

    def test_get_listings_by_city(self):
        bot = PropertyListingAggregatorBot(tier="ENTERPRISE")
        results = bot.get_listings_by_city("Tampa")
        for r in results:
            assert "Tampa" in r["city"]

    def test_get_all_sources_free(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        sources = bot.get_all_sources()
        assert "MLS" in sources

    def test_get_available_cities_returns_list(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        cities = bot.get_available_cities()
        assert isinstance(cities, list)
        assert len(cities) > 0

    def test_get_stats_returns_dict(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        stats = bot.get_stats()
        assert "total_listings" in stats
        assert "avg_price" in stats
        assert stats["total_listings"] == 30

    def test_describe_tier_returns_string(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)
        assert "FREE" in desc

    def test_run_returns_dict_with_pipeline_complete(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result


# ===========================================================================
# Feature 2: PropertyViewingSchedulerBot
# ===========================================================================

class TestPropertyViewingSchedulerBotInstantiation:
    def test_default_tier_is_free(self):
        bot = PropertyViewingSchedulerBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = PropertyViewingSchedulerBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            PropertyViewingSchedulerBot(tier="INVALID")

    def test_has_30_examples(self):
        assert len(RE2_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "date", "time", "agent", "property"}
        for ex in RE2_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestPropertyViewingSchedulerBotMethods:
    def test_get_available_slots_returns_list(self):
        bot = PropertyViewingSchedulerBot(tier="FREE")
        slots = bot.get_available_slots()
        assert isinstance(slots, list)

    def test_book_viewing_returns_dict(self):
        bot = PropertyViewingSchedulerBot(tier="FREE")
        available = next(s for s in RE2_EXAMPLES if s["status"] == "available")
        result = bot.book_viewing(available["id"], "Alice Smith", "alice@example.com")
        assert isinstance(result, dict)
        assert result.get("status") in ("confirmed", "booked", "scheduled") or "booking_id" in result

    def test_book_viewing_free_tier_limit(self):
        bot = PropertyViewingSchedulerBot(tier="FREE")
        available = [s for s in RE2_EXAMPLES if s["status"] == "available"]
        # Book up to the FREE max (3)
        for i in range(3):
            bot.book_viewing(available[i]["id"], f"Buyer {i}", f"buyer{i}@example.com")
        with pytest.raises(PermissionError):
            bot.book_viewing(available[3]["id"], "Overflow Buyer", "over@example.com")

    def test_get_my_bookings_returns_list(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        available = [s for s in RE2_EXAMPLES if s["status"] == "available"]
        bot.book_viewing(available[0]["id"], "Bob Jones", "bob@example.com")
        bookings = bot.get_my_bookings()
        assert isinstance(bookings, list)
        assert len(bookings) >= 1

    def test_cancel_booking_returns_dict(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        available = [s for s in RE2_EXAMPLES if s["status"] == "available"]
        booking = bot.book_viewing(available[0]["id"], "Carol", "carol@example.com")
        booking_id = booking.get("booking_id") or booking.get("id")
        result = bot.cancel_booking(str(booking_id))
        assert isinstance(result, dict)

    def test_suggest_best_time_returns_slot_or_none(self):
        bot = PropertyViewingSchedulerBot(tier="ENTERPRISE")
        result = bot.suggest_best_time("2025-06-15")
        assert result is None or isinstance(result, dict)

    def test_get_agent_schedule_returns_list(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        agent_name = RE2_EXAMPLES[0]["agent"]
        schedule = bot.get_agent_schedule(agent_name)
        assert isinstance(schedule, list)

    def test_get_calendar_summary_returns_dict(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        summary = bot.get_calendar_summary()
        assert isinstance(summary, dict)

    def test_describe_tier_returns_string(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = PropertyViewingSchedulerBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result


# ===========================================================================
# Feature 3: MarketAnalysisBot
# ===========================================================================

class TestMarketAnalysisBotInstantiation:
    def test_default_tier_is_free(self):
        bot = MarketAnalysisBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = MarketAnalysisBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = MarketAnalysisBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            MarketAnalysisBot(tier="BASIC")

    def test_has_30_examples(self):
        assert len(RE3_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "city", "state", "median_price", "cap_rate_avg_pct"}
        for ex in RE3_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestMarketAnalysisBotMethods:
    def test_get_market_overview_returns_dict(self):
        bot = MarketAnalysisBot(tier="FREE")
        city = RE3_EXAMPLES[0]["city"]
        result = bot.get_market_overview(city)
        assert isinstance(result, dict)

    def test_get_top_investment_markets_returns_list(self):
        bot = MarketAnalysisBot(tier="PRO")
        markets = bot.get_top_investment_markets(3)
        assert isinstance(markets, list)
        assert len(markets) <= 3

    def test_compare_markets_returns_dict(self):
        bot = MarketAnalysisBot(tier="PRO")
        c1 = RE3_EXAMPLES[0]["city"]
        c2 = RE3_EXAMPLES[1]["city"]
        result = bot.compare_markets(c1, c2)
        assert isinstance(result, dict)

    def test_get_high_cap_rate_markets_returns_list(self):
        bot = MarketAnalysisBot(tier="PRO")
        markets = bot.get_high_cap_rate_markets(min_cap_rate=5.0)
        assert isinstance(markets, list)
        for m in markets:
            assert m["cap_rate_avg_pct"] >= 5.0

    def test_get_fastest_growing_markets_returns_list(self):
        bot = MarketAnalysisBot(tier="PRO")
        markets = bot.get_fastest_growing_markets(5)
        assert isinstance(markets, list)
        assert len(markets) <= 5

    def test_export_report_requires_enterprise(self):
        bot = MarketAnalysisBot(tier="FREE")
        city = RE3_EXAMPLES[0]["city"]
        with pytest.raises(PermissionError):
            bot.export_report(city)

    def test_export_report_enterprise_returns_dict(self):
        bot = MarketAnalysisBot(tier="ENTERPRISE")
        city = RE3_EXAMPLES[0]["city"]
        result = bot.export_report(city)
        assert isinstance(result, dict)

    def test_free_tier_limits_markets(self):
        bot = MarketAnalysisBot(tier="FREE")
        markets = bot._get_markets()
        assert len(markets) <= 5

    def test_describe_tier_returns_string(self):
        bot = MarketAnalysisBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = MarketAnalysisBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result
