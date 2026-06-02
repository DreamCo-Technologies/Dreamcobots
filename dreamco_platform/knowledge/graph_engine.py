"""DreamCo knowledge graph engine with Neo4j-compatible and in-memory backends."""

from __future__ import annotations

import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover
    GraphDatabase = None


VALID_NODE_TYPES = {"Bot", "Division", "Capability", "RevenueEvent"}
VALID_EDGE_TYPES = {"CALLS", "DEPENDS_ON", "EARNS_FROM", "GOVERNS", "BELONGS_TO"}


@dataclass
class GraphNode:
    node_id: str
    node_type: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    source: str
    edge_type: str
    target: str
    properties: dict[str, Any] = field(default_factory=dict)


class KnowledgeGraphEngine:
    """Provide graph operations with optional Neo4j persistence."""

    def __init__(self, uri: str | None = None, auth: tuple[str, str] | None = None) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge] = []
        self._adjacency: dict[str, list[GraphEdge]] = defaultdict(list)
        self._driver = GraphDatabase.driver(uri, auth=auth) if uri and GraphDatabase else None

    def add_node(self, node_id: str, node_type: str, **properties: Any) -> GraphNode:
        if node_type not in VALID_NODE_TYPES:
            raise ValueError(f"Unsupported node type: {node_type}")
        node = GraphNode(node_id=node_id, node_type=node_type, properties=properties)
        self._nodes[node_id] = node
        if self._driver is not None:
            with self._driver.session() as session:
                session.run(
                    f"MERGE (n:{node_type} {{node_id: $node_id}}) SET n += $properties",
                    node_id=node_id,
                    properties=properties,
                )
        return node

    def add_edge(self, source: str, edge_type: str, target: str, **properties: Any) -> GraphEdge:
        if edge_type not in VALID_EDGE_TYPES:
            raise ValueError(f"Unsupported edge type: {edge_type}")
        edge = GraphEdge(source=source, edge_type=edge_type, target=target, properties=properties)
        self._edges.append(edge)
        self._adjacency[source].append(edge)
        if self._driver is not None:
            with self._driver.session() as session:
                session.run(
                    f"MATCH (a {{node_id: $source}}), (b {{node_id: $target}}) "
                    f"MERGE (a)-[r:{edge_type}]->(b) SET r += $properties",
                    source=source,
                    target=target,
                    properties=properties,
                )
        return edge

    def query_neighbors(self, node_id: str, edge_type: str | None = None) -> list[GraphNode]:
        neighbors = []
        for edge in self._adjacency.get(node_id, []):
            if edge_type and edge.edge_type != edge_type:
                continue
            if edge.target in self._nodes:
                neighbors.append(self._nodes[edge.target])
        return neighbors

    def shortest_path(self, start: str, end: str) -> list[str]:
        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            node_id, path = queue.popleft()
            if node_id == end:
                return path
            for edge in self._adjacency.get(node_id, []):
                if edge.target not in visited:
                    visited.add(edge.target)
                    queue.append((edge.target, path + [edge.target]))
        return []

    def export_graphml(self, output_path: str | Path) -> Path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
            '  <graph edgedefault="directed">',
        ]
        for node in self._nodes.values():
            lines.append(f'    <node id="{node.node_id}"><data key="type">{node.node_type}</data></node>')
        for index, edge in enumerate(self._edges, start=1):
            lines.append(
                f'    <edge id="e{index}" source="{edge.source}" target="{edge.target}">'
                f'<data key="type">{edge.edge_type}</data></edge>'
            )
        lines.extend(['  </graph>', '</graphml>'])
        output.write_text("\n".join(lines) + "\n")
        return output

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [{"node_id": n.node_id, "node_type": n.node_type, "properties": n.properties} for n in self._nodes.values()],
            "edges": [{"source": e.source, "edge_type": e.edge_type, "target": e.target, "properties": e.properties} for e in self._edges],
        }

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
