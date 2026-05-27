from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Protocol

from dreamco_platform.swarm.stigmergy import (
    PersistentStigmergyEnvironment,
    PheromoneTrace,
    StigmergicBot,
)


class RedisLikeClient(Protocol):
    def xadd(self, stream: str, values: dict[str, str], maxlen: int | None = None, approximate: bool = False) -> str: ...

    def zadd(self, key: str, mapping: dict[str, float]) -> int: ...


@dataclass(frozen=True)
class DreamCoRuntimeConfig:
    redis_stream_key: str = "dreamco:swarm:traces"
    redis_sorted_set_key: str = "dreamco:swarm:trace_strength"
    stream_max_len: int = 5_000
    decay_rate: float = 0.05


class DreamCoRuntime:
    def __init__(
        self,
        *,
        environment: PersistentStigmergyEnvironment | None = None,
        redis_client: RedisLikeClient | None = None,
        config: DreamCoRuntimeConfig | None = None,
    ) -> None:
        self.environment = environment or PersistentStigmergyEnvironment()
        self.redis_client = redis_client
        self.config = config or DreamCoRuntimeConfig()
        self._bot = StigmergicBot()

    def create_semantic_trace(
        self,
        *,
        trace_type: str,
        strength: float,
        position: tuple[int, int],
        bot_id: str,
        semantic_category: str,
        embedding: tuple[float, ...] = (),
        metadata: dict | None = None,
        foraging_role: str = "scout",
        trust_score: float = 0.5,
        economic_score: float = 0.0,
        profitability_signal: float = 0.0,
        volatility_signal: float = 0.0,
        origin_lineage: tuple[str, ...] = (),
        risk: float = 0.0,
    ) -> PheromoneTrace:
        return PheromoneTrace(
            trace_type=trace_type,
            strength=strength,
            position=position,
            bot_id=bot_id,
            risk=risk,
            embedding=embedding,
            semantic_category=semantic_category,
            trust_score=trust_score,
            economic_score=economic_score,
            profitability_signal=profitability_signal,
            volatility_signal=volatility_signal,
            origin_lineage=origin_lineage,
            foraging_role=foraging_role,
            metadata=dict(metadata or {}),
        )

    def deposit_trace(self, trace: PheromoneTrace, *, bot_role: str = "worker", approval: bool = False) -> dict:
        decision = self.environment.deposit(trace, bot_role=bot_role, approval=approval)
        if decision.allowed:
            self._write_trace_to_redis(trace)
        return {
            "allowed": decision.allowed,
            "reason": decision.reason,
            "requires_approval": decision.requires_approval,
        }

    def reinforce_trace(self, trace: PheromoneTrace, outcome: dict[str, float]) -> PheromoneTrace:
        return self._bot.reinforce_trace(trace, outcome)

    def apply_adaptive_decay(self) -> list[PheromoneTrace]:
        decayed: list[PheromoneTrace] = []
        active = list(self.environment.active_traces())
        self.environment._active_traces = []  # noqa: SLF001
        for trace in active:
            decayed_trace = self._bot.decay_trace(trace, base_decay_rate=self.config.decay_rate)
            if decayed_trace.strength > 0:
                self.environment._active_traces.append(decayed_trace)  # noqa: SLF001
                decayed.append(decayed_trace)
        return decayed

    def metrics(self) -> dict:
        payload = self.environment.metrics()
        payload["runtime"] = {
            "stream_key": self.config.redis_stream_key,
            "sorted_set_key": self.config.redis_sorted_set_key,
            "fetched_at": time.time(),
        }
        return payload

    def _write_trace_to_redis(self, trace: PheromoneTrace) -> None:
        if self.redis_client is None:
            return
        try:
            encoded_trace = {
                "bot_id": trace.bot_id,
                "trace_type": trace.trace_type,
                "semantic_category": trace.semantic_category,
                "foraging_role": trace.foraging_role,
                "strength": f"{trace.strength:.6f}",
                "risk": f"{trace.risk:.6f}",
            }
            self.redis_client.xadd(
                self.config.redis_stream_key,
                encoded_trace,
                maxlen=self.config.stream_max_len,
                approximate=True,
            )
            score_key = f"{trace.bot_id}:{trace.trace_type}:{trace.position[0]}:{trace.position[1]}"
            self.redis_client.zadd(self.config.redis_sorted_set_key, {score_key: float(trace.strength)})
        except Exception:  # noqa: BLE001
            return
