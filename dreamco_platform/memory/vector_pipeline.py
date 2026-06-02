"""Pipeline that converts DreamMemory entries into vector embeddings."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from typing import Any

from dreamco_platform.memory.dream_memory import MemoryEntry, MemoryType
from dreamco_platform.memory.embedding_store import EmbeddingStore


class VectorMemoryPipeline:
    """Serialize important memory entries and push them into vector storage."""

    def __init__(self, store: Any | None = None) -> None:
        self.store = store or EmbeddingStore()

    def _serialize_entry(self, entry: MemoryEntry) -> str:
        payload = {
            "subject": entry.subject,
            "source": entry.source,
            "type": entry.memory_type.value,
            "data": entry.data,
            "profitability_usd": entry.profitability_usd,
            "tags": entry.tags,
        }
        return json.dumps(payload, sort_keys=True)

    def _embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [(digest[i % len(digest)] / 255.0) * 2 - 1 for i in range(32)]

    def flush_to_vector_db(self, entries: list[MemoryEntry]) -> dict[str, Any]:
        stored = 0
        clusters = self.cluster_similar_outcomes(entries)
        for entry in entries:
            if entry.memory_type not in {MemoryType.OUTCOME, MemoryType.PROFITABILITY}:
                continue
            payload = self._serialize_entry(entry)
            metadata = {"subject": entry.subject, "type": entry.memory_type.value, "cluster": clusters.get(entry.memory_id)}
            self.store.upsert(f"memory:{entry.memory_id}", self._embed(payload), metadata=metadata)
            stored += 1
        return {"stored": stored, "clusters": len(set(c for c in clusters.values() if c is not None))}

    def cluster_similar_outcomes(self, entries: list[MemoryEntry], threshold: float = 0.92) -> dict[str, str | None]:
        clusters: dict[str, str | None] = {}
        centroids: dict[str, list[float]] = {}
        for entry in entries:
            if entry.memory_type not in {MemoryType.OUTCOME, MemoryType.PROFITABILITY}:
                continue
            vector = self._embed(self._serialize_entry(entry))
            assigned = None
            for cluster_id, centroid in centroids.items():
                score = sum(a * b for a, b in zip(vector, centroid)) / max(sum(x * x for x in vector), 1)
                if score >= threshold:
                    assigned = cluster_id
                    break
            if assigned is None:
                assigned = f"cluster-{len(centroids) + 1}"
                centroids[assigned] = vector
            clusters[entry.memory_id] = assigned
        return clusters
