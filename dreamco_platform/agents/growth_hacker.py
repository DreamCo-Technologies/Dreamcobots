from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class GrowthExperiment:
    hypothesis: str
    implementation: str
    expected_lift: float
    actual_lift: float = 0.0

    @property
    def ice_score(self) -> float:
        impact = self.expected_lift
        confidence = 0.7 if self.actual_lift == 0 else min(1.0, 0.5 + abs(self.actual_lift - self.expected_lift))
        ease = 0.9 if 'email' in self.implementation.lower() else 0.6
        return round(impact * confidence * ease, 3)


class GrowthHacker:
    def generate_experiments(self, division: str) -> List[GrowthExperiment]:
        experiments = [
            GrowthExperiment(f'{division}: launch referral loop', 'Add referral CTA to onboarding email and dashboard', 0.22),
            GrowthExperiment(f'{division}: showcase social proof', 'Inject customer win cards into pricing pages', 0.14),
            GrowthExperiment(f'{division}: activate creator incentives', 'Reward user-generated tutorials and templates', 0.18),
        ]
        return sorted(experiments, key=lambda item: item.ice_score, reverse=True)

def rank_by_ice(self, experiments: Iterable[GrowthExperiment]) -> List[GrowthExperiment]:
    return sorted(list(experiments), key=lambda item: item.ice_score, reverse=True)


def record_result(self, experiment: GrowthExperiment, actual_lift: float) -> GrowthExperiment:
    experiment.actual_lift = actual_lift
    return experiment


def summary(self, division: str) -> List[dict]:
    return [
        {
            'hypothesis': item.hypothesis,
            'ice_score': item.ice_score,
            'implementation': item.implementation,
        }
        for item in self.generate_experiments(division)
    ]


GrowthHacker.rank_by_ice = rank_by_ice
GrowthHacker.record_result = record_result
GrowthHacker.summary = summary

def best_experiment(self, division: str) -> GrowthExperiment:
    return self.generate_experiments(division)[0]


def total_expected_lift(self, division: str) -> float:
    return round(sum(item.expected_lift for item in self.generate_experiments(division)), 3)


GrowthHacker.best_experiment = best_experiment
GrowthHacker.total_expected_lift = total_expected_lift
