"""
dashboard.py – Reporting & Visualization for Residual Income Streams.

Generates human-readable text reports and JSON data exports for income,
traffic, and engagement metrics.  Output can be printed to the console
or written to the ``dashboard_output_dir`` configured in ``config.py``.
"""

from __future__ import annotations

import datetime
import json
import logging
import os
from typing import Any

from .event_bus import EventBus
from .income_tracker import IncomeRecord

logger = logging.getLogger(__name__)


class Dashboard:
    """
    Renders income, traffic, and engagement data as formatted reports.

    Usage::

        dash = Dashboard(cfg, bus)
        dash.render(records, summary)
        dash.save_report(summary, filename="report_2024-01.json")
    """

    def __init__(self, cfg: dict, bus: EventBus) -> None:
        self.cfg = cfg
        self.bus = bus
        self.output_dir = cfg.get("dashboard_output_dir", "output/dashboard")
        self.report_format = cfg.get("report_format", "text")

        # Auto-render whenever income is summarized
        bus.subscribe("income.summarized", self._on_summary)

    # ------------------------------------------------------------------
    # Event handler
    # ------------------------------------------------------------------

    def _on_summary(self, summary: dict) -> None:
        self.print_summary(summary)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(
        self,
        records: list[IncomeRecord],
        summary: dict[str, Any],
        *,
        save: bool = False,
    ) -> str:
        """
        Build and return a formatted report string.

        If *save* is ``True`` the report is also written to disk.
        """
        report = self._build_text_report(records, summary)
        if save:
            self._write_report(summary, report)
        return report

    def print_summary(self, summary: dict[str, Any]) -> None:
        """Print a concise summary table to stdout."""
        sep = "─" * 60
        print(f"\n{'═' * 60}")
        print(f"  {self.cfg.get('buddy_bot_name', 'BuddyBot')} — Income Dashboard")
        print(f"  {summary.get('date', datetime.date.today().isoformat())}")
        print(f"{'═' * 60}")
        print(f"  Total Revenue  : ${summary.get('total_revenue', 0):>10,.2f}")
        print(f"  Total Traffic  : {summary.get('total_traffic', 0):>12,}")
        print(f"  Sources Tracked: {summary.get('source_count', 0):>12}")
        print(f"  Top Source     : {summary.get('top_source', 'N/A'):>12}  "
              f"(${summary.get('top_revenue', 0):,.2f})")
        print(sep)
        by_source = summary.get("by_source", {})
        if by_source:
            print(f"  {'Source':<14} {'Revenue':>10}  {'Traffic':>10}  {'Engagement':>10}")
            print(f"  {'-'*14} {'-'*10}  {'-'*10}  {'-'*10}")
            for src, data in by_source.items():
                print(
                    f"  {src:<14} ${data['revenue']:>9,.2f}  "
                    f"{data['traffic']:>10,}  {data['engagement']:>10.2f}"
                )
        print(f"{'═' * 60}\n")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_text_report(
        self, records: list[IncomeRecord], summary: dict[str, Any]
    ) -> str:
        lines: list[str] = []
        lines.append("=" * 70)
        lines.append(
            f"BuddyBot Residual Income Report — {summary.get('date', '')}"
        )
        lines.append("=" * 70)
        lines.append(f"Total Revenue : ${summary.get('total_revenue', 0):,.2f}")
        lines.append(f"Total Traffic : {summary.get('total_traffic', 0):,}")
        lines.append(f"Sources       : {summary.get('source_count', 0)}")
        lines.append(f"Top Source    : {summary.get('top_source', 'N/A')} "
                     f"(${summary.get('top_revenue', 0):,.2f})")
        lines.append("-" * 70)
        lines.append(
            f"{'Source':<14} {'Revenue':>10}  {'Traffic':>12}  {'Engagement':>12}"
        )
        lines.append("-" * 70)
        for record in records:
            lines.append(
                f"{record.source:<14} ${record.revenue:>9,.2f}  "
                f"{record.traffic:>12,}  {record.engagement:>12.2f}"
            )
        lines.append("=" * 70)
        return "\n".join(lines)

    def _write_report(self, summary: dict, text_report: str) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        date_str = summary.get("date", datetime.date.today().isoformat())
        if self.report_format == "json":
            filename = os.path.join(self.output_dir, f"report_{date_str}.json")
            with open(filename, "w", encoding="utf-8") as fh:
                json.dump(summary, fh, indent=2)
        else:
            filename = os.path.join(self.output_dir, f"report_{date_str}.txt")
            with open(filename, "w", encoding="utf-8") as fh:
                fh.write(text_report)
        logger.info("Report saved to %s", filename)
        self.bus.publish("dashboard.report_saved", {"filename": filename})

    def save_report(
        self, summary: dict[str, Any], filename: str | None = None
    ) -> str:
        """Persist a JSON summary report and return the file path."""
        os.makedirs(self.output_dir, exist_ok=True)
        if filename is None:
            date_str = summary.get("date", datetime.date.today().isoformat())
            filename = f"report_{date_str}.json"
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
        logger.info("Summary report saved to %s", path)
        return path
