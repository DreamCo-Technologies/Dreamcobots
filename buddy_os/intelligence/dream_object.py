"""Universal world-model object used by Buddy's intelligence layers."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional


LIFECYCLE = ("discovered", "observed", "planned", "simulated", "verified", "authorized", "executing", "completed", "measured", "learned")


@dataclass
class DreamObject:
    object_id: str
    object_type: str
    name: str = ""
    state: str = "discovered"
    capabilities: List[str] = field(default_factory=list)
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    properties: Dict[str, object] = field(default_factory=dict)
    provenance: List[str] = field(default_factory=list)
    confidence: float = 0.0
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def transition(self, new_state: str) -> None:
        if new_state not in LIFECYCLE:
            raise ValueError(f"unsupported lifecycle state: {new_state}")
        self.state = new_state
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def relate(self, relation: str, target_id: str) -> None:
        targets = self.relationships.setdefault(relation, [])
        if target_id not in targets:
            targets.append(target_id)

    def export(self) -> dict:
        return asdict(self)
