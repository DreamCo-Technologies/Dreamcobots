"""
Tests for bots/coding_assistant_bot/tiers.py and bots/coding_assistant_bot/bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.coding_assistant_bot.tiers import CODING_ASSISTANT_FEATURES, get_coding_assistant_tier_info
from bots.coding_assistant_bot.bot import (
    CodingAssistantBot,
    CodingAssistantBotTierError,
    CodingAssistantBotRequestLimitError,
)


class TestCodingAssistantTierInfo:
    def test_free_tier_info_keys(self):
        info = get_coding_assistant_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "support_level", "bot_features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_coding_assistant_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        info = get_coding_assistant_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_features_exist_for_all_tiers(self):
        for tier in Tier:
            assert tier.value in CODING_ASSISTANT_FEATURES
            assert len(CODING_ASSISTANT_FEATURES[tier.value]) > 0


class TestCodingAssistantBot:
    def test_default_tier_is_free(self):
        bot = CodingAssistantBot()
        assert bot.tier == Tier.FREE

    def test_complete_code_returns_expected_keys(self):
        bot = CodingAssistantBot(tier=Tier.FREE)
        result = bot.complete_code({"code": "def add(a, b):", "language": "python"})
        for key in ("completion", "language", "suggestions", "tier"):
            assert key in result

    def test_complete_code_tier_value(self):
        bot = CodingAssistantBot(tier=Tier.FREE)
        result = bot.complete_code({"code": "function hello() {", "language": "javascript"})
        assert result["tier"] == "free"

    def test_complete_code_completion_is_string(self):
        bot = CodingAssistantBot(tier=Tier.PRO)
        result = bot.complete_code({"code": "def sort_list(lst):", "language": "python"})
        assert isinstance(result["completion"], str)

    def test_complete_code_suggestions_is_list(self):
        bot = CodingAssistantBot(tier=Tier.FREE)
        result = bot.complete_code({"code": "class MyClass:", "language": "python"})
        assert isinstance(result["suggestions"], list)

    def test_unsupported_language_free_raises(self):
        bot = CodingAssistantBot(tier=Tier.FREE)
        with pytest.raises(CodingAssistantBotTierError):
            bot.complete_code({"code": "fn main() {}", "language": "rust"})

    def test_pro_supports_more_languages(self):
        bot = CodingAssistantBot(tier=Tier.PRO)
        result = bot.complete_code({"code": "fn main() {}", "language": "rust"})
        assert "completion" in result

    def test_review_code_returns_dict(self):
        bot = CodingAssistantBot(tier=Tier.FREE)
        result = bot.review_code("def add(a, b):\n    return a + b", "python")
        assert isinstance(result, dict)
        assert "tier" in result

    def test_generate_tests_free_raises(self):
        bot = CodingAssistantBot(tier=Tier.FREE)
        with pytest.raises(CodingAssistantBotTierError):
            bot.generate_tests("def add(a, b):\n    return a + b", "python")

    def test_generate_tests_pro_tier(self):
        bot = CodingAssistantBot(tier=Tier.PRO)
        result = bot.generate_tests("def multiply(a, b):\n    return a * b", "python")
        assert "tier" in result
        assert "tests" in result or "test_code" in result or "content" in result

    def test_request_counter_increments(self):
        bot = CodingAssistantBot(tier=Tier.FREE)
        bot.complete_code({"code": "x = 1", "language": "python"})
        bot.complete_code({"code": "y = 2", "language": "python"})
        assert bot._request_count == 2

    def test_request_limit_exceeded(self):
        bot = CodingAssistantBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(CodingAssistantBotRequestLimitError):
            bot.complete_code({"code": "z = 3", "language": "python"})

    def test_enterprise_no_request_limit(self):
        bot = CodingAssistantBot(tier=Tier.ENTERPRISE)
        bot._request_count = 9999
        result = bot.complete_code({"code": "a = 1", "language": "python"})
        assert "completion" in result

    def test_get_stats_buddy_integration(self):
        bot = CodingAssistantBot(tier=Tier.FREE)
        stats = bot.get_stats()
        assert stats["buddy_integration"] is True

    def test_get_stats_keys(self):
        bot = CodingAssistantBot(tier=Tier.PRO)
        stats = bot.get_stats()
        assert "tier" in stats
        assert "requests_used" in stats
