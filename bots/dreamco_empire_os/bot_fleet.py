"""
DreamCo Empire OS — Bot Fleet Module

Manages the full collection of DreamCo bots: registration, activation,
speed control, stats, profitability tracking, and autonomy toggles.
Designed to handle 877+ bots in the Full Auto configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from framework import GlobalAISourcesFlow  # noqa: F401


class BotSpeed(Enum):
    SLOW = "slow"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    FULL_AUTO = "full_auto"


class BotStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class BotEntry:
    """Registry entry for a single bot in the fleet."""
    name: str
    category: str
    status: BotStatus = BotStatus.IDLE
    speed: BotSpeed = BotSpeed.MODERATE
    profit_per_day_usd: float = 0.0
    usage_pct: float = 0.0
    total_runs: int = 0
    success_runs: int = 0
    is_autonomous: bool = False
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_run: Optional[str] = None

    @property
    def success_rate(self) -> float:
        if self.total_runs == 0:
            return 0.0
        return round(self.success_runs / self.total_runs * 100, 1)


class BotFleet:
    """
    Bot Fleet — manages all DreamCo bots.

    Supports registration, activation, speed control, usage tracking,
    profitability analytics, and autonomy management.
    """

    def __init__(self) -> None:
        self._fleet: dict[str, BotEntry] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_bot(
        self,
        name: str,
        category: str = "general",
        profit_per_day_usd: float = 0.0,
        usage_pct: float = 0.0,
    ) -> BotEntry:
        """Add a bot to the fleet."""
        entry = BotEntry(
            name=name,
            category=category,
            profit_per_day_usd=profit_per_day_usd,
            usage_pct=usage_pct,
        )
        self._fleet[name] = entry
        return entry

    def unregister_bot(self, name: str) -> bool:
        """Remove a bot from the fleet. Returns True if removed."""
        if name in self._fleet:
            del self._fleet[name]
            return True
        return False

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def activate_bot(self, name: str) -> dict:
        """Set bot status to RUNNING."""
        bot = self._get_bot(name)
        bot.status = BotStatus.RUNNING
        bot.last_run = datetime.now(timezone.utc).isoformat()
        return {"bot": name, "status": bot.status.value}

    def pause_bot(self, name: str) -> dict:
        """Pause a running bot."""
        bot = self._get_bot(name)
        bot.status = BotStatus.PAUSED
        return {"bot": name, "status": bot.status.value}

    def set_speed(self, name: str, speed: BotSpeed) -> dict:
        """Set the operating speed for a specific bot."""
        bot = self._get_bot(name)
        bot.speed = speed
        return {"bot": name, "speed": speed.value}

    def set_fleet_speed(self, speed: BotSpeed) -> dict:
        """Apply a speed setting to all bots in the fleet."""
        for bot in self._fleet.values():
            bot.speed = speed
        return {"fleet_speed": speed.value, "bots_updated": len(self._fleet)}

    def toggle_autonomy(self, name: str, autonomous: bool) -> dict:
        """Enable or disable autonomous mode for a bot."""
        bot = self._get_bot(name)
        bot.is_autonomous = autonomous
        return {"bot": name, "autonomous": autonomous}

    # ------------------------------------------------------------------
    # Run tracking
    # ------------------------------------------------------------------

    def record_run(self, name: str, success: bool = True) -> None:
        """Record a bot run result."""
        bot = self._get_bot(name)
        bot.total_runs += 1
        if success:
            bot.success_runs += 1
        bot.last_run = datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_top_bots(self, n: int = 10, sort_by: str = "profit") -> list:
        """Return top N bots sorted by 'profit' or 'usage' or 'success_rate'."""
        bots = list(self._fleet.values())
        if sort_by == "usage":
            bots.sort(key=lambda b: b.usage_pct, reverse=True)
        elif sort_by == "success_rate":
            bots.sort(key=lambda b: b.success_rate, reverse=True)
        else:
            bots.sort(key=lambda b: b.profit_per_day_usd, reverse=True)
        return [_bot_to_dict(b) for b in bots[:n]]

    def get_fleet_stats(self) -> dict:
        """Return aggregate fleet statistics."""
        bots = list(self._fleet.values())
        total = len(bots)
        running = sum(1 for b in bots if b.status == BotStatus.RUNNING)
        autonomous = sum(1 for b in bots if b.is_autonomous)
        total_profit = sum(b.profit_per_day_usd for b in bots)
        avg_usage = (sum(b.usage_pct for b in bots) / total) if total > 0 else 0.0

        return {
            "total_bots": total,
            "running": running,
            "idle": sum(1 for b in bots if b.status == BotStatus.IDLE),
            "paused": sum(1 for b in bots if b.status == BotStatus.PAUSED),
            "autonomous_bots": autonomous,
            "total_daily_profit_usd": round(total_profit, 2),
            "avg_usage_pct": round(avg_usage, 1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_bot(self, name: str) -> dict:
        """Return details for a specific bot."""
        return _bot_to_dict(self._get_bot(name))

    def list_bots(self) -> list:
        """Return summary list of all bots."""
        return [_bot_to_dict(b) for b in self._fleet.values()]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_bot(self, name: str) -> BotEntry:
        if name not in self._fleet:
            raise KeyError(f"Bot '{name}' is not registered in the fleet.")
        return self._fleet[name]


def _bot_to_dict(bot: BotEntry) -> dict:
    return {
        "name": bot.name,
        "category": bot.category,
        "status": bot.status.value,
        "speed": bot.speed.value,
        "profit_per_day_usd": round(bot.profit_per_day_usd, 2),
        "usage_pct": bot.usage_pct,
        "total_runs": bot.total_runs,
        "success_rate": bot.success_rate,
        "autonomous": bot.is_autonomous,
        "registered_at": bot.registered_at,
        "last_run": bot.last_run,
    }
