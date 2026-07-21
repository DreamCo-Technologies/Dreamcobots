"""Tests for bots/deal_finder_bot/tiers.py and bots/deal_finder_bot/deal_finder_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.deal_finder_bot.deal_finder_bot import DealFinderBot, DealFinderBotTierError


class TestDealFinderBotInstantiation:
    def test_default_tier_is_free(self):
        bot = DealFinderBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = DealFinderBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = DealFinderBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = DealFinderBot()
        assert bot.config is not None


class TestScanMarketplace:
    def test_returns_list(self):
        bot = DealFinderBot(tier=Tier.FREE)
        result = bot.scan_marketplace("ebay")
        assert isinstance(result, list)

    def test_free_can_scan_ebay(self):
        bot = DealFinderBot(tier=Tier.FREE)
        result = bot.scan_marketplace("ebay")
        assert len(result) > 0

    def test_free_cannot_scan_amazon(self):
        bot = DealFinderBot(tier=Tier.FREE)
        with pytest.raises(DealFinderBotTierError):
            bot.scan_marketplace("amazon")

    def test_pro_can_scan_5_platforms(self):
        bot = DealFinderBot(tier=Tier.PRO)
        for platform in ["ebay", "amazon", "craigslist", "facebook", "mercari"]:
            result = bot.scan_marketplace(platform)
            assert isinstance(result, list)

    def test_free_limited_to_10_items(self):
        bot = DealFinderBot(tier=Tier.FREE)
        result = bot.scan_marketplace("ebay")
        assert len(result) <= 10

    def test_enterprise_can_scan_all_platforms(self):
        bot = DealFinderBot(tier=Tier.ENTERPRISE)
        result = bot.scan_marketplace("offerup")
        assert isinstance(result, list)


class TestEvaluateDeal:
    def test_returns_dict(self):
        bot = DealFinderBot(tier=Tier.FREE)
        item = {"id": "t1", "title": "Test", "buy_price": 50.0, "market_value": 100.0, "condition": "Good", "platform": "ebay", "category": "electronics"}
        result = bot.evaluate_deal(item)
        assert isinstance(result, dict)

    def test_has_deal_score(self):
        bot = DealFinderBot(tier=Tier.FREE)
        item = {"id": "t1", "title": "Test", "buy_price": 50.0, "market_value": 100.0, "condition": "Good", "platform": "ebay", "category": "electronics"}
        result = bot.evaluate_deal(item)
        assert "deal_score" in result
        assert isinstance(result["deal_score"], int)

    def test_has_recommendation(self):
        bot = DealFinderBot(tier=Tier.FREE)
        item = {"id": "t1", "title": "Test", "buy_price": 20.0, "market_value": 100.0, "condition": "Good", "platform": "ebay", "category": "electronics"}
        result = bot.evaluate_deal(item)
        assert "recommendation" in result
        assert result["recommendation"] in ("Strong Buy", "Buy", "Consider", "Pass")

    def test_pro_has_profit_calculator(self):
        bot = DealFinderBot(tier=Tier.PRO)
        item = {"id": "t1", "title": "Test", "buy_price": 50.0, "market_value": 150.0, "condition": "Good", "platform": "ebay", "category": "electronics"}
        result = bot.evaluate_deal(item)
        assert "profit_calculator" in result


class TestEstimateProfit:
    def test_returns_positive_for_good_deal(self):
        bot = DealFinderBot(tier=Tier.FREE)
        item = {"buy_price": 50.0, "market_value": 100.0}
        profit = bot.estimate_profit(item)
        assert profit > 0

    def test_profit_formula(self):
        bot = DealFinderBot(tier=Tier.FREE)
        item = {"buy_price": 50.0, "market_value": 100.0}
        expected = (100.0 - 50.0) * 0.85
        assert abs(bot.estimate_profit(item) - expected) < 0.01


class TestGetBestDeals:
    def test_returns_list(self):
        bot = DealFinderBot(tier=Tier.FREE)
        bot.scan_marketplace("ebay")
        result = bot.get_best_deals(limit=3)
        assert isinstance(result, list)

    def test_sorted_by_profit_descending(self):
        bot = DealFinderBot(tier=Tier.PRO)
        bot.scan_marketplace("ebay")
        result = bot.get_best_deals(limit=5)
        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i]["estimated_profit"] >= result[i + 1]["estimated_profit"]
