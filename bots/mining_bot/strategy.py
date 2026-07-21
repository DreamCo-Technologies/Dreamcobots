"""
Mining Strategy module for the Dreamcobots Mining Bot.

Supports three primary strategies:
  - Pool Mining   : Mine with a pool to receive steady, smaller payouts.
  - Solo Mining   : Mine independently for potentially larger but rarer rewards.
  - Merged Mining : Mine two compatible coins simultaneously on the same algorithm.

The AdaptiveStrategyEngine selects the highest-profitability strategy and coin
in real-time based on provided market data.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class StrategyType(Enum):
    POOL = "pool_mining"
    SOLO = "solo_mining"
    MERGED = "merged_mining"


@dataclass
class CoinProfile:
    """Snapshot of a single coin's mining characteristics."""

    symbol: str
    algorithm: str
    network_difficulty: float     # current network difficulty
    block_reward: float           # coin units per block
    coin_price_usd: float         # current USD price
    network_hashrate: float       # H/s  (total network)
    pool_fee_pct: float = 1.0     # pool fee percentage (0–100)
    merged_pair: Optional[str] = None  # symbol of merged-mining partner, if any

    @property
    def estimated_revenue_per_th(self) -> float:
        """Rough USD revenue per TH/s per day (simplified model)."""
        if self.network_hashrate <= 0 or self.network_difficulty <= 0:
            return 0.0
        blocks_per_day = 86_400 / max(self.network_difficulty * 2**32 /
                                      max(self.network_hashrate, 1), 1)
        return blocks_per_day * self.block_reward * self.coin_price_usd


@dataclass
class StrategyResult:
    """Outcome of executing or simulating a mining strategy."""

    strategy: StrategyType
    coin: str
    estimated_daily_revenue_usd: float
    estimated_daily_cost_usd: float
    net_profit_usd: float
    notes: List[str] = field(default_factory=list)

    @property
    def is_profitable(self) -> bool:
        return self.net_profit_usd > 0


class MiningStrategyError(Exception):
    """Raised when an unsupported or misconfigured strategy is requested."""


# ---------------------------------------------------------------------------
# Standalone helper used by StrategyEngine
# ---------------------------------------------------------------------------

def coin_revenue(coin: CoinProfile, hashrate_ths: float) -> float:
    """Raw gross daily revenue for *coin* at *hashrate_ths* TH/s."""
    return coin.estimated_revenue_per_th * hashrate_ths


