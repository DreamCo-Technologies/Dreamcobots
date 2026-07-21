"""Tests for Fiverr_bots/feature_1.py, feature_2.py, feature_3.py"""
from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from Fiverr_bots.feature_1 import FiverrServiceListingBot, EXAMPLES as FV1_EXAMPLES
from Fiverr_bots.feature_2 import FiverrOrderManagerBot, EXAMPLES as FV2_EXAMPLES
from Fiverr_bots.feature_3 import FiverrReviewGeneratorBot, EXAMPLES as FV3_EXAMPLES


# ===========================================================================
# Feature 1: FiverrServiceListingBot
# ===========================================================================

class TestFiverrServiceListingBotInstantiation:
    def test_default_tier_is_free(self):
        bot = FiverrServiceListingBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = FiverrServiceListingBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = FiverrServiceListingBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            FiverrServiceListingBot(tier="GOLD")

    def test_has_30_examples(self):
        assert len(FV1_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "title", "category", "base_price", "delivery_days", "keywords", "demand", "avg_rating"}
        for ex in FV1_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestFiverrServiceListingBotMethods:
    def test_create_listing_returns_dict(self):
        bot = FiverrServiceListingBot(tier="PRO")
        listing = bot.create_listing(1)
        assert isinstance(listing, dict)
        assert listing["id"] == 1

    def test_create_listing_invalid_id_raises(self):
        bot = FiverrServiceListingBot(tier="PRO")
        with pytest.raises(ValueError):
            bot.create_listing(9999)

    def test_free_tier_max_3_gigs(self):
        bot = FiverrServiceListingBot(tier="FREE")
        for i in range(1, 4):
            bot.create_listing(i)
        with pytest.raises(PermissionError):
            bot.create_listing(4)

    def test_pro_tier_has_optimized_titles(self):
        bot = FiverrServiceListingBot(tier="PRO")
        listing = bot.create_listing(1)
        assert "optimized_title" in listing

    def test_enterprise_has_keyword_injection(self):
        bot = FiverrServiceListingBot(tier="ENTERPRISE")
        listing = bot.create_listing(1)
        assert "injected_keywords" in listing

    def test_search_templates_returns_list(self):
        bot = FiverrServiceListingBot(tier="FREE")
        results = bot.search_templates()
        assert isinstance(results, list)

    def test_search_templates_by_category(self):
        bot = FiverrServiceListingBot(tier="FREE")
        results = bot.search_templates(category="programming")
        for r in results:
            assert r["category"] == "programming"

    def test_search_templates_by_max_price(self):
        bot = FiverrServiceListingBot(tier="FREE")
        results = bot.search_templates(max_price=30)
        for r in results:
            assert r["base_price"] <= 30

    def test_get_high_demand_gigs_returns_list(self):
        bot = FiverrServiceListingBot(tier="PRO")
        gigs = bot.get_high_demand_gigs()
        assert isinstance(gigs, list)
        for g in gigs:
            assert g["demand"] == "high"

    def test_get_top_rated_gigs_returns_sorted(self):
        bot = FiverrServiceListingBot(tier="PRO")
        gigs = bot.get_top_rated_gigs(5)
        assert len(gigs) <= 5
        ratings = [g["avg_rating"] for g in gigs]
        assert ratings == sorted(ratings, reverse=True)

    def test_estimate_monthly_revenue_returns_dict(self):
        bot = FiverrServiceListingBot(tier="PRO")
        result = bot.estimate_monthly_revenue(1)
        assert isinstance(result, dict)
        assert "monthly_revenue" in result or "revenue" in result or any("revenue" in k for k in result)

    def test_get_active_listings_returns_list(self):
        bot = FiverrServiceListingBot(tier="PRO")
        bot.create_listing(1)
        listings = bot.get_active_listings()
        assert isinstance(listings, list)
        assert len(listings) >= 1

    def test_get_categories_returns_list(self):
        bot = FiverrServiceListingBot(tier="FREE")
        cats = bot.get_categories()
        assert isinstance(cats, list)
        assert len(cats) > 0

    def test_describe_tier_returns_string(self):
        bot = FiverrServiceListingBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = FiverrServiceListingBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result


# ===========================================================================
# Feature 2: FiverrOrderManagerBot
# ===========================================================================

