"""
Workflow Bottleneck Detector for DreamOps.

Provides real-time flow monitoring, bottleneck heat mapping,
and queue depth analysis.

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
class WorkflowStage:
    stage_id: str
    name: str
    avg_duration: float     # seconds
    queue_depth: int
    throughput: float       # tasks/sec


@dataclass
class Bottleneck:
    bottleneck_id: str
    workflow_id: str
    stage_id: str
    severity_score: float   # 0.0 - 10.0
    remediation_suggestions: List[str]
    detected_at: datetime = field(default_factory=datetime.utcnow)


class BottleneckDetector:
    """Detects and maps bottlenecks in multi-stage workflows."""

    BOTTLENECK_THRESHOLD = 5.0

    def __init__(self) -> None:
        self._workflow_stages: Dict[str, List[WorkflowStage]] = {}
        self._bottlenecks: Dict[str, Bottleneck] = {}

    def analyze_workflow(self, workflow_id: str, stages: List[WorkflowStage]) -> List[Bottleneck]:
        """Analyze workflow stages and identify bottlenecks."""
        self._workflow_stages[workflow_id] = stages
        detected = []
        avg_throughput = (sum(s.throughput for s in stages) / len(stages)) if stages else 1.0
        for stage in stages:
            score = self._compute_severity(stage, avg_throughput)
            if score >= self.BOTTLENECK_THRESHOLD:
                bottleneck = Bottleneck(
                    bottleneck_id=str(uuid.uuid4()),
                    workflow_id=workflow_id,
                    stage_id=stage.stage_id,
                    severity_score=round(score, 2),
                    remediation_suggestions=self._suggest_remediation(stage),
                )
                self._bottlenecks[bottleneck.bottleneck_id] = bottleneck
                detected.append(bottleneck)
        return detected

    def _compute_severity(self, stage: WorkflowStage, avg_throughput: float) -> float:
        queue_score = min(stage.queue_depth / 10.0, 5.0)
        throughput_score = max(0.0, 5.0 * (1.0 - stage.throughput / max(avg_throughput, 1e-9)))
        return queue_score + throughput_score

    def _suggest_remediation(self, stage: WorkflowStage) -> List[str]:
        suggestions = []
        if stage.queue_depth > 20:
            suggestions.append(f"Scale up workers for stage '{stage.name}'.")
        if stage.throughput < 0.5:
            suggestions.append(f"Optimize processing logic in '{stage.name}'.")
        if stage.avg_duration > 60:
            suggestions.append(f"Introduce async processing for '{stage.name}'.")
        suggestions.append("Review stage resource allocation.")
        return suggestions

    def get_bottlenecks(self) -> List[Bottleneck]:
        """Return all detected bottlenecks."""
        return list(self._bottlenecks.values())

    def generate_heat_map(self, workflow_id: str) -> dict:
        """Generate a heat map of severity scores for each stage."""
        stages = self._workflow_stages.get(workflow_id, [])
        if not stages:
            return {"workflow_id": workflow_id, "heat_map": {}}
        avg_throughput = sum(s.throughput for s in stages) / len(stages)
        heat_map = {
            s.stage_id: {
                "name": s.name,
                "severity": round(self._compute_severity(s, avg_throughput), 2),
                "queue_depth": s.queue_depth,
            }
            for s in stages
        }
        return {"workflow_id": workflow_id, "heat_map": heat_map}

    def remediate(self, bottleneck_id: str) -> dict:
        """Apply remediation for a specific bottleneck (simulation)."""
        bottleneck = self._bottlenecks.get(bottleneck_id)
        if not bottleneck:
            return {"error": f"Bottleneck {bottleneck_id} not found."}
        bottleneck.severity_score = max(0.0, bottleneck.severity_score - 3.0)
        return {
            "bottleneck_id": bottleneck_id,
            "new_severity_score": bottleneck.severity_score,
            "status": "remediated",
        }

    def get_workflow_summary(self, workflow_id: str) -> dict:
        """Return a summary of bottleneck analysis for a workflow."""
        relevant = [b for b in self._bottlenecks.values() if b.workflow_id == workflow_id]
        return {
            "workflow_id": workflow_id,
            "total_bottlenecks": len(relevant),
            "max_severity": max((b.severity_score for b in relevant), default=0.0),
            "bottleneck_ids": [b.bottleneck_id for b in relevant],
        }
