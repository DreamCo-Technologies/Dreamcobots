"""
DreamCo Platform — Unified Bot/Capability Metadata Registry
============================================================

Single JSON/Python source of truth per bot or capability.  Every entry
records what the component *is*, what it *can do*, what events it emits and
consumes, how much it costs, and whether it participates in adaptive
learning.

This registry is the backbone of the marketplace, orchestration layer,
deployment pipeline, and monitoring systems.

Usage
-----
::

    from dreamco_platform.registry import BotRegistry, BotRegistryEntry, HealthStatus

    registry = BotRegistry()
    registry.register(BotRegistryEntry(
        bot_id="lead_gen_bot",
        display_name="Lead Generation Bot",
        capabilities=["lead.scrape", "lead.enrich", "lead.score"],
        events_emitted=["bot.started", "bot.completed", "capability.invoked"],
        events_consumed=["workflow.started"],
        pricing_tier="pro",
        runtime_requirements={"python": ">=3.9"},
        dependencies=["framework.GlobalAISourcesFlow"],
        learning_enabled=True,
    ))
    entry = registry.get("lead_gen_bot")
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Health status
# ---------------------------------------------------------------------------

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Registry entry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BotRegistryEntry:
    """
    Unified metadata record for a single DreamCo bot or capability bundle.

    Attributes
    ----------
    bot_id : str
        Canonical unique identifier (snake_case, e.g. ``lead_gen_bot``).
    display_name : str
        Human-readable name for marketplace / UI display.
    capabilities : list[str]
        List of capability identifiers this bot exposes
        (e.g. ``["lead.scrape", "lead.enrich"]``).
    events_emitted : list[str]
        Event types this bot publishes (e.g. ``["bot.started", "bot.completed"]``).
    events_consumed : list[str]
        Event types this bot subscribes to.
    pricing_tier : str
        Billing tier: ``"free"`` | ``"starter"`` | ``"pro"`` | ``"enterprise"``.
    runtime_requirements : dict
        Runtime constraints (e.g. ``{"python": ">=3.9", "memory_mb": 512}``).
    dependencies : list[str]
        List of platform or framework dependencies
        (e.g. ``["framework.GlobalAISourcesFlow"]``).
    health : HealthStatus
        Current health state. Defaults to ``HealthStatus.UNKNOWN``.
    learning_enabled : bool
        Whether this bot participates in adaptive learning cycles.
    description : str
        Short human-readable description.
    version : str
        Semantic version of this bot.
    category : str
        Broad category (e.g. ``"lead_gen"``, ``"finance"``, ``"real_estate"``).
    tags : list[str]
        Arbitrary searchable tags.
    lifecycle_state : str
        Current lifecycle phase (e.g. ``"draft"``, ``"idle"``, ``"active"``).
    swarm_role : str
        Coordination role inside the swarm (e.g. ``"specialist"``, ``"observer"``).
    memory_nodes : list[str]
        Persistent memory fabrics or nodes the bot reads/writes.
    revenue_attribution : dict
        Revenue / ROI metadata used by economic monitoring surfaces.
    permissions : list[str]
        Runtime permissions exposed for governance and audit layers.
    trust_score : float
        Normalised trust / reliability score in the range ``0.0`` – ``1.0``.
    specialization : str
        Primary specialisation or working identity for the bot.
    identity : dict
        Persistent identity metadata such as cohort, lineage, or progression.
    metadata : dict
        Catch-all for extra structured metadata.
    """

    bot_id: str
    display_name: str
    capabilities: List[str] = field(default_factory=list)
    events_emitted: List[str] = field(default_factory=list)
    events_consumed: List[str] = field(default_factory=list)
    pricing_tier: str = "free"
    runtime_requirements: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    health: HealthStatus = HealthStatus.UNKNOWN
    learning_enabled: bool = False
    description: str = ""
    version: str = "1.0.0"
    category: str = ""
    tags: List[str] = field(default_factory=list)
    lifecycle_state: str = "draft"
    swarm_role: str = "specialist"
    memory_nodes: List[str] = field(default_factory=list)
    revenue_attribution: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    trust_score: float = 0.5
    specialization: str = ""
    identity: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        if not re.match(r"^[a-z][a-z0-9_]*$", self.bot_id):
            raise ValueError(
                f"Invalid bot_id {self.bot_id!r}: must start with a lowercase letter "
                "and contain only lowercase letters, digits, and underscores."
            )
        object.__setattr__(self, "trust_score", max(0.0, min(1.0, float(self.trust_score))))

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dict."""
        return {
            "schema": "bot_registry_entry.v1",
            "bot_id": self.bot_id,
            "display_name": self.display_name,
            "capabilities": list(self.capabilities),
            "events_emitted": list(self.events_emitted),
            "events_consumed": list(self.events_consumed),
            "pricing_tier": self.pricing_tier,
            "runtime_requirements": dict(self.runtime_requirements),
            "dependencies": list(self.dependencies),
            "health": self.health.value,
            "learning_enabled": self.learning_enabled,
            "description": self.description,
            "version": self.version,
            "category": self.category,
            "tags": list(self.tags),
            "lifecycle_state": self.lifecycle_state,
            "swarm_role": self.swarm_role,
            "memory_nodes": list(self.memory_nodes),
            "revenue_attribution": dict(self.revenue_attribution),
            "permissions": list(self.permissions),
            "trust_score": self.trust_score,
            "specialization": self.specialization,
            "identity": dict(self.identity),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BotRegistryEntry":
        """Reconstruct a ``BotRegistryEntry`` from a serialised dict."""
        health_raw = data.get("health", HealthStatus.UNKNOWN.value)
        try:
            health = HealthStatus(health_raw)
        except ValueError:
            health = HealthStatus.UNKNOWN
        return cls(
            bot_id=data["bot_id"],
            display_name=data.get("display_name", data["bot_id"]),
            capabilities=data.get("capabilities", []),
            events_emitted=data.get("events_emitted", []),
            events_consumed=data.get("events_consumed", []),
            pricing_tier=data.get("pricing_tier", "free"),
            runtime_requirements=data.get("runtime_requirements", {}),
            dependencies=data.get("dependencies", []),
            health=health,
            learning_enabled=data.get("learning_enabled", False),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            category=data.get("category", ""),
            tags=data.get("tags", []),
            lifecycle_state=data.get("lifecycle_state", "draft"),
            swarm_role=data.get("swarm_role", "specialist"),
            memory_nodes=data.get("memory_nodes", []),
            revenue_attribution=data.get("revenue_attribution", {}),
            permissions=data.get("permissions", []),
            trust_score=data.get("trust_score", 0.5),
            specialization=data.get("specialization", ""),
            identity=data.get("identity", {}),
            metadata=data.get("metadata", {}),
        )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class BotRegistry:
    """
    In-memory registry of all DreamCo bots and capability bundles.

    Provides lookup by ID, capability, emitted event, consumed event,
    pricing tier, and health status.  The registry is intentionally kept
    in-memory; swap ``_store`` for a database-backed store in production.
    """

    def __init__(self) -> None:
        self._store: Dict[str, BotRegistryEntry] = {}

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def register(self, entry: BotRegistryEntry) -> None:
        """Add or replace a registry entry for *entry.bot_id*."""
        self._store[entry.bot_id] = entry

    def update_health(self, bot_id: str, status: HealthStatus) -> None:
        """Update the health status of the bot identified by *bot_id*."""
        entry = self._require(bot_id)
        self._store[bot_id] = replace(entry, health=status)

    def remove(self, bot_id: str) -> Optional[BotRegistryEntry]:
        """Remove and return the entry for *bot_id*, or ``None`` if absent."""
        return self._store.pop(bot_id, None)

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get(self, bot_id: str) -> Optional[BotRegistryEntry]:
        """Return the entry for *bot_id*, or ``None`` if not found."""
        return self._store.get(bot_id)

    def list_all(self) -> List[BotRegistryEntry]:
        """Return all registered entries sorted by ``bot_id``."""
        return sorted(self._store.values(), key=lambda e: e.bot_id)

    def find_by_capability(self, capability: str) -> List[BotRegistryEntry]:
        """Return every bot that exposes *capability*."""
        return [e for e in self._store.values() if capability in e.capabilities]

    def find_by_event_emitted(self, event_type: str) -> List[BotRegistryEntry]:
        """Return every bot that emits *event_type*."""
        return [e for e in self._store.values() if event_type in e.events_emitted]

    def find_by_event_consumed(self, event_type: str) -> List[BotRegistryEntry]:
        """Return every bot that consumes *event_type*."""
        return [e for e in self._store.values() if event_type in e.events_consumed]

    def find_by_tier(self, pricing_tier: str) -> List[BotRegistryEntry]:
        """Return every bot at *pricing_tier*."""
        return [e for e in self._store.values() if e.pricing_tier == pricing_tier]

    def find_by_health(self, status: HealthStatus) -> List[BotRegistryEntry]:
        """Return every bot with *status*."""
        return [e for e in self._store.values() if e.health == status]

    def find_learning_enabled(self) -> List[BotRegistryEntry]:
        """Return every bot with learning enabled."""
        return [e for e in self._store.values() if e.learning_enabled]

    def find_by_category(self, category: str) -> List[BotRegistryEntry]:
        """Return every bot in *category*."""
        return [e for e in self._store.values() if e.category == category]

    def find_by_coordination_mode(self, coordination_mode: str) -> List[BotRegistryEntry]:
        """Return every bot using the given coordination mode."""
        return [
            e for e in self._store.values()
            if e.metadata.get("coordination_mode", "centralized") == coordination_mode
        ]

    def find_swarm_enabled(self) -> List[BotRegistryEntry]:
        """Return every bot participating in swarm or MARL coordination."""
        return [e for e in self._store.values() if self._is_swarm_enabled(e)]

    def swarm_summary(self) -> Dict[str, Any]:
        """Summarise coordination modes and swarm participation across the registry."""
        coordination_modes: Dict[str, int] = {}
        marl_enabled = 0
        stigmergic = 0
        swarm_enabled = 0
        for entry in self._store.values():
            metadata = entry.metadata or {}
            coordination_mode = metadata.get("coordination_mode", "centralized")
            coordination_modes[coordination_mode] = coordination_modes.get(coordination_mode, 0) + 1
            if metadata.get("marl_enabled"):
                marl_enabled += 1
            if metadata.get("stigmergic_channels"):
                stigmergic += 1
            if self._is_swarm_enabled(entry):
                swarm_enabled += 1
        return {
            "total_bots": len(self._store),
            "swarm_enabled": swarm_enabled,
            "marl_enabled": marl_enabled,
            "stigmergic": stigmergic,
            "coordination_modes": coordination_modes,
        }

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the full registry to a plain dict."""
        return {bot_id: entry.to_dict() for bot_id, entry in self._store.items()}

    def lifecycle_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for entry in self._store.values():
            counts[entry.lifecycle_state] = counts.get(entry.lifecycle_state, 0) + 1
        return counts

    def swarm_role_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for entry in self._store.values():
            counts[entry.swarm_role] = counts.get(entry.swarm_role, 0) + 1
        return counts

    def average_trust_score(self) -> float:
        if not self._store:
            return 0.0
        total = sum(entry.trust_score for entry in self._store.values())
        return round(total / len(self._store), 4)

    def permission_index(self) -> List[str]:
        permissions = {
            permission
            for entry in self._store.values()
            for permission in entry.permissions
        }
        return sorted(permissions)

    def memory_node_index(self) -> List[str]:
        memory_nodes = {
            node
            for entry in self._store.values()
            for node in entry.memory_nodes
        }
        return sorted(memory_nodes)

    def revenue_summary(self) -> Dict[str, float]:
        estimated = 0.0
        realized = 0.0
        for entry in self._store.values():
            estimated += float(entry.revenue_attribution.get("estimated_monthly_usd", 0.0) or 0.0)
            realized += float(entry.revenue_attribution.get("realized_usd", 0.0) or 0.0)
        return {
            "estimated_monthly_usd": round(estimated, 2),
            "realized_usd": round(realized, 2),
        }

    def manifest_summary(self) -> Dict[str, Any]:
        return {
            "total_bots": self.count(),
            "lifecycle_states": self.lifecycle_counts(),
            "swarm_roles": self.swarm_role_counts(),
            "avg_trust_score": self.average_trust_score(),
            "permissions": self.permission_index(),
            "memory_nodes": self.memory_node_index(),
            "revenue": self.revenue_summary(),
        }

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def all_manifests(self) -> List[BotRegistryEntry]:
        """Alias for :meth:`list_all` — returns all registered entries."""
        return self.list_all()

    def count(self) -> int:
        """Return the number of registered bot entries."""
        return len(self._store)

    def __len__(self) -> int:
        return len(self._store)

    def __contains__(self, bot_id: str) -> bool:
        return bot_id in self._store

    def __repr__(self) -> str:
        return f"BotRegistry({len(self._store)} entries)"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require(self, bot_id: str) -> BotRegistryEntry:
        entry = self._store.get(bot_id)
        if entry is None:
            raise KeyError(f"No registry entry for bot_id={bot_id!r}")
        return entry

    @staticmethod
    def _is_swarm_enabled(entry: BotRegistryEntry) -> bool:
        metadata = entry.metadata or {}
        coordination_mode = metadata.get("coordination_mode", "centralized")
        return bool(
            metadata.get("swarm_enabled")
            or metadata.get("marl_enabled")
            or metadata.get("stigmergic_channels")
            or coordination_mode != "centralized"
        )
