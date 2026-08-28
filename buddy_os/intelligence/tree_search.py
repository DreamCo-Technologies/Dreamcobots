"""Bounded tree-search primitives for Buddy decision support."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class SearchNode:
    node_id: str
    state: tuple[tuple[str, str], ...]
    depth: int
    value: float = 0.0
    probability: float = 1.0
    parent_id: str | None = None
    action: str | None = None

    def __post_init__(self) -> None:
        if self.depth < 0:
            raise ValueError("depth cannot be negative")
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("probability must be between 0 and 1")


class BoundedTreeSearch:
    """Explore a supplied finite search tree without executing actions."""

    def __init__(self, max_depth: int = 3, beam_width: int = 8) -> None:
        if max_depth < 0 or beam_width < 1:
            raise ValueError("max_depth must be >= 0 and beam_width must be >= 1")
        self.max_depth = max_depth
        self.beam_width = beam_width

    def search(self, root: SearchNode, expand: Callable[[SearchNode], list[SearchNode]]) -> tuple[SearchNode, ...]:
        frontier = [root]
        leaves: list[SearchNode] = []
        for _ in range(self.max_depth):
            candidates: list[SearchNode] = []
            for node in frontier:
                children = [child for child in expand(node) if child.parent_id == node.node_id]
                candidates.extend(children)
            if not candidates:
                break
            candidates.sort(key=lambda n: (-(n.probability * n.value), -n.value, n.node_id))
            frontier = candidates[: self.beam_width]
            leaves.extend(frontier)
        return tuple(leaves or [root])
