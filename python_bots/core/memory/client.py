"""
DreamCo OS — MemoryClient (Unified Façade)
===========================================

``MemoryClient`` wires all four memory tiers together and exposes the single
interface that every ``DreamCoBot`` uses:

* ``memory.save(key, value)``        — short-term session storage
* ``memory.load(key)``               — short-term recall
* ``memory.store_doc(id, text)``     — long-term vector storage
* ``memory.recall(query, top_k)``    — semantic search
* ``memory.state(key, value)``       — relational state upsert
* ``memory.get_state(key)``          — relational state read
* ``memory.event(type, payload)``    — behavioral graph event
* ``memory.forget(key)``             — GDPR-compliant deletion across all tiers
"""

from __future__ import annotations

from typing import Any

from python_bots.core.memory.short_term import ShortTermMemory
from python_bots.core.memory.long_term import LongTermMemory
from python_bots.core.memory.structured import StructuredMemory
from python_bots.core.memory.behavioral import BehavioralMemory, BehavioralEvent


class MemoryClient:
    """Unified four-tier memory interface for DreamCo bots.

    Parameters
    ----------
    bot_id:
        Unique identifier for the owning bot.
    redis_url:
        Optional Redis connection URL (overrides ``REDIS_URL`` env-var).
    db_url:
        Optional database URL for structured memory.
    vector_backend:
        ``"chroma"`` (default) or ``"pinecone"``.
    """

    def __init__(
        self,
        bot_id: str,
        redis_url: str | None = None,
        db_url: str | None = None,
        vector_backend: str = "chroma",
    ) -> None:
        self.bot_id = bot_id
        self.short = ShortTermMemory(bot_id=bot_id, redis_url=redis_url)
        self.long = LongTermMemory(bot_id=bot_id, backend=vector_backend)
        self.structured = StructuredMemory(bot_id=bot_id, db_url=db_url)
        self.behavioral = BehavioralMemory(bot_id=bot_id)

    # ------------------------------------------------------------------
    # Short-term
    # ------------------------------------------------------------------

    def save(self, key: str, value: Any) -> None:
        """Save to short-term (Redis/in-process) memory."""
        self.short.save(key, value)
        self.behavioral.record_event("memory.save", {"key": key})

    def load(self, key: str) -> Any | None:
        """Load from short-term memory."""
        return self.short.load(key)

    # ------------------------------------------------------------------
    # Long-term / semantic
    # ------------------------------------------------------------------

    def store_doc(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        """Store a document in the vector database."""
        self.long.store(doc_id, text, metadata)
        self.behavioral.record_event("memory.store_doc", {"doc_id": doc_id})

    def recall(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Semantic recall from the vector database."""
        return self.long.recall(query, top_k)

    # ------------------------------------------------------------------
    # Structured / relational
    # ------------------------------------------------------------------

    def state(self, key: str, value: Any) -> None:
        """Upsert a value in structured (relational) state."""
        self.structured.upsert_state(key, value)

    def get_state(self, key: str) -> Any | None:
        """Get a value from structured state."""
        return self.structured.get_state(key)

    def record_run(self, **kwargs: Any) -> str:
        """Record a bot run to the structured store. Returns run_id."""
        return self.structured.record_run(**kwargs)

    # ------------------------------------------------------------------
    # Behavioral / event graph
    # ------------------------------------------------------------------

    def event(
        self, event_type: str, payload: dict[str, Any] | None = None, *, pin: bool = False
    ) -> BehavioralEvent:
        """Record a behavioral event to the graph."""
        return self.behavioral.record_event(event_type, payload, pin=pin)

    # ------------------------------------------------------------------
    # GDPR / deletion
    # ------------------------------------------------------------------

    def forget(self, key: str) -> None:
        """Delete *key* from ALL memory tiers."""
        self.short.forget(key)
        self.long.forget(key)
        self.structured.delete_state(key)

    # ------------------------------------------------------------------
    # Cross-session bootstrap
    # ------------------------------------------------------------------

    def load_last_session(self) -> dict[str, Any] | None:
        """Return the most recent structured state snapshot for cross-session continuity."""
        return self.structured.get_state("__last_session__")

    def save_session(self, snapshot: dict[str, Any]) -> None:
        """Persist a session snapshot for future cross-session recall."""
        self.structured.upsert_state("__last_session__", snapshot)
        self.save("__last_session__", snapshot)

    def stats(self) -> dict[str, Any]:
        return {
            "bot_id": self.bot_id,
            "short_term_keys": len(self.short.keys()),
            "long_term_docs": self.long.count(),
            "behavioral": self.behavioral.stats(),
        }
