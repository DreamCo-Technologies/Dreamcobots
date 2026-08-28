"""Provenance graph for tracing Buddy conclusions back to evidence and checks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ProvenanceNode:
    node_id: str
    kind: str
    label: str
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ProvenanceEdge:
    source: str
    relation: str
    target: str


class ReasoningProvenanceGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, ProvenanceNode] = {}
        self.edges: list[ProvenanceEdge] = []

    def add_node(self, node: ProvenanceNode) -> None:
        if node.node_id in self.nodes:
            raise ValueError(f"duplicate provenance node: {node.node_id}")
        self.nodes[node.node_id] = node

    def connect(self, source: str, relation: str, target: str) -> None:
        if source not in self.nodes or target not in self.nodes:
            raise KeyError("provenance edge references an unknown node")
        edge = ProvenanceEdge(source, relation, target)
        if edge not in self.edges:
            self.edges.append(edge)

    def predecessors(self, node_id: str) -> tuple[ProvenanceEdge, ...]:
        return tuple(edge for edge in self.edges if edge.target == node_id)

    def trace(self, node_id: str) -> tuple[str, ...]:
        if node_id not in self.nodes:
            raise KeyError(node_id)
        visited: set[str] = set()
        stack = [node_id]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            stack.extend(edge.source for edge in self.predecessors(current))
        return tuple(sorted(visited))
