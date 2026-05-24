from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from .governance import CapabilityScope, GovernanceEngine
from .lifecycle import BotLifecycleState
from .memory.client import MemoryClient
from .observability import Observability


@dataclass
class DreamCoBot(ABC):
    bot_id: str
    name: str
    capabilities: Iterable[CapabilityScope] = field(default_factory=lambda: [CapabilityScope.READ])
    memory: MemoryClient = field(default_factory=MemoryClient)
    governance: GovernanceEngine = field(default_factory=GovernanceEngine)
    observability: Observability = field(default_factory=Observability)

    state: BotLifecycleState = BotLifecycleState.IDLE
    audit_log: List[Dict[str, Any]] = field(default_factory=list)

    @abstractmethod
    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def analyze(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def monetize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.governance.enforce(self.bot_id, self.capabilities)
        if self.governance.is_quarantined(self.bot_id):
            self.state = BotLifecycleState.QUARANTINED
            return {"status": "quarantined", "reason": self.governance.quarantine_reason(self.bot_id)}

        self.state = BotLifecycleState.RUNNING
        started = datetime.now(timezone.utc).isoformat()
        self._audit("started", {"payload": payload, "started": started})

        analyzed = await self.analyze(payload)
        outcome = await self.run(analyzed)
        revenue = await self.monetize(outcome)
        final = await self.report(revenue)

        await self.memory.remember(self.bot_id, {"final": final, "started": started})
        await self.memory.set_state(self.bot_id, {"state": BotLifecycleState.IDLE.value})

        self.state = BotLifecycleState.IDLE
        self._audit("completed", {"result": final})
        self.observability.incr("bot_runs_total")
        return final

    def _audit(self, action: str, payload: Dict[str, Any]) -> None:
        event = {
            "bot_id": self.bot_id,
            "state": self.state.value,
            "action": action,
            "payload": payload,
            "at": datetime.now(timezone.utc).isoformat(),
        }
        self.audit_log.append(event)
        self.observability.track("audit", **event)
