"""
profit_dashboard.py — Dashboard for market performance tracking.

Aggregates ROI records and market signals from the profit layer and
renders an executive-level summary of financial performance.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class ProfitDashboard:
    """
    Renders a summary of profit and market-adaptation metrics.

    Parameters
    ----------
    title : str
        Dashboard title.
    currency : str
        Display currency label.
    """

    def __init__(self, title: str = "DreamCo Profit Intelligence Dashboard", currency: str = "USD"):
        self.title = title
        self.currency = currency
        self._roi_records: List[Dict[str, Any]] = []
        self._market_signals: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def record_roi(self, record: Dict[str, Any]) -> None:
        """
        Ingest an ROI record.

        Expected keys: ``strategy_id``, ``revenue``, ``cost``.
        """
        self._roi_records.append(record)

    def record_signal(self, signal: Dict[str, Any]) -> None:
        """
        Ingest a market signal.

        Expected keys: ``strategy_id``, ``value``, ``alert``.
        """
        self._market_signals.append(signal)

    def render(self) -> str:
        """
        Render the profit dashboard as a formatted string.

        Returns
        -------
        str
        """
        total_revenue = sum(r.get("revenue", 0.0) for r in self._roi_records)
        total_cost = sum(r.get("cost", 0.0) for r in self._roi_records)
        total_profit = total_revenue - total_cost
        roi = total_profit / total_cost if total_cost > 0 else 0.0
        alert_count = sum(1 for s in self._market_signals if s.get("alert"))

        lines = [
            "=" * 60,
            f"  {self.title}",
            "=" * 60,
            f"  Currency       : {self.currency}",
            f"  Total Revenue  : {total_revenue:,.2f}",
            f"  Total Cost     : {total_cost:,.2f}",
            f"  Total Profit   : {total_profit:,.2f}",
            f"  ROI            : {roi:.2%}",
            f"  Market Alerts  : {alert_count}",
            "=" * 60,
        ]

        output = "\n".join(lines)
        print(output)
        return output

    def summary(self) -> Dict[str, Any]:
        """Return financial summary statistics."""
        total_revenue = sum(r.get("revenue", 0.0) for r in self._roi_records)
        total_cost = sum(r.get("cost", 0.0) for r in self._roi_records)
        total_profit = total_revenue - total_cost
        roi = total_profit / total_cost if total_cost > 0 else 0.0
        return {
            "total_revenue": round(total_revenue, 2),
            "total_cost": round(total_cost, 2),
            "total_profit": round(total_profit, 2),
            "roi": round(roi, 6),
            "market_alert_count": sum(1 for s in self._market_signals if s.get("alert")),
        }

    def clear(self) -> None:
        """Clear all recorded data."""
        self._roi_records = []
        self._market_signals = []
