"""Tests for bots/social_media_manager_bot"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.social_media_manager_bot.social_media_manager_bot import SocialMediaManagerBot
from bots.social_media_manager_bot.tiers import BOT_FEATURES, get_bot_tier_info


class TestSocialMediaManagerBotInstantiation:
    def test_default_tier_is_free(self):
        bot = SocialMediaManagerBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = SocialMediaManagerBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = SocialMediaManagerBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE


class TestCreatePost:
    def test_free_can_post_to_instagram(self):
        bot = SocialMediaManagerBot()
        result = bot.create_post("instagram", "new product")
        assert result["platform"] == "instagram"

    def test_free_cannot_post_to_twitter(self):
        bot = SocialMediaManagerBot()
        with pytest.raises(PermissionError):
            bot.create_post("twitter", "new product")

    def test_free_cannot_post_to_linkedin(self):
        bot = SocialMediaManagerBot()
        with pytest.raises(PermissionError):
            bot.create_post("linkedin", "update")

    def test_pro_can_post_to_twitter(self):
        bot = SocialMediaManagerBot(tier=Tier.PRO)
        result = bot.create_post("twitter", "big news")
        assert result["platform"] == "twitter"

    def test_post_has_required_keys(self):
        bot = SocialMediaManagerBot()
        result = bot.create_post("instagram", "sale")
        for key in ["platform", "topic", "caption", "hashtags", "estimated_reach", "best_time_to_post", "media_suggestion", "tier_used"]:
            assert key in result

    def test_hashtags_included_by_default(self):
        bot = SocialMediaManagerBot()
        result = bot.create_post("instagram", "sale", include_hashtags=True)
        assert len(result["hashtags"]) > 0

    def test_hashtags_excluded(self):
        bot = SocialMediaManagerBot()
        result = bot.create_post("instagram", "sale", include_hashtags=False)
        assert result["hashtags"] == []


class TestScheduleContent:
    def test_schedule_returns_calendar(self):
        bot = SocialMediaManagerBot()
        result = bot.schedule_content("instagram", posts_per_week=3)
        assert len(result["calendar"]) == 3

    def test_schedule_wrong_platform_raises(self):
        bot = SocialMediaManagerBot()
        with pytest.raises(PermissionError):
            bot.schedule_content("facebook")


class TestHashtagSuggestions:
    def test_hashtag_suggestions_raises_on_free(self):
        bot = SocialMediaManagerBot()
        with pytest.raises(PermissionError):
            bot.get_hashtag_suggestions("marketing", "instagram")

    def test_hashtag_suggestions_works_on_pro(self):
        bot = SocialMediaManagerBot(tier=Tier.PRO)
        result = bot.get_hashtag_suggestions("marketing", "instagram")
        assert isinstance(result, list)
        assert len(result) == 10


class TestEngagementAnalysis:
    def test_analyze_engagement_returns_dict(self):
        bot = SocialMediaManagerBot()
        result = bot.analyze_engagement("instagram", "post_123")
        assert isinstance(result, dict)
        assert "engagement_rate" in result
        assert "likes" in result


class TestSocialMediaBotTiers:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_tier_config_price(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_run_returns_pipeline_complete(self):
        bot = SocialMediaManagerBot()
        result = bot.run()
        assert result.get("pipeline_complete") is True
