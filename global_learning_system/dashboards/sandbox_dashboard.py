"""
sandbox_dashboard.py — Dashboard for sandbox testing.

Provides a summary view of sandbox experiment runs, including pass/fail
rates, average durations, and metric trends.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class SandboxDashboard:
    """
    Renders a summary view of sandbox experiment activity.

    Parameters
    ----------
    title : str
        Dashboard title.
    """

    def __init__(self, title: str = "DreamCo Sandbox Lab Dashboard"):
        self.title = title
        self._run_records: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def record_run(self, run: Dict[str, Any]) -> None:
        """
        Ingest a sandbox run record for display.

        The dict should contain at minimum:
        - ``experiment_name`` (str)
        - ``status`` (str)
        - ``duration_ms`` (float)
        - ``metrics`` (dict[str, float])
        """
        self._run_records.append(run)

    def render(self) -> str:
        """
        Render the sandbox dashboard as a formatted string.

        Returns
        -------
        str
        """
        total = len(self._run_records)
        success = sum(1 for r in self._run_records if r.get("status") == "success")
        failed = sum(1 for r in self._run_records if r.get("status") == "failed")
        durations = [r.get("duration_ms", 0.0) for r in self._run_records]
        avg_duration = sum(durations) / total if total > 0 else 0.0

        lines = [
            "=" * 60,
            f"  {self.title}",
            "=" * 60,
            f"  Total runs   : {total}",
            f"  Successful   : {success}",
            f"  Failed       : {failed}",
            f"  Avg duration : {avg_duration:.1f} ms",
            "",
            "  Recent runs:",
        ]
        for run in self._run_records[-5:]:
            name = run.get("experiment_name", "unknown")
            status = run.get("status", "unknown")
            dur = run.get("duration_ms", 0.0)
            lines.append(f"    [{status.upper():8s}] {name} ({dur:.1f} ms)")
        lines.append("=" * 60)

        output = "\n".join(lines)
        print(output)
        return output

    def summary(self) -> Dict[str, Any]:
        """Return aggregate statistics about recorded runs."""
        total = len(self._run_records)
        if total == 0:
            return {"total": 0, "success": 0, "failed": 0, "avg_duration_ms": 0.0}
        success = sum(1 for r in self._run_records if r.get("status") == "success")
        failed = sum(1 for r in self._run_records if r.get("status") == "failed")
        durations = [r.get("duration_ms", 0.0) for r in self._run_records]
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "avg_duration_ms": round(sum(durations) / total, 3),
        }

    def clear(self) -> None:
        """Clear all recorded run data."""
        self._run_records = []
