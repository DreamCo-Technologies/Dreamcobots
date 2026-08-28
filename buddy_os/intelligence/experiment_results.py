"""Record experimental observations and produce transparent hypothesis updates."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Observation:
    observation_id: str
    experiment_id: str
    outcome: str
    supports: tuple[str, ...] = ()
    contradicts: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True)
class HypothesisUpdate:
    hypothesis_id: str
    supporting_observations: tuple[str, ...]
    contradicting_observations: tuple[str, ...]
    direction: str


class ExperimentResults:
    def __init__(self) -> None:
        self.observations: dict[str, Observation] = {}

    def record(self, observation: Observation) -> None:
        if observation.observation_id in self.observations:
            raise ValueError(f"duplicate observation: {observation.observation_id}")
        self.observations[observation.observation_id] = observation

    def update_for(self, hypothesis_id: str) -> HypothesisUpdate:
        supporting = tuple(o.observation_id for o in self.observations.values() if hypothesis_id in o.supports)
        contradicting = tuple(o.observation_id for o in self.observations.values() if hypothesis_id in o.contradicts)
        if supporting and not contradicting:
            direction = "supported"
        elif contradicting and not supporting:
            direction = "contradicted"
        elif supporting and contradicting:
            direction = "mixed"
        else:
            direction = "unchanged"
        return HypothesisUpdate(hypothesis_id, supporting, contradicting, direction)
