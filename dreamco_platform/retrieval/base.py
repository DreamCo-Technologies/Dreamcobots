"""
DreamCo Platform — Retrieval Backend Interface
===============================================

All retrieval adapters (Redis, Pinecone, Elastic, SQL) implement this
abstract base class so ``RetrievalLayer`` can dispatch calls uniformly.
"""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RetrievalRecord:
    """
    A single record stored in / retrieved from a retrieval backend.

    Attributes
    ----------
    key : str
        Unique identifier for this record.
    content : str
        Textual content (document chunk, fact, conversation turn, etc.).
    embedding : list[float] | None
        Dense vector embedding (required by vector backends).
    score : float
        Relevance score returned by similarity search (0.0 – 1.0).
    metadata : dict
        Arbitrary key-value labels (e.g. source, workflow_id, timestamp).
    created_at : float
        Unix timestamp when the record was stored.
    """

    key: str
    content: str
    embedding: list[float] | None = None
    score: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "key": self.key,
            "content": self.content,
            "score": self.score,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }


class RetrievalBackend(ABC):
    """
    Abstract interface for all DreamCo retrieval backends.

    Implementations must provide:
    * ``upsert`` — insert or update a record.
    * ``get`` — fetch a record by exact key.
    * ``search`` — semantic / keyword / SQL search.
    * ``delete`` — remove a record by key.
    * ``count`` — number of stored records.
    * ``backend_name`` — identifier string.
    """

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Return a short identifier for this backend (e.g. ``"redis"``)."""

    @abstractmethod
    def upsert(self, record: RetrievalRecord) -> None:
        """Insert or update *record*."""

    @abstractmethod
    def get(self, key: str) -> RetrievalRecord | None:
        """Return the record for *key*, or ``None`` if not found."""

    @abstractmethod
    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        embedding: list[float] | None = None,
    ) -> list[RetrievalRecord]:
        """
        Search for records matching *query*.

        Parameters
        ----------
        query : str
            Keyword or natural-language query string.
        limit : int
            Maximum number of results to return.
        filters : dict | None
            Backend-specific metadata filters.
        embedding : list[float] | None
            Query embedding for vector similarity search.

        Returns
        -------
        list[RetrievalRecord]
            Matching records, sorted by relevance score descending.
        """

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete the record with *key*.  Return ``True`` if found."""

    @abstractmethod
    def count(self) -> int:
        """Return the number of stored records."""
