#!/usr/bin/env python3
"""One lesson from every benchmark in the index. A missing run is not a pass."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "config" / "generated" / "buddy_benchmark_index.json"


def lesson(row: dict) -> str:
    name = row.get("name") or row["id"]
    live = int(row.get("live_results_completed") or 0)
    if live > 0:
        return name + ": a live result is on file. Keep that check. This process did not rerun it."
    command = row.get("check_command") or "its local contract"
    return name + ": no live result. The next run is " + command + ". Do not record a pass."


def learn() -> dict:
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    rows = list(data["programs"]) + list(data["repositorySuites"])
    lessons = [lesson(row) for row in rows]
    if len(lessons) != len(rows):
        raise RuntimeError("A benchmark was skipped.")
    live = sum(int(row.get("live_results_completed") or 0) for row in rows)
    return {
        "benchmarks": len(rows),
        "programs": len(data["programs"]),
        "suites": len(data["repositorySuites"]),
        "live_results": live,
        "lessons": lessons,
        "mastered": False,
        "weights_trained": False,
    }


if __name__ == "__main__":
    report = learn()
    assert report["benchmarks"] == report["programs"] + report["suites"]
    assert report["benchmarks"] == 40
    assert report["live_results"] == 0
    assert report["mastered"] is False
    assert all("Do not record a pass." in line for line in report["lessons"])
    print(json.dumps({"benchmarks": report["benchmarks"], "live_results": 0, "mastered": False}))
