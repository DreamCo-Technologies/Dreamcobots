"""Small state-transition world-model primitives for Buddy.

The model is deterministic and intentionally explicit: state, action, and
predicted next state are recorded separately so simulations remain auditable.
It does not execute real-world actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping


State = tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Transition:
    action: str
    next_state: State
    probability: float = 1.0
    rationale: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("probability must be between 0 and 1")


class WorldModel:
    def __init__(self) -> None:
        self._transitions: dict[tuple[State, str], Transition] = {}

    @staticmethod
    def normalize(state: Mapping[str, str]) -> State:
        return tuple(sorted((str(k), str(v)) for k, v in state.items()))

    def learn_transition(self, state: Mapping[str, str], transition: Transition) -> None:
        key = (self.normalize(state), transition.action)
        self._transitions[key] = transition

    def predict(self, state: Mapping[str, str], action: str) -> Transition | None:
        return self._transitions.get((self.normalize(state), action))

    def rollout(self, state: Mapping[str, str], actions: tuple[str, ...]) -> tuple[State, ...]:
        current = self.normalize(state)
        states = [current]
        for action in actions:
            transition = self._transitions.get((current, action))
            if transition is None:
                break
            current = transition.next_state
            states.append(current)
        return tuple(states)
