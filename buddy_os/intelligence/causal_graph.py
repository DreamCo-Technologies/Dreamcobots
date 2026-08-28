"""Lightweight causal graph primitives for Buddy.

This represents candidate causal structure; it does not claim that an edge is
causal merely because it exists. Intervention and observation are distinct.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CausalEdge:
    cause: str
    effect: str
    confidence: float = 0.5
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.cause == self.effect:
            raise ValueError("self-causal edges are not allowed")


class CausalGraph:
    def __init__(self) -> None:
        self.edges: list[CausalEdge] = []

    def add_edge(self, edge: CausalEdge) -> None:
        if edge in self.edges:
            return
        self.edges.append(edge)

    def parents(self, effect: str) -> tuple[str, ...]:
        return tuple(edge.cause for edge in self.edges if edge.effect == effect)

    def children(self, cause: str) -> tuple[str, ...]:
        return tuple(edge.effect for edge in self.edges if edge.cause == cause)

    def intervention_candidates(self, effect: str) -> tuple[str, ...]:
        """Return upstream candidates; intervention still requires authorization."""
        return self.parents(effect)
