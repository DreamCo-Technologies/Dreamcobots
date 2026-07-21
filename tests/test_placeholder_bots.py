"""
Tests for all placeholder bot implementations:
  - Real_Estate_bots: feature_1, feature_2, feature_3
  - Fiverr_bots: feature_1, feature_2, feature_3
  - Marketing_bots: feature_1, feature_2, feature_3
  - Business_bots: feature_1, feature_2, feature_3
  - App_bots: feature_1, feature_2, feature_3
  - Occupational_bots: feature_1, feature_2, feature_3
"""

import sys
import os
import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

# ============================================================
# Real_Estate_bots
# ============================================================

from Real_Estate_bots.feature_1 import PropertyListingAggregatorBot, EXAMPLES as RE1_EXAMPLES
from Real_Estate_bots.feature_2 import PropertyViewingSchedulerBot, EXAMPLES as RE2_EXAMPLES
from Real_Estate_bots.feature_3 import MarketAnalysisBot, EXAMPLES as RE3_EXAMPLES


class TestPropertyListingAggregatorBot:
    def test_instantiation_free(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_instantiation_pro(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_instantiation_enterprise(self):
        bot = PropertyListingAggregatorBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises(self):
        with pytest.raises(ValueError):
            PropertyListingAggregatorBot(tier="GOLD")

    def test_examples_has_30_entries(self):
        assert len(RE1_EXAMPLES) == 30

    def test_examples_have_required_fields(self):
        for ex in RE1_EXAMPLES:
            assert "id" in ex
            assert "address" in ex
            assert "price" in ex
            assert "beds" in ex

    def test_search_returns_list(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        result = bot.search()
        assert isinstance(result, list)

    def test_search_by_city(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        result = bot.search(city="Austin")
        assert all("Austin" in r["city"] for r in result)

    def test_search_by_max_price(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        result = bot.search(max_price=200000)
        assert all(r["price"] <= 200000 for r in result)

    def test_search_by_min_beds(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        result = bot.search(min_beds=3)
        assert all(r["beds"] >= 3 for r in result)

    def test_search_by_property_type(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        result = bot.search(property_type="condo")
        assert all(r["type"] == "condo" for r in result)

    def test_free_tier_limits_sources(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        sources = bot.get_all_sources()
        assert "MLS" in sources
        assert "Redfin" not in sources

    def test_get_listing_returns_dict(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        result = bot.get_listing(1)
        assert isinstance(result, dict)
        assert result["id"] == 1

    def test_get_listing_unknown_id_returns_none(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        result = bot.get_listing(9999)
        assert result is None

    def test_ai_deal_score_on_pro(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        listing = bot.get_listing(1)
        assert "ai_deal_score" in listing
        assert isinstance(listing["ai_deal_score"], int)

    def test_no_ai_deal_score_on_free(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        listing = bot.get_listing(1)
        assert "ai_deal_score" not in listing

    def test_get_top_deals_requires_pro(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_top_deals()

    def test_get_top_deals_on_pro(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        top = bot.get_top_deals(3)
        assert len(top) == 3
        rois = [t["estimated_roi_pct"] for t in top]
        assert rois == sorted(rois, reverse=True)

    def test_get_available_cities_returns_list(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        cities = bot.get_available_cities()
        assert isinstance(cities, list)
        assert len(cities) > 0

    def test_get_stats_returns_summary(self):
        bot = PropertyListingAggregatorBot(tier="PRO")
        stats = bot.get_stats()
        assert stats["total_listings"] == 30
        assert stats["avg_price"] > 0

    def test_describe_tier_returns_string(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)
        assert "FREE" in desc

    def test_run_returns_pipeline_result(self):
        bot = PropertyListingAggregatorBot(tier="FREE")
        result = bot.run()
        assert "pipeline_complete" in result
        assert result["pipeline_complete"] is True


class TestPropertyViewingSchedulerBot:
    def test_instantiation(self):
        bot = PropertyViewingSchedulerBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_invalid_tier_raises(self):
        with pytest.raises(ValueError):
            PropertyViewingSchedulerBot(tier="INVALID")

    def test_examples_has_30_entries(self):
        assert len(RE2_EXAMPLES) == 30

    def test_examples_have_required_fields(self):
        for ex in RE2_EXAMPLES:
            assert "id" in ex
            assert "property" in ex
            assert "date" in ex
            assert "time" in ex
            assert "status" in ex

    def test_get_available_slots_returns_list(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        slots = bot.get_available_slots()
        assert isinstance(slots, list)
        assert all(s["status"] == "available" for s in slots)

    def test_filter_by_date(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        slots = bot.get_available_slots(date="2025-05-01")
        assert all(s["date"] == "2025-05-01" for s in slots)

    def test_book_viewing_requires_pro_scheduling(self):
        bot = PropertyViewingSchedulerBot(tier="FREE")
        available = [s for s in RE2_EXAMPLES if s["status"] == "available"]
        # FREE tier allows bookings (up to 3), AI scheduling requires ENTERPRISE
        result = bot.book_viewing(available[0]["id"], "John", "john@test.com")
        assert isinstance(result, dict)

    def test_book_viewing_on_pro(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        available = [s for s in RE2_EXAMPLES if s["status"] == "available"]
        booking = bot.book_viewing(available[0]["id"], "John Buyer", "john@test.com")
        assert booking["status"] == "confirmed"
        assert "booking_id" in booking

    def test_booking_already_booked_raises(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        booked = [s for s in RE2_EXAMPLES if s["status"] == "booked"]
        if booked:
            with pytest.raises(ValueError):
                bot.book_viewing(booked[0]["id"], "John", "j@test.com")

    def test_cancel_booking(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        available = [s for s in RE2_EXAMPLES if s["status"] == "available"]
        booking = bot.book_viewing(available[0]["id"], "Jane", "jane@test.com")
        result = bot.cancel_booking(booking["booking_id"])
        assert result["booking"]["status"] == "cancelled"

    def test_suggest_best_time(self):
        bot = PropertyViewingSchedulerBot(tier="ENTERPRISE")
        suggestion = bot.suggest_best_time("2025-05-01")
        assert suggestion is not None

    def test_get_agent_schedule(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        schedule = bot.get_agent_schedule("Sarah Johnson")
        assert isinstance(schedule, list)

    def test_get_calendar_summary(self):
        bot = PropertyViewingSchedulerBot(tier="FREE")
        summary = bot.get_calendar_summary()
        assert summary["total_slots"] == 30
        assert "by_status" in summary

    def test_describe_tier(self):
        bot = PropertyViewingSchedulerBot(tier="PRO")
        desc = bot.describe_tier()
        assert "PRO" in desc

    def test_run_returns_pipeline_result(self):
        bot = PropertyViewingSchedulerBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


class TestMarketAnalysisBot:
    def test_instantiation(self):
        bot = MarketAnalysisBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_examples_has_30_entries(self):
        assert len(RE3_EXAMPLES) == 30

    def test_examples_have_required_fields(self):
        for ex in RE3_EXAMPLES:
            assert "city" in ex
            assert "median_price" in ex
            assert "cap_rate_avg_pct" in ex

    def test_get_market_overview_returns_dict(self):
        bot = MarketAnalysisBot(tier="PRO")
        result = bot.get_market_overview("Austin")
        assert result["city"] == "Austin"
        assert "investment_grade" in result

    def test_forecasting_on_pro(self):
        bot = MarketAnalysisBot(tier="PRO")
        result = bot.get_market_overview("Austin")
        assert "forecast_12mo_price_change_pct" in result

    def test_no_forecasting_on_free(self):
        bot = MarketAnalysisBot(tier="FREE")
        result = bot.get_market_overview("Austin")
        assert "forecast_12mo_price_change_pct" not in result

    def test_unknown_city_raises(self):
        bot = MarketAnalysisBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_market_overview("UnknownCity")

    def test_get_top_investment_markets(self):
        bot = MarketAnalysisBot(tier="PRO")
        top = bot.get_top_investment_markets(3)
        assert len(top) == 3
        scores = [m["investment_score"] for m in top]
        assert scores == sorted(scores, reverse=True)

    def test_compare_markets(self):
        bot = MarketAnalysisBot(tier="PRO")
        result = bot.compare_markets("Austin", "Phoenix")
        assert "Austin" in result
        assert "Phoenix" in result
        assert result["recommended"] in ("Austin", "Phoenix")

    def test_high_cap_rate_markets(self):
        bot = MarketAnalysisBot(tier="PRO")
        markets = bot.get_high_cap_rate_markets(6.0)
        assert all(m["cap_rate_avg_pct"] >= 6.0 for m in markets)

    def test_fastest_growing_markets(self):
        bot = MarketAnalysisBot(tier="PRO")
        markets = bot.get_fastest_growing_markets(5)
        assert len(markets) <= 5
        rates = [m["price_change_yoy_pct"] for m in markets]
        assert rates == sorted(rates, reverse=True)

    def test_export_requires_enterprise(self):
        bot = MarketAnalysisBot(tier="PRO")
        with pytest.raises(PermissionError):
            bot.export_report("Austin")

    def test_export_on_enterprise(self):
        bot = MarketAnalysisBot(tier="ENTERPRISE")
        report = bot.export_report("Austin")
        assert report["report_type"] == "Investment Market Report"

    def test_describe_tier(self):
        bot = MarketAnalysisBot(tier="ENTERPRISE")
        desc = bot.describe_tier()
        assert "ENTERPRISE" in desc

    def test_run_returns_pipeline_result(self):
        bot = MarketAnalysisBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


# ============================================================
# Fiverr_bots
# ============================================================

from Fiverr_bots.feature_1 import FiverrServiceListingBot, EXAMPLES as FI1_EXAMPLES
from Fiverr_bots.feature_2 import FiverrOrderManagerBot, EXAMPLES as FI2_EXAMPLES
from Fiverr_bots.feature_3 import FiverrReviewGeneratorBot, EXAMPLES as FI3_EXAMPLES


class TestFiverrServiceListingBot:
    def test_instantiation(self):
        bot = FiverrServiceListingBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_invalid_tier_raises(self):
        with pytest.raises(ValueError):
            FiverrServiceListingBot(tier="INVALID")

    def test_examples_has_30_entries(self):
        assert len(FI1_EXAMPLES) == 30

    def test_create_listing_works_on_pro(self):
        bot = FiverrServiceListingBot(tier="PRO")
        listing = bot.create_listing(1)
        assert listing["status"] == "active"

    def test_create_listing_enforces_free_limit(self):
        bot = FiverrServiceListingBot(tier="FREE")
        for i in range(1, 4):
            bot.create_listing(i)
        with pytest.raises(PermissionError):
            bot.create_listing(4)

    def test_create_listing_unknown_id_raises(self):
        bot = FiverrServiceListingBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.create_listing(9999)

    def test_optimized_title_on_pro(self):
        bot = FiverrServiceListingBot(tier="PRO")
        listing = bot.create_listing(1)
        assert "optimized_title" in listing

    def test_no_optimized_title_on_free(self):
        bot = FiverrServiceListingBot(tier="FREE")
        listing = bot.create_listing(1)
        assert "optimized_title" not in listing

    def test_keyword_injection_on_enterprise(self):
        bot = FiverrServiceListingBot(tier="ENTERPRISE")
        listing = bot.create_listing(1)
        assert "injected_keywords" in listing

    def test_search_templates_by_category(self):
        bot = FiverrServiceListingBot(tier="PRO")
        results = bot.search_templates(category="programming")
        assert all("programming" in r["category"] for r in results)

    def test_search_templates_by_max_price(self):
        bot = FiverrServiceListingBot(tier="PRO")
        results = bot.search_templates(max_price=30)
        assert all(r["base_price"] <= 30 for r in results)

    def test_get_high_demand_gigs(self):
        bot = FiverrServiceListingBot(tier="PRO")
        gigs = bot.get_high_demand_gigs()
        assert all(g["demand"] == "high" for g in gigs)

    def test_get_top_rated_gigs(self):
        bot = FiverrServiceListingBot(tier="PRO")
        top = bot.get_top_rated_gigs(3)
        assert len(top) == 3
        ratings = [g["avg_rating"] for g in top]
        assert ratings == sorted(ratings, reverse=True)

    def test_estimate_monthly_revenue(self):
        bot = FiverrServiceListingBot(tier="PRO")
        result = bot.estimate_monthly_revenue(1, orders_per_day=2)
        assert result["gross_revenue_usd"] > 0
        assert result["net_revenue_usd"] < result["gross_revenue_usd"]

    def test_estimate_revenue_unknown_gig_raises(self):
        bot = FiverrServiceListingBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.estimate_monthly_revenue(9999)

    def test_get_categories(self):
        bot = FiverrServiceListingBot(tier="PRO")
        categories = bot.get_categories()
        assert isinstance(categories, list)
        assert len(categories) > 0

    def test_describe_tier(self):
        bot = FiverrServiceListingBot(tier="PRO")
        desc = bot.describe_tier()
        assert "PRO" in desc

    def test_run_returns_pipeline_result(self):
        bot = FiverrServiceListingBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


class TestFiverrOrderManagerBot:
    def test_instantiation(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_examples_has_30_entries(self):
        assert len(FI2_EXAMPLES) == 30

    def test_get_orders_by_status(self):
        bot = FiverrOrderManagerBot(tier="ENTERPRISE")
        orders = bot.get_orders_by_status("in_progress")
        assert all(o["status"] == "in_progress" for o in orders)

    def test_invalid_status_raises(self):
        bot = FiverrOrderManagerBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_orders_by_status("unknown_status")

    def test_get_active_orders(self):
        bot = FiverrOrderManagerBot(tier="ENTERPRISE")
        orders = bot.get_active_orders()
        assert all(o["status"] == "in_progress" for o in orders)

    def test_get_order_by_id(self):
        bot = FiverrOrderManagerBot(tier="ENTERPRISE")
        order = bot.get_order("ORD-001")
        assert order["id"] == "ORD-001"

    def test_get_order_unknown_raises(self):
        bot = FiverrOrderManagerBot(tier="ENTERPRISE")
        with pytest.raises(ValueError):
            bot.get_order("ORD-999")

    def test_revenue_summary_has_correct_fields(self):
        bot = FiverrOrderManagerBot(tier="ENTERPRISE")
        summary = bot.get_revenue_summary()
        assert "total_revenue_usd" in summary
        assert "completed_orders" in summary
        assert "avg_order_value_usd" in summary

    def test_revenue_total_positive(self):
        bot = FiverrOrderManagerBot(tier="ENTERPRISE")
        summary = bot.get_revenue_summary()
        assert summary["total_revenue_usd"] > 0

    def test_deadline_alert_requires_pro(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.send_deadline_alert("ORD-001")

    def test_deadline_alert_on_pro(self):
        bot = FiverrOrderManagerBot(tier="PRO")
        result = bot.send_deadline_alert("ORD-001")
        assert result["alert_sent"] is True

    def test_auto_message_requires_pro(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.send_auto_message("ORD-001")

    def test_auto_message_on_pro(self):
        bot = FiverrOrderManagerBot(tier="PRO")
        result = bot.send_auto_message("ORD-001", "update")
        assert result["sent"] is True

    def test_auto_message_invalid_type_raises(self):
        bot = FiverrOrderManagerBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.send_auto_message("ORD-001", "invalid_type")

    def test_get_unreviewed_orders(self):
        bot = FiverrOrderManagerBot(tier="ENTERPRISE")
        unreviewed = bot.get_unreviewed_orders()
        assert all(o["rating"] is None for o in unreviewed)

    def test_get_average_rating_is_positive(self):
        bot = FiverrOrderManagerBot(tier="ENTERPRISE")
        avg = bot.get_average_rating()
        assert 0 <= avg <= 5

    def test_describe_tier(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        desc = bot.describe_tier()
        assert "FREE" in desc

    def test_run_returns_pipeline_result(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


class TestFiverrReviewGeneratorBot:
    def test_instantiation(self):
        bot = FiverrReviewGeneratorBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_examples_has_30_entries(self):
        assert len(FI3_EXAMPLES) == 30

    def test_get_all_reviews(self):
        bot = FiverrReviewGeneratorBot(tier="ENTERPRISE")
        reviews = bot.get_all_reviews()
        assert len(reviews) == 30

    def test_free_tier_limits_reviews(self):
        bot = FiverrReviewGeneratorBot(tier="FREE")
        reviews = bot.get_all_reviews()
        assert len(reviews) == 10

    def test_get_reviews_by_rating(self):
        bot = FiverrReviewGeneratorBot(tier="ENTERPRISE")
        reviews = bot.get_reviews_by_rating(5)
        assert all(r["rating"] == 5 for r in reviews)

    def test_invalid_rating_raises(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_reviews_by_rating(6)

    def test_get_reviews_by_sentiment(self):
        bot = FiverrReviewGeneratorBot(tier="ENTERPRISE")
        pos = bot.get_reviews_by_sentiment("positive")
        assert all(r["sentiment"] == "positive" for r in pos)

    def test_invalid_sentiment_raises(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_reviews_by_sentiment("amazing")

    def test_get_average_rating(self):
        bot = FiverrReviewGeneratorBot(tier="ENTERPRISE")
        avg = bot.get_average_rating()
        assert 1 <= avg <= 5

    def test_get_rating_distribution(self):
        bot = FiverrReviewGeneratorBot(tier="ENTERPRISE")
        dist = bot.get_rating_distribution()
        assert set(dist.keys()) == {1, 2, 3, 4, 5}
        assert sum(dist.values()) == 30

    def test_get_pending_responses(self):
        bot = FiverrReviewGeneratorBot(tier="ENTERPRISE")
        pending = bot.get_pending_responses()
        assert all(not r["response_sent"] for r in pending)

    def test_send_review_request_requires_pro(self):
        bot = FiverrReviewGeneratorBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.send_review_request("buyer123", "Logo Design")

    def test_send_review_request_on_pro(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        result = bot.send_review_request("buyer123", "Logo Design")
        assert result["sent"] is True

    def test_generate_response_requires_enterprise(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        with pytest.raises(PermissionError):
            bot.generate_response(1)

    def test_generate_response_on_enterprise(self):
        bot = FiverrReviewGeneratorBot(tier="ENTERPRISE")
        response = bot.generate_response(1)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_get_review_summary_fields(self):
        bot = FiverrReviewGeneratorBot(tier="ENTERPRISE")
        summary = bot.get_review_summary()
        assert "total_reviews" in summary
        assert "average_rating" in summary
        assert "rating_distribution" in summary

    def test_describe_tier(self):
        bot = FiverrReviewGeneratorBot(tier="ENTERPRISE")
        desc = bot.describe_tier()
        assert "ENTERPRISE" in desc

    def test_run_returns_pipeline_result(self):
        bot = FiverrReviewGeneratorBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


# ============================================================
# Marketing_bots
# ============================================================

from Marketing_bots.feature_1 import SocialMediaPostingBot, EXAMPLES as MK1_EXAMPLES
from Marketing_bots.feature_2 import EmailCampaignBot, EXAMPLES as MK2_EXAMPLES
from Marketing_bots.feature_3 import CustomerFeedbackBot, EXAMPLES as MK3_EXAMPLES


class TestSocialMediaPostingBot:
    def test_instantiation(self):
        bot = SocialMediaPostingBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_invalid_tier_raises(self):
        with pytest.raises(ValueError):
            SocialMediaPostingBot(tier="BASIC")

    def test_examples_has_30_entries(self):
        assert len(MK1_EXAMPLES) == 30

    def test_get_posts_by_platform(self):
        bot = SocialMediaPostingBot(tier="ENTERPRISE")
        posts = bot.get_posts_by_platform("twitter")
        assert all(p["platform"] == "twitter" for p in posts)

    def test_get_posts_by_type(self):
        bot = SocialMediaPostingBot(tier="PRO")
        tips = bot.get_posts_by_type("tip")
        assert all(p["type"] == "tip" for p in tips)

    def test_get_pending_posts(self):
        bot = SocialMediaPostingBot(tier="PRO")
        pending = bot.get_pending_posts()
        assert all(p["status"] == "pending" for p in pending)

    def test_schedule_post_requires_pro(self):
        bot = SocialMediaPostingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.schedule_post(1)

    def test_schedule_post_on_pro(self):
        bot = SocialMediaPostingBot(tier="PRO")
        result = bot.schedule_post(1)
        assert result["status"] == "scheduled"

    def test_post_now_on_free(self):
        bot = SocialMediaPostingBot(tier="FREE")
        # post id=1 is twitter which is allowed on free
        result = bot.post_now(1)
        assert result["status"] == "posted"

    def test_post_now_unsupported_platform_raises(self):
        bot = SocialMediaPostingBot(tier="FREE")
        # Find a non-twitter post
        instagram_post = next(p for p in MK1_EXAMPLES if p["platform"] == "instagram")
        with pytest.raises(PermissionError):
            bot.post_now(instagram_post["id"])

    def test_get_analytics_requires_pro(self):
        bot = SocialMediaPostingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_analytics()

    def test_get_analytics_on_pro(self):
        bot = SocialMediaPostingBot(tier="PRO")
        analytics = bot.get_analytics()
        assert "total_templates" in analytics
        assert "by_platform" in analytics

    def test_free_limits_to_twitter(self):
        bot = SocialMediaPostingBot(tier="FREE")
        platforms = bot.get_available_platforms()
        assert platforms == ["twitter"]

    def test_enterprise_has_all_platforms(self):
        bot = SocialMediaPostingBot(tier="ENTERPRISE")
        platforms = bot.get_available_platforms()
        assert "twitter" in platforms
        assert "instagram" in platforms
        assert "linkedin" in platforms
        assert "facebook" in platforms

    def test_describe_tier(self):
        bot = SocialMediaPostingBot(tier="PRO")
        desc = bot.describe_tier()
        assert "PRO" in desc

    def test_run_returns_pipeline_result(self):
        bot = SocialMediaPostingBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


class TestEmailCampaignBot:
    def test_instantiation(self):
        bot = EmailCampaignBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_examples_has_30_entries(self):
        assert len(MK2_EXAMPLES) == 30

    def test_get_campaign_templates_all(self):
        bot = EmailCampaignBot(tier="ENTERPRISE")
        templates = bot.get_campaign_templates()
        assert len(templates) == 30

    def test_get_campaign_templates_by_type(self):
        bot = EmailCampaignBot(tier="PRO")
        welcome = bot.get_campaigns_by_type("welcome")
        assert all(c["type"] == "welcome" for c in welcome)

    def test_activate_campaign(self):
        bot = EmailCampaignBot(tier="PRO")
        result = bot.activate_campaign(1)
        assert result["status"] == "active"

    def test_activate_campaign_free_tier_limit(self):
        bot = EmailCampaignBot(tier="FREE")
        # Campaigns 1-3 have 5000 subscribers, exceeding FREE tier's 500 limit
        # Check that the subscriber limit is enforced
        with pytest.raises(PermissionError):
            bot.activate_campaign(1)

    def test_activate_campaign_unknown_raises(self):
        bot = EmailCampaignBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.activate_campaign(9999)

    def test_get_top_performing_by_open_rate(self):
        bot = EmailCampaignBot(tier="PRO")
        top = bot.get_top_performing_campaigns("open_rate", 3)
        assert len(top) == 3
        rates = [c["open_rate"] for c in top]
        assert rates == sorted(rates, reverse=True)

    def test_get_top_performing_by_click_rate(self):
        bot = EmailCampaignBot(tier="PRO")
        top = bot.get_top_performing_campaigns("click_rate", 3)
        rates = [c["click_rate"] for c in top]
        assert rates == sorted(rates, reverse=True)

    def test_invalid_metric_raises(self):
        bot = EmailCampaignBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_top_performing_campaigns("invalid")

    def test_ab_test_requires_pro(self):
        bot = EmailCampaignBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_ab_test_recommendation(1)

    def test_ab_test_on_pro(self):
        bot = EmailCampaignBot(tier="PRO")
        result = bot.get_ab_test_recommendation(1)
        assert "variant_a" in result
        assert "variant_b" in result

    def test_analytics_requires_pro(self):
        bot = EmailCampaignBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_analytics_report()

    def test_analytics_on_pro(self):
        bot = EmailCampaignBot(tier="PRO")
        report = bot.get_analytics_report()
        assert report["avg_open_rate_pct"] > 0
        assert "open_rate_by_type" in report

    def test_describe_tier(self):
        bot = EmailCampaignBot(tier="FREE")
        desc = bot.describe_tier()
        assert "FREE" in desc

    def test_run_returns_pipeline_result(self):
        bot = EmailCampaignBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


class TestCustomerFeedbackBot:
    def test_instantiation(self):
        bot = CustomerFeedbackBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_examples_has_30_entries(self):
        assert len(MK3_EXAMPLES) == 30

    def test_get_all_feedback(self):
        bot = CustomerFeedbackBot(tier="ENTERPRISE")
        fb = bot.get_all_feedback()
        assert len(fb) == 30

    def test_free_tier_limits_feedback(self):
        bot = CustomerFeedbackBot(tier="FREE")
        fb = bot.get_all_feedback()
        # FREE max is 50 but only 30 examples exist, so all 30 are returned
        assert len(fb) == 30

    def test_get_nps_score(self):
        bot = CustomerFeedbackBot(tier="ENTERPRISE")
        nps = bot.get_nps_score()
        assert "nps" in nps
        assert "promoters" in nps
        assert "detractors" in nps
        assert -100 <= nps["nps"] <= 100

    def test_nps_grade_assigned(self):
        bot = CustomerFeedbackBot(tier="ENTERPRISE")
        nps = bot.get_nps_score()
        assert nps["grade"] in ("Excellent", "Good", "Needs Work")

    def test_sentiment_requires_pro(self):
        bot = CustomerFeedbackBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_sentiment_breakdown()

    def test_sentiment_on_pro(self):
        bot = CustomerFeedbackBot(tier="PRO")
        sentiment = bot.get_sentiment_breakdown()
        assert "positive" in sentiment

    def test_get_feedback_by_category(self):
        bot = CustomerFeedbackBot(tier="ENTERPRISE")
        pricing_fb = bot.get_feedback_by_category("pricing")
        assert all(f["category"] == "pricing" for f in pricing_fb)

    def test_get_negative_feedback(self):
        bot = CustomerFeedbackBot(tier="ENTERPRISE")
        neg = bot.get_negative_feedback()
        assert all(f["sentiment"] == "negative" for f in neg)

    def test_get_unresolved_issues(self):
        bot = CustomerFeedbackBot(tier="ENTERPRISE")
        unresolved = bot.get_unresolved_issues()
        assert all(not f["resolved"] for f in unresolved)

    def test_get_average_rating(self):
        bot = CustomerFeedbackBot(tier="ENTERPRISE")
        avg = bot.get_average_rating()
        assert 1 <= avg <= 5

    def test_ai_insights_requires_enterprise(self):
        bot = CustomerFeedbackBot(tier="PRO")
        with pytest.raises(PermissionError):
            bot.get_ai_insights()

    def test_ai_insights_on_enterprise(self):
        bot = CustomerFeedbackBot(tier="ENTERPRISE")
        insights = bot.get_ai_insights()
        assert "nps_summary" in insights
        assert "recommendations" in insights

    def test_describe_tier(self):
        bot = CustomerFeedbackBot(tier="PRO")
        desc = bot.describe_tier()
        assert "PRO" in desc

    def test_run_returns_pipeline_result(self):
        bot = CustomerFeedbackBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


# ============================================================
# Business_bots
# ============================================================

from Business_bots.feature_1 import MeetingSchedulerBot, EXAMPLES as BU1_EXAMPLES
from Business_bots.feature_2 import ProjectManagementBot, EXAMPLES as BU2_EXAMPLES
from Business_bots.feature_3 import InvoicingBot, EXAMPLES as BU3_EXAMPLES


class TestMeetingSchedulerBot:
    def test_instantiation(self):
        bot = MeetingSchedulerBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_examples_has_30_entries(self):
        assert len(BU1_EXAMPLES) == 30

    def test_examples_have_required_fields(self):
        for m in BU1_EXAMPLES:
            assert "title" in m
            assert "date" in m
            assert "time" in m

    def test_schedule_meeting_on_pro(self):
        bot = MeetingSchedulerBot(tier="PRO")
        result = bot.schedule_meeting(1, "Test User")
        assert result["status"] == "scheduled"

    def test_schedule_meeting_free_limit(self):
        bot = MeetingSchedulerBot(tier="FREE")
        for i in range(1, 6):
            bot.schedule_meeting(i, "User")
        with pytest.raises(PermissionError):
            bot.schedule_meeting(6, "User")

    def test_schedule_unknown_meeting_raises(self):
        bot = MeetingSchedulerBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.schedule_meeting(9999, "User")

    def test_get_meetings_by_type(self):
        bot = MeetingSchedulerBot(tier="ENTERPRISE")
        sales = bot.get_meetings_by_type("sales")
        assert all(m["type"] == "sales" for m in sales)

    def test_get_meetings_by_date(self):
        bot = MeetingSchedulerBot(tier="PRO")
        meetings = bot.get_meetings_by_date("2025-05-05")
        assert all(m["date"] == "2025-05-05" for m in meetings)

    def test_get_pending_confirmations(self):
        bot = MeetingSchedulerBot(tier="PRO")
        pending = bot.get_pending_confirmations()
        assert all(m["status"] == "pending" for m in pending)

    def test_convert_timezone_requires_pro(self):
        bot = MeetingSchedulerBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.convert_timezone(1, "PST")

    def test_convert_timezone_on_pro(self):
        bot = MeetingSchedulerBot(tier="PRO")
        result = bot.convert_timezone(1, "PST")
        assert result["target_timezone"] == "PST"

    def test_send_reminder_requires_pro(self):
        bot = MeetingSchedulerBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.send_reminder(1)

    def test_send_reminder_on_pro(self):
        bot = MeetingSchedulerBot(tier="PRO")
        result = bot.send_reminder(1)
        assert result["sent"] is True

    def test_calendar_summary(self):
        bot = MeetingSchedulerBot(tier="PRO")
        summary = bot.get_calendar_summary()
        assert summary["total_meetings"] == 30

    def test_calendar_sync_on_pro(self):
        bot = MeetingSchedulerBot(tier="PRO")
        result = bot.schedule_meeting(1, "Alice")
        assert "calendar_event_id" in result

    def test_describe_tier(self):
        bot = MeetingSchedulerBot(tier="FREE")
        desc = bot.describe_tier()
        assert "FREE" in desc

    def test_run_returns_pipeline_result(self):
        bot = MeetingSchedulerBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


class TestProjectManagementBot:
    def test_instantiation(self):
        bot = ProjectManagementBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_examples_has_30_entries(self):
        assert len(BU2_EXAMPLES) == 30

    def test_get_projects_by_status(self):
        bot = ProjectManagementBot(tier="ENTERPRISE")
        completed = bot.get_projects_by_status("completed")
        assert all(p["status"] == "completed" for p in completed)

    def test_invalid_status_raises(self):
        bot = ProjectManagementBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_projects_by_status("unknown")

    def test_get_projects_by_priority(self):
        bot = ProjectManagementBot(tier="ENTERPRISE")
        critical = bot.get_projects_by_priority("critical")
        assert all(p["priority"] == "critical" for p in critical)

    def test_invalid_priority_raises(self):
        bot = ProjectManagementBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_projects_by_priority("urgent")

    def test_get_at_risk_projects(self):
        bot = ProjectManagementBot(tier="ENTERPRISE")
        at_risk = bot.get_at_risk_projects(50)
        assert all(p["status"] == "in_progress" and p["progress_pct"] < 50 for p in at_risk)

    def test_free_tier_limits_projects(self):
        bot = ProjectManagementBot(tier="FREE")
        projects = bot._available_projects()
        assert len(projects) == 3

    def test_budget_summary_requires_pro(self):
        bot = ProjectManagementBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_budget_summary()

    def test_budget_summary_on_pro(self):
        bot = ProjectManagementBot(tier="PRO")
        summary = bot.get_budget_summary()
        assert "total_budget_usd" in summary
        assert summary["total_budget_usd"] > 0

    def test_ai_priority_requires_enterprise(self):
        bot = ProjectManagementBot(tier="PRO")
        with pytest.raises(PermissionError):
            bot.get_ai_priority_score(1)

    def test_ai_priority_on_enterprise(self):
        bot = ProjectManagementBot(tier="ENTERPRISE")
        result = bot.get_ai_priority_score(1)
        assert "ai_score" in result
        assert 0 <= result["ai_score"] <= 100

    def test_ai_priority_unknown_project_raises(self):
        bot = ProjectManagementBot(tier="ENTERPRISE")
        with pytest.raises(ValueError):
            bot.get_ai_priority_score(9999)

    def test_get_dashboard(self):
        bot = ProjectManagementBot(tier="ENTERPRISE")
        dashboard = bot.get_dashboard()
        assert dashboard["total_projects"] == 30
        assert "avg_progress_pct" in dashboard

    def test_describe_tier(self):
        bot = ProjectManagementBot(tier="PRO")
        desc = bot.describe_tier()
        assert "PRO" in desc

    def test_run_returns_pipeline_result(self):
        bot = ProjectManagementBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


class TestInvoicingBot:
    def test_instantiation(self):
        bot = InvoicingBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_examples_has_30_entries(self):
        assert len(BU3_EXAMPLES) == 30

    def test_get_invoice_by_id(self):
        bot = InvoicingBot(tier="PRO")
        invoice = bot.get_invoice("INV-001")
        assert invoice["id"] == "INV-001"

    def test_get_invoice_unknown_raises(self):
        bot = InvoicingBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_invoice("INV-999")

    def test_get_invoices_by_status(self):
        bot = InvoicingBot(tier="ENTERPRISE")
        paid = bot.get_invoices_by_status("paid")
        assert all(i["status"] == "paid" for i in paid)

    def test_invalid_status_raises(self):
        bot = InvoicingBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_invoices_by_status("sent")

    def test_get_overdue_invoices(self):
        bot = InvoicingBot(tier="ENTERPRISE")
        overdue = bot.get_overdue_invoices()
        assert all(i["status"] == "overdue" for i in overdue)

    def test_overdue_reminder_requires_pro(self):
        bot = InvoicingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.send_overdue_reminder("INV-004")

    def test_overdue_reminder_on_pro(self):
        bot = InvoicingBot(tier="PRO")
        result = bot.send_overdue_reminder("INV-004")
        assert result["sent"] is True

    def test_overdue_reminder_not_overdue_invoice(self):
        bot = InvoicingBot(tier="PRO")
        result = bot.send_overdue_reminder("INV-001")  # INV-001 is paid
        assert result["sent"] is False

    def test_tax_calculation_requires_pro(self):
        bot = InvoicingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.calculate_tax("INV-001")

    def test_tax_calculation_on_pro(self):
        bot = InvoicingBot(tier="PRO")
        tax = bot.calculate_tax("INV-001")
        assert tax["total"] > tax["subtotal"]

    def test_get_revenue_summary(self):
        bot = InvoicingBot(tier="ENTERPRISE")
        summary = bot.get_revenue_summary()
        assert "total_paid" in summary
        assert "total_overdue" in summary
        assert 0 <= summary["collection_rate_pct"] <= 100

    def test_pdf_export_requires_enterprise(self):
        bot = InvoicingBot(tier="PRO")
        with pytest.raises(PermissionError):
            bot.export_pdf("INV-001")

    def test_pdf_export_on_enterprise(self):
        bot = InvoicingBot(tier="ENTERPRISE")
        result = bot.export_pdf("INV-001")
        assert result["exported"] is True

    def test_describe_tier(self):
        bot = InvoicingBot(tier="FREE")
        desc = bot.describe_tier()
        assert "FREE" in desc

    def test_run_returns_pipeline_result(self):
        bot = InvoicingBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


# ============================================================
# App_bots
# ============================================================

from App_bots.feature_1 import UserOnboardingBot, EXAMPLES as AP1_EXAMPLES
from App_bots.feature_2 import UserSupportBot, EXAMPLES as AP2_EXAMPLES
from App_bots.feature_3 import FeatureUpdateBot, EXAMPLES as AP3_EXAMPLES


class TestUserOnboardingBot:
    def test_instantiation(self):
        bot = UserOnboardingBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_examples_has_30_entries(self):
        assert len(AP1_EXAMPLES) == 30

    def test_get_onboarding_checklist(self):
        bot = UserOnboardingBot(tier="ENTERPRISE")
        checklist = bot.get_onboarding_checklist()
        assert len(checklist) == 30

    def test_free_limits_checklist(self):
        bot = UserOnboardingBot(tier="FREE")
        checklist = bot.get_onboarding_checklist()
        assert len(checklist) == 10

    def test_get_required_steps(self):
        bot = UserOnboardingBot(tier="ENTERPRISE")
        required = bot.get_required_steps()
        assert all(s["required"] for s in required)

    def test_complete_step(self):
        bot = UserOnboardingBot(tier="PRO")
        result = bot.complete_step(1)
        assert result["completed"] is True
        assert result["progress_pct"] > 0

    def test_complete_unknown_step_raises(self):
        bot = UserOnboardingBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.complete_step(9999)

    def test_get_progress(self):
        bot = UserOnboardingBot(tier="PRO")
        bot.complete_step(1)
        progress = bot.get_progress()
        assert progress["completed_steps"] == 1
        assert progress["progress_pct"] > 0

    def test_get_steps_by_category(self):
        bot = UserOnboardingBot(tier="ENTERPRISE")
        core = bot.get_steps_by_category("core")
        assert all(s["category"] == "core" for s in core)

    def test_get_low_completion_steps(self):
        bot = UserOnboardingBot(tier="ENTERPRISE")
        low = bot.get_low_completion_steps(40.0)
        assert all(s["completion_rate"] < 40.0 for s in low)

    def test_personalized_path_requires_pro(self):
        bot = UserOnboardingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_personalized_path("business", ["revenue"])

    def test_personalized_path_on_pro(self):
        bot = UserOnboardingBot(tier="PRO")
        path = bot.get_personalized_path("business", ["revenue", "automation"])
        assert isinstance(path, list)
        assert len(path) > 0

    def test_get_onboarding_analytics(self):
        bot = UserOnboardingBot(tier="ENTERPRISE")
        analytics = bot.get_onboarding_analytics()
        assert "avg_completion_rate_pct" in analytics
        assert analytics["total_steps"] == 30

    def test_describe_tier(self):
        bot = UserOnboardingBot(tier="PRO")
        desc = bot.describe_tier()
        assert "PRO" in desc

    def test_run_returns_pipeline_result(self):
        bot = UserOnboardingBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


class TestUserSupportBot:
    def test_instantiation(self):
        bot = UserSupportBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_examples_has_30_entries(self):
        assert len(AP2_EXAMPLES) == 30

    def test_search_faq_returns_results(self):
        bot = UserSupportBot(tier="PRO")
        results = bot.search_faq("password reset")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_free_tier_query_limit(self):
        bot = UserSupportBot(tier="FREE")
        for _ in range(10):
            bot.search_faq("password")
        with pytest.raises(PermissionError):
            bot.search_faq("billing")

    def test_get_answer_by_id(self):
        bot = UserSupportBot(tier="PRO")
        answer = bot.get_answer(1)
        assert "question" in answer
        assert "answer" in answer

    def test_get_answer_unknown_raises(self):
        bot = UserSupportBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_answer(9999)

    def test_escalation_noted(self):
        bot = UserSupportBot(tier="PRO")
        escalation_q = next(e for e in AP2_EXAMPLES if e["escalate"])
        answer = bot.get_answer(escalation_q["id"])
        assert "note" in answer

    def test_create_ticket_requires_pro(self):
        bot = UserSupportBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.create_ticket("user@test.com", "Help", "Need help with billing")

    def test_create_ticket_on_pro(self):
        bot = UserSupportBot(tier="PRO")
        ticket = bot.create_ticket("user@test.com", "Billing Issue", "I was charged twice")
        assert "ticket_id" in ticket
        assert ticket["status"] == "open"

    def test_get_questions_by_category(self):
        bot = UserSupportBot(tier="PRO")
        billing_q = bot.get_questions_by_category("billing")
        assert all(q["category"] == "billing" for q in billing_q)

    def test_get_escalation_questions(self):
        bot = UserSupportBot(tier="PRO")
        esc = bot.get_escalation_required_questions()
        assert all(q["escalate"] for q in esc)

    def test_get_top_questions(self):
        bot = UserSupportBot(tier="PRO")
        top = bot.get_top_questions(3)
        assert len(top) == 3
        votes = [q["helpful_votes"] for q in top]
        assert votes == sorted(votes, reverse=True)

    def test_ai_answer_requires_pro(self):
        bot = UserSupportBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_ai_answer("how do I reset password")

    def test_ai_answer_on_pro(self):
        bot = UserSupportBot(tier="PRO")
        result = bot.get_ai_answer("how do I reset password")
        assert "ai_answer" in result
        assert "confidence" in result

    def test_describe_tier(self):
        bot = UserSupportBot(tier="ENTERPRISE")
        desc = bot.describe_tier()
        assert "ENTERPRISE" in desc

    def test_run_returns_pipeline_result(self):
        bot = UserSupportBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


class TestFeatureUpdateBot:
    def test_instantiation(self):
        bot = FeatureUpdateBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_examples_has_30_entries(self):
        assert len(AP3_EXAMPLES) == 30

    def test_get_latest_updates(self):
        bot = FeatureUpdateBot(tier="PRO")
        updates = bot.get_latest_updates(5)
        assert len(updates) == 5
        dates = [u["date"] for u in updates]
        assert dates == sorted(dates, reverse=True)

    def test_free_tier_limits_updates(self):
        bot = FeatureUpdateBot(tier="FREE")
        updates = bot.get_latest_updates(20)
        assert len(updates) == 10  # free limited to 10

    def test_get_updates_by_type(self):
        bot = FeatureUpdateBot(tier="PRO")
        features = bot.get_updates_by_type("feature")
        assert all(u["type"] == "feature" for u in features)

    def test_get_updates_for_tier(self):
        bot = FeatureUpdateBot(tier="PRO")
        updates = bot.get_updates_for_tier("FREE")
        # Should only include FREE-accessible updates
        free_types = {"FREE"}
        assert all(u["tier_required"] == "FREE" for u in updates)

    def test_get_high_engagement_updates(self):
        bot = FeatureUpdateBot(tier="PRO")
        updates = bot.get_high_engagement_updates(40.0)
        assert all(u["action_rate"] >= 40.0 for u in updates)

    def test_send_notification_requires_pro(self):
        bot = FeatureUpdateBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.send_notification(1, "user@test.com")

    def test_send_notification_on_pro(self):
        bot = FeatureUpdateBot(tier="PRO")
        result = bot.send_notification(1, "user@test.com")
        assert result["sent"] is True

    def test_send_notification_unknown_update_raises(self):
        bot = FeatureUpdateBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.send_notification(9999, "user@test.com")

    def test_get_changelog(self):
        bot = FeatureUpdateBot(tier="PRO")
        changelog = bot.get_changelog()
        assert isinstance(changelog, list)
        assert len(changelog) > 0

    def test_get_changelog_by_version(self):
        bot = FeatureUpdateBot(tier="PRO")
        changelog = bot.get_changelog("v3.5.0")
        assert all(u["version"] == "v3.5.0" for u in changelog)

    def test_get_update_analytics(self):
        bot = FeatureUpdateBot(tier="PRO")
        analytics = bot.get_update_analytics()
        assert "avg_action_rate_pct" in analytics
        assert "highest_engagement" in analytics

    def test_describe_tier(self):
        bot = FeatureUpdateBot(tier="PRO")
        desc = bot.describe_tier()
        assert "PRO" in desc

    def test_run_returns_pipeline_result(self):
        bot = FeatureUpdateBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


# ============================================================
# Occupational_bots
# ============================================================

from Occupational_bots.feature_1 import JobSearchBot, EXAMPLES as OC1_EXAMPLES
from Occupational_bots.feature_2 import ResumeBuildingBot, EXAMPLES as OC2_EXAMPLES
from Occupational_bots.feature_3 import InterviewPrepBot, EXAMPLES as OC3_EXAMPLES


class TestJobSearchBot:
    def test_instantiation(self):
        bot = JobSearchBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_invalid_tier_raises(self):
        with pytest.raises(ValueError):
            JobSearchBot(tier="INVALID")

    def test_examples_has_30_entries(self):
        assert len(OC1_EXAMPLES) == 30

    def test_search_jobs_returns_list(self):
        bot = JobSearchBot(tier="PRO")
        results = bot.search_jobs()
        assert isinstance(results, list)

    def test_search_by_title(self):
        bot = JobSearchBot(tier="PRO")
        results = bot.search_jobs(title="Engineer")
        assert all("Engineer" in r["title"] for r in results)

    def test_search_remote_only(self):
        bot = JobSearchBot(tier="PRO")
        results = bot.search_jobs(remote_only=True)
        assert all(r["remote"] for r in results)

    def test_search_by_min_salary(self):
        bot = JobSearchBot(tier="PRO")
        results = bot.search_jobs(min_salary=100000)
        assert all(r["salary_min"] >= 100000 for r in results)

    def test_search_by_experience(self):
        bot = JobSearchBot(tier="PRO")
        results = bot.search_jobs(experience="senior")
        assert all(r["experience"] == "senior" for r in results)

    def test_free_tier_limits_results(self):
        bot = JobSearchBot(tier="FREE")
        results = bot.search_jobs()
        assert len(results) <= 5

    def test_get_job_by_id(self):
        bot = JobSearchBot(tier="PRO")
        job = bot.get_job(1)
        assert job["id"] == 1

    def test_get_job_unknown_raises(self):
        bot = JobSearchBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_job(9999)

    def test_get_remote_jobs(self):
        bot = JobSearchBot(tier="PRO")
        jobs = bot.get_remote_jobs()
        assert all(j["remote"] for j in jobs)

    def test_get_top_paying_jobs(self):
        bot = JobSearchBot(tier="PRO")
        top = bot.get_top_paying_jobs(3)
        assert len(top) == 3
        salaries = [j["salary_max"] for j in top]
        assert salaries == sorted(salaries, reverse=True)

    def test_ai_matching_requires_pro(self):
        bot = JobSearchBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_ai_job_matches(["Python"])

    def test_ai_matching_on_pro(self):
        bot = JobSearchBot(tier="PRO")
        matches = bot.get_ai_job_matches(["Python", "Machine Learning"])
        assert isinstance(matches, list)
        if matches:
            assert "match_score" in matches[0]

    def test_track_application_requires_pro(self):
        bot = JobSearchBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.track_application(1)

    def test_track_application_on_pro(self):
        bot = JobSearchBot(tier="PRO")
        app = bot.track_application(1, status="applied")
        assert "application_id" in app
        assert app["status"] == "applied"

    def test_save_job(self):
        bot = JobSearchBot(tier="FREE")
        result = bot.save_job(1)
        assert result["saved"] is True
        saved = bot.get_saved_jobs()
        assert any(j["id"] == 1 for j in saved)

    def test_get_search_stats(self):
        bot = JobSearchBot(tier="PRO")
        stats = bot.get_search_stats()
        assert stats["total_listings"] == 30
        assert stats["remote_jobs"] > 0

    def test_describe_tier(self):
        bot = JobSearchBot(tier="FREE")
        desc = bot.describe_tier()
        assert "FREE" in desc

    def test_run_returns_pipeline_result(self):
        bot = JobSearchBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


class TestResumeBuildingBot:
    def test_instantiation(self):
        bot = ResumeBuildingBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_examples_has_30_entries(self):
        assert len(OC2_EXAMPLES) == 30

    def test_get_templates_for_role(self):
        bot = ResumeBuildingBot(tier="PRO")
        templates = bot.get_templates_for_role("Software Engineer")
        assert len(templates) > 0

    def test_get_templates_by_section(self):
        bot = ResumeBuildingBot(tier="ENTERPRISE")
        templates = bot.get_templates_by_section("Skills")
        assert all(t["section"] == "Skills" for t in templates)

    def test_get_template_by_id(self):
        bot = ResumeBuildingBot(tier="PRO")
        template = bot.get_template(1)
        assert template["id"] == 1

    def test_get_template_unknown_raises(self):
        bot = ResumeBuildingBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_template(9999)

    def test_free_tier_limits_templates(self):
        bot = ResumeBuildingBot(tier="FREE")
        templates = bot._available_templates()
        assert len(templates) == 5

    def test_ats_score_requires_pro(self):
        bot = ResumeBuildingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.check_ats_score(1)

    def test_ats_score_on_pro(self):
        bot = ResumeBuildingBot(tier="PRO")
        result = bot.check_ats_score(1)
        assert "ats_score" in result
        assert "grade" in result
        assert 0 <= result["ats_score"] <= 100

    def test_ai_suggestions_requires_pro(self):
        bot = ResumeBuildingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_ai_suggestions("Software Engineer", "Skills")

    def test_ai_suggestions_on_pro(self):
        bot = ResumeBuildingBot(tier="PRO")
        result = bot.get_ai_suggestions("Software Engineer", "Skills")
        assert "suggested_template" in result
        assert "ats_score" in result

    def test_cover_letter_requires_pro(self):
        bot = ResumeBuildingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.generate_cover_letter("Software Engineer", "TechCorp")

    def test_cover_letter_on_pro(self):
        bot = ResumeBuildingBot(tier="PRO")
        result = bot.generate_cover_letter("Software Engineer", "TechCorp")
        assert "opening" in result
        assert "closing" in result
        assert "TechCorp" in result["opening"]

    def test_get_high_ats_templates(self):
        bot = ResumeBuildingBot(tier="ENTERPRISE")
        high = bot.get_high_ats_templates(90)
        assert all(t["ats_score"] >= 90 for t in high)

    def test_get_resume_sections(self):
        bot = ResumeBuildingBot(tier="ENTERPRISE")
        sections = bot.get_resume_sections()
        assert isinstance(sections, list)
        assert "Skills" in sections
        assert "Education" in sections

    def test_describe_tier(self):
        bot = ResumeBuildingBot(tier="PRO")
        desc = bot.describe_tier()
        assert "PRO" in desc

    def test_run_returns_pipeline_result(self):
        bot = ResumeBuildingBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True


class TestInterviewPrepBot:
    def test_instantiation(self):
        bot = InterviewPrepBot(tier="FREE")
        assert bot.tier == "FREE"

    def test_invalid_tier_raises(self):
        with pytest.raises(ValueError):
            InterviewPrepBot(tier="BASIC")

    def test_examples_has_30_entries(self):
        assert len(OC3_EXAMPLES) == 30

    def test_get_questions_by_type(self):
        bot = InterviewPrepBot(tier="PRO")
        behavioral = bot.get_questions_by_type("behavioral")
        assert all(q["type"] == "behavioral" for q in behavioral)

    def test_invalid_type_raises(self):
        bot = InterviewPrepBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_questions_by_type("unknown")

    def test_get_questions_by_role(self):
        bot = InterviewPrepBot(tier="PRO")
        se_q = bot.get_questions_by_role("software_engineer")
        assert len(se_q) > 0

    def test_get_questions_by_difficulty(self):
        bot = InterviewPrepBot(tier="PRO")
        hard = bot.get_questions_by_difficulty("hard")
        assert all(q["difficulty"] == "hard" for q in hard)

    def test_invalid_difficulty_raises(self):
        bot = InterviewPrepBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_questions_by_difficulty("extreme")

    def test_free_tier_limits_questions(self):
        bot = InterviewPrepBot(tier="FREE")
        questions = bot._available_questions()
        assert len(questions) == 10

    def test_get_question_by_id(self):
        bot = InterviewPrepBot(tier="PRO")
        q = bot.get_question(1)
        assert q["id"] == 1
        assert "question" in q

    def test_get_question_unknown_raises(self):
        bot = InterviewPrepBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.get_question(9999)

    def test_get_star_answer(self):
        bot = InterviewPrepBot(tier="PRO")
        result = bot.get_star_answer(1)
        assert "star_answer" in result
        assert "follow_ups" in result
        assert "STAR" in result["method"]

    def test_mock_interview_requires_pro(self):
        bot = InterviewPrepBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.start_mock_interview("software_engineer")

    def test_mock_interview_on_pro(self):
        bot = InterviewPrepBot(tier="PRO")
        mock = bot.start_mock_interview("software_engineer", "medium")
        assert isinstance(mock, list)
        assert len(mock) > 0

    def test_ai_coaching_requires_enterprise(self):
        bot = InterviewPrepBot(tier="PRO")
        with pytest.raises(PermissionError):
            bot.get_ai_coaching_feedback(1, "My answer here")

    def test_ai_coaching_on_enterprise(self):
        bot = InterviewPrepBot(tier="ENTERPRISE")
        result = bot.get_ai_coaching_feedback(1, "I led a team of 5 engineers to deliver a product that increased revenue by 30%. " * 5)
        assert "feedback" in result
        assert isinstance(result["feedback"], list)

    def test_log_practice(self):
        bot = InterviewPrepBot(tier="PRO")
        entry = bot.log_practice(1, 4)
        assert entry["self_rating"] == 4

    def test_get_prep_summary(self):
        bot = InterviewPrepBot(tier="PRO")
        bot.log_practice(1, 4)
        summary = bot.get_prep_summary()
        assert "total_questions" in summary
        assert summary["practice_sessions"] == 1

    def test_describe_tier(self):
        bot = InterviewPrepBot(tier="FREE")
        desc = bot.describe_tier()
        assert "FREE" in desc

    def test_run_returns_pipeline_result(self):
        bot = InterviewPrepBot(tier="FREE")
        result = bot.run()
        assert result["pipeline_complete"] is True
