#!/usr/bin/env python3
"""Small deterministic ledger for what Buddy tried, learned, and must not repeat."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass(frozen=True)
class LearningAttempt:
    capability: str
    strategy: str
    result: str
    score_before: float
    score_after: float
    lesson: str
    evidence_id: str = ""
    timestamp: str = ""

    def normalized(self) -> "LearningAttempt":
        return LearningAttempt(
            **{**asdict(self), "timestamp": self.timestamp or datetime.now(timezone.utc).isoformat()}
        )


def record_attempt(history: list[LearningAttempt], attempt: LearningAttempt) -> list[LearningAttempt]:
    """Append an immutable evidence record; callers can persist the returned list."""
    return [*history, attempt.normalized()]


def lessons_for(history: list[LearningAttempt], capability: str) -> list[str]:
    """Return unique lessons, newest evidence first, for targeted remediation."""
    seen: set[str] = set()
    lessons: list[str] = []
    for item in reversed(history):
        if item.capability != capability or not item.lesson.strip():
            continue
        if item.lesson not in seen:
            seen.add(item.lesson)
            lessons.append(item.lesson)
    return lessons


def regression_warning(history: list[LearningAttempt], capability: str, threshold: float = .9) -> bool:
    """Flag a capability whose latest measured score fell below the promotion threshold."""
    relevant = [item for item in history if item.capability == capability]
    return bool(relevant and relevant[-1].score_after < threshold)
