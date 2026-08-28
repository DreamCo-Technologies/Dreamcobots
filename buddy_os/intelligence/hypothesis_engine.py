"""Competing-hypothesis management for scientific and diagnostic reasoning."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id: str
    statement: str
    prior_confidence: float
    predictions: tuple[str, ...] = ()
    falsifiers: tuple[str, ...] = ()
    evidence_for: tuple[str, ...] = ()
    evidence_against: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.prior_confidence <= 1.0:
            raise ValueError("prior_confidence must be between 0 and 1")


class HypothesisEngine:
    def __init__(self) -> None:
        self._hypotheses: dict[str, Hypothesis] = {}

    def add(self, hypothesis: Hypothesis) -> None:
        if hypothesis.hypothesis_id in self._hypotheses:
            raise ValueError(f"duplicate hypothesis: {hypothesis.hypothesis_id}")
        self._hypotheses[hypothesis.hypothesis_id] = hypothesis

    def rank(self) -> tuple[Hypothesis, ...]:
        def score(h: Hypothesis) -> float:
            # Evidence count adjusts the prior only as a transparent heuristic;
            # this is not presented as a Bayesian posterior.
            return h.prior_confidence + 0.05 * len(h.evidence_for) - 0.05 * len(h.evidence_against)
        return tuple(sorted(self._hypotheses.values(), key=lambda h: (-score(h), h.hypothesis_id)))

    def discriminating_questions(self) -> tuple[str, ...]:
        questions: list[str] = []
        for hypothesis in self._hypotheses.values():
            for prediction in hypothesis.predictions:
                questions.append(f"What observation would distinguish {hypothesis.hypothesis_id} via: {prediction}?")
            for falsifier in hypothesis.falsifiers:
                questions.append(f"Can we test falsifier for {hypothesis.hypothesis_id}: {falsifier}?")
        return tuple(dict.fromkeys(questions))
