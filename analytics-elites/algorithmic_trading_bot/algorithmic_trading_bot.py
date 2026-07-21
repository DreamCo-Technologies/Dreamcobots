# GLOBAL AI SOURCES FLOW
"""Algorithmic Trading Bot - technical indicator signals and backtesting engine."""
import sys
import os
import importlib.util
_TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_TOOL_DIR, '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
# Load local tiers.py by path to avoid sys.modules conflicts with other tiers modules
_tiers_spec = importlib.util.spec_from_file_location('_local_tiers', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. Past performance does not guarantee future results."
)


class AlgorithmicTradingBot:
    """Technical analysis signals and backtesting engine for educational use."""

    def __init__(self, tier: str = "free"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["free"])
        self._symbol_count = 0
        self._symbol_limit = 3 if tier == "free" else (10 if tier == "pro" else None)

    def _check_limit(self):
        if self._symbol_limit and self._symbol_count >= self._symbol_limit:
            raise PermissionError(f"Symbol limit ({self._symbol_limit}) reached. Upgrade to a higher tier.")

    @staticmethod
    def _sma(prices: list, period: int) -> list:
        """Simple Moving Average."""
        return [
            round(sum(prices[i - period:i]) / period, 4)
            for i in range(period, len(prices) + 1)
        ]

    @staticmethod
    def _ema(prices: list, period: int) -> list:
        """Exponential Moving Average."""
        if len(prices) < period:
            return []
        k = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]
        for price in prices[period:]:
            ema.append(round(price * k + ema[-1] * (1 - k), 4))
        return ema

    def moving_average_signal(self, symbol: str, prices: list, short: int = 10, long: int = 20) -> dict:
        """Generate a buy/sell/hold signal based on SMA crossover."""
        self._check_limit()
        self._symbol_count += 1
        return self._compute_sma_signal(symbol, prices, short, long)

    def _compute_sma_signal(self, symbol: str, prices: list, short: int, long: int) -> dict:
        """Internal SMA crossover computation (no limit check, no counter increment)."""
        if len(prices) < long + 1:
            return {"symbol": symbol, "signal": "insufficient_data", "disclaimer": DISCLAIMER}
        sma_short = self._sma(prices, short)
        sma_long = self._sma(prices, long)

        short_now = sma_short[-1]
        long_now = sma_long[-1]
        short_prev = sma_short[-2] if len(sma_short) >= 2 else short_now
        long_prev = sma_long[-2] if len(sma_long) >= 2 else long_now

        if short_prev <= long_prev and short_now > long_now:
            signal = "buy"
        elif short_prev >= long_prev and short_now < long_now:
            signal = "sell"
        else:
            signal = "hold"

        return {
            "symbol": symbol,
            "signal": signal,
            "sma_short": short_now,
            "sma_long": long_now,
            "tier": self.tier,
            "disclaimer": DISCLAIMER,
        }

    def rsi_signal(self, symbol: str, prices: list, period: int = 14) -> dict:
        """Calculate RSI and return an overbought/oversold signal (Pro+ only)."""
        if self.tier == "free":
            raise PermissionError("RSI signals require Pro tier or higher.")
        if len(prices) < period + 1:
            return {"symbol": symbol, "signal": "insufficient_data", "disclaimer": DISCLAIMER}
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        gains = [d for d in deltas[-period:] if d > 0]
        losses = [-d for d in deltas[-period:] if d < 0]
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        rs = avg_gain / avg_loss if avg_loss != 0 else float("inf")
        rsi = round(100 - (100 / (1 + rs)), 2)

        signal = "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral"
        return {
            "symbol": symbol,
            "rsi": rsi,
            "signal": signal,
            "tier": self.tier,
            "disclaimer": DISCLAIMER,
        }

    def backtest(self, symbol: str, prices: list, short: int = 10, long: int = 20) -> dict:
        """Backtest a moving average crossover strategy (Pro+ only)."""
        if self.tier == "free":
            raise PermissionError("Backtesting requires Pro tier or higher.")
        trades = []
        position = None
        for i in range(long + 1, len(prices)):
            result = self._compute_sma_signal(symbol, prices[:i+1], short, long)
            sig = result.get("signal")
            if sig == "buy" and position is None:
                position = {"type": "buy", "price": prices[i], "index": i}
            elif sig == "sell" and position is not None:
                pnl = round(prices[i] - position["price"], 4)
                trades.append({"buy_price": position["price"], "sell_price": prices[i], "pnl": pnl})
                position = None

        wins = [t for t in trades if t["pnl"] > 0]
        total_pnl = round(sum(t["pnl"] for t in trades), 4)
        return {
            "symbol": symbol,
            "total_trades": len(trades),
            "winning_trades": len(wins),
            "win_rate": round(len(wins) / len(trades), 3) if trades else 0.0,
            "total_pnl": total_pnl,
            "disclaimer": DISCLAIMER,
        }
