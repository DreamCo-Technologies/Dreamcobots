"""Simple, auditable uncertainty propagation primitives for Buddy."""
from __future__ import annotations

from dataclasses import dataclass
from math import prod
from typing import Iterable


@dataclass(frozen=True)
class Uncertainty:
    confidence: float
    basis: str = "unspecified"

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

    @property
    def uncertainty(self) -> float:
        return 1.0 - self.confidence


def independent_support(*evidence: Uncertainty) -> Uncertainty:
    """Combine independent support conservatively: residual uncertainty multiplies."""
    if not evidence:
        return Uncertainty(0.0, "no evidence")
    confidence = 1.0 - prod(item.uncertainty for item in evidence)
    return Uncertainty(confidence, "independent-support approximation")


def weakest_link(*steps: Uncertainty) -> Uncertainty:
    """A chain cannot be more reliable than its least reliable step."""
    if not steps:
        return Uncertainty(0.0, "no steps")
    return Uncertainty(min(item.confidence for item in steps), "weakest-link approximation")


def uncertainty_budget(items: Iterable[Uncertainty]) -> float:
    values = tuple(items)
    return sum(item.uncertainty for item in values)
