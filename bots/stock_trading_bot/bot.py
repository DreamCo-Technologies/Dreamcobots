"""
Dreamcobots StockTradingBot — tier-aware stock analysis and trading signals.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.stock_trading_bot.tiers import STOCK_TRADING_FEATURES, get_stock_trading_tier_info
import uuid
from datetime import datetime


class StockTradingBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class StockTradingBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class StockTradingBot:
    """Tier-aware stock analysis and trading signals bot."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._watchlist: list[str] = []

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise StockTradingBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_feature(self, feature: str) -> None:
        features = STOCK_TRADING_FEATURES[self.tier.value]
        if not any(feature.lower() in f.lower() for f in features):
            raise StockTradingBotTierError(
                f"'{feature}' is not available on the {self.config.name} tier. "
                f"Please upgrade to access this feature."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    def _add_to_watchlist(self, ticker: str) -> None:
        """Add a ticker to the watchlist, enforcing tier limits."""
        if ticker in self._watchlist:
            return
        watchlist_limits = {"free": 5, "pro": 100, "enterprise": None}
        limit = watchlist_limits[self.tier.value]
        if limit is not None and len(self._watchlist) >= limit:
            raise StockTradingBotTierError(
                f"Watchlist limit of {limit} stocks reached on the {self.config.name} tier. "
                f"Please upgrade to track more stocks."
            )
        self._watchlist.append(ticker)

    def _deterministic_signal(self, ticker: str) -> str:
        """Produce a deterministic signal from the ticker string."""
        signals = ["BUY", "SELL", "HOLD"]
        return signals[hash(ticker) % 3]

    def analyze_stock(self, ticker: str) -> dict:
        """
        Analyze a stock and return a trading signal with indicators.

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL").

        Returns:
            {"ticker": str, "signal": str, "confidence": float, "indicators": dict, "tier": str}
        """
        self._check_request_limit()
        self._request_count += 1
        self._add_to_watchlist(ticker)

        signal = self._deterministic_signal(ticker)

        if self.tier == Tier.FREE:
            confidence = 0.6
            indicators = {"sma_20": 150.0, "rsi": 50.0}

        elif self.tier == Tier.PRO:
            confidence = 0.75
            indicators = {
                "sma_20": 150.0,
                "rsi": 50.0,
                "ema_50": 148.5,
                "macd": 1.2,
                "bollinger_bands": {"upper": 158.0, "lower": 142.0},
            }

        else:  # ENTERPRISE
            confidence = 0.9
            indicators = {
                "sma_20": 150.0,
                "rsi": 50.0,
                "ema_50": 148.5,
                "macd": 1.2,
                "bollinger_bands": {"upper": 158.0, "lower": 142.0},
                "atr": 3.5,
                "obv": 1200000,
                "volume_analysis": "above_average",
                "institutional_flow": "accumulation",
            }

        return {
            "ticker": ticker,
            "signal": signal,
            "confidence": confidence,
            "indicators": indicators,
            "tier": self.tier.value,
        }

    def get_signals(self, ticker: str) -> dict:
        """
        Get trading signals for a ticker.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            {"ticker": str, "signals": list, "tier": str}
        """
        signal = self._deterministic_signal(ticker)

        if self.tier == Tier.FREE:
            signals = [{"type": "daily", "signal": signal, "timestamp": datetime.now().isoformat()}]
        elif self.tier == Tier.PRO:
            signals = [
                {"type": "real_time", "signal": signal, "timestamp": datetime.now().isoformat()},
                {"type": "momentum", "signal": "BUY" if signal != "SELL" else "SELL", "timestamp": datetime.now().isoformat()},
                {"type": "trend", "signal": "HOLD", "timestamp": datetime.now().isoformat()},
            ]
        else:  # ENTERPRISE
            signals = [
                {"type": "real_time", "signal": signal, "timestamp": datetime.now().isoformat()},
                {"type": "algorithmic", "signal": signal, "strategy": "mean_reversion", "timestamp": datetime.now().isoformat()},
                {"type": "options_flow", "signal": "BUY", "contract": "call", "timestamp": datetime.now().isoformat()},
                {"type": "institutional", "signal": "accumulation", "timestamp": datetime.now().isoformat()},
            ]

        return {
            "ticker": ticker,
            "signals": signals,
            "tier": self.tier.value,
        }

    def backtest(self, strategy: dict) -> dict:
        """
        Backtest a trading strategy.

        Args:
            strategy: {"name": str, "parameters": dict}

        Returns:
            {"strategy": str, "returns": float, "sharpe_ratio": float, "tier": str}
        """
        if self.tier == Tier.FREE:
            raise StockTradingBotTierError(
                "Backtesting is not available on the Free tier. "
                "Please upgrade to PRO or ENTERPRISE."
            )

        name = strategy.get("name", "unnamed_strategy")
        returns = 0.18 if self.tier == Tier.PRO else 0.24
        sharpe_ratio = 1.4 if self.tier == Tier.PRO else 1.9

        return {
            "strategy": name,
            "returns": returns,
            "sharpe_ratio": sharpe_ratio,
            "tier": self.tier.value,
        }

    def get_stats(self) -> dict:
        return {
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
            "watchlist_count": len(self._watchlist),
            "buddy_integration": True,
        }
