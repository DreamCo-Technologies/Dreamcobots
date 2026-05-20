"""Canonical ontology object contracts and in-memory object registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List


CORE_OBJECT_TYPES = {
    "Bot",
    "Division",
    "Workflow",
    "Agent",
    "User",
    "Lead",
    "Deal",
    "RevenueStream",
    "Integration",
    "MemoryNode",
    "PermissionPolicy",
}

DEFAULT_VERSION = "1.0"


def canonical_id(object_type: str, name: str) -> str:
    """Generate a canonical ontology object ID."""
    return f"{object_type.lower()}.{name.strip().lower().replace(' ', '_')}"


@dataclass(frozen=True)
class OntologyObjectContract:
    """Canonical ontology object contract."""

    id: str
    type: str
    version: str = DEFAULT_VERSION
    name: str = ""
    division: str = ""
    state: str = "active"
    capabilities: List[str] = field(default_factory=list)
    relationships: List[Dict[str, str]] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    deprecated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "version": self.version,
            "name": self.name,
            "division": self.division,
            "state": self.state,
            "capabilities": list(self.capabilities),
            "relationships": list(self.relationships),
            "aliases": list(self.aliases),
            "metadata": dict(self.metadata),
            "deprecated": self.deprecated,
        }


class ObjectRegistry:
    """In-memory object registry for ontology projection."""

    def __init__(self, allowed_types: Iterable[str] = CORE_OBJECT_TYPES):
        self._allowed_types = set(allowed_types)
        self._objects: Dict[str, OntologyObjectContract] = {}

    def register(self, contract: OntologyObjectContract) -> OntologyObjectContract:
        if contract.type not in self._allowed_types:
            raise ValueError(f"Unsupported object type: {contract.type}")
        self._objects[contract.id] = contract
        return contract

    def upsert(self, payload: Dict[str, Any]) -> OntologyObjectContract:
        object_type = payload["type"]
        object_id = payload.get("id") or canonical_id(object_type, payload["name"])
        existing = self._objects.get(object_id)
        aliases = list(payload.get("aliases", []))
        if existing and existing.id != object_id:
            aliases = sorted(set(aliases + [existing.id]))
        contract = OntologyObjectContract(
            id=object_id,
            type=object_type,
            version=payload.get("version", DEFAULT_VERSION),
            name=payload.get("name", ""),
            division=payload.get("division", ""),
            state=payload.get("state", "active"),
            capabilities=list(payload.get("capabilities", [])),
            relationships=list(payload.get("relationships", [])),
            aliases=aliases,
            metadata=dict(payload.get("metadata", {})),
            deprecated=bool(payload.get("deprecated", False)),
        )
        return self.register(contract)

    def add_alias(self, object_id: str, alias: str) -> OntologyObjectContract:
        current = self.require(object_id)
        aliases = sorted(set(current.aliases + [alias]))
        updated = OntologyObjectContract(**{**current.to_dict(), "aliases": aliases})
        return self.register(updated)

    def transition_state(self, object_id: str, new_state: str) -> OntologyObjectContract:
        current = self.require(object_id)
        updated = OntologyObjectContract(**{**current.to_dict(), "state": new_state})
        return self.register(updated)

    def deprecate(self, object_id: str) -> OntologyObjectContract:
        current = self.require(object_id)
        updated = OntologyObjectContract(**{**current.to_dict(), "deprecated": True, "state": "deprecated"})
        return self.register(updated)

    def require(self, object_id: str) -> OntologyObjectContract:
        if object_id not in self._objects:
            raise KeyError(f"Object not found: {object_id}")
        return self._objects[object_id]

    def get(self, object_id: str) -> OntologyObjectContract | None:
        return self._objects.get(object_id)

    def list(self) -> List[OntologyObjectContract]:
        return list(self._objects.values())

    def clear(self) -> None:
        self._objects.clear()
