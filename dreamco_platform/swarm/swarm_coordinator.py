from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class CoordinationStrategy(Enum):
    SEQUENTIAL = 'sequential'
    PARALLEL = 'parallel'
    AUCTION = 'auction'
    CONSENSUS = 'consensus'


@dataclass
class SwarmTask:
    objective: str
    participating_bots: List[str]
    coordination_strategy: CoordinationStrategy
    pheromone_tag: str = 'default'


class SwarmCoordinator:
    def __init__(self) -> None:
        self.pheromones: Dict[str, float] = {}
        self.history: List[dict] = []

    def execute(self, task: SwarmTask) -> List[dict]:
        self.pheromones[task.pheromone_tag] = self.pheromones.get(task.pheromone_tag, 0.0) + 1.0
        if task.coordination_strategy == CoordinationStrategy.SEQUENTIAL:
            result = [{'bot': bot, 'order': index + 1} for index, bot in enumerate(task.participating_bots)]
        elif task.coordination_strategy == CoordinationStrategy.PARALLEL:
            result = [{'bot': bot, 'order': 'parallel'} for bot in task.participating_bots]
        elif task.coordination_strategy == CoordinationStrategy.AUCTION:
            ranked = sorted(task.participating_bots, key=lambda bot: self._bid(bot, task.objective), reverse=True)
            result = [{'bot': bot, 'score': self._bid(bot, task.objective)} for bot in ranked]
        else:
            result = [{'bot': bot, 'vote': self._vote(bot, task.objective)} for bot in task.participating_bots]
        self.history.append({'objective': task.objective, 'result': result})
        return result

    def _bid(self, bot_id: str, objective: str) -> float:
        return (sum(map(ord, bot_id)) + len(objective) + self.pheromones.get('default', 0.0)) % 100 / 100

    def _vote(self, bot_id: str, objective: str) -> bool:
        return (sum(map(ord, bot_id + objective)) % 2) == 0

def pheromone_level(self, tag: str) -> float:
    return round(self.pheromones.get(tag, 0.0), 3)


def decay_pheromones(self, factor: float = 0.9) -> Dict[str, float]:
    for key in list(self.pheromones):
        self.pheromones[key] = round(self.pheromones[key] * factor, 3)
    return dict(self.pheromones)


def last_execution(self) -> dict | None:
    return self.history[-1] if self.history else None


SwarmCoordinator.pheromone_level = pheromone_level
SwarmCoordinator.decay_pheromones = decay_pheromones
SwarmCoordinator.last_execution = last_execution
