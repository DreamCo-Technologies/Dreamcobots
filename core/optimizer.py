"""
DreamCo Optimizer — Self-Improving Bot System

Analyses bot output and recommends strategic adjustments.
"""

from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Thresholds (module-level defaults for backwards compatibility)
# ---------------------------------------------------------------------------

LOW_CONVERSION_THRESHOLD: float = 0.05
HIGH_REVENUE_THRESHOLD: float = 1000.0
MIN_LEADS_THRESHOLD: int = 3


# ---------------------------------------------------------------------------
# OptimizationResult
# ---------------------------------------------------------------------------

@dataclass
class OptimizationResult:
    bot_name: str
    recommendation: str
    revenue: float
    conversion_rate: float
    leads_generated: int = 0
    priority_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bot_name": self.bot_name,
            "recommendation": self.recommendation,
            "revenue": round(self.revenue, 2),
            "conversion_rate": round(self.conversion_rate, 4),
            "leads_generated": self.leads_generated,
            "priority_score": round(self.priority_score, 4),
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Optimizer
# ---------------------------------------------------------------------------

class Optimizer:
    """
    Analyses bot performance and recommends the next action.

    Parameters
    ----------
    low_conversion_threshold : float
        Conversion rates below this are "Change strategy".
    scale_revenue_threshold : float
        Revenue above this is "Scale aggressively".
    """

    def __init__(
        self,
        low_conversion_threshold: float = LOW_CONVERSION_THRESHOLD,
        scale_revenue_threshold: float = HIGH_REVENUE_THRESHOLD,
    ) -> None:
        self._low_conv = low_conversion_threshold
        self._scale_rev = scale_revenue_threshold
        self._history: List[OptimizationResult] = []

    def improve(self, bot_output: Dict[str, Any]) -> str:
        """Return a single strategic recommendation string."""
        revenue: float = float(bot_output.get("revenue", 0))
        conversion_rate: float = float(bot_output.get("conversion_rate", 0.0))
        leads_generated: int = int(bot_output.get("leads_generated", 0))

        if leads_generated < 3:
            return "Expand reach"
        if conversion_rate < self._low_conv:
            return "Change strategy"
        if revenue > self._scale_rev:
            return "Scale aggressively"
        if revenue > 0:
            return "Maintain"
        return "Expand reach"

    def evaluate(self, bot_name: str, bot_output: Dict[str, Any]) -> OptimizationResult:
        """Evaluate a bot and return a rich OptimizationResult."""
        revenue = float(bot_output.get("revenue", 0))
        conversion_rate = float(bot_output.get("conversion_rate", 0.0))
        leads_generated = int(bot_output.get("leads_generated", 0))
        recommendation = self.improve(bot_output)
        priority_score = revenue * conversion_rate * (1 + leads_generated * 0.01)
        result = OptimizationResult(
            bot_name=bot_name,
            recommendation=recommendation,
            revenue=revenue,
            conversion_rate=conversion_rate,
            leads_generated=leads_generated,
            priority_score=priority_score,
        )
        self._history.append(result)
        return result

    def get_history(self) -> List[OptimizationResult]:
        """Return all evaluated results."""
        return list(self._history)

    def evaluate_all(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate a list of bot result dicts sorted by priority (descending)."""
        results = []
        for item in items:
            bot_name = item.get("bot_name", item.get("bot", "unknown"))
            output = item.get("output") or {}
            result = self.evaluate(bot_name, output)
            results.append({**item, "bot_name": bot_name, "result": result})
        results.sort(key=lambda x: x["result"].priority_score, reverse=True)
        return results

    def get_top_performers(self, n: int = 5) -> List[Dict[str, Any]]:
        """Return the top N bots by priority score from history."""
        sorted_history = sorted(self._history, key=lambda r: r.priority_score, reverse=True)
        return [r.to_dict() for r in sorted_history[:n]]

    def analyse_all(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Legacy method — analyse results and return enriched recommendations."""
        enriched = []
        for result in results:
            bot_name = result.get("bot", "unknown")
            output = result.get("output") or {}
            recommendation = self.improve(output) if output else "Insufficient data"
            enriched.append({"bot": bot_name, "recommendation": recommendation, "output": output})
        return enriched
