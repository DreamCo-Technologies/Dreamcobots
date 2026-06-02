from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List


@dataclass
class AttributionNode:
    bot_id: str
    contribution_pct: float
    revenue_usd: float
    confidence: float


class RevenueAttributionGraph:
    def attribute(self, bot_chain: List[str], revenue_usd: float, model: str = 'linear') -> List[AttributionNode]:
        if not bot_chain:
            return []
        weights = self._weights(len(bot_chain), model)
        return [
            AttributionNode(bot_id=bot_id, contribution_pct=round(weight * 100, 2), revenue_usd=round(revenue_usd * weight, 2), confidence=round(0.6 + weight * 0.4, 2))
            for bot_id, weight in zip(bot_chain, weights)
        ]

    def _weights(self, count: int, model: str) -> List[float]:
        if model == 'first-touch':
            return [1.0] + [0.0] * (count - 1)
        if model == 'last-touch':
            return [0.0] * (count - 1) + [1.0]
        if model == 'time-decay':
            raw = [2 ** index for index in range(count)]
            total = sum(raw)
            return [value / total for value in raw]
        return [1 / count for _ in range(count)]

    def export_d3(self, nodes: List[AttributionNode]) -> Dict[str, object]:
        return {
            'nodes': [asdict(node) for node in nodes],
            'links': [
                {'source': nodes[index].bot_id, 'target': nodes[index + 1].bot_id, 'value': nodes[index + 1].revenue_usd}
                for index in range(len(nodes) - 1)
            ],
        }
