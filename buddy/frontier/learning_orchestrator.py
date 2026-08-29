"""Deterministic capability-learning orchestration primitives.

This module intentionally does not train models or auto-close production work by
itself. It creates auditable learning jobs from benchmark failures and requires
independent validation before a capability is promoted.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class LearningAction(str, Enum):
    RETRIEVE = "retrieve"
    TOOL = "tool"
    TRAIN = "train"
    ROUTING = "routing"
    ARCHITECTURE = "architecture"
    HUMAN_REVIEW = "human_review"


@dataclass(frozen=True)
class EvaluationFailure:
    evaluation_id: str
    capability: str
    failure_mode: str
    baseline_score: float
    current_score: float
    external_assistance_used: bool = False
    evidence_refs: tuple[str, ...] = ()


@dataclass
class LearningJob:
    capability: str
    action: LearningAction
    source_failures: list[str] = field(default_factory=list)
    regression_tests: list[str] = field(default_factory=list)
    held_out_required: bool = True
    status: str = "proposed"


def propose_learning_jobs(failures: Iterable[EvaluationFailure]) -> list[LearningJob]:
    """Cluster failures by capability/failure mode into bounded learning jobs."""
    groups: dict[tuple[str, str], LearningJob] = {}
    for failure in failures:
        key = (failure.capability, failure.failure_mode)
        job = groups.get(key)
        if job is None:
            job = LearningJob(
                capability=failure.capability,
                action=LearningAction.TOOL if failure.failure_mode.startswith("tool") else LearningAction.TRAIN,
            )
            groups[key] = job
        job.source_failures.append(failure.evaluation_id)
        job.regression_tests.extend(failure.evidence_refs)
    return list(groups.values())


def can_promote(*, held_out_passed: bool, regression_passed: bool, safety_passed: bool) -> bool:
    """Promotion requires independent held-out, regression, and safety evidence."""
    return held_out_passed and regression_passed and safety_passed
