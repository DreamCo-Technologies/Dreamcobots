from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EdgeNode:
    region: str
    latency_ms: int
    capacity: int
    active_bots: int = 0
    healthy: bool = True

    @property
    def load_factor(self) -> float:
        return self.active_bots / max(self.capacity, 1)


class Dispatcher:
    REGION_LATENCY = {
        'na': ['us-east-1', 'us-west-2'],
        'eu': ['eu-west-1', 'us-east-1'],
        'apac': ['ap-southeast-1', 'us-west-2'],
    }

    def __init__(self, nodes: List[EdgeNode], cloud_region: str = 'us-east-1') -> None:
        self.nodes: Dict[str, EdgeNode] = {node.region: node for node in nodes}
        self.cloud_region = cloud_region
        self.routes: List[dict] = []

    def route(self, bot_id: str, user_region: str) -> EdgeNode:
        preferred = self.REGION_LATENCY.get(user_region, list(self.nodes.keys()))
        candidates = [self.nodes[region] for region in preferred if region in self.nodes and self.nodes[region].healthy]
        if not candidates:
            fallback = self.nodes.setdefault(self.cloud_region, EdgeNode(self.cloud_region, 90, 1000))
            self.routes.append({'bot_id': bot_id, 'region': fallback.region, 'reason': 'cloud-fallback'})
            fallback.active_bots += 1
            return fallback
        selected = min(candidates, key=lambda node: (node.load_factor, node.latency_ms))
        if selected.load_factor >= 1.0:
            fallback = self.nodes.setdefault(self.cloud_region, EdgeNode(self.cloud_region, 90, 1000))
            self.routes.append({'bot_id': bot_id, 'region': fallback.region, 'reason': 'edge-saturated'})
            fallback.active_bots += 1
            return fallback
        selected.active_bots += 1
        self.routes.append({'bot_id': bot_id, 'region': selected.region, 'reason': 'edge-optimal'})
        return selected

def release(self, region: str, count: int = 1) -> None:
    if region in self.nodes:
        self.nodes[region].active_bots = max(0, self.nodes[region].active_bots - count)


def regional_status(self) -> dict:
    return {
        region: {
            'healthy': node.healthy,
            'load_factor': round(node.load_factor, 3),
            'latency_ms': node.latency_ms,
            'active_bots': node.active_bots,
        }
        for region, node in self.nodes.items()
    }


def set_health(self, region: str, healthy: bool) -> None:
    if region in self.nodes:
        self.nodes[region].healthy = healthy


Dispatcher.release = release
Dispatcher.regional_status = regional_status
Dispatcher.set_health = set_health
