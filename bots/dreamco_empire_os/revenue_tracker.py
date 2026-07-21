"""
DreamCo Empire OS — Revenue Tracker Module

Real-time revenue dashboard: tracks gross/net revenue, bot performance
contributions, projections, and MRR/ARR metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from framework import GlobalAISourcesFlow  # noqa: F401


@dataclass
class RevenueEntry:
    """A single revenue event."""
    entry_id: str
    source: str
    amount_usd: float
    category: str = "general"
    bot_name: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RevenueTracker:
    """
    Revenue Tracker — real-time revenue analytics for the empire.

    Tracks per-source and per-bot revenue, computes MRR/ARR projections,
    and surfaces top-performing revenue channels.
    """

    def __init__(self) -> None:
        self._entries: list[RevenueEntry] = []
        self._costs: list[dict] = []
        self._counter: int = 0

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_revenue(
        self,
        source: str,
        amount_usd: float,
        category: str = "general",
        bot_name: Optional[str] = None,
    ) -> dict:
        """Record a revenue event."""
        self._counter += 1
        entry = RevenueEntry(
            entry_id=f"rev_{self._counter:06d}",
            source=source,
            amount_usd=round(amount_usd, 2),
            category=category,
            bot_name=bot_name,
        )
        self._entries.append(entry)
        return {"entry_id": entry.entry_id, "source": source, "amount_usd": entry.amount_usd}

    def record_cost(self, source: str, amount_usd: float, category: str = "general") -> dict:
        """Record an operational cost."""
        entry = {
            "source": source,
            "amount_usd": round(amount_usd, 2),
            "category": category,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._costs.append(entry)
        return entry

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        """Return comprehensive revenue summary."""
        gross = sum(e.amount_usd for e in self._entries)
        total_costs = sum(c["amount_usd"] for c in self._costs)
        net = gross - total_costs

        by_source: dict[str, float] = {}
        by_bot: dict[str, float] = {}
        by_category: dict[str, float] = {}

        for e in self._entries:
            by_source[e.source] = round(by_source.get(e.source, 0.0) + e.amount_usd, 2)
            by_category[e.category] = round(by_category.get(e.category, 0.0) + e.amount_usd, 2)
            if e.bot_name:
                by_bot[e.bot_name] = round(by_bot.get(e.bot_name, 0.0) + e.amount_usd, 2)

        return {
            "gross_revenue_usd": round(gross, 2),
            "total_costs_usd": round(total_costs, 2),
            "net_revenue_usd": round(net, 2),
            "profit_margin_pct": round((net / gross * 100) if gross > 0 else 0.0, 1),
            "revenue_by_source": by_source,
            "revenue_by_bot": by_bot,
            "revenue_by_category": by_category,
            "total_entries": len(self._entries),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_top_sources(self, n: int = 5) -> list:
        """Return the top N revenue sources by total amount."""
        summary = self.get_summary()
        sorted_sources = sorted(summary["revenue_by_source"].items(), key=lambda x: x[1], reverse=True)
        return [{"source": s, "revenue_usd": v} for s, v in sorted_sources[:n]]

    def get_mrr(self) -> float:
        """Estimate Monthly Recurring Revenue from all entries."""
        return round(sum(e.amount_usd for e in self._entries), 2)

    def get_arr(self) -> float:
        """Estimate Annual Recurring Revenue (MRR × 12)."""
        return round(self.get_mrr() * 12, 2)

    def get_recent_entries(self, limit: int = 20) -> list:
        """Return the most recent revenue entries."""
        return [
            {
                "entry_id": e.entry_id,
                "source": e.source,
                "amount_usd": e.amount_usd,
                "category": e.category,
                "bot_name": e.bot_name,
                "timestamp": e.timestamp,
            }
            for e in self._entries[-limit:]
        ]
