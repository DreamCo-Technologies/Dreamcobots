"""
Tests for bots/shopify_automation_bot/tiers.py and bots/shopify_automation_bot/bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.shopify_automation_bot.tiers import SHOPIFY_AUTOMATION_FEATURES, get_shopify_automation_tier_info
from bots.shopify_automation_bot.bot import (
    ShopifyAutomationBot,
    ShopifyAutomationBotTierError,
    ShopifyAutomationBotRequestLimitError,
)


class TestShopifyAutomationTierInfo:
    def test_free_tier_info_keys(self):
        info = get_shopify_automation_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "support_level", "bot_features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_shopify_automation_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        info = get_shopify_automation_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_features_exist_for_all_tiers(self):
        for tier in Tier:
            assert tier.value in SHOPIFY_AUTOMATION_FEATURES
            assert len(SHOPIFY_AUTOMATION_FEATURES[tier.value]) > 0


class TestShopifyAutomationBot:
    def test_default_tier_is_free(self):
        bot = ShopifyAutomationBot()
        assert bot.tier == Tier.FREE

    def test_process_order_returns_expected_keys(self):
        bot = ShopifyAutomationBot(tier=Tier.FREE)
        order = {"order_id": "ORD-001", "items": [{"sku": "ITEM1", "qty": 2}], "customer": {"email": "c@example.com"}}
        result = bot.process_order(order)
        for key in ("order_id", "status", "automated_actions", "tier"):
            assert key in result

    def test_process_order_tier_value(self):
        bot = ShopifyAutomationBot(tier=Tier.FREE)
        result = bot.process_order({"order_id": "ORD-001", "items": [], "customer": {}})
        assert result["tier"] == "free"

    def test_process_order_automated_actions_is_list(self):
        bot = ShopifyAutomationBot(tier=Tier.PRO)
        result = bot.process_order({"order_id": "ORD-002", "items": [], "customer": {}})
        assert isinstance(result["automated_actions"], list)

    def test_sync_inventory_returns_dict(self):
        bot = ShopifyAutomationBot(tier=Tier.FREE)
        result = bot.sync_inventory("STORE-001")
        assert isinstance(result, dict)
        assert "tier" in result

    def test_automate_workflow_free_tier_raises(self):
        bot = ShopifyAutomationBot(tier=Tier.FREE)
        with pytest.raises(ShopifyAutomationBotTierError):
            bot.automate_workflow({"type": "abandoned_cart", "trigger": "cart_abandoned"})

    def test_automate_workflow_pro_tier(self):
        bot = ShopifyAutomationBot(tier=Tier.PRO)
        result = bot.automate_workflow({"type": "abandoned_cart", "trigger": "cart_abandoned"})
        assert "tier" in result

    def test_request_counter_increments(self):
        bot = ShopifyAutomationBot(tier=Tier.FREE)
        bot.process_order({"order_id": "ORD-1", "items": [], "customer": {}})
        bot.process_order({"order_id": "ORD-2", "items": [], "customer": {}})
        assert bot._request_count == 2

    def test_request_limit_exceeded(self):
        bot = ShopifyAutomationBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(ShopifyAutomationBotRequestLimitError):
            bot.process_order({"order_id": "ORD-OVER", "items": [], "customer": {}})

    def test_enterprise_no_request_limit(self):
        bot = ShopifyAutomationBot(tier=Tier.ENTERPRISE)
        bot._request_count = 9999
        result = bot.process_order({"order_id": "ORD-ENT", "items": [], "customer": {}})
        assert "order_id" in result

    def test_get_stats_buddy_integration(self):
        bot = ShopifyAutomationBot(tier=Tier.FREE)
        stats = bot.get_stats()
        assert stats["buddy_integration"] is True

    def test_get_stats_keys(self):
        bot = ShopifyAutomationBot(tier=Tier.PRO)
        stats = bot.get_stats()
        assert "tier" in stats
        assert "requests_used" in stats
