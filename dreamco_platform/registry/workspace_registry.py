"""
DreamCo Platform — Workspace Registry
======================================

Tracks organisational workspaces at the registry layer.  Complements the
``RBACRegistry`` in ``governance/rbac.py`` but operates at the metadata
level: workspace settings, feature flags, quota limits, and billing plan.

A ``WorkspaceRecord`` is lightweight — the full membership/permission graph
lives in ``RBACRegistry``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Workspace record
# ---------------------------------------------------------------------------

@dataclass
class WorkspaceRecord:
    workspace_id: str
    name: str
    owner_user_id: str
    billing_plan: str = "free"
    feature_flags: dict[str, bool] = field(default_factory=dict)
    quotas: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "name": self.name,
            "owner_user_id": self.owner_user_id,
            "billing_plan": self.billing_plan,
            "feature_flags": self.feature_flags,
            "quotas": self.quotas,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "active": self.active,
        }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class WorkspaceRegistry:
    """In-memory registry for organisational workspaces."""

    def __init__(self) -> None:
        self._store: dict[str, WorkspaceRecord] = {}

    # ------------------------------------------------------------------
    # Mutating operations
    # ------------------------------------------------------------------

    def create(self, record: WorkspaceRecord) -> None:
        if record.workspace_id in self._store:
            raise ValueError(
                f"Workspace '{record.workspace_id}' already exists"
            )
        self._store[record.workspace_id] = record

    def update_plan(self, workspace_id: str, plan: str) -> bool:
        ws = self._store.get(workspace_id)
        if ws is None:
            return False
        ws.billing_plan = plan
        return True

    def set_feature_flag(
        self, workspace_id: str, flag: str, value: bool
    ) -> bool:
        ws = self._store.get(workspace_id)
        if ws is None:
            return False
        ws.feature_flags[flag] = value
        return True

    def set_quota(self, workspace_id: str, resource: str, limit: int) -> bool:
        ws = self._store.get(workspace_id)
        if ws is None:
            return False
        ws.quotas[resource] = limit
        return True

    def deactivate(self, workspace_id: str) -> bool:
        ws = self._store.get(workspace_id)
        if ws is None:
            return False
        ws.active = False
        return True

    def delete(self, workspace_id: str) -> bool:
        if workspace_id not in self._store:
            return False
        del self._store[workspace_id]
        return True

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get(self, workspace_id: str) -> WorkspaceRecord | None:
        return self._store.get(workspace_id)

    def all_active(self) -> list[WorkspaceRecord]:
        return [ws for ws in self._store.values() if ws.active]

    def by_owner(self, owner_user_id: str) -> list[WorkspaceRecord]:
        return [ws for ws in self._store.values() if ws.owner_user_id == owner_user_id]

    def has_feature(self, workspace_id: str, flag: str) -> bool:
        ws = self._store.get(workspace_id)
        return bool(ws and ws.feature_flags.get(flag, False))

    def quota_for(self, workspace_id: str, resource: str) -> int | None:
        ws = self._store.get(workspace_id)
        if ws is None:
            return None
        return ws.quotas.get(resource)

    def count(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        return f"WorkspaceRegistry(count={self.count()})"
