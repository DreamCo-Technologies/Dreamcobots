"""
DreamCo Platform — Unified Registry Store
==========================================

``RegistryStore`` is the single access point for all sub-registries in the
platform.  It wires together:

* ``BotRegistry``        — bot manifests
* ``CapabilityRegistry`` — capability entries
* ``WorkspaceRegistry``  — workspace records

Having a unified store means that orchestration, marketplace, and monitoring
code can obtain all registry data from one import rather than importing each
sub-registry individually.

Usage::

    store = RegistryStore()
    store.bots.register(bot_manifest)
    store.capabilities.register(cap_entry)
    store.workspaces.create(workspace_record)

    # Snapshot for serialisation / export
    snapshot = store.snapshot()
"""

from __future__ import annotations

from typing import Any

from dreamco_platform.registry.bot_registry import BotRegistry
from dreamco_platform.registry.capability_registry import CapabilityRegistry
from dreamco_platform.registry.workspace_registry import WorkspaceRegistry


class RegistryStore:
    """Unified access point for all platform registries."""

    def __init__(self) -> None:
        self.bots = BotRegistry()
        self.capabilities = CapabilityRegistry()
        self.workspaces = WorkspaceRegistry()

    # ------------------------------------------------------------------
    # Cross-registry queries
    # ------------------------------------------------------------------

    def capabilities_for_bot(self, bot_id: str) -> list[str]:
        """Return capability_ids owned by *bot_id* (from capability registry)."""
        return [c.capability_id for c in self.capabilities.by_owner(bot_id)]

    def workspace_bots(self, workspace_id: str) -> list[str]:
        """Return bot_ids whose workspace matches *workspace_id*.

        This is a metadata lookup — full membership lives in RBACRegistry.
        Bots store workspace affinity in their manifest metadata field.
        """
        results = []
        for manifest in self.bots.all_manifests():
            if manifest.metadata.get("workspace_id") == workspace_id:
                results.append(manifest.bot_id)
        return results

    def snapshot(self) -> dict[str, Any]:
        """Return a serialisable snapshot of all sub-registries."""
        return {
            "bots": [m.to_dict() for m in self.bots.all_manifests()],
            "capabilities": [c.to_dict() for c in self.capabilities.all_entries()],
            "workspaces": [w.to_dict() for w in self.workspaces.all_active()],
        }

    def stats(self) -> dict[str, int]:
        return {
            "bots": self.bots.count(),
            "capabilities": self.capabilities.count(),
            "workspaces": self.workspaces.count(),
        }

    def __repr__(self) -> str:
        s = self.stats()
        return (
            f"RegistryStore("
            f"bots={s['bots']}, "
            f"capabilities={s['capabilities']}, "
            f"workspaces={s['workspaces']})"
        )
