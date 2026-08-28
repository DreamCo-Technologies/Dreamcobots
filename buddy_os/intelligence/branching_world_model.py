"""Branching future-state simulation for Buddy's decision support."""
from __future__ import annotations

from dataclasses import dataclass
from .world_model import State


@dataclass(frozen=True)
class FutureBranch:
    branch_id: str
    state: State
    probability: float
    utility: float = 0.0
    rationale: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("probability must be between 0 and 1")


class BranchingWorldModel:
    @staticmethod
    def normalize(branches: tuple[FutureBranch, ...] | list[FutureBranch]) -> tuple[FutureBranch, ...]:
        total = sum(branch.probability for branch in branches)
        if total <= 0:
            return ()
        return tuple(
            FutureBranch(b.branch_id, b.state, b.probability / total, b.utility, b.rationale)
            for b in branches
        )

    @staticmethod
    def expected_utility(branches: tuple[FutureBranch, ...] | list[FutureBranch]) -> float:
        return sum(branch.probability * branch.utility for branch in branches)

    @staticmethod
    def highest_probability(branches: tuple[FutureBranch, ...] | list[FutureBranch]) -> FutureBranch | None:
        return max(branches, key=lambda branch: (branch.probability, branch.branch_id), default=None)
