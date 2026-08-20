#!/usr/bin/env python3
"""Choose the next learning action from benchmark evidence."""
from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Gap:
    capability: str
    quality: float
    speed: float
    reliability: float
    safety: float
    cost: float = 0.5

    @property
    def severity(self) -> float:
        return max(0.0, 1.0 - (0.35*self.quality + 0.20*self.speed + 0.20*self.reliability + 0.25*self.safety))


def rank_gaps(gaps: list[Gap]) -> list[Gap]:
    return sorted(gaps, key=lambda g: (g.severity, g.cost), reverse=True)


def next_actions(gap: Gap) -> list[str]:
    actions = []
    if gap.quality < .9: actions.append("study-targeted-resources")
    if gap.reliability < .9: actions.append("generate-repeatability-tests")
    if gap.speed < .9: actions.append("run-performance-optimization")
    if gap.safety < .95: actions.append("run-safety-evaluation")
    actions.extend(["sandbox-practice", "benchmark-retest", "record-regression"])
    return actions


def curriculum_decision(gaps: list[Gap]) -> dict:
    ranked = rank_gaps(gaps)
    return {
        "strategy": "highest-expected-improvement-first",
        "selected": [
            {"gap": asdict(g), "severity": round(g.severity, 4), "actions": next_actions(g)}
            for g in ranked[:10]
        ],
        "promotion_rule": "Do not promote a capability on study completion alone; require repeatable benchmark evidence.",
    }
