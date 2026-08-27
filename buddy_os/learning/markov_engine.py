"""Markov-chain utilities for Buddy's probabilistic workflow learning."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import log
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


@dataclass(frozen=True)
class TransitionPrediction:
    state: str
    probability: float


class MarkovChain:
    """Explainable first-order Markov model for discrete Buddy states."""

    def __init__(self, smoothing: float = 0.1) -> None:
        if smoothing < 0:
            raise ValueError("smoothing must be non-negative")
        self.smoothing = float(smoothing)
        self._counts: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._states: set[str] = set()

    def fit(self, sequences: Iterable[Sequence[str]]) -> "MarkovChain":
        """Learn transition counts from observed state sequences."""
        for sequence in sequences:
            if not sequence:
                continue
            self._states.update(sequence)
            for current, nxt in zip(sequence, sequence[1:]):
                self._counts[current][nxt] += 1.0
        return self

    @property
    def states(self) -> Tuple[str, ...]:
        return tuple(sorted(self._states))

    def transition_probability(self, current: str, nxt: str) -> float:
        """Return P(next_state | current_state) with optional smoothing."""
        states = self.states
        if not states or current not in self._states or nxt not in self._states:
            return 0.0
        row = self._counts[current]
        denominator = sum(row.values()) + self.smoothing * len(states)
        if denominator == 0:
            return 1.0 / len(states)
        return (row.get(nxt, 0.0) + self.smoothing) / denominator

    def predict_next(self, current: str, top_k: int = 5) -> List[TransitionPrediction]:
        """Rank likely next states from the current state."""
        if top_k <= 0:
            return []
        predictions = [
            TransitionPrediction(state, self.transition_probability(current, state))
            for state in self.states
        ]
        predictions.sort(key=lambda item: (-item.probability, item.state))
        return predictions[:top_k]

    def sequence_log_likelihood(self, sequence: Sequence[str]) -> float:
        """Score a sequence under the learned transition model."""
        if len(sequence) < 2:
            return 0.0
        total = 0.0
        for current, nxt in zip(sequence, sequence[1:]):
            probability = self.transition_probability(current, nxt)
            if probability <= 0:
                return float("-inf")
            total += log(probability)
        return total

    def transition_matrix(self) -> Mapping[str, Mapping[str, float]]:
        """Return a deterministic, JSON-friendly transition matrix."""
        return {
            current: {nxt: self.transition_probability(current, nxt) for nxt in self.states}
            for current in self.states
        }

    def anomaly_score(self, current: str, nxt: str) -> float:
        """Return -log(P(next|current)); larger values are more surprising."""
        probability = self.transition_probability(current, nxt)
        if probability <= 0:
            return float("inf")
        return -log(probability)


__all__ = ["MarkovChain", "TransitionPrediction"]
