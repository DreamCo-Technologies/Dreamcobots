"""
DreamCo Platform — Capability Registry
=======================================

Tracks every ``CapabilityNode`` that has been registered with the platform.
Acts as the authoritative index for orchestration, marketplace, and billing.

A capability entry records:
* ``capability_id`` and ``version``
* ``owner_bot_id`` — the bot that owns/provides this capability
* ``tags`` — searchable labels
* ``cost_profile`` — per-call and per-token pricing
* ``event_contracts`` — list of event types the capability emits
* ``enabled`` — soft-disable without deletion
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Capability entry
# ---------------------------------------------------------------------------

@dataclass
class CapabilityEntry:
    capability_id: str
    version: str
    owner_bot_id: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    cost_profile: dict[str, Any] = field(default_factory=dict)
    event_contracts: list[str] = field(default_factory=list)
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    permissions_required: list[str] = field(default_factory=list)
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "version": self.version,
            "owner_bot_id": self.owner_bot_id,
            "description": self.description,
            "tags": self.tags,
            "cost_profile": self.cost_profile,
            "event_contracts": self.event_contracts,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "permissions_required": self.permissions_required,
            "enabled": self.enabled,
        }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class CapabilityRegistry:
    """In-memory registry for capability entries.

    Keyed by ``capability_id``.  Multiple versions of the same capability
    are tracked; ``get()`` returns the latest-registered version by default.
    """

    def __init__(self) -> None:
        # capability_id → list of CapabilityEntry (ordered by registration time)
        self._store: dict[str, list[CapabilityEntry]] = {}

    # ------------------------------------------------------------------
    # Mutating operations
    # ------------------------------------------------------------------

    def register(self, entry: CapabilityEntry) -> None:
        """Register *entry*.  Multiple versions may be registered for the same id."""
        if entry.capability_id not in self._store:
            self._store[entry.capability_id] = []
        self._store[entry.capability_id].append(entry)

    def enable(self, capability_id: str) -> bool:
        """Enable all versions of *capability_id*.  Returns False if not found."""
        entries = self._store.get(capability_id)
        if not entries:
            return False
        for e in entries:
            e.enabled = True
        return True

    def disable(self, capability_id: str) -> bool:
        """Soft-disable all versions of *capability_id*.  Returns False if not found."""
        entries = self._store.get(capability_id)
        if not entries:
            return False
        for e in entries:
            e.enabled = False
        return True

    def remove(self, capability_id: str) -> bool:
        """Permanently remove *capability_id* from the registry."""
        if capability_id not in self._store:
            return False
        del self._store[capability_id]
        return True

    # ------------------------------------------------------------------
    # Query operations
    # ------------------------------------------------------------------

    def get(self, capability_id: str) -> CapabilityEntry | None:
        """Return the latest-registered version of *capability_id*, or None."""
        entries = self._store.get(capability_id)
        return entries[-1] if entries else None

    def get_version(self, capability_id: str, version: str) -> CapabilityEntry | None:
        """Return a specific version of *capability_id*, or None."""
        for entry in self._store.get(capability_id, []):
            if entry.version == version:
                return entry
        return None

    def all_entries(self, enabled_only: bool = False) -> list[CapabilityEntry]:
        """Return all latest-version entries, optionally filtered to enabled ones."""
        results = []
        for entries in self._store.values():
            latest = entries[-1]
            if enabled_only and not latest.enabled:
                continue
            results.append(latest)
        return results

    def by_owner(self, owner_bot_id: str) -> list[CapabilityEntry]:
        """Return all capabilities owned by *owner_bot_id*."""
        return [
            entries[-1]
            for entries in self._store.values()
            if entries and entries[-1].owner_bot_id == owner_bot_id
        ]

    def by_tag(self, tag: str) -> list[CapabilityEntry]:
        """Return all capabilities that carry the given *tag*."""
        return [
            entries[-1]
            for entries in self._store.values()
            if entries and tag in entries[-1].tags
        ]

    def count(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        return f"CapabilityRegistry(count={self.count()})"
