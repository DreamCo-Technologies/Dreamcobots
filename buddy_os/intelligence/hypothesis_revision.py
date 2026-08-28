"""Versioned, auditable hypothesis revision for Buddy."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HypothesisRevision:
    revision_id: str
    hypothesis_id: str
    parent_revision_id: str | None
    action: str
    rationale: str
    confidence: float
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.action not in {"strengthen", "weaken", "split", "merge", "retire", "retain"}:
            raise ValueError("invalid revision action")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.rationale.strip():
            raise ValueError("rationale cannot be empty")


class HypothesisRevisionLog:
    def __init__(self) -> None:
        self._revisions: dict[str, HypothesisRevision] = {}

    def record(self, revision: HypothesisRevision) -> None:
        if revision.revision_id in self._revisions:
            raise ValueError(f"duplicate revision: {revision.revision_id}")
        if revision.parent_revision_id is not None and revision.parent_revision_id not in self._revisions:
            raise KeyError(f"unknown parent revision: {revision.parent_revision_id}")
        self._revisions[revision.revision_id] = revision

    def history(self, hypothesis_id: str) -> tuple[HypothesisRevision, ...]:
        return tuple(r for r in self._revisions.values() if r.hypothesis_id == hypothesis_id)

    def latest(self, hypothesis_id: str) -> HypothesisRevision | None:
        rows = self.history(hypothesis_id)
        return rows[-1] if rows else None
