"""
DreamCo OS — Bot Lifecycle States
===================================

Every DreamCoBot must be in exactly one of these states at all times.

Allowed transitions
-------------------
IDLE → RUNNING           (dispatch called)
RUNNING → IDLE           (run completed successfully)
RUNNING → QUARANTINED    (circuit breaker tripped after 3 errors)
QUARANTINED → IDLE       (manual release by operator)
RUNNING → STOPPED        (kill switch triggered)
IDLE → STOPPED           (graceful shutdown)
STOPPED → IDLE           (restart)
"""

from __future__ import annotations

from enum import Enum


class BotState(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    QUARANTINED = "QUARANTINED"
    STOPPED = "STOPPED"


# Adjacency map — source state → set of valid next states
_VALID_TRANSITIONS: dict[BotState, set[BotState]] = {
    BotState.IDLE: {BotState.RUNNING, BotState.STOPPED},
    BotState.RUNNING: {BotState.IDLE, BotState.QUARANTINED, BotState.STOPPED},
    BotState.QUARANTINED: {BotState.IDLE, BotState.STOPPED},
    BotState.STOPPED: {BotState.IDLE},
}


class IllegalStateTransitionError(Exception):
    """Raised when a state transition is not permitted by the lifecycle machine."""


def assert_transition(current: BotState, next_state: BotState) -> None:
    """Raise *IllegalStateTransitionError* if the transition is not allowed."""
    allowed = _VALID_TRANSITIONS.get(current, set())
    if next_state not in allowed:
        raise IllegalStateTransitionError(
            f"Transition {current.value} → {next_state.value} is not permitted. "
            f"Valid transitions from {current.value}: {[s.value for s in allowed]}"
        )
