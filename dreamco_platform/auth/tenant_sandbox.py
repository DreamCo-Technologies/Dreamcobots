"""Multi-tenant sandbox isolation wrappers for DreamCo memory systems."""

from __future__ import annotations

from typing import Any

from dreamco_platform.memory.dream_memory import DreamMemory


class TenantSandbox:
    """Scope DreamMemory and embedding access to a single workspace."""

    def __init__(self, workspace_id: str, memory: DreamMemory, embedding_store: Any) -> None:
        self.workspace_id = workspace_id
        self.memory = memory
        self.embedding_store = embedding_store

    def _validate_workspace(self, workspace_id: str | None) -> None:
        if workspace_id != self.workspace_id:
            raise PermissionError(f"Cross-tenant access denied for {workspace_id}")

    def record_memory(self, entry) -> Any:
        self._validate_workspace(entry.metadata.get("workspace_id"))
        return self.memory.record(entry)

    def query_memory(self, *, workspace_id: str, **kwargs: Any) -> list[Any]:
        self._validate_workspace(workspace_id)
        return [entry for entry in self.memory.query(**kwargs) if entry.metadata.get("workspace_id") == workspace_id]

    def upsert_embedding(self, key: str, vector: list[float], metadata: dict[str, Any]) -> None:
        self._validate_workspace(metadata.get("workspace_id"))
        self.embedding_store.upsert(key, vector, metadata=metadata)

    def nearest_embeddings(self, vector: list[float], *, workspace_id: str, top_k: int = 10) -> list[Any]:
        self._validate_workspace(workspace_id)
        matches = self.embedding_store.nearest(vector, top_k=top_k)
        return [match for match in matches if getattr(match, "metadata", {}).get("workspace_id") == workspace_id]
