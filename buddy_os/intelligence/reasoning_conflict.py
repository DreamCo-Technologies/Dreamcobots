"""Conflict analysis for Buddy's multi-method reasoning.

The resolver explains disagreement rather than hiding it. It produces a
verification agenda; it does not declare an uncertain dispute solved.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .reasoning_ensemble import ReasoningOpinion


@dataclass(frozen=True)
class Conflict:
    answers: tuple[object, ...]
    methods: tuple[str, ...]
    evidence: tuple[str, ...]
    confidence_range: tuple[float, float]
    verification_questions: tuple[str, ...]


class ReasoningConflictResolver:
    def analyze(self, opinions: Iterable[ReasoningOpinion]) -> Conflict | None:
        rows = tuple(opinions)
        answers = tuple(dict.fromkeys(o.answer for o in rows))
        if len(answers) <= 1:
            return None
        methods = tuple(o.method for o in rows)
        evidence = tuple(dict.fromkeys(e for o in rows for e in o.evidence))
        low = min(o.confidence for o in rows)
        high = max(o.confidence for o in rows)
        questions = (
            "Which assumptions differ between the competing methods?",
            "Which evidence independently distinguishes the competing answers?",
            "What observation or experiment would falsify each leading answer?",
            "Is the disagreement caused by definitions, missing evidence, or model uncertainty?",
        )
        return Conflict(answers, methods, evidence, (low, high), questions)
