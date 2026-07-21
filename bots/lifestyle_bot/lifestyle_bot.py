"""
Dreamcobots Lifestyle Bot — tier-aware habit tracking and wellness management.

Usage
-----
    from lifestyle_bot import LifestyleBot
    from tiers import Tier

    bot = LifestyleBot(tier=Tier.FREE)
    result = bot.track_habit("morning_run", True)
    print(result)
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path

import importlib.util as _ilu
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_spec = _ilu.spec_from_file_location("_lifestyle_tiers", os.path.join(_THIS_DIR, "tiers.py"))
_lifestyle_tiers = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_lifestyle_tiers)
LIFESTYLE_FEATURES = _lifestyle_tiers.LIFESTYLE_FEATURES
HABIT_LIMITS = _lifestyle_tiers.HABIT_LIMITS
get_lifestyle_tier_info = _lifestyle_tiers.get_lifestyle_tier_info


class LifestyleBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class LifestyleBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class LifestyleBot:
    """
    Tier-aware habit tracking and lifestyle management bot.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling habit limits and feature availability.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._habits: dict[str, list[dict]] = {}
        self._goals: list[dict] = []
        self._mood_log: list[dict] = []

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def track_habit(self, habit_name: str, completed: bool, date: str | None = None) -> dict:
        """
        Track a habit completion.

        Parameters
        ----------
        habit_name : str
            Name of the habit.
        completed : bool
            Whether the habit was completed.
        date : str | None
            Date string (e.g., "2025-01-01"). Defaults to "today" (mock).

        Returns
        -------
        dict
        """
        self._check_request_limit()
        habit_limit = HABIT_LIMITS[self.tier.value]
        if habit_name not in self._habits:
            if habit_limit is not None and len(self._habits) >= habit_limit:
                raise LifestyleBotTierError(
                    f"Habit limit of {habit_limit} reached on the {self.config.name} tier. "
                    "Upgrade to track more habits."
                )
            self._habits[habit_name] = []
        self._request_count += 1
        entry = {"date": date or "today", "completed": completed}
        self._habits[habit_name].append(entry)
        return {
            "habit_name": habit_name,
            "completed": completed,
            "date": entry["date"],
            "total_entries": len(self._habits[habit_name]),
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def set_goal(self, goal: str, target_date: str) -> dict:
        """
        Set a personal goal.

        Parameters
        ----------
        goal : str
            Description of the goal.
        target_date : str
            Target completion date.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        self._request_count += 1
        goal_entry = {
            "goal_id": f"GOAL-{len(self._goals) + 1:03d}",
            "goal": goal,
            "target_date": target_date,
            "status": "active",
        }
        self._goals.append(goal_entry)
        return {
            "goal": goal_entry,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def get_habits_summary(self) -> dict:
        """
        Return a summary of all tracked habits and completion rates.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        self._request_count += 1
        summary = {}
        for name, entries in self._habits.items():
            total = len(entries)
            completed = sum(1 for e in entries if e["completed"])
            rate = round((completed / total) * 100, 1) if total > 0 else 0.0
            summary[name] = {
                "total_entries": total,
                "completed": completed,
                "completion_rate_pct": rate,
            }
        return {
            "habits": summary,
            "total_habits": len(self._habits),
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def log_mood(self, mood: str, notes: str = "") -> dict:
        """
        Log a mood entry.  Requires PRO or ENTERPRISE tier.

        Parameters
        ----------
        mood : str
            Mood descriptor (e.g., "happy", "stressed").
        notes : str
            Optional notes about the mood.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        if self.tier == Tier.FREE:
            raise LifestyleBotTierError(
                "Mood journaling requires PRO or ENTERPRISE tier."
            )
        self._request_count += 1
        entry = {
            "mood_id": f"MOOD-{len(self._mood_log) + 1:03d}",
            "mood": mood,
            "notes": notes,
            "date": "today",
        }
        self._mood_log.append(entry)
        return {
            "mood_entry": entry,
            "total_entries": len(self._mood_log),
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current tier."""
        info = get_lifestyle_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        habit_limit = (
            "Unlimited"
            if info["habit_limit"] is None
            else str(info["habit_limit"])
        )
        lines = [
            f"=== {info['name']} Lifestyle Bot Tier ===",
            f"Price       : ${info['price_usd_monthly']:.2f}/month",
            f"Requests    : {limit}/month",
            f"Habit limit : {habit_limit}",
            f"Support     : {info['support_level']}",
            "",
            "Features:",
        ]
        for feat in info["lifestyle_features"]:
            lines.append(f"  ✓ {feat}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg
        current_feats = set(LIFESTYLE_FEATURES[self.tier.value])
        new_feats = [f for f in LIFESTYLE_FEATURES[next_cfg.tier.value] if f not in current_feats]
        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features:",
        ]
        for feat in new_feats:
            lines.append(f"  + {feat}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing LifestyleBot or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise LifestyleBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))


if __name__ == "__main__":
    bot = LifestyleBot(tier=Tier.FREE)
    bot.describe_tier()
    result = bot.track_habit("morning_run", True)
    print(result)
