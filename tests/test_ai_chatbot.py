"""
Tests for bots/ai_chatbot/tiers.py and bots/ai_chatbot/chatbot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

# Clear cached 'tiers' module to prevent cross-test sys.modules pollution
sys.modules.pop('tiers', None)

import pytest
from tiers import Tier, NLP_GPT35, NLP_GPT4, NLP_BERT_BASE, NLP_BERT_LARGE
from bots.ai_chatbot.tiers import (
    get_chatbot_tier_info,
    CHATBOT_EXTRA_FEATURES,
    CHATBOT_MODELS,
)
from bots.ai_chatbot.chatbot import Chatbot, ChatbotTierError, ChatbotRequestLimitError


# -----------------------------------------------------------------------
# Chatbot tier info tests
# -----------------------------------------------------------------------

class TestChatbotTierInfo:
    def test_free_tier_info_keys(self):
        info = get_chatbot_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "platform_features", "chatbot_features", "available_models",
                    "support_level"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_chatbot_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_pro_price(self):
        info = get_chatbot_tier_info(Tier.PRO)
        assert info["price_usd_monthly"] == 49.0

    def test_enterprise_unlimited(self):
        info = get_chatbot_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_free_has_fewer_models_than_pro(self):
        free_info = get_chatbot_tier_info(Tier.FREE)
        pro_info = get_chatbot_tier_info(Tier.PRO)
        assert len(pro_info["available_models"]) > len(free_info["available_models"])

    def test_pro_includes_gpt4(self):
        pro_info = get_chatbot_tier_info(Tier.PRO)
        assert NLP_GPT4 in pro_info["available_models"]

    def test_free_does_not_include_gpt4(self):
        free_info = get_chatbot_tier_info(Tier.FREE)
        assert NLP_GPT4 not in free_info["available_models"]

    def test_chatbot_extra_features_populated(self):
        for tier in Tier:
            extras = CHATBOT_EXTRA_FEATURES[tier.value]
            assert isinstance(extras, list)
            assert len(extras) > 0

    def test_pro_has_markdown_feature(self):
        extras = CHATBOT_EXTRA_FEATURES[Tier.PRO.value]
        assert any("Markdown" in feat for feat in extras)

    def test_enterprise_has_audit_logging(self):
        extras = CHATBOT_EXTRA_FEATURES[Tier.ENTERPRISE.value]
        assert any("Audit" in feat for feat in extras)

    def test_free_has_history_limit_note(self):
        extras = CHATBOT_EXTRA_FEATURES[Tier.FREE.value]
        assert any("history" in feat.lower() for feat in extras)


# -----------------------------------------------------------------------
# Chatbot class tests
# -----------------------------------------------------------------------

class TestChatbot:
    def test_free_chatbot_default_model(self):
        bot = Chatbot(tier=Tier.FREE)
        assert bot.default_model == CHATBOT_MODELS[Tier.FREE.value][0]

    def test_chat_returns_dict(self):
        bot = Chatbot(tier=Tier.FREE)
        result = bot.chat("Hello!")
        assert isinstance(result, dict)

    def test_chat_result_keys(self):
        bot = Chatbot(tier=Tier.FREE)
        result = bot.chat("What is AI?")
        for key in ("message", "model", "tier", "history_turns",
                    "requests_used", "requests_remaining"):
            assert key in result

    def test_chat_increments_request_count(self):
        bot = Chatbot(tier=Tier.FREE)
        bot.chat("a")
        bot.chat("b")
        assert bot._request_count == 2

    def test_chat_free_with_free_model_ok(self):
        bot = Chatbot(tier=Tier.FREE)
        result = bot.chat("test", model=NLP_GPT35)
        assert result["model"] == NLP_GPT35

    def test_chat_free_with_pro_model_raises(self):
        bot = Chatbot(tier=Tier.FREE)
        with pytest.raises(ChatbotTierError):
            bot.chat("test", model=NLP_GPT4)

    def test_chat_pro_with_gpt4_ok(self):
        bot = Chatbot(tier=Tier.PRO)
        result = bot.chat("test", model=NLP_GPT4)
        assert result["model"] == NLP_GPT4

    def test_request_limit_raises(self):
        bot = Chatbot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(ChatbotRequestLimitError):
            bot.chat("over limit")

    def test_enterprise_no_request_limit(self):
        bot = Chatbot(tier=Tier.ENTERPRISE)
        bot._request_count = 999_999
        result = bot.chat("still works")
        assert result["requests_remaining"] == "unlimited"

    def test_history_appended(self):
        bot = Chatbot(tier=Tier.FREE)
        bot.chat("Hello")
        history = bot.get_history()
        assert len(history) == 2  # user + assistant
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_history_trimmed_on_free_tier(self):
        bot = Chatbot(tier=Tier.FREE)
        # 5 turns max = 10 history entries; send 6 turns
        for i in range(6):
            bot.chat(f"Message {i}")
        history = bot.get_history()
        assert len(history) <= 10

    def test_history_not_trimmed_on_enterprise(self):
        bot = Chatbot(tier=Tier.ENTERPRISE)
        for i in range(20):
            bot.chat(f"Message {i}")
        history = bot.get_history()
        assert len(history) == 40  # 20 turns * 2

    def test_clear_history(self):
        bot = Chatbot(tier=Tier.FREE)
        bot.chat("Hello")
        bot.clear_history()
        assert bot.get_history() == []

    def test_get_history_returns_copy(self):
        bot = Chatbot(tier=Tier.FREE)
        bot.chat("Hello")
        h1 = bot.get_history()
        h1.append({"role": "intruder", "content": "injected"})
        assert len(bot.get_history()) == 2  # original unchanged

    def test_invalid_default_model_raises(self):
        with pytest.raises(ChatbotTierError):
            Chatbot(tier=Tier.FREE, default_model=NLP_GPT4)

    def test_valid_default_model_accepted(self):
        bot = Chatbot(tier=Tier.PRO, default_model=NLP_GPT4)
        assert bot.default_model == NLP_GPT4

    def test_describe_tier_returns_string(self):
        bot = Chatbot(tier=Tier.FREE)
        output = bot.describe_tier()
        assert "Free" in output
        assert "$0.00" in output

    def test_show_upgrade_path_from_free(self):
        bot = Chatbot(tier=Tier.FREE)
        output = bot.show_upgrade_path()
        assert "Pro" in output

    def test_show_upgrade_path_enterprise_no_upgrade(self):
        bot = Chatbot(tier=Tier.ENTERPRISE)
        output = bot.show_upgrade_path()
        assert "top-tier" in output

    def test_tier_attribute_matches_input(self):
        for tier in Tier:
            bot = Chatbot(tier=tier)
            assert bot.tier == tier

    def test_pro_has_bert_large(self):
        bot = Chatbot(tier=Tier.PRO)
        result = bot.chat("NLP test", model=NLP_BERT_LARGE)
        assert result["model"] == NLP_BERT_LARGE

    def test_free_cannot_use_bert_large(self):
        bot = Chatbot(tier=Tier.FREE)
        with pytest.raises(ChatbotTierError):
            bot.chat("NLP test", model=NLP_BERT_LARGE)
