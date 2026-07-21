from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random
from typing import Dict, Iterable, List


@dataclass
class LocalUpdate:
    bot_id: str
    gradients: Dict[str, float]
    sample_count: int


@dataclass
class FederatedRound:
    round_id: int
    participants: List[str]
    started_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AggregatedUpdate:
    round_id: int
    weights: Dict[str, float]
    participant_count: int
    privacy_budget_used: float


class Coordinator:
    def __init__(self, noise_scale: float = 0.01, seed: int = 7) -> None:
        self.noise_scale = noise_scale
        self.random = random.Random(seed)
        self.round_counter = 0
        self.history: list[AggregatedUpdate] = []

    def run_round(self, participating_bots: Iterable[LocalUpdate]) -> AggregatedUpdate:
        updates = list(participating_bots)
        round_info = FederatedRound(self.round_counter + 1, [update.bot_id for update in updates])
        aggregated = self._fedavg(updates)
        noisy = {name: value + self.random.gauss(0.0, self.noise_scale) for name, value in aggregated.items()}
        result = AggregatedUpdate(
            round_id=round_info.round_id,
            weights=noisy,
            participant_count=len(updates),
            privacy_budget_used=round(self.noise_scale * max(1, len(noisy)), 4),
        )
        self.history.append(result)
        self.round_counter = round_info.round_id
        return result

    def _fedavg(self, updates: List[LocalUpdate]) -> Dict[str, float]:
        if not updates:
            return {}
        total_samples = sum(update.sample_count for update in updates) or 1
        aggregate: Dict[str, float] = {}
        for update in updates:
            weight = update.sample_count / total_samples
            for name, gradient in update.gradients.items():
                aggregate[name] = aggregate.get(name, 0.0) + gradient * weight
        return aggregate

    def summarize_history(self) -> List[dict]:
        return [
            {
                'round_id': entry.round_id,
                'participants': entry.participant_count,
                'privacy_budget': entry.privacy_budget_used,
            }
            for entry in self.history
        ]
