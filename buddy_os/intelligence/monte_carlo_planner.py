"""Deterministic, budget-bounded Monte Carlo-style planning primitives.

This module samples supplied successor branches rather than executing actions.
It is intentionally dependency-free and keeps the planning calculation
inspectable for audits and tests.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable


@dataclass(frozen=True)
class Simulation:
    state: tuple[tuple[str, str], ...]
    value: float
    probability: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("probability must be between 0 and 1")


class MonteCarloPlanner:
    def __init__(self, simulations: int = 100, seed: int = 0) -> None:
        if simulations < 1:
            raise ValueError("simulations must be positive")
        self.simulations = simulations
        self.seed = seed

    def evaluate(self, initial_state: tuple[tuple[str, str], ...], sampler: Callable[[random.Random, tuple[tuple[str, str], ...]], Simulation]) -> float:
        rng = random.Random(self.seed)
        values = [sampler(rng, initial_state).value for _ in range(self.simulations)]
        return sum(values) / len(values)
