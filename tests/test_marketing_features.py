"""Tests for Marketing_bots/feature_1.py, feature_2.py, feature_3.py"""
from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from Marketing_bots.feature_1 import SocialMediaPostingBot, EXAMPLES as MK1_EXAMPLES
from Marketing_bots.feature_2 import EmailCampaignBot, EXAMPLES as MK2_EXAMPLES
from Marketing_bots.feature_3 import CustomerFeedbackBot, EXAMPLES as MK3_EXAMPLES


# ===========================================================================
# Feature 1: SocialMediaPostingBot
# ===========================================================================

class TestSocialMediaPostingBotInstantiation:
    def test_default_tier_is_free(self):
        bot = SocialMediaPostingBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = SocialMediaPostingBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = SocialMediaPostingBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            SocialMediaPostingBot(tier="BASIC")

    def test_has_30_examples(self):
        assert len(MK1_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "platform", "content", "type"}
        for ex in MK1_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestSocialMediaPostingBotMethods:
    def test_schedule_post_returns_dict(self):
        bot = SocialMediaPostingBot(tier="PRO")
        # Find a twitter post (FREE accessible)
        twitter_post = next(p for p in MK1_EXAMPLES if p["platform"] == "twitter")
        result = bot.schedule_post(twitter_post["id"])
        assert isinstance(result, dict)

    def test_free_tier_only_twitter(self):
        bot = SocialMediaPostingBot(tier="FREE")
        non_twitter = next((p for p in MK1_EXAMPLES if p["platform"] != "twitter"), None)
        if non_twitter:
            with pytest.raises(PermissionError):
                bot.schedule_post(non_twitter["id"])

    def test_post_now_returns_dict(self):
        bot = SocialMediaPostingBot(tier="PRO")
        twitter_post = next(p for p in MK1_EXAMPLES if p["platform"] == "twitter")
        result = bot.post_now(twitter_post["id"])
        assert isinstance(result, dict)

    def test_get_posts_by_platform_returns_list(self):
        bot = SocialMediaPostingBot(tier="PRO")
        posts = bot.get_posts_by_platform("twitter")
        assert isinstance(posts, list)
        for p in posts:
            assert p["platform"] == "twitter"

    def test_get_posts_by_type_returns_list(self):
        bot = SocialMediaPostingBot(tier="PRO")
        first_type = MK1_EXAMPLES[0]["type"]
        posts = bot.get_posts_by_type(first_type)
        assert isinstance(posts, list)
        for p in posts:
            assert p["type"] == first_type

    def test_get_pending_posts_returns_list(self):
        bot = SocialMediaPostingBot(tier="PRO")
        bot.schedule_post(next(p for p in MK1_EXAMPLES if p["platform"] == "twitter")["id"])
        pending = bot.get_pending_posts()
        assert isinstance(pending, list)

    def test_get_analytics_requires_pro(self):
        bot = SocialMediaPostingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_analytics()

    def test_get_analytics_pro_returns_dict(self):
        bot = SocialMediaPostingBot(tier="PRO")
        analytics = bot.get_analytics()
        assert isinstance(analytics, dict)

    def test_get_available_platforms_returns_list(self):
        bot = SocialMediaPostingBot(tier="FREE")
        platforms = bot.get_available_platforms()
        assert isinstance(platforms, list)
        assert "twitter" in platforms

    def test_pro_has_more_platforms(self):
        free_bot = SocialMediaPostingBot(tier="FREE")
        pro_bot = SocialMediaPostingBot(tier="PRO")
        assert len(pro_bot.get_available_platforms()) > len(free_bot.get_available_platforms())

    def test_describe_tier_returns_string(self):
        bot = SocialMediaPostingBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = SocialMediaPostingBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result


# ===========================================================================
# Feature 2: EmailCampaignBot
# ===========================================================================

