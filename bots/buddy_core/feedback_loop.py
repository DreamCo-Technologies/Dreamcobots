"""
Feedback Loop for the Buddy Core System.

Tracks performance metrics and revenue, suggests optimisations, and runs
full feedback cycles — all in-memory with no external dependencies.

Part of the Buddy Core System — adheres to the GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class MetricType(Enum):
    REVENUE = "revenue"
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    ERROR_RATE = "error_rate"
    LEAD_QUALITY = "lead_quality"


@dataclass
class PerformanceMetric:
    """A single performance data-point for a bot."""

    metric_id: str
    bot_id: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    metadata: dict = field(default_factory=dict)


@dataclass
class Optimization:
    """A recorded optimisation applied to a bot."""

    optimization_id: str
    bot_id: str
    improvement_type: str
    before_value: float
    after_value: float
    applied_at: datetime = field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Performance Tracker
# ---------------------------------------------------------------------------

class PerformanceTracker:
    """Records and queries performance metrics."""

    def __init__(self) -> None:
        self._metrics: list[PerformanceMetric] = []

    def record(
        self,
        bot_id: str,
        metric_type: MetricType,
        value: float,
        metadata: Optional[dict] = None,
    ) -> PerformanceMetric:
        metric = PerformanceMetric(
            metric_id=str(uuid.uuid4()),
            bot_id=bot_id,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
        )
        self._metrics.append(metric)
        return metric

    def get_metrics(self, bot_id: str) -> list[PerformanceMetric]:
        return [m for m in self._metrics if m.bot_id == bot_id]

    def get_average(self, bot_id: str, metric_type: MetricType) -> float:
        values = [
            m.value
            for m in self._metrics
            if m.bot_id == bot_id and m.metric_type == metric_type
        ]
        return sum(values) / len(values) if values else 0.0

    def get_stats(self) -> dict:
        bots = {m.bot_id for m in self._metrics}
        return {
            "total_records": len(self._metrics),
            "unique_bots": len(bots),
            "metric_types": [mt.value for mt in MetricType],
        }


# ---------------------------------------------------------------------------
# Revenue Tracker
# ---------------------------------------------------------------------------

class RevenueTracker:
    """Tracks revenue events per bot and overall."""

    def __init__(self) -> None:
        self._records: list[dict] = []

    def record_revenue(self, bot_id: str, amount: float, source: str = "") -> dict:
        record = {
            "record_id": str(uuid.uuid4()),
            "bot_id": bot_id,
            "amount": amount,
            "source": source,
            "recorded_at": datetime.utcnow().isoformat(),
        }
        self._records.append(record)
        return record

    def get_revenue(self, bot_id: str) -> float:
        return sum(r["amount"] for r in self._records if r["bot_id"] == bot_id)

    def get_total_revenue(self) -> float:
        return sum(r["amount"] for r in self._records)

    def get_summary(self) -> dict:
        bots: dict[str, float] = {}
        for r in self._records:
            bots[r["bot_id"]] = bots.get(r["bot_id"], 0.0) + r["amount"]
        return {
            "total_revenue": self.get_total_revenue(),
            "total_records": len(self._records),
            "by_bot": bots,
        }


# ---------------------------------------------------------------------------
# Auto Optimizer
# ---------------------------------------------------------------------------

_IMPROVEMENT_THRESHOLDS: dict[MetricType, tuple[str, float]] = {
    MetricType.ERROR_RATE: ("reduce_error_rate", 0.1),
    MetricType.PERFORMANCE: ("boost_performance", 0.5),
    MetricType.ENGAGEMENT: ("increase_engagement", 0.4),
    MetricType.LEAD_QUALITY: ("improve_lead_quality", 0.6),
    MetricType.REVENUE: ("grow_revenue", 100.0),
}


class AutoOptimizer:
    """Analyses metrics and applies optimisations."""

    def __init__(self) -> None:
        self._optimizations: list[Optimization] = []

    def analyze(self, bot_id: str, tracker: PerformanceTracker) -> list[str]:
        """Return a list of suggested improvement types."""
        suggestions: list[str] = []
        for metric_type, (improvement, threshold) in _IMPROVEMENT_THRESHOLDS.items():
            avg = tracker.get_average(bot_id, metric_type)
            if metric_type == MetricType.ERROR_RATE and avg > threshold:
                suggestions.append(improvement)
            elif metric_type != MetricType.ERROR_RATE and avg < threshold:
                suggestions.append(improvement)
        return suggestions

    def apply_optimization(
        self,
        bot_id: str,
        improvement_type: str,
        tracker: PerformanceTracker,
    ) -> Optimization:
        """Record that an optimisation was applied (simulated improvement)."""
        # Find a relevant metric to show before/after
        relevant_type = MetricType.PERFORMANCE
        for mt, (it, _) in _IMPROVEMENT_THRESHOLDS.items():
            if it == improvement_type:
                relevant_type = mt
                break

        before = tracker.get_average(bot_id, relevant_type)
        after = before * 1.15 if before > 0 else 0.15  # simulate 15% improvement

        opt = Optimization(
            optimization_id=str(uuid.uuid4()),
            bot_id=bot_id,
            improvement_type=improvement_type,
            before_value=before,
            after_value=after,
        )
        self._optimizations.append(opt)
        return opt

    def get_optimizations(self, bot_id: str) -> list[Optimization]:
        return [o for o in self._optimizations if o.bot_id == bot_id]

    def get_stats(self) -> dict:
        return {
            "total_optimizations": len(self._optimizations),
            "unique_bots": len({o.bot_id for o in self._optimizations}),
        }


# ---------------------------------------------------------------------------
# FeedbackLoop (facade)
# ---------------------------------------------------------------------------

class FeedbackLoop:
    """Composes PerformanceTracker, RevenueTracker, and AutoOptimizer."""

    def __init__(self) -> None:
        self.tracker = PerformanceTracker()
        self.revenue = RevenueTracker()
        self.optimizer = AutoOptimizer()

    def run_cycle(self, bot_id: str) -> dict:
        """Run a full feedback cycle for *bot_id*."""
        suggestions = self.optimizer.analyze(bot_id, self.tracker)
        applied: list[Optimization] = []
        for suggestion in suggestions:
            opt = self.optimizer.apply_optimization(bot_id, suggestion, self.tracker)
            applied.append(opt)

        return {
            "bot_id": bot_id,
            "suggestions": suggestions,
            "optimizations_applied": len(applied),
            "metrics_summary": {
                mt.value: self.tracker.get_average(bot_id, mt)
                for mt in MetricType
            },
            "revenue": self.revenue.get_revenue(bot_id),
        }

    def get_summary(self) -> dict:
        return {
            "performance": self.tracker.get_stats(),
            "revenue": self.revenue.get_summary(),
            "optimizer": self.optimizer.get_stats(),
        }
