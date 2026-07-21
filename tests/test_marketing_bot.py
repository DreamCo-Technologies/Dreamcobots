"""
Tests for bots/marketing_bot/tiers.py and bots/marketing_bot/marketing_bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.marketing_bot.tiers import (
    get_marketing_tier_info,
    MARKETING_EXTRA_FEATURES,
    MARKETING_CHANNELS,
)
from bots.marketing_bot.marketing_bot import (
    MarketingBot,
    MarketingTierError,
    MarketingRequestLimitError,
)


class TestMarketingTierInfo:
    def test_tier_info_keys(self):
        info = get_marketing_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "platform_features", "marketing_features", "channels", "support_level"):
            assert key in info

    def test_free_price_is_zero(self):
        assert get_marketing_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        assert get_marketing_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_pro_has_more_channels_than_free(self):
        free = get_marketing_tier_info(Tier.FREE)
        pro = get_marketing_tier_info(Tier.PRO)
        assert len(pro["channels"]) > len(free["channels"])

    def test_free_channels_subset_of_pro(self):
        free_ch = set(MARKETING_CHANNELS[Tier.FREE.value])
        pro_ch = set(MARKETING_CHANNELS[Tier.PRO.value])
        assert free_ch.issubset(pro_ch)

    def test_features_populated(self):
        for tier in Tier:
            assert len(MARKETING_EXTRA_FEATURES[tier.value]) > 0

    def test_free_has_social_media(self):
        assert "social_media" in MARKETING_CHANNELS[Tier.FREE.value]

    def test_pro_has_paid_ads(self):
        assert "paid_ads" in MARKETING_CHANNELS[Tier.PRO.value]

    def test_enterprise_has_influencer(self):
        assert "influencer" in MARKETING_CHANNELS[Tier.ENTERPRISE.value]


class TestMarketingBot:
    def test_default_tier_is_free(self):
        bot = MarketingBot()
        assert bot.tier == Tier.FREE

    def test_chat_returns_dict(self):
        bot = MarketingBot(tier=Tier.FREE)
        result = bot.chat("Create a social media post")
        assert isinstance(result, dict)

    def test_chat_result_keys(self):
        bot = MarketingBot(tier=Tier.FREE)
        result = bot.chat("Create a social media post")
        for key in ("message", "channel", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_free_cannot_use_paid_ads(self):
        bot = MarketingBot(tier=Tier.FREE)
        with pytest.raises(MarketingTierError):
            bot.chat("Run a PPC campaign", channel="paid_ads")

    def test_pro_can_use_paid_ads(self):
        bot = MarketingBot(tier=Tier.PRO)
        result = bot.chat("Run a Google Ads campaign", channel="paid_ads")
        assert result["channel"] == "paid_ads"

    def test_enterprise_can_use_influencer(self):
        bot = MarketingBot(tier=Tier.ENTERPRISE)
        result = bot.chat("Find influencers", channel="influencer")
        assert result["channel"] == "influencer"

    def test_create_campaign_returns_dict(self):
        bot = MarketingBot(tier=Tier.FREE)
        result = bot.create_campaign("social_media", "Product launch campaign")
        assert result["status"] == "drafted"
        assert result["channel"] == "social_media"

    def test_create_campaign_tier_error(self):
        bot = MarketingBot(tier=Tier.FREE)
        with pytest.raises(MarketingTierError):
            bot.create_campaign("paid_ads", "PPC campaign")

    def test_list_channels_returns_list(self):
        bot = MarketingBot(tier=Tier.FREE)
        channels = bot.list_channels()
        assert isinstance(channels, list) and len(channels) > 0

    def test_request_limit_raises(self):
        bot = MarketingBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(MarketingRequestLimitError):
            bot.chat("another request")

    def test_enterprise_no_request_limit(self):
        bot = MarketingBot(tier=Tier.ENTERPRISE)
        bot._request_count = 10_000_000
        result = bot.chat("unlimited request")
        assert result["requests_remaining"] is None

    def test_history_grows(self):
        bot = MarketingBot()
        bot.chat("msg1")
        bot.chat("msg2")
        assert len(bot.get_history()) == 4

    def test_clear_history(self):
        bot = MarketingBot()
        bot.chat("msg")
        bot.clear_history()
        assert bot.get_history() == []

    def test_describe_tier_contains_marketing(self):
        bot = MarketingBot(tier=Tier.FREE)
        desc = bot.describe_tier()
        assert "Marketing" in desc

    def test_show_upgrade_path_free(self):
        bot = MarketingBot(tier=Tier.FREE)
        msg = bot.show_upgrade_path()
        assert "Pro" in msg or "Upgrade" in msg

    def test_show_upgrade_path_enterprise(self):
        bot = MarketingBot(tier=Tier.ENTERPRISE)
        msg = bot.show_upgrade_path()
        assert "highest tier" in msg

    def test_default_channel_social_keyword(self):
        bot = MarketingBot(tier=Tier.FREE)
        result = bot.chat("Post on Instagram about my product")
        assert result["channel"] == "social_media"

    def test_default_channel_email(self):
        bot = MarketingBot(tier=Tier.FREE)
        result = bot.chat("Write a newsletter email")
        assert result["channel"] == "email_marketing"

    def test_default_channel_seo(self):
        bot = MarketingBot(tier=Tier.FREE)
        result = bot.chat("Improve my SEO ranking")
        assert result["channel"] == "seo"
