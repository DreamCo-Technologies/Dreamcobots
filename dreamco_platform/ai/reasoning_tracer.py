"""Reasoning trace capture with scoreable decision steps."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List


@dataclass
class TraceStep:
    name: str
    evidence: str
    confidence: float
    outcome: str
    tags: List[str] = field(default_factory=list)


class ReasoningTracer:
    def __init__(self) -> None:
        self._steps: List[TraceStep] = []

    def add_step(self, name: str, evidence: str, confidence: float, outcome: str, tags: Iterable[str] = ()) -> TraceStep:
        step = TraceStep(name=name, evidence=evidence, confidence=max(0.0, min(1.0, confidence)), outcome=outcome, tags=list(tags))
        self._steps.append(step)
        return step

    def steps(self) -> List[TraceStep]:
        return list(self._steps)

    def trace_score(self) -> float:
        if not self._steps:
            return 0.0
        weighted = sum(step.confidence * (1.1 if "verified" in step.tags else 1.0) for step in self._steps)
        return round(weighted / len(self._steps), 3)

    def failure_points(self) -> List[TraceStep]:
        return [step for step in self._steps if step.confidence < 0.5 or "risk" in step.tags]

    def summarize(self) -> Dict[str, object]:
        return {
            "step_count": len(self._steps),
            "score": self.trace_score(),
            "risks": [step.name for step in self.failure_points()],
            "final_outcome": self._steps[-1].outcome if self._steps else None,
        }

    def export_markdown(self) -> str:
        lines = ["# Reasoning Trace", ""]
        for index, step in enumerate(self._steps, start=1):
            lines.append(f"## {index}. {step.name}")
            lines.append(f"- Evidence: {step.evidence}")
            lines.append(f"- Confidence: {step.confidence:.2f}")
            lines.append(f"- Outcome: {step.outcome}")
            if step.tags:
                lines.append(f"- Tags: {', '.join(step.tags)}")
            lines.append("")
        return "
".join(lines)


def build_trace(records: Iterable[Dict[str, object]]) -> ReasoningTracer:
    tracer = ReasoningTracer()
    for record in records:
        tracer.add_step(
            str(record.get("name", "step")),
            str(record.get("evidence", "")),
            float(record.get("confidence", 0.5)),
            str(record.get("outcome", "pending")),
            record.get("tags", ()),
        )
    return tracer
