"""
Operational Resilience Scorer for DreamOps.

Calculates resilience metrics, analyzes failure modes,
and scores recovery capabilities.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from framework import GlobalAISourcesFlow  # noqa: F401

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class ResilienceMetrics:
    system_id: str
    uptime_pct: float       # 0.0 - 100.0
    mttr_hours: float       # Mean time to recover
    mtbf_hours: float       # Mean time between failures
    redundancy_score: float  # 0.0 - 10.0


@dataclass
class ResilienceReport:
    system_id: str
    overall_score: float
    breakdown: Dict[str, float]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)


class ResilienceScorer:
    """Scores and reports on operational resilience of systems."""

    def __init__(self) -> None:
        self._metrics: Dict[str, ResilienceMetrics] = {}
        self._reports: Dict[str, ResilienceReport] = {}

    def score_system(self, system_id: str, metrics: ResilienceMetrics) -> float:
        """Compute overall resilience score for a system."""
        self._metrics[system_id] = metrics
        score = self._compute_score(metrics)
        return round(score, 2)

    def _compute_score(self, metrics: ResilienceMetrics) -> float:
        uptime_score = metrics.uptime_pct / 10.0          # max 10
        # MTTR: lower is better; 1 hour MTTR = 10, 24 hours = ~4
        mttr_score = max(0.0, 10.0 - metrics.mttr_hours * 0.4)
        # MTBF: higher is better; 720 hours (30 days) = 10
        mtbf_score = min(10.0, metrics.mtbf_hours / 72.0)
        redundancy_score = metrics.redundancy_score
        # Weighted average
        return (uptime_score * 0.35 + mttr_score * 0.25 + mtbf_score * 0.20 + redundancy_score * 0.20)

    def analyze_failure_modes(self, system_id: str) -> List[dict]:
        """Analyze potential failure modes for a system."""
        metrics = self._metrics.get(system_id)
        if not metrics:
            return []
        modes = []
        if metrics.uptime_pct < 99.9:
            modes.append({"mode": "availability_gap", "risk": "high", "uptime_pct": metrics.uptime_pct})
        if metrics.mttr_hours > 4:
            modes.append({"mode": "slow_recovery", "risk": "medium", "mttr_hours": metrics.mttr_hours})
        if metrics.redundancy_score < 5.0:
            modes.append({"mode": "insufficient_redundancy", "risk": "high", "score": metrics.redundancy_score})
        if metrics.mtbf_hours < 168:  # 168 hours = 1 week
            modes.append({"mode": "frequent_failures", "risk": "high", "mtbf_hours": metrics.mtbf_hours})
        return modes

    def calculate_recovery_score(self, system_id: str) -> dict:
        """Calculate recovery capability score."""
        metrics = self._metrics.get(system_id)
        if not metrics:
            return {"error": f"No metrics for {system_id}."}
        mttr_score = max(0.0, 10.0 - metrics.mttr_hours * 0.4)
        mtbf_score = min(10.0, metrics.mtbf_hours / 72.0)
        recovery_score = (mttr_score * 0.5 + mtbf_score * 0.5)
        return {
            "system_id": system_id,
            "recovery_score": round(recovery_score, 2),
            "mttr_score": round(mttr_score, 2),
            "mtbf_score": round(mtbf_score, 2),
            "classification": "excellent" if recovery_score >= 8 else ("good" if recovery_score >= 6 else "needs_improvement"),
        }

    def generate_resilience_report(self, system_id: str) -> ResilienceReport:
        """Generate a comprehensive resilience report."""
        metrics = self._metrics.get(system_id)
        if not metrics:
            raise KeyError(f"No metrics recorded for system {system_id}.")
        overall_score = self._compute_score(metrics)
        breakdown = {
            "uptime": round(metrics.uptime_pct / 10.0, 2),
            "mttr": round(max(0.0, 10.0 - metrics.mttr_hours * 0.4), 2),
            "mtbf": round(min(10.0, metrics.mtbf_hours / 72.0), 2),
            "redundancy": metrics.redundancy_score,
        }
        recommendations = []
        if metrics.uptime_pct < 99.9:
            recommendations.append("Improve availability to 99.9%+ SLA.")
        if metrics.mttr_hours > 2:
            recommendations.append("Invest in automated incident response to reduce MTTR.")
        if metrics.redundancy_score < 7:
            recommendations.append("Increase redundancy with active-active failover.")
        if not recommendations:
            recommendations.append("System meets resilience targets — maintain current posture.")
        report = ResilienceReport(
            system_id=system_id,
            overall_score=round(overall_score, 2),
            breakdown=breakdown,
            recommendations=recommendations,
        )
        self._reports[system_id] = report
        return report

    def compare_systems(self, system_ids: List[str]) -> List[dict]:
        """Compare resilience scores across multiple systems."""
        results = []
        for sid in system_ids:
            metrics = self._metrics.get(sid)
            if metrics:
                results.append({
                    "system_id": sid,
                    "overall_score": round(self._compute_score(metrics), 2),
                })
        return sorted(results, key=lambda x: x["overall_score"], reverse=True)
