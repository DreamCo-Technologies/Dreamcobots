from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class MoatScore:
    dimension_scores: Dict[str, float]
    total_score: float
    trend: str
    vs_competitors: Dict[str, float]


@dataclass
class MoatReport:
    division: str
    score: MoatScore
    recommendations: List[str]


class MoatAnalyzer:
    DIMENSIONS = ['network_effects', 'switching_costs', 'data_advantage', 'brand']

    def compute(self, division: Dict[str, float]) -> MoatReport:
        scores = {dimension: round(division.get(dimension, 0.5), 2) for dimension in self.DIMENSIONS}
        total = round(sum(scores.values()) / len(scores), 2)
        trend = 'strengthening' if total >= 0.65 else 'fragile'
        vs_competitors = {dimension: round(score - 0.55, 2) for dimension, score in scores.items()}
        weakest = sorted(scores, key=scores.get)[:2]
        recommendations = [f'Strengthen {dimension.replace("_", " ")}' for dimension in weakest]
        return MoatReport(division.get('name', 'unknown'), MoatScore(scores, total, trend, vs_competitors), recommendations)
