"""
DreamCo Auto-Bot Factory — Learning Loop

Monitors bot performance, identifies underperformers, and triggers
autonomous optimization cycles.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Default KPIs
# ---------------------------------------------------------------------------

DEFAULT_KPIS: Dict[str, float] = {
    "min_efficiency": 0.5,
    "min_revenue_usd": 0.0,
    "target_efficiency": 0.9,
    "target_revenue_usd": 100.0,
}

DEFAULT_UNDERPERFORM_THRESHOLD: int = 30
DEFAULT_SCORE_MIN: float = 0.0
DEFAULT_SCORE_MAX: float = 100.0


# ---------------------------------------------------------------------------
# BotPerformanceRecord
# ---------------------------------------------------------------------------

class BotPerformanceRecord:
    """Tracks performance metrics for a single bot."""

    def __init__(self, bot_name: str) -> None:
        self.bot_name = bot_name
        self.total_runs: int = 0
        self.successful_runs: int = 0
        self.failed_runs: int = 0
        self.total_revenue_usd: float = 0.0
        self._last_updated: str = datetime.now(timezone.utc).isoformat()

    @property
    def efficiency(self) -> float:
        """Ratio of successful runs to total runs."""
        if self.total_runs == 0:
            return 1.0
        return self.successful_runs / self.total_runs

    @property
    def revenue_per_run(self) -> float:
        """Average revenue per run."""
        if self.total_runs == 0:
            return 0.0
        return self.total_revenue_usd / self.total_runs

    @property
    def last_updated(self) -> str:
        return self._last_updated

    def record_run(self, success: bool, revenue: float = 0.0) -> None:
        """Record the outcome of a single run."""
        self.total_runs += 1
        if success:
            self.successful_runs += 1
        else:
            self.failed_runs += 1
        self.total_revenue_usd += revenue
        self._last_updated = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bot_name": self.bot_name,
            "total_runs": self.total_runs,
            "successful_runs": self.successful_runs,
            "failed_runs": self.failed_runs,
            "efficiency": round(self.efficiency, 4),
            "total_revenue_usd": round(self.total_revenue_usd, 2),
            "revenue_per_run": round(self.revenue_per_run, 2),
            "last_updated": self.last_updated,
        }


# ---------------------------------------------------------------------------
# Learning Loop Error
# ---------------------------------------------------------------------------

class LearningLoopError(Exception):
    """Raised when the learning loop encounters an unrecoverable state."""


# ---------------------------------------------------------------------------
# Learning Loop
# ---------------------------------------------------------------------------

class LearningLoop:
    """
    DreamCo Auto-Bot Factory — Learning Loop.

    Tracks per-bot performance, identifies underperformers, and suggests
    or generates replacement bots.

    Parameters
    ----------
    kpis : dict | None
        Override default KPI thresholds.
    control_center : any
        Optional legacy control center reference (unused internally).
    generator : any
        Optional legacy bot generator reference (unused internally).
    underperform_threshold : int
        Legacy threshold kept for backwards compatibility.
    """

    def __init__(
        self,
        control_center_or_kpis: Any = None,
        generator: Any = None,
        underperform_threshold: int = DEFAULT_UNDERPERFORM_THRESHOLD,
        kpis: Optional[Dict[str, float]] = None,
        control_center: Any = None,
        controller: Any = None,
    ) -> None:
        import random as _rand_ll
        self._rand_ll = _rand_ll
        # Resolve positional ambiguity: if first arg is a dict, treat as kpis (legacy)
        if isinstance(control_center_or_kpis, dict):
            _kpis = control_center_or_kpis
            self.control_center = control_center or controller
            self.generator = generator
        else:
            self.control_center = control_center_or_kpis or control_center or controller
            self.generator = generator
            _kpis = kpis
        # ``controller`` is kept as a dedicated attribute for architectural
        # flexibility; it also acts as a fallback when no ``control_center`` is
        # supplied (see resolution logic above).
        self.controller = controller
        self.kpis: Dict[str, float] = {**DEFAULT_KPIS, **(_kpis or {})}
        self._performance: Dict[str, BotPerformanceRecord] = {}
        self._refactor_log: List[Dict[str, Any]] = []
        self._cycle_count: int = 0
        self.underperform_threshold = underperform_threshold
        self.performance_log: Dict[str, float] = {}
        # Legacy aliases
        self._control_center = self.control_center
        self._generator = self.generator

    # ------------------------------------------------------------------
    # Performance tracking
    # ------------------------------------------------------------------

    def record_run(
        self, bot_name: str, success: bool, revenue: float = 0.0
    ) -> BotPerformanceRecord:
        """Record one run for a bot and return its record."""
        if bot_name not in self._performance:
            self._performance[bot_name] = BotPerformanceRecord(bot_name)
        self._performance[bot_name].record_run(success=success, revenue=revenue)
        return self._performance[bot_name]

    def ingest_cycle_results(self, cycle_results: List[Dict[str, Any]]) -> None:
        """Ingest a list of cycle result dicts produced by the orchestrator."""
        for cycle in cycle_results:
            bot_results = cycle.get("bot_results", {})
            for bot_name, result in bot_results.items():
                status = result.get("status", "ok") if isinstance(result, dict) else "ok"
                revenue = float(result.get("revenue", 0)) if isinstance(result, dict) else 0.0
                self.record_run(bot_name, success=(status != "error"), revenue=revenue)

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def _get_underperforming(self) -> List[BotPerformanceRecord]:
        min_eff = self.kpis.get("min_efficiency", DEFAULT_KPIS["min_efficiency"])
        min_rev = self.kpis.get("min_revenue_usd", DEFAULT_KPIS["min_revenue_usd"])
        result = []
        for rec in self._performance.values():
            if rec.efficiency < min_eff or rec.total_revenue_usd < min_rev:
                result.append(rec)
        return result

    def _get_healthy(self) -> List[BotPerformanceRecord]:
        min_eff = self.kpis.get("min_efficiency", DEFAULT_KPIS["min_efficiency"])
        min_rev = self.kpis.get("min_revenue_usd", DEFAULT_KPIS["min_revenue_usd"])
        return [
            rec for rec in self._performance.values()
            if rec.efficiency >= min_eff and rec.total_revenue_usd >= min_rev
        ]

    def analyse(self) -> Dict[str, Any]:
        """Analyse all tracked bots and return a structured report."""
        underperforming = self._get_underperforming()
        healthy = self._get_healthy()

        under_dicts = []
        for rec in underperforming:
            issues = []
            min_eff = self.kpis.get("min_efficiency", DEFAULT_KPIS["min_efficiency"])
            min_rev = self.kpis.get("min_revenue_usd", DEFAULT_KPIS["min_revenue_usd"])
            if rec.efficiency < min_eff:
                issues.append(f"efficiency {rec.efficiency:.2f} < min {min_eff}")
            if rec.total_revenue_usd < min_rev:
                issues.append(f"revenue ${rec.total_revenue_usd:.2f} < min ${min_rev:.2f}")
            under_dicts.append({**rec.to_dict(), "issues": issues})

        suggestions: List[Dict[str, Any]] = []
        for rec in underperforming:
            suggestions.append({
                "type": "refactor",
                "bot_name": rec.bot_name,
                "reason": "below KPI thresholds",
            })
        if len(healthy) < 3:
            suggestions.append({
                "type": "new_bot",
                "reason": f"only {len(healthy)} healthy bots (need ≥ 3)",
            })

        return {
            "underperforming": under_dicts,
            "healthy": [r.to_dict() for r in healthy],
            "suggestions": suggestions,
            "kpis": self.kpis,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def refactor_underperforming(self) -> List[Dict[str, Any]]:
        """Flag all underperforming bots for refactoring."""
        actions: List[Dict[str, Any]] = []
        for rec in self._get_underperforming():
            action = {
                "bot_name": rec.bot_name,
                "action": "refactor",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            actions.append(action)
            self._refactor_log.append(action)
        return actions

    def update_kpis(self, **kwargs: float) -> None:
        """Update named KPI thresholds."""
        for key, value in kwargs.items():
            if key in self.kpis:
                self.kpis[key] = value

    def get_performance_report(self) -> Dict[str, Any]:
        """Return a comprehensive performance report."""
        analysis = self.analyse()
        return {
            "cycle_count": self._cycle_count,
            "kpis": self.kpis,
            "bots": {name: rec.to_dict() for name, rec in self._performance.items()},
            "refactor_log": list(self._refactor_log),
            "suggestions": analysis["suggestions"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def run_cycle(self) -> Dict[str, Any]:
        """Execute one full learning cycle."""
        self._cycle_count += 1
        analysis = self.analyse()
        refactor_actions = self.refactor_underperforming()
        auto_generated_bots: List[str] = []
        if self._generator is not None:
            for rec in self._get_underperforming():
                try:
                    self._generator.create_bot(f"{rec.bot_name}_optimized")
                    auto_generated_bots.append(f"{rec.bot_name}_optimized")
                except Exception:  # noqa: BLE001
                    pass
        return {
            "cycle": self._cycle_count,
            "analysis": analysis,
            "refactor_actions": refactor_actions,
            "auto_generated_bots": auto_generated_bots,
        }

    # ------------------------------------------------------------------
    # Legacy API
    # ------------------------------------------------------------------

    def track_performance(self, bot_name: str = None, score: float = None) -> dict:
        """Track performance.

        New API (no args): scores all bots from control_center.bots and returns
        dict of {bot_name: score}.
        Legacy API (bot_name, score): records a single bot's score, returns
        dict with {bot_name, score, status}.
        """
        if bot_name is None and self.control_center is not None:
            # New API: score all bots in control_center
            result: Dict[str, float] = {}
            bots = getattr(self.control_center, "bots", {}) or {}
            for name in bots:
                s = round(self._rand_ll.uniform(DEFAULT_SCORE_MIN, DEFAULT_SCORE_MAX), 2)
                self.performance_log[name] = s
                result[name] = s
            return result
        # Legacy API with bot_name + score
        if score is not None and (score < DEFAULT_SCORE_MIN or score > DEFAULT_SCORE_MAX):
            raise LearningLoopError(f"Invalid score {score!r}: must be between {DEFAULT_SCORE_MIN} and {DEFAULT_SCORE_MAX}.")
        if bot_name is not None:
            self.record_run(bot_name, success=(score >= self.underperform_threshold) if score is not None else True)
            self.performance_log[bot_name] = score
        status = "underperforming" if (score is not None and score < self.underperform_threshold) else "healthy"
        return {"bot_name": bot_name, "score": score, "status": status}

    def get_underperformers(self):
        """Return underperforming bots as dict {name: score}."""
        return {name: score for name, score in self.performance_log.items()
                if score < self.underperform_threshold}

    def get_performance_log(self):
        """Return a copy of the performance log (dict)."""
        return dict(self.performance_log)

    def optimize(self):
        """Optimize underperforming bots. Returns list of created bot names."""
        print("Optimizing bots...")
        created = []
        underperformers = self.get_underperformers()
        if self.control_center is not None and not underperformers:
            # Use cc.bots if performance_log is from new-API style
            bots = getattr(self.control_center, "bots", {}) or {}
            for name in bots:
                score = self.performance_log.get(name, DEFAULT_SCORE_MAX)
                if score < self.underperform_threshold:
                    underperformers[name] = score
        for name in underperformers:
            new_name = f"{name}_optimized"
            print(f"Improving {name} → {new_name}")
            if self.generator is not None:
                self.generator.create_bot(new_name)
            created.append(new_name)
            self._refactor_log.append({"original": name, "replacement": new_name})
        return created

    def get_optimization_history(self) -> List[Dict]:
        return list(self._refactor_log)

    def track_revenue(self) -> float:
        if self.control_center is not None and hasattr(self.control_center, "get_total_revenue"):
            return float(self.control_center.get_total_revenue())
        return float(sum(r.total_revenue_usd for r in self._performance.values()))

    def count_leads(self) -> int:
        if self.control_center is not None and hasattr(self.control_center, "count_leads"):
            return int(self.control_center.count_leads())
        return sum(r.total_runs for r in self._performance.values())

    def run(self) -> str:
        result = self.run_cycle()
        return f"LearningLoop: cycle_{result['cycle']}_complete"
