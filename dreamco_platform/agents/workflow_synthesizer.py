from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class WorkflowDefinition:
    steps: List[dict]
    estimated_cost_usd: float
    estimated_duration_minutes: int


class WorkflowSynthesizer:
    def __init__(self, registry: Dict[str, List[str]]) -> None:
        self.registry = registry

    def from_description(self, goal: str) -> WorkflowDefinition:
        steps = []
        for token in [part.strip() for part in goal.replace(' then ', ',').split(',') if part.strip()]:
            bot = self._select_bot(token)
            steps.append({'task': token, 'bot': bot, 'validated': bot in self.registry})
        cost = round(sum(0.03 * len(step['task'].split()) for step in steps), 2)
        duration = len(steps) * 4 + sum(len(step['task'].split()) for step in steps)
        return WorkflowDefinition(steps, cost, duration)

    def _select_bot(self, task: str) -> str:
        task_lower = task.lower()
        best_bot = 'generalist-bot'
        best_score = -1
        for bot_id, capabilities in self.registry.items():
            score = sum(1 for capability in capabilities if capability.lower() in task_lower)
            if score > best_score:
                best_bot = bot_id
                best_score = score
        return best_bot
