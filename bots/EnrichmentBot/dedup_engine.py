"""Vector similarity deduplication engine for enriched lead records."""

from __future__ import annotations

import hashlib
from typing import Any

from dreamco_platform.memory.embedding_store import EmbeddingStore


class LeadDedupEngine:
    """Compare lead vectors and merge highly similar records."""

    def __init__(self, store: Any | None = None) -> None:
        self.store = store or EmbeddingStore()

    def _embed(self, record: dict[str, Any]) -> list[float]:
        text = "|".join([record.get("name", ""), record.get("email", ""), record.get("company", "")]).lower()
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [(digest[i % len(digest)] / 255.0) * 2 - 1 for i in range(32)]

    def find_duplicate(self, record: dict[str, Any]) -> dict[str, Any] | None:
        vector = self._embed(record)
        matches = self.store.nearest(vector, top_k=1, min_score=0.95)
        if not matches:
            return None
        match = matches[0]
        if match.score <= 0.95:
            return None
        return {"key": match.key, "score": match.score, "metadata": match.metadata}

    def merge_records(self, existing: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
        merged = dict(existing)
        for key, value in new.items():
            if value in (None, "", []):
                continue
            if key not in merged or merged[key] in (None, "", []):
                merged[key] = value
            elif merged[key] != value and key in {"notes", "tags"}:
                merged[key] = sorted({*([merged[key]] if isinstance(merged[key], str) else merged[key]), *([value] if isinstance(value, str) else value)})
        merged["dedup_status"] = "merged"
        return merged

    def upsert_record(self, record_id: str, record: dict[str, Any]) -> dict[str, Any]:
        duplicate = self.find_duplicate(record)
        if duplicate:
            merged = self.merge_records(duplicate["metadata"], record)
            self.store.upsert(duplicate["key"], self._embed(merged), metadata=merged)
            return merged
        self.store.upsert(record_id, self._embed(record), metadata=record)
        return record
