"""
Tests for bots/creator_economy/tiers.py and
bots/creator_economy/creator_economy_bot.py
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
from bots.creator_economy.tiers import (
    get_ce_tier_info,
    CE_EXTRA_FEATURES,
    CE_TOOLS,
)
from bots.creator_economy.creator_economy_bot import (
    CreatorEconomyBot,
    CreatorEconomyTierError,
    CreatorEconomyRequestLimitError,
)


class TestCETierInfo:
    def test_tier_info_keys(self):
        info = get_ce_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "platform_features", "ce_features", "tools", "support_level"):
            assert key in info

    def test_free_price_is_zero(self):
        assert get_ce_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        assert get_ce_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_pro_has_more_tools_than_free(self):
        free = get_ce_tier_info(Tier.FREE)
        pro = get_ce_tier_info(Tier.PRO)
        assert len(pro["tools"]) > len(free["tools"])

    def test_free_tools_subset_of_pro(self):
        free_tools = set(CE_TOOLS[Tier.FREE.value])
        pro_tools = set(CE_TOOLS[Tier.PRO.value])
        assert free_tools.issubset(pro_tools)

    def test_features_populated(self):
        for tier in Tier:
            assert len(CE_EXTRA_FEATURES[tier.value]) > 0

    def test_free_has_content_ideas(self):
        assert "content_ideas" in CE_TOOLS[Tier.FREE.value]

    def test_pro_has_brand_pitch_generator(self):
        assert "brand_pitch_generator" in CE_TOOLS[Tier.PRO.value]

    def test_enterprise_has_ip_protection(self):
        assert "ip_protection" in CE_TOOLS[Tier.ENTERPRISE.value]


class TestCreatorEconomyBot:
    def test_default_tier_is_free(self):
        bot = CreatorEconomyBot()
        assert bot.tier == Tier.FREE

    def test_chat_returns_dict(self):
        bot = CreatorEconomyBot(tier=Tier.FREE)
        result = bot.chat("Give me content ideas for my channel")
        assert isinstance(result, dict)

    def test_chat_result_keys(self):
        bot = CreatorEconomyBot(tier=Tier.FREE)
        result = bot.chat("Content ideas")
        for key in ("message", "tool", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_free_cannot_use_brand_pitch(self):
        bot = CreatorEconomyBot(tier=Tier.FREE)
        with pytest.raises(CreatorEconomyTierError):
            bot.chat("Generate pitch", tool="brand_pitch_generator")

    def test_pro_can_use_brand_pitch(self):
        bot = CreatorEconomyBot(tier=Tier.PRO)
        result = bot.chat("Generate pitch", tool="brand_pitch_generator")
        assert result["tool"] == "brand_pitch_generator"

    def test_enterprise_can_use_ip_protection(self):
        bot = CreatorEconomyBot(tier=Tier.ENTERPRISE)
        result = bot.chat("Protect IP", tool="ip_protection")
        assert result["tool"] == "ip_protection"

    def test_generate_pitch_returns_dict(self):
        bot = CreatorEconomyBot(tier=Tier.PRO)
        result = bot.generate_pitch("Nike", "YouTube")
        assert result["brand"] == "Nike"
        assert result["platform"] == "YouTube"
        assert "pitch" in result

    def test_generate_pitch_tier_error_on_free(self):
        bot = CreatorEconomyBot(tier=Tier.FREE)
        with pytest.raises(CreatorEconomyTierError):
            bot.generate_pitch("Nike", "YouTube")

    def test_list_tools_returns_list(self):
        bot = CreatorEconomyBot(tier=Tier.FREE)
        tools = bot.list_tools()
        assert isinstance(tools, list) and len(tools) > 0

    def test_request_limit_raises(self):
        bot = CreatorEconomyBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(CreatorEconomyRequestLimitError):
            bot.chat("another request")

    def test_enterprise_no_request_limit(self):
        bot = CreatorEconomyBot(tier=Tier.ENTERPRISE)
        bot._request_count = 10_000_000
        result = bot.chat("unlimited")
        assert result["requests_remaining"] is None

    def test_history_grows(self):
        bot = CreatorEconomyBot()
        bot.chat("idea 1")
        bot.chat("idea 2")
        assert len(bot.get_history()) == 4

    def test_clear_history(self):
        bot = CreatorEconomyBot()
        bot.chat("idea")
        bot.clear_history()
        assert bot.get_history() == []

    def test_describe_tier_contains_creator(self):
        bot = CreatorEconomyBot(tier=Tier.FREE)
        desc = bot.describe_tier()
        assert "Creator" in desc

    def test_show_upgrade_path_free(self):
        bot = CreatorEconomyBot(tier=Tier.FREE)
        msg = bot.show_upgrade_path()
        assert "Pro" in msg or "Upgrade" in msg

    def test_show_upgrade_path_enterprise(self):
        bot = CreatorEconomyBot(tier=Tier.ENTERPRISE)
        msg = bot.show_upgrade_path()
        assert "highest tier" in msg

    def test_default_tool_content_keyword(self):
        bot = CreatorEconomyBot(tier=Tier.FREE)
        result = bot.chat("Give me some content ideas")
        assert result["tool"] == "content_ideas"

    def test_default_tool_hashtag(self):
        bot = CreatorEconomyBot(tier=Tier.FREE)
        result = bot.chat("Suggest hashtags for my post")
        assert result["tool"] == "hashtag_generator"

    def test_tier_in_response(self):
        bot = CreatorEconomyBot(tier=Tier.PRO)
        result = bot.chat("content ideas")
        assert result["tier"] == "pro"
