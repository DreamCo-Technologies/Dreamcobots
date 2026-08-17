#!/usr/bin/env python3
"""Evidence-first Actions/PR recovery scanner.

This tool reports current health; it never rewrites historical GitHub results.
Use GitHub's API credentials/environment outside this script when integrating it
with a live Actions page. Repair operations must create reviewable changes.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

Status = Literal["green", "red", "yellow", "gray"]

@dataclass(frozen=True)
class Finding:
    category: str
    severity: str
    status: Status
    title: str
    evidence: str
    recommended_action: str


def benchmark_percentages(results: list[Status]) -> dict[str, float | int]:
    green = results.count("green")
    red = results.count("red")
    measured = green + red
    return {
        "green": green,
        "red": red,
        "yellow": results.count("yellow"),
        "gray": results.count("gray"),
        "measured": measured,
        "green_pct": round(green / measured * 100, 2) if measured else 0.0,
        "red_pct": round(red / measured * 100, 2) if measured else 0.0,
    }


def classify_build_failure(title: str, evidence: str) -> Finding:
    return Finding(
        category="actions",
        severity="high",
        status="red",
        title=title,
        evidence=evidence,
        recommended_action="Reproduce the failure, identify root cause, create the smallest reviewable repair, then rerun targeted verification.",
    )


def dashboard_payload(findings: list[Finding], benchmark_results: list[Status]) -> dict:
    return {
        "policy": {
            "historical_runs_are_immutable": True,
            "auto_merge": False,
            "destructive_repairs": False,
            "green_requires_current_evidence": True,
        },
        "benchmarks": benchmark_percentages(benchmark_results),
        "findings": [asdict(item) for item in findings],
    }


if __name__ == "__main__":
    # Smoke-test the calculation without claiming repository health.
    sample = benchmark_percentages(["green", "green", "red", "yellow", "gray"])
    assert sample["green_pct"] == 66.67
    assert sample["red_pct"] == 33.33
    print("Actions recovery scanner self-test: PASS")
