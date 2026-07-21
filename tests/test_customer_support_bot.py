"""
Tests for bots/customer_support_bot/tiers.py and bots/customer_support_bot/bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.customer_support_bot.tiers import CUSTOMER_SUPPORT_FEATURES, get_customer_support_tier_info
from bots.customer_support_bot.bot import (
    CustomerSupportBot,
    CustomerSupportBotTierError,
    CustomerSupportBotRequestLimitError,
)


class TestCustomerSupportTierInfo:
    def test_free_tier_info_keys(self):
        info = get_customer_support_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "support_level", "bot_features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_customer_support_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_pro_price(self):
        info = get_customer_support_tier_info(Tier.PRO)
        assert info["price_usd_monthly"] == 49.0

    def test_enterprise_unlimited(self):
        info = get_customer_support_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_features_exist_for_all_tiers(self):
        for tier in Tier:
            assert tier.value in CUSTOMER_SUPPORT_FEATURES
            assert len(CUSTOMER_SUPPORT_FEATURES[tier.value]) > 0


class TestCustomerSupportBot:
    def test_default_tier_is_free(self):
        bot = CustomerSupportBot()
        assert bot.tier == Tier.FREE

    def test_handle_ticket_returns_expected_keys(self):
        bot = CustomerSupportBot(tier=Tier.FREE)
        result = bot.handle_ticket({"message": "I need help with billing."})
        for key in ("ticket_id", "response", "category", "sentiment", "escalated", "tier"):
            assert key in result

    def test_handle_ticket_tier_value(self):
        bot = CustomerSupportBot(tier=Tier.FREE)
        result = bot.handle_ticket({"message": "Help!"})
        assert result["tier"] == "free"

    def test_handle_ticket_with_id(self):
        bot = CustomerSupportBot(tier=Tier.FREE)
        result = bot.handle_ticket({"id": "TKT-001", "message": "Test"})
        assert result["ticket_id"] == "TKT-001"

    def test_handle_ticket_category_defaults_general(self):
        bot = CustomerSupportBot(tier=Tier.FREE)
        result = bot.handle_ticket({"message": "Random question"})
        assert result["category"] in ("general", "billing", "technical")

    def test_free_tier_invalid_category_redirected(self):
        bot = CustomerSupportBot(tier=Tier.FREE)
        result = bot.handle_ticket({"message": "Enterprise analytics?", "category": "analytics"})
        assert result["category"] == "general"

    def test_pro_tier_sentiment_analysis(self):
        bot = CustomerSupportBot(tier=Tier.PRO)
        result = bot.handle_ticket({"message": "I am angry and frustrated with your terrible service!"})
        assert result["sentiment"] == "negative"

    def test_pro_tier_positive_sentiment(self):
        bot = CustomerSupportBot(tier=Tier.PRO)
        result = bot.handle_ticket({"message": "I love this service, it's amazing!"})
        assert result["sentiment"] == "positive"

    def test_enterprise_tier_escalation_on_negative(self):
        bot = CustomerSupportBot(tier=Tier.ENTERPRISE)
        result = bot.handle_ticket({"message": "This is terrible and broken!"})
        assert result["escalated"] is True

    def test_request_counter_increments(self):
        bot = CustomerSupportBot(tier=Tier.FREE)
        bot.handle_ticket({"message": "Question 1"})
        bot.handle_ticket({"message": "Question 2"})
        assert bot._request_count == 2

    def test_request_limit_exceeded(self):
        bot = CustomerSupportBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(CustomerSupportBotRequestLimitError):
            bot.handle_ticket({"message": "Over limit"})

    def test_enterprise_no_request_limit(self):
        bot = CustomerSupportBot(tier=Tier.ENTERPRISE)
        bot._request_count = 9999
        result = bot.handle_ticket({"message": "Still working"})
        assert "ticket_id" in result

    def test_escalate_free_tier_raises(self):
        bot = CustomerSupportBot(tier=Tier.FREE)
        with pytest.raises(CustomerSupportBotTierError):
            bot.escalate("TKT-001")

    def test_escalate_pro_tier(self):
        bot = CustomerSupportBot(tier=Tier.PRO)
        result = bot.escalate("TKT-001")
        assert result["escalated"] is True
        assert result["ticket_id"] == "TKT-001"

    def test_escalate_enterprise_tier(self):
        bot = CustomerSupportBot(tier=Tier.ENTERPRISE)
        result = bot.escalate("TKT-002")
        assert result["escalated"] is True

    def test_get_stats_buddy_integration(self):
        bot = CustomerSupportBot(tier=Tier.FREE)
        stats = bot.get_stats()
        assert stats["buddy_integration"] is True

    def test_get_stats_keys(self):
        bot = CustomerSupportBot(tier=Tier.PRO)
        stats = bot.get_stats()
        assert "tier" in stats
        assert "requests_used" in stats
        assert "requests_remaining" in stats
