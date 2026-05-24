from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class RedisMemoryStore:
    _store: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    async def append(self, key: str, value: Dict[str, Any]) -> None:
        self._store.setdefault(key, []).append(value)

    async def read(self, key: str, limit: int = 20) -> List[Dict[str, Any]]:
        return list(self._store.get(key, [])[-limit:])


@dataclass
class VectorMemoryStore:
    _docs: List[Dict[str, Any]] = field(default_factory=list)

    async def upsert(self, text: str, metadata: Dict[str, Any]) -> None:
        self._docs.append({"text": text, "metadata": metadata})

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_terms = set(query.lower().split())

        def score(doc: Dict[str, Any]) -> int:
            terms = set(doc["text"].lower().split())
            return len(query_terms & terms)

        ranked = sorted(self._docs, key=score, reverse=True)
        return ranked[:limit]


@dataclass
class PostgresStateStore:
    _rows: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    async def upsert(self, key: str, value: Dict[str, Any]) -> None:
        self._rows[key] = value

    async def get(self, key: str) -> Dict[str, Any]:
        return dict(self._rows.get(key, {}))


class MemoryClient:
    def __init__(self) -> None:
        self.short = RedisMemoryStore()
        self.long = VectorMemoryStore()
        self.structured = PostgresStateStore()
        self.behavioral = RedisMemoryStore()

    async def remember(self, bot_id: str, payload: Dict[str, Any]) -> None:
        await self.short.append(bot_id, payload)

    async def store_doc(self, text: str, metadata: Dict[str, Any]) -> None:
        await self.long.upsert(text, metadata)

    async def set_state(self, bot_id: str, state: Dict[str, Any]) -> None:
        await self.structured.upsert(bot_id, state)

    async def recent(self, bot_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        return await self.short.read(bot_id, limit=limit)

    async def semantic_recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        return await self.long.search(query, limit=limit)

    async def get_state(self, bot_id: str) -> Dict[str, Any]:
        return await self.structured.get(bot_id)
