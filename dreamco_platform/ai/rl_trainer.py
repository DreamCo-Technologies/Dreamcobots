"""Reinforcement learning training analytics and reward tracking."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class Episode:
    reward: float
    steps: int
    success: bool


class RLTrainer:
    def __init__(self) -> None:
        self.episodes: List[Episode] = []

    def record_episode(self, reward: float, steps: int, success: bool) -> Episode:
        episode = Episode(float(reward), int(steps), bool(success))
        self.episodes.append(episode)
        return episode

    def policy_score(self) -> Dict[str, float]:
        if not self.episodes:
            return {'reward_mean': 0.0, 'success_rate': 0.0, 'efficiency': 0.0}
        reward_mean = sum(ep.reward for ep in self.episodes) / len(self.episodes)
        success_rate = sum(ep.success for ep in self.episodes) / len(self.episodes)
        avg_steps = sum(ep.steps for ep in self.episodes) / len(self.episodes)
        efficiency = max(0.0, min(1.0, reward_mean / max(avg_steps, 1)))
        return {'reward_mean': round(reward_mean, 3), 'success_rate': round(success_rate, 3), 'efficiency': round(efficiency, 3)}

    def training_state(self) -> Dict[str, object]:
        score = self.policy_score()
        trend = 'improving' if len(self.episodes) >= 2 and self.episodes[-1].reward >= self.episodes[0].reward else 'flat'
        return {'episodes': len(self.episodes), 'trend': trend, 'score': score}


def replay(episodes: Iterable[Dict[str, object]]) -> Dict[str, object]:
    trainer = RLTrainer()
    for item in episodes:
        trainer.record_episode(float(item['reward']), int(item['steps']), bool(item['success']))
    return trainer.training_state()
