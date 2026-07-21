from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ErrorPattern:
    signature: str
    root_cause: str
    recovery_strategy: str
    success_rate: float


@dataclass
class RecoveryPlan:
    bot_id: str
    actions: List[str]
    selected_strategy: str
    confidence: float


class ErrorRecovery:
    def __init__(self) -> None:
        self.patterns: List[ErrorPattern] = [
            ErrorPattern('timeout', 'network slowness', 'retry', 0.78),
            ErrorPattern('missing dependency', 'deployment drift', 'fallback', 0.61),
            ErrorPattern('quota exceeded', 'upstream limit', 'degrade', 0.72),
        ]

    def handle(self, bot_id: str, error: str) -> RecoveryPlan:
        pattern = next((item for item in self.patterns if item.signature in error.lower()), None)
        if pattern is None:
            pattern = ErrorPattern(error[:30], 'unknown', 'escalate', 0.4)
        actions = self._actions(pattern.recovery_strategy)
        return RecoveryPlan(bot_id, actions, pattern.recovery_strategy, pattern.success_rate)

    def learn(self, signature: str, root_cause: str, strategy: str, success_rate: float) -> None:
        self.patterns.append(ErrorPattern(signature, root_cause, strategy, success_rate))

    def _actions(self, strategy: str) -> List[str]:
        mapping = {
            'retry': ['Wait with backoff', 'Retry request', 'Record outcome'],
            'fallback': ['Switch to fallback dependency', 'Replay work item'],
            'degrade': ['Disable non-critical features', 'Notify operator'],
            'escalate': ['Open incident', 'Attach logs'],
            'self_repair': ['Restart worker', 'Refresh cache', 'Retry validation'],
        }
        return mapping.get(strategy, mapping['escalate'])

def catalog(self) -> Dict[str, str]:
    return {pattern.signature: pattern.recovery_strategy for pattern in self.patterns}


def best_strategy(self, error: str) -> str:
    plan = self.handle('preview', error)
    return plan.selected_strategy


ErrorRecovery.catalog = catalog
ErrorRecovery.best_strategy = best_strategy
