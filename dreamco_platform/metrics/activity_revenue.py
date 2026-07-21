"""Attach revenue attribution to activity events and query the resulting ledger."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class BotActivity:
    activity_id: str
    bot_id: str
    timestamp: str
    action: str
    revenue_attributed_usd: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class ActivityRevenueLedger:
    """Persist attributed revenue events in memory for analytics surfaces."""

    def __init__(self) -> None:
        self._entries: list[BotActivity] = []

    def append(self, entry: BotActivity) -> BotActivity:
        self._entries.append(entry)
        return entry

    def query_by_bot(self, bot_id: str) -> list[BotActivity]:
        return [entry for entry in self._entries if entry.bot_id == bot_id]

    def query_by_period(self, start: str, end: str) -> list[BotActivity]:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        return [entry for entry in self._entries if start_dt <= datetime.fromisoformat(entry.timestamp) <= end_dt]

    def daily_totals(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        for entry in self._entries:
            day = entry.timestamp[:10]
            totals[day] = totals.get(day, 0.0) + entry.revenue_attributed_usd
        return totals

    def serialize(self) -> list[dict[str, Any]]:
        return [asdict(entry) for entry in self._entries]
