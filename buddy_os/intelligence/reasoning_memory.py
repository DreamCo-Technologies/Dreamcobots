"""Auditable case memory for Buddy's reasoning system.

Cases store methods and outcomes, not authority. Retrieval is similarity by
explicit tags/metadata and callers must still verify conclusions on new cases.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ReasoningCase:
    case_id: str
    domain: str
    tags: frozenset[str]
    problem_signature: str
    successful_methods: tuple[str, ...]
    failure_modes: tuple[str, ...] = ()
    verified: bool = False


class ReasoningCaseLibrary:
    def __init__(self) -> None:
        self._cases: dict[str, ReasoningCase] = {}

    def add(self, case: ReasoningCase) -> None:
        if case.case_id in self._cases:
            raise ValueError(f"duplicate case: {case.case_id}")
        self._cases[case.case_id] = case

    def retrieve(self, domain: str, tags: Iterable[str] = (), limit: int = 5) -> tuple[ReasoningCase, ...]:
        if limit < 1:
            raise ValueError("limit must be positive")
        wanted = set(tags)
        candidates = []
        for case in self._cases.values():
            if case.domain != domain:
                continue
            overlap = len(wanted & case.tags)
            verified_bonus = 1 if case.verified else 0
            candidates.append((overlap, verified_bonus, case))
        candidates.sort(key=lambda row: (-row[0], -row[1], row[2].case_id))
        return tuple(row[2] for row in candidates[:limit])

    def verified_cases(self) -> tuple[ReasoningCase, ...]:
        return tuple(case for case in self._cases.values() if case.verified)
