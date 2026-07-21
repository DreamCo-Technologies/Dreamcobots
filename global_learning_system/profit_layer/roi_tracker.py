"""
roi_tracker.py — Evaluates ROI for AI solution deployments.

Tracks revenue, cost, and profit metrics for each deployed AI strategy
and calculates return on investment over configurable time windows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class ROIRecord:
    """A single ROI data point for a strategy."""

    strategy_id: str
    period: str  # e.g. "2025-Q1"
    revenue: float
    cost: float
    recorded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def profit(self) -> float:
        return self.revenue - self.cost

    @property
    def roi(self) -> float:
        """Return ROI as a fraction; returns 0 when cost is zero."""
        if self.cost == 0:
            return 0.0
        return self.profit / self.cost


class ROITracker:
    """
    Tracks and analyses ROI across AI strategy deployments.

    Parameters
    ----------
    currency : str
        Display currency label (default ``"USD"``).
    """

    def __init__(self, currency: str = "USD"):
        self.currency = currency
        self._records: List[ROIRecord] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def record(
        self,
        strategy_id: str,
        period: str,
        revenue: float,
        cost: float,
    ) -> ROIRecord:
        """
        Record a revenue/cost observation for *strategy_id*.

        Parameters
        ----------
        strategy_id : str
        period : str
            Reporting period label (e.g. ``"2025-Q1"``).
        revenue : float
        cost : float

        Returns
        -------
        ROIRecord
        """
        if revenue < 0 or cost < 0:
            raise ValueError("revenue and cost must be non-negative.")
        rec = ROIRecord(strategy_id=strategy_id, period=period, revenue=revenue, cost=cost)
        self._records.append(rec)
        return rec

    def summary(self, strategy_id: Optional[str] = None) -> Dict[str, float]:
        """
        Return aggregated totals and ROI.

        Parameters
        ----------
        strategy_id : str | None
            Filter records by strategy; ``None`` aggregates all.
        """
        records = self._records
        if strategy_id is not None:
            records = [r for r in records if r.strategy_id == strategy_id]
        if not records:
            return {"total_revenue": 0.0, "total_cost": 0.0, "total_profit": 0.0, "roi": 0.0}

        total_revenue = sum(r.revenue for r in records)
        total_cost = sum(r.cost for r in records)
        total_profit = total_revenue - total_cost
        roi = total_profit / total_cost if total_cost > 0 else 0.0

        return {
            "total_revenue": round(total_revenue, 2),
            "total_cost": round(total_cost, 2),
            "total_profit": round(total_profit, 2),
            "roi": round(roi, 6),
        }

    def get_records(self, strategy_id: Optional[str] = None) -> List[ROIRecord]:
        """Return all records, optionally filtered by *strategy_id*."""
        if strategy_id is not None:
            return [r for r in self._records if r.strategy_id == strategy_id]
        return list(self._records)

    def top_strategies(self, top_n: int = 5) -> List[Dict]:
        """
        Return the *top_n* strategies sorted by ROI (highest first).

        Returns
        -------
        list[dict] with keys: ``strategy_id``, ``roi``, ``total_profit``.
        """
        strategy_ids = {r.strategy_id for r in self._records}
        ranked = []
        for sid in strategy_ids:
            s = self.summary(sid)
            ranked.append({"strategy_id": sid, "roi": s["roi"], "total_profit": s["total_profit"]})
        ranked.sort(key=lambda x: x["roi"], reverse=True)
        return ranked[:top_n]
