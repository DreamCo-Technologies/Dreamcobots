"""Deterministic digital-twin primitives for safe Buddy planning.

The twin is intentionally side-effect free: it models state transitions and
records predicted outcomes without granting execution permissions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping


@dataclass(frozen=True)
class TwinAction:
    action_id: str
    updates: Mapping[str, object] = field(default_factory=dict)
    cost: float = 0.0
    risk: float = 0.0


@dataclass(frozen=True)
class SimulationResult:
    action_id: str
    before: Dict[str, object]
    after: Dict[str, object]
    cost: float
    risk: float


class DigitalTwin:
    """In-memory simulation model; never executes real-world actions."""

    def __init__(self, state: Mapping[str, object] | None = None) -> None:
        self.state: Dict[str, object] = dict(state or {})
        self.history: List[SimulationResult] = []

    def simulate(self, action: TwinAction) -> SimulationResult:
        before = dict(self.state)
        after = dict(before)
        after.update(action.updates)
        result = SimulationResult(action.action_id, before, after, action.cost, action.risk)
        self.history.append(result)
        return result

    def apply_simulated(self, result: SimulationResult) -> Dict[str, object]:
        self.state = dict(result.after)
        return dict(self.state)

    def snapshot(self) -> Dict[str, object]:
        return dict(self.state)
