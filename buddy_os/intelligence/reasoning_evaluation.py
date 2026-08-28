"""Outcome-based evaluation ledger for Buddy's reasoning fabric.

This module records predictions and outcomes so reasoning methods can be
compared on accuracy, calibration, cost and failure modes. It intentionally
updates statistics only from supplied observations; it never invents ground
truth and never grants execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Iterable


@dataclass(frozen=True)
class ReasoningTrial:
    trial_id: str
    method: str
    confidence: float
    correct: bool | None
    cost: float = 0.0
    failure_mode: str | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.cost < 0:
            raise ValueError("cost cannot be negative")


@dataclass(frozen=True)
class MethodScore:
    method: str
    observed_trials: int
    resolved_trials: int
    accuracy: float | None
    mean_confidence: float
    mean_cost: float
    brier_score: float | None
    failures: tuple[str, ...] = ()


class ReasoningEvaluationLab:
    def __init__(self) -> None:
        self.trials: list[ReasoningTrial] = []

    def record(self, trial: ReasoningTrial) -> None:
        self.trials.append(trial)

    def score(self, method: str) -> MethodScore:
        trials = [t for t in self.trials if t.method == method]
        resolved = [t for t in trials if t.correct is not None]
        accuracy = mean(float(t.correct) for t in resolved) if resolved else None
        brier = (mean((t.confidence - float(t.correct)) ** 2 for t in resolved)
                 if resolved else None)
        failures = tuple(sorted({t.failure_mode for t in trials if t.failure_mode}))
        return MethodScore(method, len(trials), len(resolved), accuracy,
                           mean(t.confidence for t in trials) if trials else 0.0,
                           mean(t.cost for t in trials) if trials else 0.0,
                           brier, failures)

    def leaderboard(self) -> list[MethodScore]:
        methods = sorted({t.method for t in self.trials})
        scores = [self.score(method) for method in methods]
        return sorted(scores, key=lambda s: (s.accuracy is None, -(s.accuracy or 0.0), s.mean_cost))

    def unresolved(self) -> list[ReasoningTrial]:
        return [t for t in self.trials if t.correct is None]
