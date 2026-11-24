"""Small, auditable controller for Buddy's continuous learning loop."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


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
    evidence_refs: tuple[str, ...] = ()
    run_id: str = ""
    commit_sha: str = ""
    baseline_ref: str = ""
    holdout_ref: str = ""
    regression_ref: str = ""
    safety_ref: str = ""


@dataclass(frozen=True)
class LearningDecision:
    learn: bool
    promote: bool
    reason: str


def _missing_promotion_evidence(event: LearningEvent) -> list[str]:
    """Return provenance fields that prevent an event from being promoted."""
    missing: list[str] = []
    if (
        not isinstance(event.evidence_refs, tuple)
        or not event.evidence_refs
        or any(not isinstance(ref, str) or not ref.strip() for ref in event.evidence_refs)
    ):
        missing.append("evidence_refs")

    required_refs = {
        "run_id": event.run_id,
        "baseline_ref": event.baseline_ref,
        "holdout_ref": event.holdout_ref,
        "regression_ref": event.regression_ref,
        "safety_ref": event.safety_ref,
    }
    missing.extend(
        name for name, value in required_refs.items()
        if not isinstance(value, str) or not value.strip()
    )

    if not isinstance(event.commit_sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", event.commit_sha):
        missing.append("commit_sha")
    return missing


def evaluate_event(event: LearningEvent) -> LearningDecision:
    """Decide whether an event is usable evidence and whether it can be promoted.

    Success flags are necessary but not sufficient: promotion also requires
    traceable run, commit, baseline, independent holdout, regression, safety,
    and artifact references. Inventory and catalog records cannot be promoted.
    """
    if not event.verified:
        return LearningDecision(True, False, "unverified evidence; retain for diagnosis only")
    if not event.success:
        return LearningDecision(True, False, "verified failure; create or update a learning task")
    if not event.regression_passed:
        return LearningDecision(True, False, "regression failure blocks promotion")
    if not event.safety_passed:
        return LearningDecision(True, False, "safety failure blocks promotion")

    missing = _missing_promotion_evidence(event)
    if missing:
        return LearningDecision(
            True,
            False,
            "missing promotion provenance: " + ", ".join(missing),
        )
    return LearningDecision(True, True, "verified success with complete provenance passed promotion gates")
