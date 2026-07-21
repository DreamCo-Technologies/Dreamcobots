"""Ingest DreamCo bot metadata into embeddings and the knowledge graph."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from dreamco_platform.knowledge.graph_engine import KnowledgeGraphEngine
from dreamco_platform.memory.embedding_store import EmbeddingStore

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "reports" / "knowledge_ingestion_state.json"


class KnowledgeIngestionPipeline:
    """Incrementally ingest bot profiles into vector and graph stores."""

    def __init__(self, embedding_store: Any | None = None, graph: KnowledgeGraphEngine | None = None) -> None:
        self.embedding_store = embedding_store or EmbeddingStore()
        self.graph = graph or KnowledgeGraphEngine()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if OpenAI and os.getenv("OPENAI_API_KEY") else None
        self.state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}

    def _hash_profile(self, payload: dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def _embed(self, text: str) -> list[float]:
        if self.client is None:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            return [(digest[i % len(digest)] / 255.0) * 2 - 1 for i in range(32)]
        result = self.client.embeddings.create(model="text-embedding-3-small", input=text)
        return list(result.data[0].embedding)

    def ingest(self) -> dict[str, int]:
        indexed = 0
        skipped = 0
        for profile_path in sorted((ROOT / "bots").glob("*/bot_profile.json")):
            payload = json.loads(profile_path.read_text())
            slug = payload.get("slug", profile_path.parent.name)
            digest = self._hash_profile(payload)
            if self.state.get(slug) == digest:
                skipped += 1
                continue
            text = " ".join([payload.get("displayName", slug), payload.get("description", ""), " ".join(payload.get("capabilities", []))])
            self.embedding_store.upsert(f"bot:{slug}", self._embed(text), metadata=payload)
            self.graph.add_node(slug, "Bot", **payload)
            division = payload.get("division", "Unknown")
            self.graph.add_node(division, "Division", name=division)
            self.graph.add_edge(slug, "BELONGS_TO", division)
            for capability in payload.get("capabilities", []):
                capability_id = capability.lower().replace(" ", "-")
                self.graph.add_node(capability_id, "Capability", name=capability)
                self.graph.add_edge(slug, "CALLS", capability_id)
            self.state[slug] = digest
            indexed += 1
        STATE_FILE.write_text(json.dumps(self.state, indent=2, sort_keys=True) + "\n")
        return {"indexed": indexed, "skipped": skipped, "tracked": len(self.state)}


def main() -> None:
    pipeline = KnowledgeIngestionPipeline()
    print(json.dumps(pipeline.ingest(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
