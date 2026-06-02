from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, List


@dataclass
class DelegationDecision:
    selected_bot: str
    reason: str
    confidence: float
    estimated_duration: float


class TaskDelegationMatrix:
    def __init__(self, capability_vectors: Dict[str, Dict[str, float]]) -> None:
        self.capability_vectors = capability_vectors
        self.performance_memory: Dict[str, float] = {bot: 1.0 for bot in capability_vectors}

    def score(self, bot_id: str, task_tokens: List[str]) -> float:
        vector = self.capability_vectors[bot_id]
        semantic = sum(vector.get(token, 0.0) for token in task_tokens)
        return semantic * self.performance_memory.get(bot_id, 1.0)

    def update(self, bot_id: str, outcome_score: float) -> None:
        self.performance_memory[bot_id] = self.performance_memory.get(bot_id, 1.0) * 0.7 + outcome_score * 0.3


class Delegation:
    def __init__(self, matrix: TaskDelegationMatrix) -> None:
        self.matrix = matrix

    def delegate(self, task_description: str) -> DelegationDecision:
        tokens = [token.lower() for token in task_description.split()]
        scores = {bot: self.matrix.score(bot, tokens) for bot in self.matrix.capability_vectors}
        selected = max(scores, key=scores.get)
        total = sum(max(score, 0.0) for score in scores.values()) or 1.0
        confidence = max(scores[selected], 0.0) / total
        duration = max(5.0, 60.0 / max(scores[selected], 0.5))
        return DelegationDecision(selected, f'Best semantic and historical fit for: {task_description}', round(confidence, 3), round(duration, 2))
