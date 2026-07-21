"""
Auto-Scaling Task Execution for DreamOps.

Provides demand pattern recognition, auto-scale trigger management,
and resource provisioning automation.

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


class ScalingAction(Enum):
    SCALE_UP = "SCALE_UP"
    SCALE_DOWN = "SCALE_DOWN"
    MAINTAIN = "MAINTAIN"


@dataclass
class LoadMetrics:
    task_id: str
    current_load: float   # 0.0 - 1.0
    peak_load: float
    avg_load: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourceAllocation:
    task_id: str
    allocated_units: float
    scaling_factor: float
    action: ScalingAction
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ScalingEngine:
    """Manages auto-scaling of task resources based on demand patterns."""

    SCALE_UP_THRESHOLD = 0.75
    SCALE_DOWN_THRESHOLD = 0.30

    def __init__(self) -> None:
        self._allocations: Dict[str, ResourceAllocation] = {}
        self._history: Dict[str, List[LoadMetrics]] = {}
        self._scaling_events: List[dict] = []

    def analyze_demand(self, task_id: str, load_metrics: LoadMetrics) -> ScalingAction:
        """Analyze load metrics and determine appropriate scaling action."""
        if task_id not in self._history:
            self._history[task_id] = []
        self._history[task_id].append(load_metrics)
        trend = self._compute_trend(task_id)
        if load_metrics.current_load > self.SCALE_UP_THRESHOLD or trend > 0.1:
            return ScalingAction.SCALE_UP
        if load_metrics.current_load < self.SCALE_DOWN_THRESHOLD and trend < -0.05:
            return ScalingAction.SCALE_DOWN
        return ScalingAction.MAINTAIN

    def _compute_trend(self, task_id: str) -> float:
        history = self._history.get(task_id, [])
        if len(history) < 3:
            return 0.0
        recent = history[-3:]
        loads = [m.current_load for m in recent]
        return (loads[-1] - loads[0]) / max(len(loads) - 1, 1)

    def trigger_scale_up(self, task_id: str, factor: float = 1.5) -> ResourceAllocation:
        """Scale up resources for a task by the given factor."""
        current = self._allocations.get(task_id)
        units = (current.allocated_units * factor) if current else factor
        allocation = ResourceAllocation(
            task_id=task_id,
            allocated_units=round(units, 2),
            scaling_factor=factor,
            action=ScalingAction.SCALE_UP,
        )
        self._allocations[task_id] = allocation
        self._record_event(task_id, ScalingAction.SCALE_UP, factor)
        return allocation

    def trigger_scale_down(self, task_id: str, factor: float = 0.7) -> ResourceAllocation:
        """Scale down resources for a task."""
        current = self._allocations.get(task_id)
        units = (current.allocated_units * factor) if current else factor
        allocation = ResourceAllocation(
            task_id=task_id,
            allocated_units=round(max(units, 0.1), 2),
            scaling_factor=factor,
            action=ScalingAction.SCALE_DOWN,
        )
        self._allocations[task_id] = allocation
        self._record_event(task_id, ScalingAction.SCALE_DOWN, factor)
        return allocation

    def get_resource_allocation(self, task_id: str) -> Optional[ResourceAllocation]:
        """Return current resource allocation for a task."""
        return self._allocations.get(task_id)

    def optimize_costs(self) -> dict:
        """Review all allocations and suggest cost optimizations."""
        over_provisioned = []
        for task_id, alloc in self._allocations.items():
            history = self._history.get(task_id, [])
            if history and history[-1].avg_load < self.SCALE_DOWN_THRESHOLD:
                over_provisioned.append(task_id)
        savings_estimate = len(over_provisioned) * 50.0
        return {
            "over_provisioned_tasks": over_provisioned,
            "recommended_action": "scale_down",
            "estimated_monthly_savings_usd": savings_estimate,
        }

    def _record_event(self, task_id: str, action: ScalingAction, factor: float) -> None:
        self._scaling_events.append({
            "event_id": str(uuid.uuid4()),
            "task_id": task_id,
            "action": action.value,
            "factor": factor,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_scaling_history(self) -> List[dict]:
        """Return all recorded scaling events."""
        return list(self._scaling_events)
