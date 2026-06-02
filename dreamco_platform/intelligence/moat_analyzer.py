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

def weakest_dimensions(self, report: MoatReport) -> List[str]:
    return sorted(report.score.dimension_scores, key=report.score.dimension_scores.get)[:2]


def benchmark(self, report: MoatReport, competitor_scores: Dict[str, float]) -> Dict[str, float]:
    return {
        key: round(report.score.dimension_scores.get(key, 0.0) - competitor_scores.get(key, 0.0), 2)
        for key in report.score.dimension_scores
    }


MoatAnalyzer.weakest_dimensions = weakest_dimensions
MoatAnalyzer.benchmark = benchmark

def score_card(self, report: MoatReport) -> List[tuple[str, float]]:
    return sorted(report.score.dimension_scores.items(), key=lambda item: item[1], reverse=True)


def strongest_dimension(self, report: MoatReport) -> str:
    return max(report.score.dimension_scores, key=report.score.dimension_scores.get)


MoatAnalyzer.score_card = score_card
MoatAnalyzer.strongest_dimension = strongest_dimension

def recommendation_count(self, report: MoatReport) -> int:
    return len(report.recommendations)


MoatAnalyzer.recommendation_count = recommendation_count
