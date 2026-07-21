"""
Enterprise Throughput Maximizer for DreamOps.

Optimizes end-to-end flow, identifies constraints,
and forecasts throughput capacity.

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
class FlowStage:
    stage_id: str
    capacity: float       # max tasks/hour
    current_load: float   # tasks/hour currently processed
    cycle_time: float     # seconds per task


@dataclass
class Constraint:
    constraint_id: str
    flow_id: str
    stage_id: str
    constraint_type: str   # "capacity", "cycle_time", "bottleneck"
    impact_score: float    # 0.0 - 10.0


class ThroughputMaximizer:
    """Maximizes end-to-end throughput by identifying and resolving constraints."""

    def __init__(self) -> None:
        self._flows: Dict[str, List[FlowStage]] = {}
        self._constraints: Dict[str, List[Constraint]] = {}
        self._optimization_log: List[dict] = []

    def analyze_flow(self, flow_id: str, stages: List[FlowStage]) -> dict:
        """Analyze flow stages and compute current throughput."""
        self._flows[flow_id] = stages
        if not stages:
            return {"flow_id": flow_id, "throughput": 0.0}
        # System throughput is limited by the minimum capacity stage
        min_capacity = min(s.capacity for s in stages)
        utilization = [s.current_load / max(s.capacity, 1e-9) for s in stages]
        avg_utilization = sum(utilization) / len(utilization)
        return {
            "flow_id": flow_id,
            "throughput_tasks_per_hour": min_capacity,
            "avg_utilization_pct": round(avg_utilization * 100, 2),
            "stages_analyzed": len(stages),
        }

    def identify_constraints(self, flow_id: str) -> List[Constraint]:
        """Identify constraining stages in the flow."""
        stages = self._flows.get(flow_id, [])
        if not stages:
            return []
        avg_capacity = sum(s.capacity for s in stages) / len(stages)
        constraints = []
        for stage in stages:
            c_type = None
            impact = 0.0
            if stage.capacity < avg_capacity * 0.6:
                c_type = "capacity"
                impact = round((1 - stage.capacity / avg_capacity) * 10, 2)
            elif stage.cycle_time > 120:  # 120 seconds = 2 minutes
                c_type = "cycle_time"
                impact = round(min(stage.cycle_time / 120.0, 10.0), 2)
            elif stage.current_load / max(stage.capacity, 1e-9) > 0.9:
                c_type = "bottleneck"
                impact = round((stage.current_load / stage.capacity) * 5, 2)
            if c_type:
                c = Constraint(
                    constraint_id=str(uuid.uuid4()),
                    flow_id=flow_id,
                    stage_id=stage.stage_id,
                    constraint_type=c_type,
                    impact_score=min(impact, 10.0),
                )
                constraints.append(c)
        self._constraints[flow_id] = constraints
        return constraints

    def optimize_flow(self, flow_id: str) -> dict:
        """Apply simulated optimizations to constrained stages."""
        constraints = self._constraints.get(flow_id, [])
        stages = self._flows.get(flow_id, [])
        if not stages:
            return {"error": f"Flow {flow_id} not analyzed yet."}
        improvements = []
        for stage in stages:
            for c in constraints:
                if c.stage_id == stage.stage_id and c.constraint_type == "capacity":
                    old_cap = stage.capacity
                    stage.capacity *= 1.3
                    improvements.append({
                        "stage_id": stage.stage_id,
                        "old_capacity": old_cap,
                        "new_capacity": stage.capacity,
                    })
        log_entry = {
            "flow_id": flow_id,
            "improvements": improvements,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._optimization_log.append(log_entry)
        return log_entry

    def forecast_throughput(self, flow_id: str, timeframe_days: int = 30) -> dict:
        """Forecast throughput capacity over the given timeframe."""
        stages = self._flows.get(flow_id, [])
        if not stages:
            return {"error": f"Flow {flow_id} not found."}
        current_throughput = min(s.capacity for s in stages)
        # Simple linear growth model
        growth_rate_per_day = 0.005
        forecast = {
            "flow_id": flow_id,
            "current_throughput_per_hour": current_throughput,
            "timeframe_days": timeframe_days,
            "forecasted_throughput_per_hour": round(
                current_throughput * (1 + growth_rate_per_day * timeframe_days), 2
            ),
            "projected_growth_pct": round(growth_rate_per_day * timeframe_days * 100, 2),
        }
        return forecast

    def get_optimization_report(self) -> dict:
        """Return a full report of all optimization actions taken."""
        return {
            "total_flows": len(self._flows),
            "total_constraints_identified": sum(len(v) for v in self._constraints.values()),
            "optimization_runs": len(self._optimization_log),
            "log": self._optimization_log,
        }
