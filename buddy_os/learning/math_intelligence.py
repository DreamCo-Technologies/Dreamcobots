"""Dependency-free mathematical intelligence primitives for Buddy.

These components are advisory: they produce scores/plans and never grant
permissions or execute external side effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import log, sqrt
from random import Random
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


def normalize(values: Mapping[str, float]) -> Dict[str, float]:
    total = sum(max(0.0, v) for v in values.values())
    return {k: (max(0.0, v) / total if total else 0.0) for k, v in values.items()}


def entropy(probabilities: Iterable[float]) -> float:
    return -sum(p * log(p, 2) for p in probabilities if p > 0)


def information_gain(prior: Sequence[float], posterior: Sequence[float]) -> float:
    return entropy(prior) - entropy(posterior)


@dataclass(frozen=True)
class BayesianUpdate:
    posterior: Dict[str, float]
    evidence_strength: float


def bayesian_update(prior: Mapping[str, float], likelihood: Mapping[str, float]) -> BayesianUpdate:
    weighted = {k: prior.get(k, 0.0) * likelihood.get(k, 0.0) for k in set(prior) | set(likelihood)}
    posterior = normalize(weighted)
    return BayesianUpdate(posterior, sum(weighted.values()))


class HiddenMarkovModel:
    """Minimal forward-probability inference for finite hidden states."""
    def __init__(self, initial: Mapping[str, float], transitions: Mapping[str, Mapping[str, float]], emissions: Mapping[str, Mapping[str, float]]) -> None:
        self.initial = normalize(initial)
        self.transitions = transitions
        self.emissions = emissions

    def infer(self, observations: Sequence[str]) -> Dict[str, float]:
        if not observations:
            return dict(self.initial)
        current = {state: p * self.emissions.get(state, {}).get(observations[0], 0.0) for state, p in self.initial.items()}
        current = normalize(current)
        for observation in observations[1:]:
            nxt: Dict[str, float] = {}
            for state in self.initial:
                probability = sum(current.get(prev, 0.0) * self.transitions.get(prev, {}).get(state, 0.0) for prev in self.initial)
                nxt[state] = probability * self.emissions.get(state, {}).get(observation, 0.0)
            current = normalize(nxt)
        return current


class MonteCarloEstimator:
    def __init__(self, seed: int | None = 0) -> None:
        self.random = Random(seed)

    def estimate(self, trials: int, outcome_fn) -> float:
        if trials <= 0:
            raise ValueError("trials must be positive")
        return sum(float(outcome_fn(self.random)) for _ in range(trials)) / trials


@dataclass(frozen=True)
class KalmanState:
    estimate: float
    variance: float


def kalman_update(state: KalmanState, measurement: float, measurement_variance: float) -> KalmanState:
    if state.variance < 0 or measurement_variance <= 0:
        raise ValueError("invalid variance")
    gain = state.variance / (state.variance + measurement_variance)
    estimate = state.estimate + gain * (measurement - state.estimate)
    variance = (1 - gain) * state.variance
    return KalmanState(estimate, variance)


def pareto_front(points: Sequence[Mapping[str, float]], maximize: Sequence[str], minimize: Sequence[str] = ()) -> List[Mapping[str, float]]:
    def dominates(a, b):
        better_or_equal = all(a[k] >= b[k] for k in maximize) and all(a[k] <= b[k] for k in minimize)
        strictly_better = any(a[k] > b[k] for k in maximize) or any(a[k] < b[k] for k in minimize)
        return better_or_equal and strictly_better
    return [p for p in points if not any(dominates(other, p) for other in points if other is not p)]
