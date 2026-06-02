from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class CognitiveLoad:
    tokens_per_request: int
    context_length: int
    tool_calls: int
    parallel_requests: int

    def complexity(self) -> float:
        return self.tokens_per_request * 0.002 + self.context_length * 0.001 + self.tool_calls * 0.8 + self.parallel_requests * 1.2


@dataclass
class BotInstance:
    instance_id: str
    max_complexity: float
    queued_complexity: float = 0.0


class LoadBalancer:
    def __init__(self, instances: List[BotInstance]) -> None:
        self.instances = instances

    def route(self, request: CognitiveLoad) -> BotInstance:
        complexity = request.complexity()
        candidates = sorted(self.instances, key=lambda instance: (instance.queued_complexity / max(instance.max_complexity, 1), instance.queued_complexity))
        for instance in candidates:
            if instance.queued_complexity + complexity <= instance.max_complexity:
                instance.queued_complexity += complexity
                return instance
        selected = min(self.instances, key=lambda instance: instance.queued_complexity)
        selected.queued_complexity += complexity * 0.5
        return selected

    def estimate_completion_time(self, instance_id: str) -> float:
        instance = next(instance for instance in self.instances if instance.instance_id == instance_id)
        return round(instance.queued_complexity / max(instance.max_complexity, 1) * 60, 2)

def queue_snapshot(self) -> list[dict]:
    return [
        {
            'instance_id': instance.instance_id,
            'queued_complexity': round(instance.queued_complexity, 3),
            'estimated_minutes': self.estimate_completion_time(instance.instance_id),
        }
        for instance in self.instances
    ]


def release(self, instance_id: str, complexity: float) -> None:
    instance = next(instance for instance in self.instances if instance.instance_id == instance_id)
    instance.queued_complexity = max(0.0, instance.queued_complexity - complexity)


LoadBalancer.queue_snapshot = queue_snapshot
LoadBalancer.release = release
