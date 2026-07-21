"""
Tests for bots/stock_trading_bot/tiers.py and bots/stock_trading_bot/bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.stock_trading_bot.tiers import STOCK_TRADING_FEATURES, get_stock_trading_tier_info
from bots.stock_trading_bot.bot import (
    StockTradingBot,
    StockTradingBotTierError,
    StockTradingBotRequestLimitError,
)


class TestStockTradingTierInfo:
    def test_free_tier_info_keys(self):
        info = get_stock_trading_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "support_level", "bot_features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_stock_trading_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        info = get_stock_trading_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_features_exist_for_all_tiers(self):
        for tier in Tier:
            assert tier.value in STOCK_TRADING_FEATURES
            assert len(STOCK_TRADING_FEATURES[tier.value]) > 0


class TestStockTradingBot:
    def test_default_tier_is_free(self):
        bot = StockTradingBot()
        assert bot.tier == Tier.FREE

    def test_analyze_stock_returns_expected_keys(self):
        bot = StockTradingBot(tier=Tier.FREE)
        result = bot.analyze_stock("AAPL")
        for key in ("ticker", "signal", "confidence", "indicators", "tier"):
            assert key in result

    def test_analyze_stock_tier_value(self):
        bot = StockTradingBot(tier=Tier.FREE)
        result = bot.analyze_stock("MSFT")
        assert result["tier"] == "free"

    def test_analyze_stock_signal_is_valid(self):
        bot = StockTradingBot(tier=Tier.FREE)
        result = bot.analyze_stock("GOOG")
        assert result["signal"].upper() in ("BUY", "SELL", "HOLD")

    def test_analyze_stock_confidence_in_range(self):
        bot = StockTradingBot(tier=Tier.PRO)
        result = bot.analyze_stock("TSLA")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_watchlist_limit_free_tier(self):
        bot = StockTradingBot(tier=Tier.FREE)
        tickers = ["AAPL", "MSFT", "GOOG", "TSLA", "AMZN"]
        for t in tickers:
            bot.analyze_stock(t)
        with pytest.raises(StockTradingBotTierError):
            bot.analyze_stock("META")

    def test_pro_tier_larger_watchlist(self):
        bot = StockTradingBot(tier=Tier.PRO)
        for i in range(10):
            bot.analyze_stock(f"TICK{i}")
        result = bot.analyze_stock("EXTRA")
        assert "ticker" in result

    def test_get_signals_returns_dict(self):
        bot = StockTradingBot(tier=Tier.PRO)
        result = bot.get_signals("AAPL")
        assert isinstance(result, dict)
        assert "tier" in result

    def test_backtest_free_tier_raises(self):
        bot = StockTradingBot(tier=Tier.FREE)
        with pytest.raises(StockTradingBotTierError):
            bot.backtest({"strategy": "moving_average", "ticker": "AAPL"})

    def test_backtest_pro_tier(self):
        bot = StockTradingBot(tier=Tier.PRO)
        result = bot.backtest({"strategy": "moving_average", "ticker": "AAPL"})
        assert "tier" in result

    def test_request_counter_increments(self):
        bot = StockTradingBot(tier=Tier.FREE)
        bot.analyze_stock("AAPL")
        bot.analyze_stock("MSFT")
        assert bot._request_count == 2

    def test_request_limit_exceeded(self):
        bot = StockTradingBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        # Reset watchlist to avoid watchlist limit
        bot._watchlist = set()
        with pytest.raises(StockTradingBotRequestLimitError):
            bot.analyze_stock("AAPL")

    def test_enterprise_no_request_limit(self):
        bot = StockTradingBot(tier=Tier.ENTERPRISE)
        bot._request_count = 9999
        result = bot.analyze_stock("AAPL")
        assert "ticker" in result

    def test_get_stats_buddy_integration(self):
        bot = StockTradingBot(tier=Tier.FREE)
        stats = bot.get_stats()
        assert stats["buddy_integration"] is True

    def test_get_stats_keys(self):
        bot = StockTradingBot(tier=Tier.PRO)
        stats = bot.get_stats()
        assert "tier" in stats
        assert "requests_used" in stats
