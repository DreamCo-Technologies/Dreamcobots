# BuddyAI Client Dashboard
# Aggregates metrics, earnings, compute usage, tasks, and stress-test results
# into a unified view for each client.

from typing import List, Optional

from .metrics import MetricsCollector, TaskRecord, ComputeSnapshot
from .stress_test import StressTestResult, StressTestRunner
from ..financial.models import Account, Transaction


class ClientDashboard:
    """
    Unified client dashboard for the BuddyAI financial system.

    Brings together:
    - Profitability metrics (earnings over time)
    - Compute usage (CPU / memory snapshots)
    - Task completion records
    - Data visualizations (ASCII charts for terminals; dict payloads for UIs)
    - Stress test results

    Example::

        dashboard = ClientDashboard(client_id="client-123", client_name="Alice")
        dashboard.metrics.record_task("t1", "data_scrape", 2.4)
        dashboard.metrics.record_earning(50.0)
        dashboard.metrics.record_compute_snapshot(cpu_percent=45.2, memory_percent=62.0)
        print(dashboard.render())
    """

    def __init__(
        self,
        client_id: str,
        client_name: str,
        account: Optional[Account] = None,
    ) -> None:
        self.client_id = client_id
        self.client_name = client_name
        self.account = account
        self.metrics = MetricsCollector(client_id=client_id)
        self.stress_runner = StressTestRunner()

    # ------------------------------------------------------------------
    # Dashboard rendering
    # ------------------------------------------------------------------

    def render(self) -> dict:
        """
        Return a structured dict representing the full dashboard state.

        This payload can be serialised to JSON and consumed by any frontend
        or printed directly for terminal monitoring.
        """
        summary = self.metrics.summary()
        snapshots = [s.to_dict() for s in self.metrics.get_compute_snapshots()]
        tasks = [t.to_dict() for t in self.metrics.get_tasks()]
        earnings_tl = self.metrics.earnings_timeline()
        stress_results = [r.to_dict() for r in self.stress_runner.list_results()]

        dashboard = {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "account_balance": self.account.balance if self.account else None,
            "profitability": {
                "total_earnings": summary["total_earnings"],
                "earnings_timeline": earnings_tl,
            },
            "compute_usage": {
                "average_cpu_percent": summary["average_cpu_percent"],
                "average_memory_percent": summary["average_memory_percent"],
                "snapshots": snapshots,
            },
            "tasks": {
                "completed": summary["tasks_completed"],
                "average_duration_seconds": summary["average_task_duration_seconds"],
                "records": tasks,
            },
            "stress_tests": stress_results,
            "visualizations": self._build_visualizations(),
        }
        return dashboard

    def print_summary(self) -> None:
        """Print a human-readable summary to stdout."""
        data = self.render()
        print("=" * 60)
        print(f"  BuddyAI Dashboard – {data['client_name']} ({data['client_id']})")
        print("=" * 60)

        bal = data["account_balance"]
        print(f"  Account Balance   : ${bal:.2f}" if bal is not None else "  Account Balance   : N/A")
        print(f"  Total Earnings    : ${data['profitability']['total_earnings']:.2f}")
        print(f"  Tasks Completed   : {data['tasks']['completed']}")
        print(f"  Avg Task Duration : {data['tasks']['average_duration_seconds']:.2f}s")
        print(f"  Avg CPU Usage     : {data['compute_usage']['average_cpu_percent']:.1f}%")
        print(f"  Avg Memory Usage  : {data['compute_usage']['average_memory_percent']:.1f}%")
        print(f"  Stress Tests Run  : {len(data['stress_tests'])}")
        print("-" * 60)

        # ASCII earnings bar chart
        if data["profitability"]["earnings_timeline"]:
            print("  Earnings Timeline (ASCII):")
            self._print_earnings_chart(data["profitability"]["earnings_timeline"])
            print()

        print("=" * 60)

    # ------------------------------------------------------------------
    # Visualizations
    # ------------------------------------------------------------------

    def _build_visualizations(self) -> dict:
        """
        Construct visualisation payloads for CPU, memory, and earnings trends.

        Each payload is a list of {x, y} points suitable for rendering with
        any charting library (e.g. Chart.js, Plotly, Recharts).
        """
        snapshots = self.metrics.get_compute_snapshots()
        cpu_series = [
            {"x": s.timestamp.isoformat(), "y": s.cpu_percent} for s in snapshots
        ]
        memory_series = [
            {"x": s.timestamp.isoformat(), "y": s.memory_percent} for s in snapshots
        ]
        earnings_series = [
            {"x": e["timestamp"], "y": e["amount"]}
            for e in self.metrics.earnings_timeline()
        ]

        return {
            "cpu_over_time": cpu_series,
            "memory_over_time": memory_series,
            "earnings_over_time": earnings_series,
        }

    @staticmethod
    def _print_earnings_chart(timeline: list, width: int = 40) -> None:
        """Simple ASCII bar chart of earnings values."""
        if not timeline:
            return
        amounts = [e["amount"] for e in timeline]
        max_val = max(amounts) or 1
        for entry in timeline:
            bar_len = int((entry["amount"] / max_val) * width)
            bar = "█" * bar_len
            ts = entry["timestamp"][:10]  # date portion only
            print(f"  {ts} | {bar} ${entry['amount']:.2f}")