class TestEmailCampaignBotInstantiation:
    def test_default_tier_is_free(self):
        bot = EmailCampaignBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = EmailCampaignBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = EmailCampaignBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            EmailCampaignBot(tier="STARTER")

    def test_has_30_examples(self):
        assert len(MK2_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "name", "type", "subject", "open_rate", "click_rate"}
        for ex in MK2_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestEmailCampaignBotMethods:
    def test_get_campaign_templates_returns_list(self):
        bot = EmailCampaignBot(tier="FREE")
        templates = bot.get_campaign_templates()
        assert isinstance(templates, list)

    def test_get_campaign_templates_by_type(self):
        bot = EmailCampaignBot(tier="FREE")
        first_type = MK2_EXAMPLES[0]["type"]
        templates = bot.get_campaign_templates(campaign_type=first_type)
        for t in templates:
            assert t["type"] == first_type

    def test_activate_campaign_returns_dict(self):
        bot = EmailCampaignBot(tier="PRO")
        result = bot.activate_campaign(1)
        assert isinstance(result, dict)

    def test_free_tier_subscriber_limit_enforced(self):
        bot = EmailCampaignBot(tier="FREE")
        # FREE tier has 500 subscriber limit - any campaign with more should fail
        large_campaign = next(c for c in MK2_EXAMPLES if c["subscribers"] > 500)
        with pytest.raises(PermissionError):
            bot.activate_campaign(large_campaign["id"])

    def test_get_top_performing_campaigns_returns_list(self):
        bot = EmailCampaignBot(tier="PRO")
        top = bot.get_top_performing_campaigns(metric="open_rate", count=5)
        assert isinstance(top, list)
        assert len(top) <= 5

    def test_get_ab_test_recommendation_requires_pro(self):
        bot = EmailCampaignBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_ab_test_recommendation(1)

    def test_get_ab_test_recommendation_pro_returns_dict(self):
        bot = EmailCampaignBot(tier="PRO")
        result = bot.get_ab_test_recommendation(1)
        assert isinstance(result, dict)

    def test_get_analytics_report_requires_pro(self):
        bot = EmailCampaignBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_analytics_report()

    def test_get_analytics_report_pro_returns_dict(self):
        bot = EmailCampaignBot(tier="PRO")
        report = bot.get_analytics_report()
        assert isinstance(report, dict)

    def test_get_campaigns_by_type_returns_list(self):
        bot = EmailCampaignBot(tier="PRO")
        first_type = MK2_EXAMPLES[0]["type"]
        campaigns = bot.get_campaigns_by_type(first_type)
        assert isinstance(campaigns, list)

    def test_describe_tier_returns_string(self):
        bot = EmailCampaignBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = EmailCampaignBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result


# ===========================================================================
# Feature 3: CustomerFeedbackBot
# ===========================================================================

class TestCustomerFeedbackBotInstantiation:
    def test_default_tier_is_free(self):
        bot = CustomerFeedbackBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = CustomerFeedbackBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = CustomerFeedbackBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            CustomerFeedbackBot(tier="PREMIUM")

    def test_has_30_examples(self):
        assert len(MK3_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "customer", "nps_score", "sentiment", "category"}
        for ex in MK3_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestCustomerFeedbackBotMethods:
    def test_get_all_feedback_returns_list(self):
        bot = CustomerFeedbackBot(tier="FREE")
        feedback = bot.get_all_feedback()
        assert isinstance(feedback, list)

    def test_get_nps_score_returns_dict(self):
        bot = CustomerFeedbackBot(tier="PRO")
        nps = bot.get_nps_score()
        assert isinstance(nps, dict)
        assert "nps" in nps or "score" in nps or any("nps" in k.lower() for k in nps)

    def test_get_sentiment_breakdown_requires_pro(self):
        bot = CustomerFeedbackBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_sentiment_breakdown()

    def test_get_sentiment_breakdown_pro_returns_dict(self):
        bot = CustomerFeedbackBot(tier="PRO")
        breakdown = bot.get_sentiment_breakdown()
        assert isinstance(breakdown, dict)

    def test_get_feedback_by_category_returns_list(self):
        bot = CustomerFeedbackBot(tier="PRO")
        first_category = MK3_EXAMPLES[0]["category"]
        feedback = bot.get_feedback_by_category(first_category)
        assert isinstance(feedback, list)
        for f in feedback:
            assert f["category"] == first_category

    def test_get_negative_feedback_returns_list(self):
        bot = CustomerFeedbackBot(tier="PRO")
        neg = bot.get_negative_feedback()
        assert isinstance(neg, list)

    def test_free_tier_limits_responses(self):
        bot = CustomerFeedbackBot(tier="FREE")
        feedback = bot.get_all_feedback()
        assert len(feedback) <= 50

    def test_describe_tier_returns_string(self):
        bot = CustomerFeedbackBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = CustomerFeedbackBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result
