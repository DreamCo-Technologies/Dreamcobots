"""
Tests for bots/social_media_bot/tiers.py and bots/social_media_bot/bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.social_media_bot.tiers import SOCIAL_MEDIA_FEATURES, get_social_media_tier_info
from bots.social_media_bot.bot import (
    SocialMediaBot,
    SocialMediaBotTierError,
    SocialMediaBotRequestLimitError,
)


class TestSocialMediaTierInfo:
    def test_free_tier_info_keys(self):
        info = get_social_media_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "support_level", "bot_features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_social_media_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        info = get_social_media_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_features_exist_for_all_tiers(self):
        for tier in Tier:
            assert tier.value in SOCIAL_MEDIA_FEATURES
            assert len(SOCIAL_MEDIA_FEATURES[tier.value]) > 0


class TestSocialMediaBot:
    def test_default_tier_is_free(self):
        bot = SocialMediaBot()
        assert bot.tier == Tier.FREE

    def test_schedule_post_returns_expected_keys(self):
        bot = SocialMediaBot(tier=Tier.FREE)
        result = bot.schedule_post({"content": "Hello world!", "platform": "twitter"})
        for key in ("post_id", "platform", "scheduled_time", "status", "tier"):
            assert key in result

    def test_schedule_post_tier_value(self):
        bot = SocialMediaBot(tier=Tier.FREE)
        result = bot.schedule_post({"content": "Test post", "platform": "instagram"})
        assert result["tier"] == "free"

    def test_schedule_post_status(self):
        bot = SocialMediaBot(tier=Tier.PRO)
        result = bot.schedule_post({"content": "Scheduled content", "platform": "linkedin"})
        assert result["status"] in ("scheduled", "queued", "published")

    def test_post_limit_free_tier(self):
        from bots.social_media_bot.bot import SocialMediaBotRequestLimitError
        bot = SocialMediaBot(tier=Tier.FREE)
        bot._posts_this_month = 10
        with pytest.raises((SocialMediaBotTierError, SocialMediaBotRequestLimitError)):
            bot.schedule_post({"content": "Over limit", "platform": "twitter"})

    def test_analyze_engagement_returns_dict(self):
        bot = SocialMediaBot(tier=Tier.PRO)
        result = bot.analyze_engagement("ACC-001")
        assert isinstance(result, dict)
        assert "tier" in result

    def test_generate_hashtags_returns_list(self):
        bot = SocialMediaBot(tier=Tier.FREE)
        hashtags = bot.generate_hashtags("technology")
        assert isinstance(hashtags, list)
        assert len(hashtags) > 0

    def test_generate_hashtags_are_strings(self):
        bot = SocialMediaBot(tier=Tier.PRO)
        hashtags = bot.generate_hashtags("fitness")
        for tag in hashtags:
            assert isinstance(tag, str)

    def test_request_counter_increments(self):
        bot = SocialMediaBot(tier=Tier.FREE)
        bot.schedule_post({"content": "Post 1", "platform": "twitter"})
        bot.schedule_post({"content": "Post 2", "platform": "twitter"})
        assert bot._request_count == 2

    def test_request_limit_exceeded(self):
        bot = SocialMediaBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        bot._posts_this_month = 0  # Reset post count to isolate request limit
        with pytest.raises(SocialMediaBotRequestLimitError):
            bot.schedule_post({"content": "Over limit", "platform": "twitter"})

    def test_enterprise_no_request_limit(self):
        bot = SocialMediaBot(tier=Tier.ENTERPRISE)
        bot._request_count = 9999
        result = bot.schedule_post({"content": "Enterprise post", "platform": "twitter"})
        assert "post_id" in result

    def test_get_stats_buddy_integration(self):
        bot = SocialMediaBot(tier=Tier.FREE)
        stats = bot.get_stats()
        assert stats["buddy_integration"] is True

    def test_get_stats_keys(self):
        bot = SocialMediaBot(tier=Tier.PRO)
        stats = bot.get_stats()
        assert "tier" in stats
        assert "requests_used" in stats
