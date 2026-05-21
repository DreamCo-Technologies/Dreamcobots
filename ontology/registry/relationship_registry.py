"""Canonical relationship types and in-memory relationship registry."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List


RELATIONSHIP_TYPES = {
    "BELONGS_TO",
    "EXECUTES",
    "DEPENDS_ON",
    "MANAGES",
    "REPORTS_TO",
    "USES",
    "STORES_IN",
    "GENERATED",
    "AUTHORIZED_BY",
}


@dataclass(frozen=True)
class OntologyRelationship:
    source: str
    type: str
    target: str
    timestamp: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "source": self.source,
            "type": self.type,
            "target": self.target,
            "timestamp": self.timestamp,
        }


class RelationshipRegistry:
    """In-memory relationship graph projection."""

    def __init__(self):
        self._relationships: List[OntologyRelationship] = []

    def register(self, source: str, relation_type: str, target: str) -> OntologyRelationship:
        if relation_type not in RELATIONSHIP_TYPES:
            raise ValueError(f"Unsupported relationship type: {relation_type}")
        if source == target:
            raise ValueError("Relationship source and target must differ")
        relationship = OntologyRelationship(
            source=source,
            type=relation_type,
            target=target,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._relationships.append(relationship)
        return relationship

    def list(self) -> List[OntologyRelationship]:
        return list(self._relationships)

    def list_for_source(self, source: str) -> List[OntologyRelationship]:
        return [r for r in self._relationships if r.source == source]

    def serialize(self) -> List[Dict[str, str]]:
        return [r.to_dict() for r in self._relationships]

    def clear(self) -> None:
        self._relationships.clear()
