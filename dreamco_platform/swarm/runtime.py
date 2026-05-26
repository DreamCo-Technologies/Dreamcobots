from __future__ import annotations

from typing import Any

from dreamco_platform.memory.embedding_store import EmbeddingStore
from dreamco_platform.swarm.stigmergy.environment import StigmergyEnvironment


class DreamCoRuntime:
    """Shared runtime services for swarm-enabled bots."""

    def __init__(
        self,
        *,
        redis_url: str | None = None,
        vector_store: EmbeddingStore | None = None,
        governance: Any | None = None,
        memory: Any | None = None,
    ) -> None:
        self.vector_store = vector_store or EmbeddingStore()
        self.governance = governance
        self.memory = memory
        self.stigmergy = StigmergyEnvironment(redis_url=redis_url, embedding_store=self.vector_store)
        self._bot_roles: dict[str, str] = {}

    def register_bot_role(self, bot_id: str, role: str) -> None:
        self._bot_roles[bot_id] = role

    def bot_roles(self) -> dict[str, str]:
        return dict(self._bot_roles)

    def reinforce_trace(self, pheromone_id: str, *, profit_delta: float, success: bool = True) -> bool:
        return self.stigmergy.reinforce(pheromone_id, profit_delta=profit_delta, success=success)
