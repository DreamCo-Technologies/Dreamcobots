"""Semantic search API for DreamCo capabilities and bots."""

from __future__ import annotations

import hashlib
import os
from typing import Any

from fastapi import APIRouter, Query

from dreamco_platform.memory.embedding_store import EmbeddingStore

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


class SemanticSearchService:
    """Embed queries and retrieve ranked capability matches."""

    def __init__(self, store: Any | None = None, model: str = "text-embedding-3-small") -> None:
        self.store = store or EmbeddingStore()
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if OpenAI and os.getenv("OPENAI_API_KEY") else None

    def _fallback_embedding(self, text: str, dimension: int = 32) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = [(digest[i % len(digest)] / 255.0) * 2 - 1 for i in range(dimension)]
        return values

    def embed_query(self, query: str) -> list[float]:
        if self.client is None:
            return self._fallback_embedding(query)
        response = self.client.embeddings.create(model=self.model, input=query)
        return list(response.data[0].embedding)

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        vector = self.embed_query(query)
        matches = self.store.nearest(vector, top_k=top_k)
        return [{"key": match.key, "score": match.score, "metadata": getattr(match, "metadata", {})} for match in matches]


def build_router(service: SemanticSearchService | None = None) -> APIRouter:
    router = APIRouter(tags=["semantic-search"])
    search_service = service or SemanticSearchService()

    @router.get("/api/capabilities/search")
    async def capability_search(q: str = Query(..., min_length=1), top_k: int = Query(10, ge=1, le=50)) -> dict[str, Any]:
        return {"query": q, "results": search_service.search(q, top_k=top_k)}

    return router


router = build_router()
