from __future__ import annotations

import json
import os
import threading
from collections import defaultdict, deque
from typing import Any

from dreamco_platform.memory.embedding_store import EmbeddingStore
from dreamco_platform.swarm.stigmergy.pheromone import SemanticPheromone

try:
    import redis as _redis  # type: ignore[import]
except Exception:  # pragma: no cover - optional runtime dependency
    _redis = None  # type: ignore[assignment]


class StigmergyEnvironment:
    def __init__(
        self,
        *,
        redis_url: str | None = None,
        embedding_store: EmbeddingStore | None = None,
        key_prefix: str = "dreamco:stigmergy",
    ) -> None:
        self._lock = threading.Lock()
        self._key_prefix = key_prefix.rstrip(":")
        self._store: dict[str, list[SemanticPheromone]] = defaultdict(list)
        self._stream: deque[dict[str, Any]] = deque(maxlen=20_000)
        self._embedding_store = embedding_store or EmbeddingStore()
        self._redis = self._connect_redis(redis_url)

    def _connect_redis(self, redis_url: str | None) -> Any:
        if _redis is None:
            return None
        url = redis_url or os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        try:
            client = _redis.from_url(url, decode_responses=True)
            client.ping()
            return client
        except Exception:
            return None

    def _trace_key(self, trace_type: str) -> str:
        return f"{self._key_prefix}:{trace_type}"

    def deposit(self, pheromone: SemanticPheromone) -> None:
        with self._lock:
            self._store[pheromone.trace_type].append(pheromone)
            self._stream.append({"action": "deposit", "pheromone": pheromone.to_dict()})
        if pheromone.embedding:
            self._embedding_store.upsert(pheromone.id, pheromone.embedding, metadata=pheromone.to_dict())
        if self._redis is not None:
            payload = json.dumps(pheromone.to_dict())
            key = self._trace_key(pheromone.trace_type)
            try:
                self._redis.xadd(key, {"payload": payload}, maxlen=10_000, approximate=True)
                self._redis.zadd(f"{key}:rank", {payload: pheromone.strength})
            except Exception:
                pass

    def reinforce(self, pheromone_id: str, *, profit_delta: float, success: bool = True) -> bool:
        with self._lock:
            for traces in self._store.values():
                for pheromone in traces:
                    if pheromone.id == pheromone_id:
                        pheromone.reinforce(profit_delta=profit_delta, success=success)
                        self._stream.append({"action": "reinforce", "pheromone": pheromone.to_dict()})
                        return True
        return False

    def read_traces(
        self,
        *,
        context: dict[str, Any] | None = None,
        trace_types: list[str] | None = None,
        embedding: list[float] | None = None,
        limit: int = 20,
    ) -> list[SemanticPheromone]:
        context = context or {}
        with self._lock:
            selected_types = trace_types or list(self._store.keys())
            candidates = [p for t in selected_types for p in self._store.get(t, [])]
        filtered = [p for p in candidates if all(p.context.get(k) == v for k, v in context.items())]
        if embedding:
            nearest = self._embedding_store.nearest(embedding, top_k=limit, min_score=0.1)
            by_id = {item.key for item in nearest}
            filtered = [p for p in filtered if p.id in by_id]
        scored = sorted(
            [p for p in filtered if p.is_active()],
            key=lambda p: p.current_strength() * (0.5 + p.trust_score),
            reverse=True,
        )
        return scored[:limit]

    def cleanup(self) -> int:
        removed = 0
        with self._lock:
            for trace_type, traces in list(self._store.items()):
                active = [p for p in traces if p.is_active()]
                removed += len(traces) - len(active)
                self._store[trace_type] = active
        return removed

    def get_stream_entries(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._stream)[-limit:]

    def metrics(self) -> dict[str, Any]:
        with self._lock:
            traces = [p for values in self._store.values() for p in values if p.is_active()]
        by_category: dict[str, int] = defaultdict(int)
        total_strength = 0.0
        for pheromone in traces:
            by_category[pheromone.semantic_category] += 1
            total_strength += pheromone.current_strength()
        return {
            "active_traces": len(traces),
            "total_strength": round(total_strength, 4),
            "density_by_category": dict(by_category),
            "redis_connected": self._redis is not None,
        }
