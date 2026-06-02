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

def summarize_by_bot(self, nodes: List[AttributionNode]) -> Dict[str, float]:
    return {node.bot_id: node.revenue_usd for node in nodes}


def compare_models(self, bot_chain: List[str], revenue_usd: float) -> Dict[str, List[AttributionNode]]:
    return {
        'first-touch': self.attribute(bot_chain, revenue_usd, 'first-touch'),
        'last-touch': self.attribute(bot_chain, revenue_usd, 'last-touch'),
        'linear': self.attribute(bot_chain, revenue_usd, 'linear'),
        'time-decay': self.attribute(bot_chain, revenue_usd, 'time-decay'),
    }


RevenueAttributionGraph.summarize_by_bot = summarize_by_bot
RevenueAttributionGraph.compare_models = compare_models

def total_revenue(self, nodes: List[AttributionNode]) -> float:
    return round(sum(node.revenue_usd for node in nodes), 2)


RevenueAttributionGraph.total_revenue = total_revenue
