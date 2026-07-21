"""
Auto-Bot Factory — Revenue Tracker Module

Tracks revenue per bot with tiered pricing ($99 basic, $299 pro,
usage-based enterprise).  Results are saved to data/revenue.json.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

import json
from datetime import datetime, timezone
from typing import List, Optional


# ---------------------------------------------------------------------------
# Pricing constants
# ---------------------------------------------------------------------------

TIER_PRICES_USD: dict = {
    "basic": 99.0,
    "pro": 299.0,
    "enterprise": 0.0,  # usage-based
}

USAGE_RATE_USD = 0.05  # per billable action (enterprise)


def _default_revenue_path() -> str:
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "revenue.json"
    )


# ---------------------------------------------------------------------------
# Revenue Tracker
# ---------------------------------------------------------------------------

class RevenueTrackerError(Exception):
    """Raised when a revenue operation fails."""


class RevenueTracker:
    """
    DreamCo Auto-Bot Factory — Revenue Tracker.

    Tracks subscription revenue, billable actions, and total income per
    bot.  Results are persisted to ``data/revenue.json`` so the learning
    loop can identify underperformers.

    Pricing tiers:
    - **basic**      : $99/month flat
    - **pro**        : $299/month flat
    - **enterprise** : $0.05 per billable action (usage-based)

    Usage::

        tracker = RevenueTracker()
        tracker.record_subscription("lead_gen_bot", tier="pro")
        tracker.record_action("lead_gen_bot", count=10)
        report = tracker.get_report("lead_gen_bot")
        print(report["total_revenue_usd"])
    """

    def __init__(self, revenue_path: Optional[str] = None) -> None:
        self._revenue_path = os.path.abspath(revenue_path or _default_revenue_path())
        self._bots: dict = {}  # bot_name -> {tier, subscriptions, actions, revenue}
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record_subscription(self, bot_name: str, tier: str = "basic") -> float:
        """
        Record a new monthly subscription for *bot_name* on *tier*.

        Parameters
        ----------
        bot_name : str
            Identifier for the bot generating revenue.
        tier : str
            Subscription tier: "basic", "pro", or "enterprise".

        Returns
        -------
        float
            Charge amount in USD.
        """
        if tier not in TIER_PRICES_USD:
            raise RevenueTrackerError(
                f"Unknown tier '{tier}'. Choose from: {list(TIER_PRICES_USD)}"
            )
        entry = self._ensure(bot_name, tier)
        charge = TIER_PRICES_USD[tier]
        entry["subscriptions"] += 1
        entry["revenue_usd"] = round(entry["revenue_usd"] + charge, 2)
        self._save()
        return charge

    def record_action(self, bot_name: str, count: int = 1) -> float:
        """
        Record billable actions for *bot_name* (enterprise usage-based billing).

        Parameters
        ----------
        bot_name : str
            Bot generating the actions.
        count : int
            Number of billable actions to record.

        Returns
        -------
        float
            Charge amount in USD (0.0 for non-enterprise bots).
        """
        if count < 0:
            raise RevenueTrackerError("count must be >= 0")
        entry = self._ensure(bot_name)
        entry["billable_actions"] += count
        charge = 0.0
        if entry["tier"] == "enterprise":
            charge = round(count * USAGE_RATE_USD, 2)
            entry["revenue_usd"] = round(entry["revenue_usd"] + charge, 2)
        self._save()
        return charge

    def get_report(self, bot_name: str) -> dict:
        """Return a revenue report for *bot_name*."""
        entry = self._bots.get(bot_name)
        if entry is None:
            return {
                "bot_name": bot_name,
                "tier": "basic",
                "subscriptions": 0,
                "billable_actions": 0,
                "total_revenue_usd": 0.0,
            }
        return {
            "bot_name": bot_name,
            "tier": entry["tier"],
            "subscriptions": entry["subscriptions"],
            "billable_actions": entry["billable_actions"],
            "total_revenue_usd": entry["revenue_usd"],
        }

    def get_total_revenue(self) -> float:
        """Return total revenue across all tracked bots."""
        return round(sum(e["revenue_usd"] for e in self._bots.values()), 2)

    def list_bots(self) -> List[dict]:
        """Return revenue data for all tracked bots."""
        return [
            self.get_report(name) for name in self._bots
        ]

    def get_underperformers(self, threshold_usd: float = 100.0) -> List[str]:
        """Return bot names whose total revenue is below *threshold_usd*."""
        return [
            name for name, entry in self._bots.items()
            if entry["revenue_usd"] < threshold_usd
        ]

    def run(self) -> str:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return (
            f"RevenueTracker active — "
            f"${self.get_total_revenue():.2f} total revenue across "
            f"{len(self._bots)} bot(s)."
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure(self, bot_name: str, tier: str = "basic") -> dict:
        if bot_name not in self._bots:
            self._bots[bot_name] = {
                "tier": tier,
                "subscriptions": 0,
                "billable_actions": 0,
                "revenue_usd": 0.0,
            }
        return self._bots[bot_name]

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self._revenue_path), exist_ok=True)
        payload = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_revenue_usd": self.get_total_revenue(),
            "bots": [self.get_report(n) for n in self._bots],
        }
        with open(self._revenue_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

    def _load(self) -> None:
        if not os.path.exists(self._revenue_path):
            self._bots = {}
            return
        try:
            with open(self._revenue_path, encoding="utf-8") as fh:
                data = json.load(fh)
            for entry in data.get("bots", []):
                name = entry.get("bot_name")
                if name:
                    self._bots[name] = {
                        "tier": entry.get("tier", "basic"),
                        "subscriptions": entry.get("subscriptions", 0),
                        "billable_actions": entry.get("billable_actions", 0),
                        "revenue_usd": entry.get("total_revenue_usd", 0.0),
                    }
        except (json.JSONDecodeError, OSError):
            self._bots = {}
