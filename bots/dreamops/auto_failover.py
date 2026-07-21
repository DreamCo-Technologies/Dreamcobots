"""
Auto-Failover Operations for DreamOps.

Provides failover trigger configuration, health check orchestration,
and state transfer automation.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from framework import GlobalAISourcesFlow  # noqa: F401

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class FailoverConfig:
    primary_id: str
    backup_id: str
    health_check_interval: int   # seconds
    auto_restore: bool = True


@dataclass
class FailoverEvent:
    event_id: str
    system_id: str
    trigger_reason: str
    timestamp: datetime
    restored: bool = False


class AutoFailover:
    """Manages automatic failover between primary and backup systems."""

    def __init__(self) -> None:
        self._configs: Dict[str, FailoverConfig] = {}
        self._health: Dict[str, float] = {}     # system_id -> health 0-100
        self._active: Dict[str, str] = {}       # primary_id -> currently active id
        self._events: List[FailoverEvent] = []

    def configure_failover(self, primary_id: str, backup_id: str, config: dict) -> FailoverConfig:
        """Configure failover pairing between primary and backup."""
        fc = FailoverConfig(
            primary_id=primary_id,
            backup_id=backup_id,
            health_check_interval=config.get("health_check_interval", 30),
            auto_restore=config.get("auto_restore", True),
        )
        self._configs[primary_id] = fc
        self._health[primary_id] = 100.0
        self._health[backup_id] = 100.0
        self._active[primary_id] = primary_id
        return fc

    def check_health(self, system_id: str) -> dict:
        """Perform a health check on a system."""
        health = self._health.get(system_id, 0.0)
        config = self._configs.get(system_id)
        status = "healthy" if health >= 70 else ("degraded" if health >= 40 else "down")
        result = {
            "system_id": system_id,
            "health_score": health,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if config and health < 40 and self._active.get(system_id) == system_id:
            result["recommendation"] = "trigger_failover"
        return result

    def trigger_failover(self, system_id: str, reason: str = "health_threshold_breached") -> FailoverEvent:
        """Trigger failover from primary to backup."""
        config = self._configs.get(system_id)
        if not config:
            raise KeyError(f"No failover config for system {system_id}.")
        self._active[system_id] = config.backup_id
        event = FailoverEvent(
            event_id=str(uuid.uuid4()),
            system_id=system_id,
            trigger_reason=reason,
            timestamp=datetime.utcnow(),
        )
        self._events.append(event)
        return event

    def restore_primary(self, system_id: str) -> dict:
        """Restore traffic to the primary system."""
        config = self._configs.get(system_id)
        if not config:
            return {"error": f"No config for {system_id}."}
        self._health[system_id] = 95.0
        self._active[system_id] = system_id
        for event in self._events:
            if event.system_id == system_id and not event.restored:
                event.restored = True
        return {"system_id": system_id, "status": "primary_restored", "health": 95.0}

    def set_health(self, system_id: str, health: float) -> None:
        """Update simulated health score for a system."""
        self._health[system_id] = max(0.0, min(100.0, health))

    def get_failover_status(self) -> dict:
        """Return current failover status across all configured pairs."""
        pairs = []
        for primary_id, config in self._configs.items():
            pairs.append({
                "primary_id": primary_id,
                "backup_id": config.backup_id,
                "currently_active": self._active.get(primary_id, primary_id),
                "primary_health": self._health.get(primary_id, 0.0),
                "backup_health": self._health.get(config.backup_id, 0.0),
                "failover_events": sum(1 for e in self._events if e.system_id == primary_id),
            })
        return {"failover_pairs": pairs, "total_events": len(self._events)}
