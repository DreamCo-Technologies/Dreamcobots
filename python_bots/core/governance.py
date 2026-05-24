from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, Set


class CapabilityScope(str, Enum):
    READ = "read"
    WRITE = "write"
    NETWORK = "network"
    EXECUTE = "execute"


class PolicyViolation(Exception):
    pass


@dataclass
class GovernanceEngine:
    allowed_scopes: Set[CapabilityScope] = field(default_factory=lambda: {CapabilityScope.READ})
    rate_limit_per_minute: int = 120
    _requests: int = 0
    _quarantined: Dict[str, str] = field(default_factory=dict)

    def enforce(self, bot_id: str, requested: Iterable[CapabilityScope]) -> None:
        self._requests += 1
        if self._requests > self.rate_limit_per_minute:
            self.quarantine(bot_id, "rate_limit_exceeded")
            raise PolicyViolation("rate limit exceeded")

        for scope in requested:
            if scope not in self.allowed_scopes:
                self.quarantine(bot_id, f"scope_blocked:{scope.value}")
                raise PolicyViolation(f"scope not allowed: {scope.value}")

    def quarantine(self, bot_id: str, reason: str) -> None:
        self._quarantined[bot_id] = reason

    def release(self, bot_id: str) -> None:
        self._quarantined.pop(bot_id, None)

    def is_quarantined(self, bot_id: str) -> bool:
        return bot_id in self._quarantined

    def quarantine_reason(self, bot_id: str) -> str:
        return self._quarantined.get(bot_id, "")
