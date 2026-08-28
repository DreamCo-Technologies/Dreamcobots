"""Turn reasoning conflicts into explicit, auditable verification work."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class VerificationTask:
    task_id: str
    question: str
    priority: float
    falsifies: tuple[object, ...] = ()
    evidence_needed: tuple[str, ...] = ()
    status: str = "pending"

    def __post_init__(self) -> None:
        if not 0.0 <= self.priority <= 1.0:
            raise ValueError("priority must be between 0 and 1")
        if self.status not in {"pending", "verified", "failed", "blocked"}:
            raise ValueError("invalid verification status")


class VerificationAgenda:
    def __init__(self) -> None:
        self.tasks: list[VerificationTask] = []

    def add(self, task: VerificationTask) -> None:
        if any(existing.task_id == task.task_id for existing in self.tasks):
            raise ValueError(f"duplicate verification task: {task.task_id}")
        self.tasks.append(task)

    def pending(self) -> tuple[VerificationTask, ...]:
        return tuple(sorted((t for t in self.tasks if t.status == "pending"),
                            key=lambda t: -t.priority))

    def coverage(self, claims: Iterable[object]) -> float:
        claims = tuple(claims)
        if not claims:
            return 1.0
        covered = sum(any(claim in task.falsifies for task in self.tasks) for claim in claims)
        return covered / len(claims)
