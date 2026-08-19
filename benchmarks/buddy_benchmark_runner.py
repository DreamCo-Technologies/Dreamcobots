#!/usr/bin/env python3
"""Free-first, offline-friendly benchmark runner for Buddy.

This runner deliberately uses only the Python standard library. It turns a
machine-readable benchmark task file into deterministic benchmark records.
It does not call paid models or external services. Model execution can be
plugged in later through an authorized adapter.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


MASTERY_STATES = ("discovered", "learned", "practiced", "mastered", "production_proven")


@dataclass
class BenchmarkResult:
    benchmark_id: int
    task_id: str
    status: str
    score: float
    threshold: float
    passed: bool
    duration_seconds: float
    cost_usd: float
    model_route: str
    human_intervention: bool = False
    failures: list[str] = field(default_factory=list)
    remediation: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)


def load_tasks(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        raise ValueError("Benchmark file must contain a top-level 'tasks' list")
    return data


def evaluate_task(task: dict[str, Any], score: float | None = None) -> BenchmarkResult:
    started = time.monotonic()
    benchmark_id = int(task.get("benchmark_id", 1000))
    task_id = str(task["task_id"])
    threshold = float(task.get("mastery_threshold", 0.9))
    measured_score = float(task.get("baseline_score", 0.0) if score is None else score)
    passed = measured_score >= threshold
    failures: list[str] = [] if passed else ["benchmark_gap"]
    remediation = [] if passed else ["identify_gap", "run_targeted_practice", "retest"]
    evidence = ["deterministic_local_runner"]
    return BenchmarkResult(
        benchmark_id=benchmark_id,
        task_id=task_id,
        status="mastered" if passed else "practiced",
        score=measured_score,
        threshold=threshold,
        passed=passed,
        duration_seconds=time.monotonic() - started,
        cost_usd=0.0,
        model_route="free-first/local-runner",
        failures=failures,
        remediation=remediation,
        evidence=evidence,
    )


def run(path: Path, score_override: float | None = None) -> dict[str, Any]:
    data = load_tasks(path)
    results = [evaluate_task(task, score_override) for task in data["tasks"]]
    passed = sum(result.passed for result in results)
    return {
        "benchmark_id": int(data.get("benchmark_id", 1000)),
        "tasks": len(results),
        "passed": passed,
        "pass_rate": passed / len(results) if results else 0.0,
        "cost_usd": 0.0,
        "free_first": True,
        "results": [asdict(result) for result in results],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Buddy benchmark tasks locally.")
    parser.add_argument("tasks", type=Path, help="JSON benchmark task file")
    parser.add_argument("--score", type=float, default=None, help="Optional deterministic score override")
    parser.add_argument("--output", type=Path, default=None, help="Write JSON results to this file")
    args = parser.parse_args()
    report = run(args.tasks, args.score)
    encoded = json.dumps(report, indent=2, sort_keys=True)
    print(encoded)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
