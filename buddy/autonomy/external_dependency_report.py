"""Small, dependency-free report generator for Buddy autonomy telemetry."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskObservation:
    used_external_model: bool = False
    used_external_bot: bool = False
    completed: bool = True
    native_success: bool = False


def summarize(observations: list[TaskObservation]) -> dict[str, float]:
    eligible = [item for item in observations if item.completed]
    if not eligible:
        return {
            "eligible_tasks": 0,
            "external_dependency_ratio": 0.0,
            "native_success_rate": 0.0,
        }
    external = sum(item.used_external_model or item.used_external_bot for item in eligible)
    native = sum(item.native_success for item in eligible)
    return {
        "eligible_tasks": float(len(eligible)),
        "external_dependency_ratio": external / len(eligible),
        "native_success_rate": native / len(eligible),
    }