class StrategyEngine:
    """
    Evaluates and executes mining strategies for a given set of coins.

    Parameters
    ----------
    hashrate_ths : float
        Miner's hash rate in TH/s.
    power_kw : float
        Miner's power consumption in kilowatts.
    electricity_rate : float
        Electricity cost in USD per kWh.
    available_strategies : list[StrategyType]
        Strategies allowed by the current tier.
    """

    def __init__(
        self,
        hashrate_ths: float,
        power_kw: float,
        electricity_rate: float,
        available_strategies: List[StrategyType],
    ):
        if hashrate_ths <= 0:
            raise ValueError("hashrate_ths must be positive")
        if power_kw < 0:
            raise ValueError("power_kw cannot be negative")
        if electricity_rate < 0:
            raise ValueError("electricity_rate cannot be negative")

        self.hashrate_ths = hashrate_ths
        self.power_kw = power_kw
        self.electricity_rate = electricity_rate
        self.available_strategies = list(available_strategies)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def daily_energy_cost(self) -> float:
        return self.power_kw * 24 * self.electricity_rate

    def _pool_revenue(self, coin: CoinProfile) -> float:
        """Estimated daily pool-mining revenue in USD (after pool fee)."""
        gross = coin.estimated_revenue_per_th * self.hashrate_ths
        return gross * (1 - coin.pool_fee_pct / 100)

    def _solo_revenue(self, coin: CoinProfile) -> float:
        """
        Expected daily solo-mining revenue.  Uses the same gross model but
        applies no pool fee.  In practice, solo mining is higher-variance.
        """
        return coin.estimated_revenue_per_th * self.hashrate_ths

    def _merged_revenue(self, primary: CoinProfile, secondary: CoinProfile) -> float:
        """
        Combined daily revenue when merged-mining two compatible coins.
        The secondary coin's contribution is net of a small merged-mining
        overhead (modelled as 0.5 % efficiency loss on both).
        """
        return (
            self._pool_revenue(primary) * 0.995
            + coin_revenue(secondary, self.hashrate_ths) * 0.995
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def _require_strategy(self, strategy: StrategyType) -> None:
        if strategy not in self.available_strategies:
            raise MiningStrategyError(
                f"Strategy '{strategy.value}' is not available on your current tier."
            )

    def evaluate_pool(self, coin: CoinProfile) -> StrategyResult:
        self._require_strategy(StrategyType.POOL)
        daily_cost = self.daily_energy_cost()
        revenue = self._pool_revenue(coin)
        return StrategyResult(
            strategy=StrategyType.POOL,
            coin=coin.symbol,
            estimated_daily_revenue_usd=round(revenue, 4),
            estimated_daily_cost_usd=round(daily_cost, 4),
            net_profit_usd=round(revenue - daily_cost, 4),
            notes=[f"Pool fee: {coin.pool_fee_pct}%"],
        )

    def evaluate_solo(self, coin: CoinProfile) -> StrategyResult:
        self._require_strategy(StrategyType.SOLO)
        daily_cost = self.daily_energy_cost()
        revenue = self._solo_revenue(coin)
        return StrategyResult(
            strategy=StrategyType.SOLO,
            coin=coin.symbol,
            estimated_daily_revenue_usd=round(revenue, 4),
            estimated_daily_cost_usd=round(daily_cost, 4),
            net_profit_usd=round(revenue - daily_cost, 4),
            notes=["High variance — infrequent but larger payouts"],
        )

    def evaluate_merged(
        self, primary: CoinProfile, secondary: CoinProfile
    ) -> StrategyResult:
        self._require_strategy(StrategyType.MERGED)
        if primary.algorithm != secondary.algorithm:
            raise MiningStrategyError(
                f"Merged mining requires the same algorithm. "
                f"{primary.symbol} uses '{primary.algorithm}', "
                f"{secondary.symbol} uses '{secondary.algorithm}'."
            )
        daily_cost = self.daily_energy_cost()
        revenue = self._merged_revenue(primary, secondary)
        return StrategyResult(
            strategy=StrategyType.MERGED,
            coin=f"{primary.symbol}+{secondary.symbol}",
            estimated_daily_revenue_usd=round(revenue, 4),
            estimated_daily_cost_usd=round(daily_cost, 4),
            net_profit_usd=round(revenue - daily_cost, 4),
            notes=[
                f"Primary: {primary.symbol}, Secondary: {secondary.symbol}",
                "0.5% efficiency overhead applied to both coins",
            ],
        )

    def compare_strategies(
        self,
        coins: List[CoinProfile],
    ) -> List[StrategyResult]:
        """
        Evaluate all available strategies across all supplied coins and return
        results sorted by net profit (descending).
        """
        results: List[StrategyResult] = []

        for coin in coins:
            if StrategyType.POOL in self.available_strategies:
                results.append(self.evaluate_pool(coin))
            if StrategyType.SOLO in self.available_strategies:
                results.append(self.evaluate_solo(coin))

        # Merged mining: try all algorithm-compatible pairs
        if StrategyType.MERGED in self.available_strategies:
            for i, primary in enumerate(coins):
                for secondary in coins[i + 1:]:
                    if primary.algorithm == secondary.algorithm:
                        results.append(self.evaluate_merged(primary, secondary))

        results.sort(key=lambda r: r.net_profit_usd, reverse=True)
        return results


class AdaptiveStrategyEngine(StrategyEngine):
    """
    Extends StrategyEngine with an adaptive recommendation system.
    Dynamically selects the best strategy based on real-time coin profiles.
    """

    def best_strategy(self, coins: List[CoinProfile]) -> Optional[StrategyResult]:
        """Return the single most profitable strategy result, or None."""
        results = self.compare_strategies(coins)
        return results[0] if results else None

    def recommend(self, coins: List[CoinProfile]) -> Dict:
        """
        High-level recommendation report.

        Returns
        -------
        dict with keys: ``best``, ``all_results``, ``reasoning``
        """
        best = self.best_strategy(coins)
        all_results = self.compare_strategies(coins)
        reasoning = []

        if best is None:
            reasoning.append("No strategies available for the supplied coins.")
        else:
            reasoning.append(
                f"Best strategy: {best.strategy.value} on {best.coin} "
                f"(net profit: ${best.net_profit_usd:.4f}/day)"
            )
            if not best.is_profitable:
                reasoning.append(
                    "WARNING: No strategy is currently profitable — "
                    "consider pausing mining or reducing power consumption."
                )

        return {
            "best": best,
            "all_results": all_results,
            "reasoning": reasoning,
        }
