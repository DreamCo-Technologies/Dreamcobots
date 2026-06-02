"""Merge chaos-testing signals with benchmark data for DreamCo reports."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"


class ChaosBenchmarkIntegrator:
    """Combine chaos history with benchmark output into one JSON report."""

    def __init__(self, reports_dir: Path | None = None) -> None:
        self.reports_dir = reports_dir or REPORTS_DIR

    def load_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text()) if path.exists() else {}

    def integrate(self) -> Path:
        benchmark_files = sorted(self.reports_dir.glob("benchmark_*.json"))
        benchmark = self.load_json(benchmark_files[-1]) if benchmark_files else {"bots": {}}
        chaos = self.load_json(self.reports_dir / "chaos_history.json")
        merged = {"date": date.today().isoformat(), "bots": {}}
        for bot, metrics in benchmark.get("bots", {}).items():
            chaos_entry = chaos.get(bot, {})
            merged["bots"][bot] = {
                **metrics,
                "failure_rate": chaos_entry.get("failure_rate", 0.0),
                "recovery_time": chaos_entry.get("recovery_time", 0.0),
                "data_loss_events": chaos_entry.get("data_loss_events", 0),
            }
        output = self.reports_dir / f"chaos_{date.today().isoformat()}.json"
        output.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n")
        return output


def main() -> None:
    integrator = ChaosBenchmarkIntegrator()
    print(integrator.integrate())


if __name__ == "__main__":
    main()
