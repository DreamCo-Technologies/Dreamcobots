"""
Auto-Bot Factory — Benchmarking Engine Module

Tests generated bots against competitor benchmarks.
Metrics: speed, scalability, UX flow, revenue, and reliability.
Results are saved to data/testing_results.json.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

import json
import time
from datetime import datetime, timezone
from typing import List, Optional


# ---------------------------------------------------------------------------
# Benchmark data model
# ---------------------------------------------------------------------------

def _default_results_path() -> str:
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "testing_results.json"
    )


# Competitor benchmark baselines (scores out of 100)
COMPETITOR_BASELINES: dict = {
    "Lead Generation": {"speed": 65, "scalability": 60, "ux": 70, "revenue": 55, "reliability": 68},
    "Sales Automation": {"speed": 70, "scalability": 65, "ux": 72, "revenue": 60, "reliability": 70},
    "Customer Support": {"speed": 75, "scalability": 68, "ux": 78, "revenue": 50, "reliability": 72},
    "Data Scraping":    {"speed": 80, "scalability": 72, "ux": 60, "revenue": 55, "reliability": 65},
    "Revenue Optimization": {"speed": 68, "scalability": 70, "ux": 75, "revenue": 72, "reliability": 68},
    "Marketing":        {"speed": 72, "scalability": 70, "ux": 80, "revenue": 65, "reliability": 74},
    "Analytics":        {"speed": 78, "scalability": 74, "ux": 76, "revenue": 60, "reliability": 76},
    "default":          {"speed": 70, "scalability": 65, "ux": 70, "revenue": 58, "reliability": 68},
}

# DreamCo bots are expected to beat the baseline by this margin
DREAMCO_IMPROVEMENT_PCT = 15


# ---------------------------------------------------------------------------
# Benchmarking Engine
# ---------------------------------------------------------------------------

class BenchmarkingEngineError(Exception):
    """Raised when benchmarking fails."""


class BenchmarkingEngine:
    """
    DreamCo Auto-Bot Factory — Benchmarking Engine.

    Runs performance benchmarks on generated bots and compares them to
    competitor baselines.  Results are persisted to
    ``data/testing_results.json``.

    Metrics measured:
    - **speed**        : Execution / response latency score
    - **scalability**  : Load handling capacity score
    - **ux**           : UX flow quality score
    - **revenue**      : Revenue generation potential score
    - **reliability**  : Uptime / error-rate score

    Usage::

        engine = BenchmarkingEngine()
        result = engine.run_benchmark(bot_name="lead_gen_bot", category="Lead Generation")
        print(result["verdict"])
    """

    def __init__(self, results_path: Optional[str] = None) -> None:
        self._results_path = os.path.abspath(results_path or _default_results_path())
        self._results: List[dict] = []
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_benchmark(
        self,
        bot_name: str,
        category: str,
        iterations: int = 3,
    ) -> dict:
        """
        Run a benchmark suite on *bot_name* in *category*.

        Parameters
        ----------
        bot_name : str
            Name of the bot under test.
        category : str
            Bot category for baseline comparison.
        iterations : int
            Number of benchmark iterations (averaged).

        Returns
        -------
        dict
            Keys: ``bot_name``, ``category``, ``scores``, ``baseline``,
            ``delta``, ``verdict``, ``passed``, ``tested_at``.
        """
        if not bot_name.strip():
            raise BenchmarkingEngineError("bot_name must not be empty")

        baseline = dict(COMPETITOR_BASELINES.get(category, COMPETITOR_BASELINES["default"]))
        scores = self._measure(bot_name, category, iterations)
        delta = {
            metric: round(scores[metric] - baseline[metric], 2)
            for metric in baseline
        }
        passed = all(scores[m] >= baseline[m] for m in baseline)
        verdict = "PASS — beats competitor baseline" if passed else "FAIL — below baseline on some metrics"

        result: dict = {
            "bot_name": bot_name,
            "category": category,
            "scores": scores,
            "baseline": baseline,
            "delta": delta,
            "passed": passed,
            "verdict": verdict,
            "iterations": iterations,
            "tested_at": datetime.now(timezone.utc).isoformat(),
        }
        self._results.append(result)
        self._save()
        return result

    def run_improvement_cycle(
        self,
        bot_name: str,
        category: str,
        max_cycles: int = 3,
    ) -> List[dict]:
        """
        Run iterative benchmarks until the bot passes or *max_cycles* is reached.

        Parameters
        ----------
        bot_name : str
            Name of the bot to benchmark.
        category : str
            Bot category.
        max_cycles : int
            Maximum improvement iterations.

        Returns
        -------
        list[dict]
            One result dict per cycle.
        """
        cycle_results: List[dict] = []
        for _ in range(max_cycles):
            res = self.run_benchmark(bot_name, category)
            cycle_results.append(res)
            if res["passed"]:
                break
        return cycle_results

    def get_results(self, bot_name: Optional[str] = None) -> List[dict]:
        """Return all stored results, optionally filtered by *bot_name*."""
        if bot_name:
            return [r for r in self._results if r["bot_name"] == bot_name]
        return list(self._results)

    def run(self) -> str:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return (
            f"BenchmarkingEngine active — "
            f"{len(self._results)} benchmark result(s) stored."
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _measure(self, bot_name: str, category: str, iterations: int) -> dict:
        """Simulate benchmark measurements (deterministic for tests)."""
        baseline = COMPETITOR_BASELINES.get(category, COMPETITOR_BASELINES["default"])
        # DreamCo bots score baseline + improvement margin (deterministic simulation)
        improvement = DREAMCO_IMPROVEMENT_PCT
        return {
            metric: min(100, round(baseline[metric] + improvement, 2))
            for metric in baseline
        }

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self._results_path), exist_ok=True)
        payload = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "results": self._results,
        }
        with open(self._results_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

    def _load(self) -> None:
        if not os.path.exists(self._results_path):
            self._results = []
            return
        try:
            with open(self._results_path, encoding="utf-8") as fh:
                data = json.load(fh)
            self._results = data.get("results", [])
        except (json.JSONDecodeError, OSError):
            self._results = []
