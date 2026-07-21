"""
performance_engine.py — Analyses sandbox results for insights.

Computes performance rankings, trend detection, and comparison reports
across multiple sandbox experiments to feed the Global Learning Matrix.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PerformanceReport:
    """A structured performance analysis report for one or more experiments."""

    experiment_names: List[str]
    rankings: List[Dict[str, Any]]
    best_experiment: str
    worst_experiment: str
    summary: Dict[str, Any] = field(default_factory=dict)


class PerformanceEngine:
    """
    Analyses sandbox experiment results and produces ranked performance reports.

    Parameters
    ----------
    primary_metric : str
        Name of the metric used for ranking (e.g. ``"accuracy"``).
    higher_is_better : bool
        When ``True``, higher metric values rank higher.
    """

    def __init__(self, primary_metric: str = "accuracy", higher_is_better: bool = True):
        self.primary_metric = primary_metric
        self.higher_is_better = higher_is_better

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def analyse(self, results: List[Dict[str, Any]]) -> PerformanceReport:
        """
        Analyse a list of experiment result dictionaries.

        Each dict must contain at minimum:
        - ``"experiment_name"`` (str)
        - ``"metrics"`` (dict[str, float])

        Parameters
        ----------
        results : list[dict]

        Returns
        -------
        PerformanceReport

        Raises
        ------
        ValueError
            If *results* is empty or missing required keys.
        """
        if not results:
            raise ValueError("results must be a non-empty list.")

        rankings = self._rank(results)
        best = rankings[0]["experiment_name"]
        worst = rankings[-1]["experiment_name"]

        summary = {
            "primary_metric": self.primary_metric,
            "higher_is_better": self.higher_is_better,
            "experiment_count": len(results),
        }

        return PerformanceReport(
            experiment_names=[r["experiment_name"] for r in results],
            rankings=rankings,
            best_experiment=best,
            worst_experiment=worst,
            summary=summary,
        )

    def compare(
        self,
        baseline: Dict[str, Any],
        candidate: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compare a *candidate* experiment against a *baseline*.

        Returns a dict with keys: ``improvement``, ``relative_change``,
        ``better``, ``metric_used``.
        """
        b_val = baseline.get("metrics", {}).get(self.primary_metric, 0.0)
        c_val = candidate.get("metrics", {}).get(self.primary_metric, 0.0)
        improvement = c_val - b_val
        relative = (improvement / b_val) if b_val != 0 else float("inf")
        better = improvement > 0 if self.higher_is_better else improvement < 0
        return {
            "metric_used": self.primary_metric,
            "baseline_value": b_val,
            "candidate_value": c_val,
            "improvement": improvement,
            "relative_change": round(relative, 6),
            "better": better,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _rank(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return results sorted by the primary metric."""

        def key_fn(r: Dict[str, Any]) -> float:
            val = r.get("metrics", {}).get(self.primary_metric, 0.0)
            return -val if self.higher_is_better else val

        ranked = sorted(results, key=key_fn)
        for i, r in enumerate(ranked):
            r = dict(r)
            r["rank"] = i + 1
            ranked[i] = r
        return ranked
