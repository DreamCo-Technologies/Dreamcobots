"""Small, dependency-free Markov Decision Process primitives for Buddy.

This layer converts transition observations into a governed decision signal.
It does not execute actions and does not override safety or approval policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class Decision:
    state: str
    action: str
    expected_value: float


class MarkovDecisionModel:
    """Finite-state transition/reward model with value iteration."""

    def __init__(self, discount: float = 0.9) -> None:
        if not 0 <= discount < 1:
            raise ValueError("discount must be in [0, 1)")
        self.discount = discount
        self.transitions: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.rewards: Dict[str, Dict[str, float]] = {}

    def add_transition(self, state: str, action: str, next_state: str, probability: float) -> None:
        if probability < 0:
            raise ValueError("probability must be non-negative")
        self.transitions.setdefault(state, {}).setdefault(action, {})[next_state] = probability

    def set_reward(self, state: str, action: str, reward: float) -> None:
        self.rewards.setdefault(state, {})[action] = float(reward)

    def validate(self) -> None:
        for state, actions in self.transitions.items():
            for action, outcomes in actions.items():
                total = sum(outcomes.values())
                if abs(total - 1.0) > 1e-9:
                    raise ValueError(f"transition probabilities for {state}/{action} sum to {total}")

    def value_iteration(self, iterations: int = 50) -> Mapping[str, float]:
        if iterations <= 0:
            raise ValueError("iterations must be positive")
        self.validate()
        values = {state: 0.0 for state in self.transitions}
        for _ in range(iterations):
            updated = dict(values)
            for state, actions in self.transitions.items():
                if not actions:
                    continue
                updated[state] = max(
                    self.rewards.get(state, {}).get(action, 0.0)
                    + self.discount * sum(prob * values.get(nxt, 0.0) for nxt, prob in outcomes.items())
                    for action, outcomes in actions.items()
                )
            values = updated
        return values

    def recommend(self, state: str) -> Sequence[Decision]:
        self.validate()
        values = self.value_iteration()
        decisions = []
        for action, outcomes in self.transitions.get(state, {}).items():
            expected = self.rewards.get(state, {}).get(action, 0.0) + self.discount * sum(
                probability * values.get(next_state, 0.0)
                for next_state, probability in outcomes.items()
            )
            decisions.append(Decision(state, action, expected))
        return tuple(sorted(decisions, key=lambda item: (-item.expected_value, item.action)))
