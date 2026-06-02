"""Graph analysis for relationship mapping and introductions."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple


@dataclass(frozen=True)
class Connection:
    source: str
    target: str
    strength: float = 1.0


class SocialGraph:
    def __init__(self, connections: Iterable[Connection] = ()) -> None:
        self._graph: Dict[str, Dict[str, float]] = defaultdict(dict)
        for connection in connections:
            self.add_connection(connection.source, connection.target, connection.strength)

    def add_connection(self, source: str, target: str, strength: float = 1.0) -> None:
        self._graph[source][target] = max(strength, self._graph[source].get(target, 0.0))
        self._graph[target][source] = max(strength, self._graph[target].get(source, 0.0))

    def neighbors(self, node: str) -> Dict[str, float]:
        return dict(self._graph.get(node, {}))

    def shortest_intro_path(self, start: str, end: str) -> List[str]:
        if start == end:
            return [start]
        queue = deque([[start]])
        seen: Set[str] = {start}
        while queue:
            path = queue.popleft()
            for neighbor in self._graph.get(path[-1], {}):
                if neighbor in seen:
                    continue
                next_path = path + [neighbor]
                if neighbor == end:
                    return next_path
                seen.add(neighbor)
                queue.append(next_path)
        return []

    def suggest_introductions(self, person: str, limit: int = 5) -> List[Tuple[str, float]]:
        direct = set(self._graph.get(person, {}))
        scores: Dict[str, float] = defaultdict(float)
        for friend, strength in self._graph.get(person, {}).items():
            for candidate, candidate_strength in self._graph.get(friend, {}).items():
                if candidate == person or candidate in direct:
                    continue
                scores[candidate] += strength * candidate_strength
        return sorted(scores.items(), key=lambda item: item[1], reverse=True)[:limit]

    def centrality(self) -> Dict[str, float]:
        size = max(len(self._graph) - 1, 1)
        return {node: round(len(neighbors) / size, 3) for node, neighbors in self._graph.items()}

    def community_overlap(self, left: str, right: str) -> float:
        left_neighbors = set(self._graph.get(left, {}))
        right_neighbors = set(self._graph.get(right, {}))
        union = left_neighbors | right_neighbors
        return round(len(left_neighbors & right_neighbors) / max(len(union), 1), 3)


def build_from_edges(edges: Iterable[Tuple[str, str, float]]) -> SocialGraph:
    graph = SocialGraph()
    for source, target, strength in edges:
        graph.add_connection(source, target, strength)
    return graph
