"""
Workflow Anomaly Alert System for DreamOps.

Provides statistical anomaly detection using z-score analysis,
pattern deviation scoring, and alert severity classification.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from framework import GlobalAISourcesFlow  # noqa: F401

import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class AlertSeverity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class WorkflowMetrics:
    workflow_id: str
    execution_time: float  # seconds
    error_rate: float       # 0.0 - 1.0
    throughput: float       # tasks/sec
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AnomalyAlert:
    alert_id: str
    workflow_id: str
    severity: AlertSeverity
    score: float
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AnomalyDetector:
    """Detects workflow anomalies using statistical z-score analysis."""

    def __init__(self) -> None:
        self._history: Dict[str, List[WorkflowMetrics]] = {}
        self._alerts: List[AnomalyAlert] = []
        self._window_size: int = 20

    def analyze_workflow(self, workflow_id: str, metrics: WorkflowMetrics) -> Optional[AnomalyAlert]:
        """Analyze workflow metrics and return an alert if anomaly is detected."""
        if workflow_id not in self._history:
            self._history[workflow_id] = []
        history = self._history[workflow_id]
        history.append(metrics)
        if len(history) > self._window_size:
            history.pop(0)
        if len(history) < 5:
            return AnomalyAlert(
                alert_id=str(uuid.uuid4()),
                workflow_id=workflow_id,
                severity=AlertSeverity.LOW,
                score=0.0,
                description=f"Insufficient history for workflow '{workflow_id}' — collecting baseline data",
            )
        score = self._compute_deviation_score(history, metrics)
        if score < 1.5:
            return None
        severity = self.score_severity(score)
        alert = AnomalyAlert(
            alert_id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            severity=severity,
            score=round(score, 4),
            description=self._build_description(workflow_id, score, severity),
        )
        self._alerts.append(alert)
        return alert

    def _compute_deviation_score(self, history: List[WorkflowMetrics], current: WorkflowMetrics) -> float:
        """Compute composite z-score deviation across key metrics."""
        scores = []
        for attr in ("execution_time", "error_rate", "throughput"):
            values = [getattr(m, attr) for m in history[:-1]]
            if len(values) < 2:
                continue
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std = math.sqrt(variance) if variance > 0 else 1e-9
            z = abs(getattr(current, attr) - mean) / std
            scores.append(z)
        return max(scores) if scores else 0.0

    def score_severity(self, deviation: float) -> AlertSeverity:
        """Classify alert severity from deviation score."""
        if deviation >= 4.0:
            return AlertSeverity.CRITICAL
        if deviation >= 3.0:
            return AlertSeverity.HIGH
        if deviation >= 2.0:
            return AlertSeverity.MEDIUM
        return AlertSeverity.LOW

    def _build_description(self, workflow_id: str, score: float, severity: AlertSeverity) -> str:
        return (
            f"Anomaly detected in workflow '{workflow_id}': "
            f"deviation score {score:.2f} ({severity.value})"
        )

    def get_alerts(self) -> List[AnomalyAlert]:
        """Return all current alerts."""
        return list(self._alerts)

    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[AnomalyAlert]:
        """Return alerts filtered by severity."""
        return [a for a in self._alerts if a.severity == severity]

    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self._alerts.clear()

    def summary(self) -> dict:
        """Return a summary dict of alert counts by severity."""
        counts = {s.value: 0 for s in AlertSeverity}
        for a in self._alerts:
            counts[a.severity.value] += 1
        return {"total": len(self._alerts), "by_severity": counts}
