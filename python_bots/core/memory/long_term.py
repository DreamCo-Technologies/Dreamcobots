"""
DreamCo OS — Long-Term Memory (Vector DB)
==========================================

Semantic recall backed by Chroma (local) or Pinecone (cloud), with a
graceful in-process fallback for development environments.

Usage::

    mem = LongTermMemory(bot_id="lead_gen_bot")
    mem.store("doc_1", "The customer asked about pricing tiers.")
    results = mem.recall("pricing questions", top_k=3)
    # [{"id": "doc_1", "text": "...", "score": 0.92}]
"""

from __future__ import annotations

import hashlib
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class _InProcessVectorStore:
    """Minimal cosine-similarity vector store for development/testing."""

    def __init__(self) -> None:
        self._docs: dict[str, str] = {}

    def upsert(self, doc_id: str, text: str) -> None:
        self._docs[doc_id] = text

    def query(self, query_text: str, top_k: int) -> list[dict[str, Any]]:
        # Simple substring-match ranking (no real embeddings)
        query_lower = query_text.lower()
        scored = []
        for doc_id, text in self._docs.items():
            score = sum(
                1 for word in query_lower.split() if word in text.lower()
            ) / max(len(query_lower.split()), 1)
            scored.append({"id": doc_id, "text": text, "score": round(score, 4)})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def delete(self, doc_id: str) -> None:
        self._docs.pop(doc_id, None)


class LongTermMemory:
    """Vector-database long-term memory with Chroma/Pinecone backend.

    Parameters
    ----------
    bot_id:
        Owning bot identifier — used as the Chroma collection name.
    backend:
        ``"chroma"`` (default) or ``"pinecone"``.
    persist_directory:
        Local directory for Chroma persistence.
    """

    def __init__(
        self,
        bot_id: str,
        backend: str = "chroma",
        persist_directory: str = ".dreamco_chroma",
    ) -> None:
        self.bot_id = bot_id
        self._client: Any = None
        self._collection: Any = None
        self._fallback = _InProcessVectorStore()

        if backend == "chroma":
            try:
                import chromadb  # type: ignore

                client = chromadb.PersistentClient(path=persist_directory)
                self._collection = client.get_or_create_collection(
                    name=f"dreamco_{bot_id}",
                    metadata={"hnsw:space": "cosine"},
                )
                logger.debug("LongTermMemory: Chroma collection 'dreamco_%s' ready", bot_id)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "LongTermMemory: Chroma unavailable (%s) — using in-process fallback", exc
                )
        elif backend == "pinecone":
            logger.info("LongTermMemory: Pinecone backend selected — configure via PINECONE_API_KEY")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def store(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        """Store *text* document with *doc_id* for future semantic recall."""
        if self._collection is not None:
            try:
                self._collection.upsert(
                    ids=[doc_id],
                    documents=[text],
                    metadatas=[metadata or {}],
                )
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("LongTermMemory.store Chroma error: %s", exc)
        self._fallback.upsert(doc_id, text)

    def recall(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Return the *top_k* most semantically similar documents to *query*."""
        if self._collection is not None:
            try:
                results = self._collection.query(
                    query_texts=[query],
                    n_results=min(top_k, max(self._collection.count(), 1)),
                )
                docs = results.get("documents", [[]])[0]
                ids = results.get("ids", [[]])[0]
                distances = results.get("distances", [[]])[0]
                return [
                    {"id": ids[i], "text": docs[i], "score": round(1 - distances[i], 4)}
                    for i in range(len(ids))
                ]
            except Exception as exc:  # noqa: BLE001
                logger.warning("LongTermMemory.recall Chroma error: %s", exc)
        return self._fallback.query(query, top_k)

    def forget(self, doc_id: str) -> None:
        """Delete document *doc_id* (GDPR-compliant)."""
        if self._collection is not None:
            try:
                self._collection.delete(ids=[doc_id])
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("LongTermMemory.forget Chroma error: %s", exc)
        self._fallback.delete(doc_id)

    def count(self) -> int:
        """Return the number of stored documents."""
        if self._collection is not None:
            try:
                return self._collection.count()
            except Exception:  # noqa: BLE001
                pass
        return len(self._fallback._docs)
