"""
DreamCo Empire OS — Cost Tracking Module

Monitors all operational costs across bots, divisions, and infrastructure.
Generates cost-per-bot reports, budget alerts, and ROI breakdowns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from framework import GlobalAISourcesFlow  # noqa: F401


class CostCategory(Enum):
    INFRASTRUCTURE = "infrastructure"
    AI_MODELS = "ai_models"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    DEVELOPMENT = "development"
    LICENSING = "licensing"
    OTHER = "other"


@dataclass
class CostEntry:
    """A single cost record."""
    cost_id: str
    name: str
    amount_usd: float
    category: CostCategory
    bot_name: Optional[str] = None
    division: Optional[str] = None
    recurring_monthly: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CostTracking:
    """
    Cost Tracking — empire-wide cost analytics and budget management.
    """

    def __init__(self, monthly_budget_usd: float = 0.0) -> None:
        self._entries: list[CostEntry] = []
        self._monthly_budget_usd = monthly_budget_usd
        self._counter: int = 0

    def set_budget(self, monthly_budget_usd: float) -> None:
        """Set the monthly budget ceiling."""
        self._monthly_budget_usd = monthly_budget_usd

    def record_cost(
        self,
        name: str,
        amount_usd: float,
        category: CostCategory = CostCategory.OTHER,
        bot_name: Optional[str] = None,
        division: Optional[str] = None,
        recurring_monthly: bool = False,
    ) -> dict:
        """Record a new cost entry."""
        self._counter += 1
        entry = CostEntry(
            cost_id=f"cost_{self._counter:06d}",
            name=name,
            amount_usd=round(amount_usd, 2),
            category=category,
            bot_name=bot_name,
            division=division,
            recurring_monthly=recurring_monthly,
        )
        self._entries.append(entry)
        return {"cost_id": entry.cost_id, "name": name, "amount_usd": entry.amount_usd}

    def get_summary(self) -> dict:
        """Return cost breakdown by category, bot, and division."""
        total = sum(e.amount_usd for e in self._entries)
        by_category: dict[str, float] = {}
        by_bot: dict[str, float] = {}
        by_division: dict[str, float] = {}

        for e in self._entries:
            cat = e.category.value
            by_category[cat] = round(by_category.get(cat, 0.0) + e.amount_usd, 2)
            if e.bot_name:
                by_bot[e.bot_name] = round(by_bot.get(e.bot_name, 0.0) + e.amount_usd, 2)
            if e.division:
                by_division[e.division] = round(by_division.get(e.division, 0.0) + e.amount_usd, 2)

        over_budget = self._monthly_budget_usd > 0 and total > self._monthly_budget_usd
        return {
            "total_cost_usd": round(total, 2),
            "monthly_budget_usd": self._monthly_budget_usd,
            "budget_remaining_usd": round(max(0.0, self._monthly_budget_usd - total), 2),
            "over_budget": over_budget,
            "by_category": by_category,
            "by_bot": by_bot,
            "by_division": by_division,
            "total_entries": len(self._entries),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_top_costs(self, n: int = 5) -> list:
        """Return top N cost entries by amount."""
        sorted_entries = sorted(self._entries, key=lambda e: e.amount_usd, reverse=True)
        return [
            {"cost_id": e.cost_id, "name": e.name, "amount_usd": e.amount_usd, "category": e.category.value}
            for e in sorted_entries[:n]
        ]

    def get_recurring_monthly(self) -> float:
        """Return total of all recurring monthly costs."""
        return round(sum(e.amount_usd for e in self._entries if e.recurring_monthly), 2)
