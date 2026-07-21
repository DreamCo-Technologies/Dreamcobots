"""
Tests for bots/ai_writing_bot/tiers.py and bots/ai_writing_bot/bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.ai_writing_bot.tiers import AI_WRITING_FEATURES, get_ai_writing_tier_info
from bots.ai_writing_bot.bot import (
    AIWritingBot,
    AIWritingBotTierError,
    AIWritingBotRequestLimitError,
)


class TestAIWritingTierInfo:
    def test_free_tier_info_keys(self):
        info = get_ai_writing_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "support_level", "bot_features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_ai_writing_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        info = get_ai_writing_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_features_exist_for_all_tiers(self):
        for tier in Tier:
            assert tier.value in AI_WRITING_FEATURES
            assert len(AI_WRITING_FEATURES[tier.value]) > 0


class TestAIWritingBot:
    def test_default_tier_is_free(self):
        bot = AIWritingBot()
        assert bot.tier == Tier.FREE

    def test_generate_content_returns_expected_keys(self):
        bot = AIWritingBot(tier=Tier.FREE)
        result = bot.generate_content({"topic": "Python tips", "type": "blog post"})
        for key in ("content", "word_count", "seo_score", "tier"):
            assert key in result

    def test_generate_content_tier_value(self):
        bot = AIWritingBot(tier=Tier.FREE)
        result = bot.generate_content({"topic": "AI", "type": "article"})
        assert result["tier"] == "free"

    def test_generate_content_has_content(self):
        bot = AIWritingBot(tier=Tier.PRO)
        result = bot.generate_content({"topic": "Marketing", "type": "email"})
        assert isinstance(result["content"], str)
        assert len(result["content"]) > 0

    def test_generate_content_word_count_positive(self):
        bot = AIWritingBot(tier=Tier.FREE)
        result = bot.generate_content({"topic": "Test", "type": "blog post"})
        assert result["word_count"] > 0

    def test_seo_score_in_range(self):
        bot = AIWritingBot(tier=Tier.PRO)
        result = bot.generate_content({"topic": "SEO content", "type": "article"})
        assert 0.0 <= result["seo_score"] <= 1.0

    def test_optimize_seo_returns_dict(self):
        bot = AIWritingBot(tier=Tier.PRO)
        result = bot.optimize_seo("This is sample content about Python programming.")
        assert isinstance(result, dict)
        assert "tier" in result

    def test_get_templates_returns_list(self):
        bot = AIWritingBot(tier=Tier.FREE)
        templates = bot.get_templates()
        assert isinstance(templates, list)
        assert len(templates) > 0

    def test_pro_has_more_templates_than_free(self):
        free_bot = AIWritingBot(tier=Tier.FREE)
        pro_bot = AIWritingBot(tier=Tier.PRO)
        assert len(pro_bot.get_templates()) >= len(free_bot.get_templates())

    def test_request_counter_increments(self):
        bot = AIWritingBot(tier=Tier.FREE)
        bot.generate_content({"topic": "Topic 1", "type": "blog post"})
        bot.generate_content({"topic": "Topic 2", "type": "article"})
        assert bot._request_count == 2

    def test_request_limit_exceeded(self):
        bot = AIWritingBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(AIWritingBotRequestLimitError):
            bot.generate_content({"topic": "Over limit", "type": "blog post"})

    def test_enterprise_no_request_limit(self):
        bot = AIWritingBot(tier=Tier.ENTERPRISE)
        bot._request_count = 9999
        result = bot.generate_content({"topic": "Enterprise", "type": "report"})
        assert "content" in result

    def test_get_stats_buddy_integration(self):
        bot = AIWritingBot(tier=Tier.FREE)
        stats = bot.get_stats()
        assert stats["buddy_integration"] is True

    def test_get_stats_keys(self):
        bot = AIWritingBot(tier=Tier.PRO)
        stats = bot.get_stats()
        assert "tier" in stats
        assert "requests_used" in stats
        assert "requests_remaining" in stats
