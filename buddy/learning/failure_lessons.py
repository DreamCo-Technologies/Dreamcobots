#!/usr/bin/env python3
"""Lessons from the actions health report. Unknown is not a failure or a pass."""
from __future__ import annotations

import json

REPORT = {
    "source": "website/data/actions-health-report.json",
    "workflows": 72,
    "static_failing": 0,
    "runtime_failing": 0,
    "runtime_unknown": 72,
    "benchmark_workflows_without_a_run": 31,
    "recommended_upgrades": 37,
}

MISSING = [
    "Runtime evidence for the 72 workflows. Unknown is not a score.",
    "A hidden test for any model Buddy would train.",
    "A weight file this project is allowed to train.",
    "The reading ranges 301–400 and 601–1000.",
    "A published score on a public exam.",
    "A GitHub App, installed by you, before Buddy can write to the repository.",
]


def learn() -> dict:
    if REPORT["static_failing"] or REPORT["runtime_failing"]:
        failed = REPORT["static_failing"] + REPORT["runtime_failing"]
    else:
        failed = 0
    return {
        "failed_benchmarks": failed,
        "unknown_runs": REPORT["runtime_unknown"],
        "benchmark_workflows_without_a_run": REPORT["benchmark_workflows_without_a_run"],
        "lessons": [
            "Do not turn an unknown Actions run into a pass.",
            "31 benchmark workflows have commands and no run evidence. That is a missing result, not a failed score.",
            "37 workflows have a recommended upgrade. An upgrade note is not a trained model.",
            "A frontier score needs a model and a hidden exam. This repository has neither.",
        ],
        "missing": MISSING,
        "frontier_model": False,
        "agi": False,
        "singularity": False,
    }


if __name__ == "__main__":
    report = learn()
    assert report["failed_benchmarks"] == 0
    assert report["unknown_runs"] == 72
    assert report["agi"] is False and report["singularity"] is False
    assert len(report["missing"]) == 6
    print(json.dumps({"failed": report["failed_benchmarks"], "unknown": report["unknown_runs"], "agi": False}))
