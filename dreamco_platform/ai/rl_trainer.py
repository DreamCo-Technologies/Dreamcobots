"""Reinforcement learning training analytics and reward tracking."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class Episode:
    reward: float
    steps: int
    success: bool
    exploration_rate: float = 0.0


class RLTrainer:
    def __init__(self) -> None:
        self.episodes: List[Episode] = []

    def record_episode(self, reward: float, steps: int, success: bool, exploration_rate: float = 0.0) -> Episode:
        episode = Episode(float(reward), int(steps), bool(success), float(exploration_rate))
        self.episodes.append(episode)
        return episode

    def policy_score(self) -> Dict[str, float]:
        if not self.episodes:
            return {'reward_mean': 0.0, 'success_rate': 0.0, 'efficiency': 0.0, 'stability': 0.0}
        reward_mean = sum(ep.reward for ep in self.episodes) / len(self.episodes)
        success_rate = sum(ep.success for ep in self.episodes) / len(self.episodes)
        avg_steps = sum(ep.steps for ep in self.episodes) / len(self.episodes)
        efficiency = max(0.0, min(1.0, reward_mean / max(avg_steps, 1)))
        drift = max(ep.reward for ep in self.episodes) - min(ep.reward for ep in self.episodes)
        stability = max(0.0, min(1.0, 1 - drift / max(abs(reward_mean) + 1, 1)))
        return {
            'reward_mean': round(reward_mean, 3),
            'success_rate': round(success_rate, 3),
            'efficiency': round(efficiency, 3),
            'stability': round(stability, 3),
        }

    def exploration_profile(self) -> Dict[str, float]:
        if not self.episodes:
            return {'avg_exploration': 0.0, 'latest_exploration': 0.0}
        return {
            'avg_exploration': round(sum(ep.exploration_rate for ep in self.episodes) / len(self.episodes), 3),
            'latest_exploration': round(self.episodes[-1].exploration_rate, 3),
        }

    def training_state(self) -> Dict[str, object]:
        score = self.policy_score()
        trend = 'improving' if len(self.episodes) >= 2 and self.episodes[-1].reward >= self.episodes[0].reward else 'flat'
        return {
            'episodes': len(self.episodes),
            'trend': trend,
            'score': score,
            'exploration': self.exploration_profile(),
        }

    def recommend_next_step(self) -> str:
        state = self.training_state()
        if state['score']['success_rate'] < 0.4:
            return 'Increase reward shaping or simplify the environment.'
        if state['score']['stability'] < 0.5:
            return 'Reduce learning rate and extend evaluation windows.'
        return 'Continue training and decrease exploration gradually.'


def replay(episodes: Iterable[Dict[str, object]]) -> Dict[str, object]:
    trainer = RLTrainer()
    for item in episodes:
        trainer.record_episode(float(item['reward']), int(item['steps']), bool(item['success']), float(item.get('exploration_rate', 0.0)))
    state = trainer.training_state()
    state['next_step'] = trainer.recommend_next_step()
    return state