class TestFiverrOrderManagerBotInstantiation:
    def test_default_tier_is_free(self):
        bot = FiverrOrderManagerBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = FiverrOrderManagerBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = FiverrOrderManagerBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            FiverrOrderManagerBot(tier="SILVER")

    def test_has_30_examples(self):
        assert len(FV2_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "buyer", "gig", "price", "status"}
        for ex in FV2_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestFiverrOrderManagerBotMethods:
    def test_get_orders_by_status_returns_list(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        result = bot.get_orders_by_status("in_progress")
        assert isinstance(result, list)

    def test_get_active_orders_returns_list(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        orders = bot.get_active_orders()
        assert isinstance(orders, list)

    def test_get_order_returns_dict(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        order_id = FV2_EXAMPLES[0]["id"]
        result = bot.get_order(order_id)
        assert isinstance(result, dict)

    def test_get_order_invalid_id_raises(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        with pytest.raises((ValueError, KeyError)):
            bot.get_order("NONEXISTENT_ORDER_999")

    def test_get_revenue_summary_returns_dict(self):
        bot = FiverrOrderManagerBot(tier="PRO")
        summary = bot.get_revenue_summary()
        assert isinstance(summary, dict)

    def test_send_deadline_alert_requires_pro(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        order_id = FV2_EXAMPLES[0]["id"]
        with pytest.raises(PermissionError):
            bot.send_deadline_alert(order_id)

    def test_send_deadline_alert_pro_returns_dict(self):
        bot = FiverrOrderManagerBot(tier="PRO")
        # Find an active order
        active = [o for o in FV2_EXAMPLES if o["status"] == "active"]
        if active:
            result = bot.send_deadline_alert(active[0]["id"])
            assert isinstance(result, dict)

    def test_send_auto_message_requires_pro(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        order_id = FV2_EXAMPLES[0]["id"]
        with pytest.raises(PermissionError):
            bot.send_auto_message(order_id)

    def test_send_auto_message_pro_returns_dict(self):
        bot = FiverrOrderManagerBot(tier="PRO")
        order_id = FV2_EXAMPLES[0]["id"]
        result = bot.send_auto_message(order_id)
        assert isinstance(result, dict)

    def test_get_unreviewed_orders_returns_list(self):
        bot = FiverrOrderManagerBot(tier="PRO")
        orders = bot.get_unreviewed_orders()
        assert isinstance(orders, list)

    def test_get_average_rating_returns_float(self):
        bot = FiverrOrderManagerBot(tier="PRO")
        avg = bot.get_average_rating()
        assert isinstance(avg, float)
        assert 0.0 <= avg <= 5.0

    def test_describe_tier_returns_string(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = FiverrOrderManagerBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result


# ===========================================================================
# Feature 3: FiverrReviewGeneratorBot
# ===========================================================================

class TestFiverrReviewGeneratorBotInstantiation:
    def test_default_tier_is_free(self):
        bot = FiverrReviewGeneratorBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = FiverrReviewGeneratorBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            FiverrReviewGeneratorBot(tier="DIAMOND")

    def test_has_30_examples(self):
        assert len(FV3_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "buyer", "gig", "rating", "review", "sentiment"}
        for ex in FV3_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestFiverrReviewGeneratorBotMethods:
    def test_get_all_reviews_returns_list(self):
        bot = FiverrReviewGeneratorBot(tier="FREE")
        reviews = bot.get_all_reviews()
        assert isinstance(reviews, list)
        assert len(reviews) <= 10  # FREE limit

    def test_pro_tier_returns_more_reviews(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        reviews = bot.get_all_reviews()
        assert isinstance(reviews, list)
        assert len(reviews) <= 100

    def test_get_reviews_by_rating_returns_correct(self):
        bot = FiverrReviewGeneratorBot(tier="ENTERPRISE")
        fives = bot.get_reviews_by_rating(5)
        for r in fives:
            assert r["rating"] == 5

    def test_get_reviews_by_sentiment_returns_list(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        positives = bot.get_reviews_by_sentiment("positive")
        assert isinstance(positives, list)
        for r in positives:
            assert r["sentiment"] == "positive"

    def test_get_average_rating_returns_float(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        avg = bot.get_average_rating()
        assert isinstance(avg, float)
        assert 1.0 <= avg <= 5.0

    def test_get_rating_distribution_returns_dict(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        dist = bot.get_rating_distribution()
        assert isinstance(dist, dict)

    def test_get_pending_responses_returns_list(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        pending = bot.get_pending_responses()
        assert isinstance(pending, list)

    def test_send_review_request_requires_pro(self):
        bot = FiverrReviewGeneratorBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.send_review_request("buyer123", "Logo Design")

    def test_send_review_request_pro_returns_dict(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        result = bot.send_review_request("buyer123", "Logo Design")
        assert isinstance(result, dict)

    def test_generate_response_requires_enterprise(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        with pytest.raises(PermissionError):
            bot.generate_response(1)

    def test_generate_response_enterprise_returns_string(self):
        bot = FiverrReviewGeneratorBot(tier="ENTERPRISE")
        response = bot.generate_response(1)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_get_review_summary_returns_dict(self):
        bot = FiverrReviewGeneratorBot(tier="PRO")
        summary = bot.get_review_summary()
        assert isinstance(summary, dict)

    def test_describe_tier_returns_string(self):
        bot = FiverrReviewGeneratorBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = FiverrReviewGeneratorBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result
