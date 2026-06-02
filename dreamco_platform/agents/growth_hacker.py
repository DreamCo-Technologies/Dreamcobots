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
