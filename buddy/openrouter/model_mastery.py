"""Evidence-driven model selection and consolidation for Buddy.

This module intentionally does not delete models. It produces promotion and
retirement candidates after enough benchmark evidence exists. A separate
policy layer can approve changes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean


@dataclass
class ModelScore:
    model: str
    task: str
    quality: float
    cost_efficiency: float
    latency_score: float
    reliability: float
    tool_success: float = 1.0
    samples: int = 0

    @property
    def composite(self) -> float:
        return (
            self.quality * 0.45
            + self.cost_efficiency * 0.20
            + self.latency_score * 0.10
            + self.reliability * 0.15
            + self.tool_success * 0.10
        )


@dataclass
class MasteryDecision:
    task: str
    preferred: str
    keep: list[str]
    retirement_candidates: list[str]
    reason: str


@dataclass
class MasteryLedger:
    scores: dict[str, list[ModelScore]] = field(default_factory=dict)

    def record(self, score: ModelScore) -> None:
        self.scores.setdefault(score.task, []).append(score)

    def consolidate(
        self,
        task: str,
        minimum_samples: int = 30,
        keep_reserve: int = 2,
        retirement_margin: float = 0.12,
    ) -> MasteryDecision:
        candidates = [
            s for s in self.scores.get(task, []) if s.samples >= minimum_samples
        ]
        if not candidates:
            return MasteryDecision(
                task=task,
                preferred="dreamco/auto",
                keep=[],
                retirement_candidates=[],
                reason="Insufficient benchmark evidence; keep the current fleet.",
            )

        by_model: dict[str, list[ModelScore]] = {}
        for score in candidates:
            by_model.setdefault(score.model, []).append(score)

        ranked = sorted(
            ((model, mean(s.composite for s in rows)) for model, rows in by_model.items()),
            key=lambda item: item[1],
            reverse=True,
        )
        preferred = ranked[0][0]
        keep = [model for model, _ in ranked[: keep_reserve + 1]]
        cutoff = ranked[0][1] - retirement_margin
        retirement = [model for model, value in ranked[keep_reserve + 1 :] if value < cutoff]

        return MasteryDecision(
            task=task,
            preferred=preferred,
            keep=keep,
            retirement_candidates=retirement,
            reason=(
                "Promote repeated benchmark winners; retirement candidates are "
                "only models with sufficient evidence and a material score gap."
            ),
        )
