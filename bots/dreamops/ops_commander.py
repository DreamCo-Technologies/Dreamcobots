"""
Operations Commander Agent for DreamOps.

Manages infrastructure, coordinates incident response,
and oversees performance monitoring.

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
from enum import Enum
from typing import Dict, List, Optional


class SystemStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"
    MAINTENANCE = "MAINTENANCE"


@dataclass
class System:
    system_id: str
    name: str
    health_score: float       # 0.0 - 100.0
    last_checked: datetime
    status: SystemStatus
    config: dict = field(default_factory=dict)


@dataclass
class Incident:
    incident_id: str
    system_id: str
    severity: str
    description: str
    timestamp: datetime
    resolved: bool = False
    resolution_notes: str = ""


class OpsCommander:
    """Orchestrates infrastructure management and incident response."""

    def __init__(self) -> None:
        self._systems: Dict[str, System] = {}
        self._incidents: Dict[str, Incident] = {}
        self._performance_log: List[dict] = []

    def register_system(self, system_id: str, config: dict) -> System:
        """Register a new system for monitoring."""
        system = System(
            system_id=system_id,
            name=config.get("name", system_id),
            health_score=100.0,
            last_checked=datetime.utcnow(),
            status=SystemStatus.HEALTHY,
            config=config,
        )
        self._systems[system_id] = system
        return system

    def monitor_systems(self) -> List[System]:
        """Run a monitoring pass across all registered systems and update health scores."""
        for system in self._systems.values():
            system.last_checked = datetime.utcnow()
            # Simulate health check: health decays slightly unless config says stable
            decay = 0.5 if system.config.get("stable", True) else 2.0
            system.health_score = max(0.0, system.health_score - decay)
            if system.health_score >= 80:
                system.status = SystemStatus.HEALTHY
            elif system.health_score >= 50:
                system.status = SystemStatus.DEGRADED
            else:
                system.status = SystemStatus.DOWN
        return list(self._systems.values())

    def respond_to_incident(self, incident_id: str, response_plan: dict) -> Incident:
        """Execute a response plan for an existing incident."""
        if incident_id not in self._incidents:
            raise KeyError(f"Incident {incident_id} not found.")
        incident = self._incidents[incident_id]
        if response_plan.get("resolve", False):
            incident.resolved = True
            incident.resolution_notes = response_plan.get("notes", "Resolved by OpsCommander.")
            system = self._systems.get(incident.system_id)
            if system:
                system.health_score = min(100.0, system.health_score + 30.0)
                system.status = SystemStatus.HEALTHY
        return incident

    def create_incident(self, system_id: str, severity: str, description: str) -> Incident:
        """Record a new incident."""
        incident = Incident(
            incident_id=str(uuid.uuid4()),
            system_id=system_id,
            severity=severity,
            description=description,
            timestamp=datetime.utcnow(),
        )
        self._incidents[incident.incident_id] = incident
        return incident

    def optimize_performance(self, system_id: str) -> dict:
        """Run performance optimization suggestions for a system."""
        system = self._systems.get(system_id)
        if not system:
            return {"error": f"System {system_id} not registered."}
        suggestions = []
        if system.health_score < 70:
            suggestions.append("Restart degraded service workers.")
        if system.config.get("cache_enabled", False) is False:
            suggestions.append("Enable caching to reduce latency.")
        suggestions.append("Review resource allocation quarterly.")
        log_entry = {
            "system_id": system_id,
            "timestamp": datetime.utcnow().isoformat(),
            "suggestions": suggestions,
        }
        self._performance_log.append(log_entry)
        return log_entry

    def get_status_report(self) -> dict:
        """Return a status report across all systems and incidents."""
        total = len(self._systems)
        healthy = sum(1 for s in self._systems.values() if s.status == SystemStatus.HEALTHY)
        open_incidents = sum(1 for i in self._incidents.values() if not i.resolved)
        return {
            "total_systems": total,
            "healthy": healthy,
            "degraded": total - healthy,
            "open_incidents": open_incidents,
            "systems": [
                {
                    "system_id": s.system_id,
                    "name": s.name,
                    "health_score": s.health_score,
                    "status": s.status.value,
                }
                for s in self._systems.values()
            ],
        }
