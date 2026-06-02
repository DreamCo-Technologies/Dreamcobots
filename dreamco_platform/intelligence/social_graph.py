"""Bot social graph analyzer with pure Python Louvain clustering."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from collections import defaultdict


@dataclass
class SocialNode:
    id: str
    type: str
    connections: Dict[str, float] = field(default_factory=dict)
    influence_score: float = 0.0


class SocialGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, SocialNode] = {}

    def _ensure(self, node_id: str, node_type: str) -> SocialNode:
        if node_id not in self.nodes:
            self.nodes[node_id] = SocialNode(id=node_id, type=node_type)
        return self.nodes[node_id]

    def add_interaction(self, user: str, bot: str, outcome: str, revenue: float) -> None:
        user_node = self._ensure(user, "user")
        bot_node = self._ensure(bot, "bot")
        outcome_node = self._ensure(outcome, "outcome")
        revenue_node = self._ensure(f"revenue:{revenue:.2f}", "revenue")
        links = [(user_node, bot_node), (bot_node, outcome_node), (outcome_node, revenue_node)]
        for left, right in links:
            left.connections[right.id] = left.connections.get(right.id, 0.0) + 1.0
            right.connections[left.id] = right.connections.get(left.id, 0.0) + 1.0
        for node in (user_node, bot_node, outcome_node, revenue_node):
            node.influence_score = round(sum(node.connections.values()), 3)

    def find_influencers(self, top_n: int = 5) -> List[SocialNode]:
        return sorted(self.nodes.values(), key=lambda node: node.influence_score, reverse=True)[:top_n]

    def _modularity_gain(self, node_id: str, community: int, partition: Dict[str, int]) -> float:
        node = self.nodes[node_id]
        in_weight = sum(weight for neighbor, weight in node.connections.items() if partition[neighbor] == community)
        total_weight = sum(sum(n.connections.values()) for n in self.nodes.values()) or 1.0
        degree = sum(node.connections.values())
        community_degree = sum(sum(self.nodes[nid].connections.values()) for nid, cid in partition.items() if cid == community)
        return in_weight / total_weight - (degree * community_degree) / (2 * total_weight * total_weight)

    def detect_clusters(self, max_passes: int = 5) -> List[List[str]]:
        partition = {node_id: index for index, node_id in enumerate(self.nodes)}
        for _ in range(max_passes):
            moved = False
            for node_id in self.nodes:
                current = partition[node_id]
                neighbor_communities = {partition[neighbor] for neighbor in self.nodes[node_id].connections}
                best_community = current
                best_gain = 0.0
                for community in neighbor_communities:
                    gain = self._modularity_gain(node_id, community, partition)
                    if gain > best_gain:
                        best_gain = gain
                        best_community = community
                if best_community != current:
                    partition[node_id] = best_community
                    moved = True
            if not moved:
                break
        grouped: Dict[int, List[str]] = defaultdict(list)
        for node_id, community in partition.items():
            grouped[community].append(node_id)
        return list(grouped.values())
