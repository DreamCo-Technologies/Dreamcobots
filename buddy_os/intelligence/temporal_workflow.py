"""Small deterministic temporal workflow primitives for Buddy planning."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass(frozen=True)
class WorkflowTransition:
    transition_id: str
    inputs: Set[str] = field(default_factory=set)
    outputs: Set[str] = field(default_factory=set)
    requires: Set[str] = field(default_factory=set)


class TemporalWorkflow:
    """Petri-style token workflow with explicit transitions and guards."""

    def __init__(self, places: Set[str] | None = None) -> None:
        self.tokens: Set[str] = set(places or ())
        self.transitions: Dict[str, WorkflowTransition] = {}

    def add_transition(self, transition: WorkflowTransition) -> None:
        if transition.transition_id in self.transitions:
            raise ValueError(f"duplicate transition: {transition.transition_id}")
        self.transitions[transition.transition_id] = transition

    def enabled(self, transition_id: str) -> bool:
        transition = self.transitions[transition_id]
        return transition.inputs.issubset(self.tokens) and transition.requires.issubset(self.tokens)

    def fire(self, transition_id: str) -> Set[str]:
        transition = self.transitions[transition_id]
        if not self.enabled(transition_id):
            raise ValueError(f"transition is not enabled: {transition_id}")
        self.tokens.difference_update(transition.inputs)
        self.tokens.update(transition.outputs)
        return set(self.tokens)

    def available(self) -> List[str]:
        return sorted(tid for tid in self.transitions if self.enabled(tid))
