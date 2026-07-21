"""
DreamCo Empire OS — Empire HQ Module

Central command hub showing real-time overview of the entire empire:
active bots, revenue, achievements, leaderboard position, and empire health.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from framework import GlobalAISourcesFlow  # noqa: F401


@dataclass
class EmpireStat:
    """A single empire-wide statistic."""
    label: str
    value: float
    unit: str
    trend: str = "stable"  # "up", "down", "stable"


class EmpireHQ:
    """
    Empire HQ — real-time overview dashboard for the entire DreamCo empire.

    Tracks active bots, revenue, profit, empire level, and growth metrics.
    """

    EMPIRE_LEVELS = [
        (0, "Street Hustler"),
        (5_000, "Small Business"),
        (25_000, "Mid-Market Player"),
        (100_000, "Empire Builder"),
        (500_000, "Industry Titan"),
        (1_000_000, "DreamCo Mogul"),
    ]

    def __init__(self) -> None:
        self._stats: dict[str, EmpireStat] = {}
        self._alerts: list[str] = []
        self._created_at: str = datetime.now(timezone.utc).isoformat()
        self._revenue_usd: float = 0.0
        self._cost_usd: float = 0.0
        self._active_bots: int = 0
        self._empire_xp: int = 0

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def update_stat(self, label: str, value: float, unit: str = "", trend: str = "stable") -> None:
        """Update or create an empire stat."""
        self._stats[label] = EmpireStat(label=label, value=value, unit=unit, trend=trend)

    def record_revenue(self, amount_usd: float) -> None:
        """Record incoming revenue and award XP."""
        self._revenue_usd += amount_usd
        self._empire_xp += max(1, int(amount_usd / 10))
        self.update_stat("Total Revenue", self._revenue_usd, "USD", trend="up")

    def record_cost(self, amount_usd: float) -> None:
        """Record an operational cost."""
        self._cost_usd += amount_usd
        self.update_stat("Total Costs", self._cost_usd, "USD")

    def set_active_bots(self, count: int) -> None:
        """Update the active bot count."""
        self._active_bots = count
        self.update_stat("Active Bots", float(count), "bots")

    # ------------------------------------------------------------------
    # Empire level
    # ------------------------------------------------------------------

    def get_empire_level(self) -> dict:
        """Return current empire level name and progress to next tier."""
        revenue = self._revenue_usd
        current_name = self.EMPIRE_LEVELS[0][1]
        next_threshold: Optional[float] = None

        for i, (threshold, name) in enumerate(self.EMPIRE_LEVELS):
            if revenue >= threshold:
                current_name = name
                if i + 1 < len(self.EMPIRE_LEVELS):
                    next_threshold = float(self.EMPIRE_LEVELS[i + 1][0])

        progress = 0.0
        if next_threshold:
            progress = min(1.0, revenue / next_threshold)

        return {
            "level_name": current_name,
            "revenue_usd": round(self._revenue_usd, 2),
            "next_milestone_usd": next_threshold,
            "progress_pct": round(progress * 100, 1),
            "empire_xp": self._empire_xp,
        }

    # ------------------------------------------------------------------
    # Alerts
    # ------------------------------------------------------------------

    def add_alert(self, message: str) -> None:
        """Add an HQ alert."""
        self._alerts.append({"message": message, "timestamp": datetime.now(timezone.utc).isoformat()})

    def get_alerts(self) -> list:
        """Return all HQ alerts."""
        return list(self._alerts)

    # ------------------------------------------------------------------
    # Dashboard snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> dict:
        """Return full Empire HQ snapshot."""
        profit = self._revenue_usd - self._cost_usd
        return {
            "module": "Empire HQ",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_bots": self._active_bots,
            "revenue_usd": round(self._revenue_usd, 2),
            "cost_usd": round(self._cost_usd, 2),
            "profit_usd": round(profit, 2),
            "profit_margin_pct": round((profit / self._revenue_usd * 100) if self._revenue_usd > 0 else 0.0, 1),
            "empire_level": self.get_empire_level(),
            "stats": {k: {"value": v.value, "unit": v.unit, "trend": v.trend} for k, v in self._stats.items()},
            "alerts": self.get_alerts(),
        }
