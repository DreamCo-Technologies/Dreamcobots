"""Bridge causal hypotheses with temporal workflow observations.

This module deliberately treats temporal order as evidence, not proof of causality.
It creates auditable observations that can be consumed by planning and simulation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .causal_engine import CausalEngine, Evidence
from .state_engine import StateEngine


@dataclass(frozen=True)
class TransitionObservation:
    entity_id: str
    previous: str
    current: str
    reason: str
    timestamp: str


@dataclass
class CausalTemporalBridge:
    causal: CausalEngine
    states: StateEngine
    observations: List[TransitionObservation] = field(default_factory=list)

    def observe(self, entity_id: str, previous: str, current: str, reason: str, timestamp: str) -> TransitionObservation:
        observation = TransitionObservation(entity_id, previous, current, reason, timestamp)
        self.observations.append(observation)
        return observation

    def add_temporal_evidence(self, hypothesis_id: str, source: str, weight: float = 0.25) -> Dict[str, object]:
        hypothesis = self.causal.get(hypothesis_id)
        if hypothesis is None:
            return {"status": "missing", "hypothesis_id": hypothesis_id}
        hypothesis.evidence.append(Evidence(source=source, supports=True, weight=weight, note="temporal observation; not causal proof"))
        return self.causal.assess(hypothesis_id)

    def timeline(self, entity_id: str) -> List[Dict[str, str]]:
        return [
            {"previous": item.previous, "current": item.current, "reason": item.reason, "timestamp": item.timestamp}
            for item in self.observations if item.entity_id == entity_id
        ]
