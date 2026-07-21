"""
Profitability Analytics module for the Dreamcobots Mining Bot.

Tracks key mining metrics:
  - Hash rate performance over time
  - Energy consumption and cost
  - Return on Investment (ROI)
  - Per-session and cumulative statistics

Analytics depth is gated by tier:
  - FREE:       basic (revenue only)
  - PRO:        advanced (revenue + energy + ROI)
  - ENTERPRISE: full (all metrics + trend analysis)
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class MiningSession:
    """A single mining session record."""

    coin: str
    strategy: str
    duration_hours: float
    hashrate_ths: float
    energy_kwh: float
    revenue_usd: float
    electricity_cost_usd: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def net_profit_usd(self) -> float:
        return self.revenue_usd - self.electricity_cost_usd

    @property
    def roi_pct(self) -> float:
        if self.electricity_cost_usd == 0:
            return float("inf") if self.revenue_usd > 0 else 0.0
        return (self.net_profit_usd / self.electricity_cost_usd) * 100


class AnalyticsDepthError(Exception):
    """Raised when a metric requires a higher analytics tier."""


class ProfitabilityAnalytics:
    """
    Aggregates mining session data and exposes analytics at the appropriate
    depth for the user's subscription tier.

    Parameters
    ----------
    depth : str
        One of ``"basic"``, ``"advanced"``, ``"full"``.
    hardware_cost_usd : float
        Total hardware investment in USD (used for overall ROI calculation).
    """

    DEPTH_ORDER = ["basic", "advanced", "full"]

    def __init__(self, depth: str = "basic", hardware_cost_usd: float = 0.0):
        if depth not in self.DEPTH_ORDER:
            raise ValueError(f"depth must be one of {self.DEPTH_ORDER}")
        self.depth = depth
        self.hardware_cost_usd = hardware_cost_usd
        self._sessions: List[MiningSession] = []

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def record_session(self, session: MiningSession) -> None:
        """Append a completed mining session to the analytics store."""
        self._sessions.append(session)

    def clear(self) -> None:
        self._sessions.clear()

    @property
    def session_count(self) -> int:
        return len(self._sessions)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_depth(self, minimum: str) -> None:
        if self.DEPTH_ORDER.index(self.depth) < self.DEPTH_ORDER.index(minimum):
            raise AnalyticsDepthError(
                f"Analytics depth '{minimum}' requires PRO or ENTERPRISE tier. "
                f"Current depth: '{self.depth}'."
            )

    # ------------------------------------------------------------------
    # Basic metrics (FREE tier)
    # ------------------------------------------------------------------

    def total_revenue_usd(self) -> float:
        return round(sum(s.revenue_usd for s in self._sessions), 6)

    def total_net_profit_usd(self) -> float:
        return round(sum(s.net_profit_usd for s in self._sessions), 6)

    def revenue_by_coin(self) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for s in self._sessions:
            result[s.coin] = round(result.get(s.coin, 0.0) + s.revenue_usd, 6)
        return result

    # ------------------------------------------------------------------
    # Advanced metrics (PRO tier)
    # ------------------------------------------------------------------

    def total_energy_kwh(self) -> float:
        self._require_depth("advanced")
        return round(sum(s.energy_kwh for s in self._sessions), 4)

    def total_electricity_cost_usd(self) -> float:
        self._require_depth("advanced")
        return round(sum(s.electricity_cost_usd for s in self._sessions), 6)

    def average_hashrate_ths(self) -> float:
        self._require_depth("advanced")
        if not self._sessions:
            return 0.0
        return round(statistics.mean(s.hashrate_ths for s in self._sessions), 4)

    def roi_pct(self) -> float:
        """
        Overall ROI taking hardware cost + electricity costs into account.
        """
        self._require_depth("advanced")
        total_cost = self.total_electricity_cost_usd() + self.hardware_cost_usd
        if total_cost == 0:
            return float("inf") if self.total_revenue_usd() > 0 else 0.0
        return round(
            (self.total_revenue_usd() - total_cost) / total_cost * 100, 4
        )

    def best_performing_coin(self) -> Optional[str]:
        self._require_depth("advanced")
        by_coin = self.revenue_by_coin()
        return max(by_coin, key=by_coin.get) if by_coin else None

    # ------------------------------------------------------------------
    # Full metrics (ENTERPRISE tier)
    # ------------------------------------------------------------------

    def hashrate_trend(self) -> List[float]:
        """Ordered list of per-session hash rates (chronological)."""
        self._require_depth("full")
        return [s.hashrate_ths for s in self._sessions]

    def revenue_trend(self) -> List[float]:
        """Ordered list of per-session revenues (chronological)."""
        self._require_depth("full")
        return [s.revenue_usd for s in self._sessions]

    def energy_efficiency(self) -> float:
        """
        Revenue per kWh across all sessions (higher is better).
        Returns 0 if no energy has been consumed.
        """
        self._require_depth("full")
        total_kwh = sum(s.energy_kwh for s in self._sessions)
        if total_kwh == 0:
            return 0.0
        return round(self.total_revenue_usd() / total_kwh, 6)

    def profit_variance(self) -> float:
        """Variance of per-session net profits (measures consistency)."""
        self._require_depth("full")
        profits = [s.net_profit_usd for s in self._sessions]
        if len(profits) < 2:
            return 0.0
        return round(statistics.variance(profits), 6)

    def summary(self) -> Dict:
        """
        Return a summary dict containing all metrics available at the
        current analytics depth.
        """
        data: Dict = {
            "sessions": self.session_count,
            "total_revenue_usd": self.total_revenue_usd(),
            "total_net_profit_usd": self.total_net_profit_usd(),
            "revenue_by_coin": self.revenue_by_coin(),
        }
        if self.depth in ("advanced", "full"):
            data.update(
                {
                    "total_energy_kwh": self.total_energy_kwh(),
                    "total_electricity_cost_usd": self.total_electricity_cost_usd(),
                    "average_hashrate_ths": self.average_hashrate_ths(),
                    "roi_pct": self.roi_pct(),
                    "best_performing_coin": self.best_performing_coin(),
                }
            )
        if self.depth == "full":
            data.update(
                {
                    "hashrate_trend": self.hashrate_trend(),
                    "revenue_trend": self.revenue_trend(),
                    "energy_efficiency": self.energy_efficiency(),
                    "profit_variance": self.profit_variance(),
                }
            )
        return data
