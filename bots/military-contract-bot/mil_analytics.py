"""
Performance analytics module for the Military Contract Bot.

Tracks runtime metrics, win rates, pipeline performance,
and provides continuous monitoring data for dashboard integration.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Optional


class PerformanceTracker:
    """Collects and aggregates runtime performance metrics."""

    def __init__(self) -> None:
        self._start_time: float = time.time()
        self._events: list[dict] = []
        self._counters: dict[str, int] = defaultdict(int)
        self._timings: dict[str, list[float]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Recording helpers
    # ------------------------------------------------------------------

    def record_event(self, event_type: str, metadata: Optional[dict] = None) -> None:
        """Record a named event with optional metadata."""
        self._events.append(
            {"ts": time.time(), "type": event_type, "meta": metadata or {}}
        )
        self._counters[event_type] += 1

    def record_timing(self, operation: str, elapsed_seconds: float) -> None:
        """Record how long an operation took."""
        self._timings[operation].append(elapsed_seconds)

    def increment(self, counter: str, amount: int = 1) -> None:
        """Increment a named counter."""
        self._counters[counter] += amount

    # ------------------------------------------------------------------
    # Contract / proposal tracking
    # ------------------------------------------------------------------

    def record_search(self, keyword: str, result_count: int) -> None:
        self.record_event("search", {"keyword": keyword, "results": result_count})
        self.increment("searches")

    def record_opportunity_viewed(self, opportunity_id: str) -> None:
        self.record_event("opportunity_viewed", {"id": opportunity_id})
        self.increment("opportunities_viewed")

    def record_proposal_submitted(self, opportunity_id: str) -> None:
        self.record_event("proposal_submitted", {"id": opportunity_id})
        self.increment("proposals_submitted")

    def record_contract_won(self, opportunity_id: str, value: float) -> None:
        self.record_event("contract_won", {"id": opportunity_id, "value": value})
        self.increment("contracts_won")
        self.increment("total_value_won", int(value))

    def record_contract_lost(self, opportunity_id: str) -> None:
        self.record_event("contract_lost", {"id": opportunity_id})
        self.increment("contracts_lost")

    # ------------------------------------------------------------------
    # Aggregate analytics
    # ------------------------------------------------------------------

    def win_rate(self) -> float:
        """Win rate as a percentage (won / (won + lost))."""
        won = self._counters.get("contracts_won", 0)
        lost = self._counters.get("contracts_lost", 0)
        total = won + lost
        return round(won / total * 100, 1) if total else 0.0

    def avg_timing(self, operation: str) -> float:
        """Average elapsed time for *operation* in seconds."""
        timings = self._timings.get(operation, [])
        return round(sum(timings) / len(timings), 4) if timings else 0.0

    def uptime_seconds(self) -> float:
        """Seconds since the tracker was created."""
        return round(time.time() - self._start_time, 1)

    def get_summary(self) -> dict[str, Any]:
        """Return a comprehensive analytics summary dict."""
        counters = dict(self._counters)
        timing_summary = {
            op: {
                "avg_sec": self.avg_timing(op),
                "calls": len(vals),
                "total_sec": round(sum(vals), 4),
            }
            for op, vals in self._timings.items()
        }
        return {
            "uptime_seconds": self.uptime_seconds(),
            "total_events": len(self._events),
            "counters": counters,
            "win_rate_pct": self.win_rate(),
            "timing_summary": timing_summary,
            "total_value_won_usd": counters.get("total_value_won", 0),
        }

    def get_recent_events(self, limit: int = 20) -> list[dict]:
        """Return the most recent *limit* events."""
        return self._events[-limit:]

    def reset(self) -> None:
        """Reset all counters, timings, and events."""
        self._start_time = time.time()
        self._events.clear()
        self._counters.clear()
        self._timings.clear()
