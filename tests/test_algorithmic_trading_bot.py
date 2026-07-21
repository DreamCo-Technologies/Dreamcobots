import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)

TOOL_DIR = os.path.join(REPO_ROOT, 'analytics-elites', 'algorithmic_trading_bot')
sys.path.insert(0, TOOL_DIR)

import pytest
from algorithmic_trading_bot import AlgorithmicTradingBot

# 30 prices: generally trending upward then reversing
PRICES_UP = [100 + i * 0.5 for i in range(30)]
PRICES_DOWN = [130 - i * 0.5 for i in range(30)]
PRICES_FLAT = [100.0] * 30


class TestAlgorithmicTradingBotInstantiation:
    def test_default_tier_is_free(self):
        bot = AlgorithmicTradingBot()
        assert bot.tier == "free"

    def test_pro_tier(self):
        bot = AlgorithmicTradingBot(tier="pro")
        assert bot.tier == "pro"


class TestMovingAverageSignal:
    def test_returns_dict(self):
        bot = AlgorithmicTradingBot(tier="pro")
        result = bot.moving_average_signal("AAPL", PRICES_UP, short=5, long=10)
        assert isinstance(result, dict)

    def test_signal_in_valid_values(self):
        bot = AlgorithmicTradingBot(tier="pro")
        result = bot.moving_average_signal("AAPL", PRICES_UP, short=5, long=10)
        assert result["signal"] in ("buy", "sell", "hold", "insufficient_data")

    def test_disclaimer_present(self):
        bot = AlgorithmicTradingBot(tier="pro")
        result = bot.moving_average_signal("AAPL", PRICES_UP)
        assert "disclaimer" in result

    def test_free_tier_symbol_limit(self):
        bot = AlgorithmicTradingBot(tier="free")
        for sym in ["A", "B", "C"]:
            bot.moving_average_signal(sym, PRICES_UP, short=5, long=10)
        with pytest.raises(PermissionError):
            bot.moving_average_signal("D", PRICES_UP, short=5, long=10)

    def test_insufficient_data(self):
        bot = AlgorithmicTradingBot(tier="pro")
        result = bot.moving_average_signal("AAPL", [100, 101, 102], short=5, long=20)
        assert result["signal"] == "insufficient_data"


class TestRsiSignal:
    def test_free_tier_raises_permission(self):
        bot = AlgorithmicTradingBot(tier="free")
        with pytest.raises(PermissionError):
            bot.rsi_signal("AAPL", PRICES_UP)

    def test_rsi_between_0_100(self):
        bot = AlgorithmicTradingBot(tier="pro")
        result = bot.rsi_signal("AAPL", PRICES_UP + [115 + i for i in range(5)])
        assert 0 <= result["rsi"] <= 100

    def test_signal_in_valid_values(self):
        bot = AlgorithmicTradingBot(tier="pro")
        result = bot.rsi_signal("AAPL", PRICES_UP + [115 + i for i in range(5)])
        assert result["signal"] in ("overbought", "oversold", "neutral")


class TestBacktest:
    def test_free_tier_raises_permission(self):
        bot = AlgorithmicTradingBot(tier="free")
        with pytest.raises(PermissionError):
            bot.backtest("AAPL", PRICES_UP)

    def test_returns_summary(self):
        bot = AlgorithmicTradingBot(tier="pro")
        prices = PRICES_UP + PRICES_DOWN
        result = bot.backtest("AAPL", prices, short=5, long=10)
        assert "total_trades" in result
        assert "win_rate" in result
        assert "disclaimer" in result

    def test_win_rate_between_0_1(self):
        bot = AlgorithmicTradingBot(tier="pro")
        prices = PRICES_UP + PRICES_DOWN
        result = bot.backtest("AAPL", prices, short=5, long=10)
        assert 0.0 <= result["win_rate"] <= 1.0
