"""Lifecycle and trust gates for Buddy digital assets."""
from __future__ import annotations

from typing import Final, Set

LIFECYCLE_STATES: Final = ("discovered", "quarantined", "evaluating", "verified", "approved", "deprecated", "revoked")

_ALLOWED = {
    "discovered": {"quarantined", "evaluating", "deprecated"},
    "quarantined": {"evaluating", "revoked", "deprecated"},
    "evaluating": {"verified", "quarantined", "deprecated"},
    "verified": {"approved", "evaluating", "deprecated"},
    "approved": {"evaluating", "deprecated", "revoked"},
    "deprecated": {"revoked"},
    "revoked": set(),
}


def can_transition(current: str, target: str) -> bool:
    if current not in LIFECYCLE_STATES or target not in LIFECYCLE_STATES:
        raise ValueError("unknown lifecycle state")
    return target in _ALLOWED[current]


def require_transition(current: str, target: str) -> str:
    if not can_transition(current, target):
        raise ValueError(f"invalid asset lifecycle transition: {current} -> {target}")
    return target


def execution_eligible(state: str, trust_score: float, risk_score: float) -> bool:
    """Conservative gate: registry state never substitutes for authorization."""
    return state == "approved" and trust_score >= 0.8 and risk_score <= 0.2
