"""Small, auditable controller for Buddy's continuous learning loop."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EventType(str, Enum):
    BENCHMARK = "benchmark"
    ISSUE_REPAIR = "issue_repair"
    CI_RECOVERY = "ci_recovery"
    TOOL_OUTCOME = "tool_outcome"
    EXTERNAL_ASSISTANCE = "external_assistance"
    USER_CORRECTION = "user_correction"


@dataclass(frozen=True)
class LearningEvent:
    event_id: str
    event_type: EventType
    capability: str
    success: bool
    verified: bool
    regression_passed: bool
    safety_passed: bool
    external_assistance: bool = False


@dataclass(frozen=True)
class LearningDecision:
    learn: bool
    promote: bool
    reason: str


def evaluate_event(event: LearningEvent) -> LearningDecision:
    """Decide whether an event is usable evidence and whether it can be promoted."""
    if not event.verified:
        return LearningDecision(True, False, "unverified evidence; retain for diagnosis only")
    if not event.success:
        return LearningDecision(True, False, "verified failure; create or update a learning task")
    if not event.regression_passed:
        return LearningDecision(True, False, "regression failure blocks promotion")
    if not event.safety_passed:
        return LearningDecision(True, False, "safety failure blocks promotion")
    return LearningDecision(True, True, "verified success passed regression and safety gates")
