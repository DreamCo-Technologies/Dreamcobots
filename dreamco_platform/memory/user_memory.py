"""
DreamCo Platform — User Memory
================================

``UserMemory`` stores persistent context per user:
* Preferences and communication style
* Past decisions and their outcomes
* Successful workflow patterns
* Profitability history by user

Built on top of ``MemoryStore``.

Usage::

    um = UserMemory()
    um.record_decision("user:alice", "chose workflow: lead_pipeline", importance=0.7)
    history = um.get_history("user:alice", limit=10)
"""

from __future__ import annotations

from typing import Any

from dreamco_platform.memory.memory_store import MemoryRecord, MemoryStore, MemoryType


class UserMemory:
    """Per-user persistent memory layer."""

    def __init__(self, store: MemoryStore | None = None) -> None:
        self._store = store or MemoryStore()

    def _subject(self, user_id: str) -> str:
        return f"user:{user_id}"

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    def record_decision(
        self,
        user_id: str,
        content: str,
        importance: float = 0.5,
        context: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> MemoryRecord:
        record = MemoryRecord(
            subject=self._subject(user_id),
            memory_type=MemoryType.DECISION,
            content=content,
            importance=importance,
            context=context or {},
            tags=tags or [],
        )
        self._store.write(record)
        return record

    def record_outcome(
        self,
        user_id: str,
        content: str,
        success: bool,
        importance: float = 0.5,
        context: dict[str, Any] | None = None,
    ) -> MemoryRecord:
        ctx = dict(context or {})
        ctx["success"] = success
        record = MemoryRecord(
            subject=self._subject(user_id),
            memory_type=MemoryType.OUTCOME,
            content=content,
            importance=importance,
            context=ctx,
        )
        self._store.write(record)
        return record

    def record_preference(
        self,
        user_id: str,
        preference_key: str,
        value: Any,
        importance: float = 0.6,
    ) -> MemoryRecord:
        record = MemoryRecord(
            subject=self._subject(user_id),
            memory_type=MemoryType.CONTEXT,
            content=f"preference:{preference_key}={value}",
            importance=importance,
            context={"key": preference_key, "value": value},
            tags=["preference"],
        )
        self._store.write(record)
        return record

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def get_history(
        self,
        user_id: str,
        memory_type: MemoryType | None = None,
        limit: int = 20,
    ) -> list[MemoryRecord]:
        return self._store.recall(
            self._subject(user_id),
            memory_type=memory_type,
            limit=limit,
        )

    def get_decisions(self, user_id: str, limit: int = 10) -> list[MemoryRecord]:
        return self._store.recall(
            self._subject(user_id),
            memory_type=MemoryType.DECISION,
            limit=limit,
        )

    def get_outcomes(self, user_id: str, limit: int = 10) -> list[MemoryRecord]:
        return self._store.recall(
            self._subject(user_id),
            memory_type=MemoryType.OUTCOME,
            limit=limit,
        )

    def total_for_user(self, user_id: str) -> int:
        return len(self._store.recall(self._subject(user_id), limit=100_000))
