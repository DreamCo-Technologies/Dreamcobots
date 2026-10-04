"""Bot performance metrics.

A run is a recorded start, finish, and cost. The summary uses the median
time so one slow run does not hide the normal case. It does not mark a bot
production ready.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[2]


def record(bot: str, task: str, started_ms: int, finished_ms: int, ok: bool, model_calls: int) -> dict:
    if finished_ms < started_ms:
        raise ValueError("finish time is before start time")
    if model_calls < 0:
        raise ValueError("cost cannot be negative")
    return {"bot": bot, "task": task, "latency_ms": finished_ms - started_ms, "ok": ok, "model_calls": model_calls}


def summarize(runs: list[dict]) -> dict:
    if not runs:
        return {"runs": 0, "success_rate": None, "median_latency_ms": None, "median_model_calls": None, "production_ready": False}
    finished = [row for row in runs if row["ok"]]
    return {
        "runs": len(runs),
        "success_rate": len(finished) / len(runs),
        "median_latency_ms": median(row["latency_ms"] for row in runs),
        "median_model_calls": median(row["model_calls"] for row in runs),
        "production_ready": False,
    }


def main() -> int:
    runs = [record("catalog-updater", "count", 0, 40, True, 0), record("catalog-updater", "count", 0, 80, False, 1)]
    report = summarize(runs)
    path = ROOT / "reports" / "BOT_PERFORMANCE.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
