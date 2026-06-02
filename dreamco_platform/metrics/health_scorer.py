"""Health scoring utilities for DreamCo bots."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class HealthReport:
    bot_id: str
    score: float
    grade: str
    telemetry: dict[str, Any]


def _grade(score: float) -> str:
    if score >= 0.9:
        return "A"
    if score >= 0.8:
        return "B"
    if score >= 0.7:
        return "C"
    if score >= 0.6:
        return "D"
    return "F"


def compute_health_score(bot_id: str, telemetry: dict[str, Any], coverage: float) -> float:
    latency_component = max(0.0, 1 - min(float(telemetry.get("p95_latency_s", 10.0)) / 5.0, 1.0))
    error_component = max(0.0, 1 - min(float(telemetry.get("error_rate", 1.0)), 1.0))
    deploy_age_component = min(float(telemetry.get("deploy_age_days", 0)) / 30.0, 1.0)
    coverage_component = max(0.0, min(coverage, 1.0))
    return round(
        latency_component * 0.30 + error_component * 0.30 + deploy_age_component * 0.20 + coverage_component * 0.20,
        4,
    )


def build_health_report(bot_id: str, telemetry: dict[str, Any], coverage: float) -> HealthReport:
    score = compute_health_score(bot_id, telemetry, coverage)
    return HealthReport(bot_id=bot_id, score=score, grade=_grade(score), telemetry=telemetry)
