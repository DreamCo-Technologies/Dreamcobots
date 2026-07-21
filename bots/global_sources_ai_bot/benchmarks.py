"""
GlobalSourcesAIBot — Continuous Benchmarking Engine

Tracks live performance scores for every model in the registry across 7 key
dimensions, supports daily test cycles, and feeds updated scores back into the
TaskRouter so routing decisions always use the freshest data.

Benchmark dimensions
--------------------
accuracy      — correctness of output (0.0–1.0)
speed         — relative response speed  (0.0–1.0, higher = faster)
cost_score    — inverted cost efficiency (0.0–1.0, higher = cheaper)
creativity    — open-ended / creative output quality (0.0–1.0)
reliability   — uptime / API stability (0.0–1.0)
context_score — handling of long contexts (0.0–1.0)
safety        — alignment and safety rating (0.0–1.0)

GLOBAL AI SOURCES FLOW: This module adheres to the Dreamcobots GLOBAL AI
SOURCES FLOW framework pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from bots.global_sources_ai_bot.model_registry import TOP_100_AI_MODELS


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

BENCHMARK_DIMENSIONS = (
    "accuracy",
    "speed",
    "cost_score",
    "creativity",
    "reliability",
    "context_score",
    "safety",
)


@dataclass
class ModelBenchmark:
    """Stores the latest benchmark scores for a single model."""
    model_id: str
    scores: dict[str, float] = field(default_factory=dict)
    last_tested: Optional[str] = None  # ISO-8601 timestamp
    test_count: int = 0
    composite_score: float = 0.0

    def update(self, new_scores: dict[str, float]) -> None:
        """Merge *new_scores* into the existing scores and recompute composite."""
        for dim in BENCHMARK_DIMENSIONS:
            if dim in new_scores:
                val = float(new_scores[dim])
                self.scores[dim] = max(0.0, min(1.0, val))
        self.last_tested = datetime.now(timezone.utc).isoformat()
        self.test_count += 1
        self.composite_score = self._compute_composite()

    def _compute_composite(self) -> float:
        """Weighted average across all dimensions."""
        weights = {
            "accuracy":      3.0,
            "speed":         1.5,
            "cost_score":    1.5,
            "creativity":    1.0,
            "reliability":   2.0,
            "context_score": 1.0,
            "safety":        2.0,
        }
        total_weight = sum(weights.values())
        weighted_sum = sum(
            self.scores.get(dim, 0.5) * w for dim, w in weights.items()
        )
        return round(weighted_sum / total_weight, 4)


# ---------------------------------------------------------------------------
# Default baseline scores (informed by public model evaluation data)
# ---------------------------------------------------------------------------

_DEFAULTS: dict[str, dict[str, float]] = {
    "chatgpt":           {"accuracy": 0.88, "speed": 0.80, "cost_score": 0.65,
                          "creativity": 0.85, "reliability": 0.92, "context_score": 0.85, "safety": 0.90},
    "claude":            {"accuracy": 0.90, "speed": 0.75, "cost_score": 0.60,
                          "creativity": 0.90, "reliability": 0.90, "context_score": 0.95, "safety": 0.95},
    "gemini":            {"accuracy": 0.87, "speed": 0.82, "cost_score": 0.65,
                          "creativity": 0.83, "reliability": 0.88, "context_score": 0.98, "safety": 0.88},
    "grok":              {"accuracy": 0.83, "speed": 0.85, "cost_score": 0.70,
                          "creativity": 0.80, "reliability": 0.85, "context_score": 0.75, "safety": 0.82},
    "meta_ai":           {"accuracy": 0.80, "speed": 0.80, "cost_score": 0.90,
                          "creativity": 0.78, "reliability": 0.85, "context_score": 0.75, "safety": 0.83},
    "claude_code":       {"accuracy": 0.93, "speed": 0.72, "cost_score": 0.55,
                          "creativity": 0.75, "reliability": 0.90, "context_score": 0.95, "safety": 0.95},
    "github_copilot":    {"accuracy": 0.88, "speed": 0.90, "cost_score": 0.80,
                          "creativity": 0.70, "reliability": 0.92, "context_score": 0.60, "safety": 0.90},
    "cursor":            {"accuracy": 0.87, "speed": 0.88, "cost_score": 0.78,
                          "creativity": 0.72, "reliability": 0.88, "context_score": 0.70, "safety": 0.88},
    "llama":             {"accuracy": 0.82, "speed": 0.85, "cost_score": 0.95,
                          "creativity": 0.78, "reliability": 0.80, "context_score": 0.75, "safety": 0.80},
    "mistral":           {"accuracy": 0.83, "speed": 0.88, "cost_score": 0.90,
                          "creativity": 0.75, "reliability": 0.82, "context_score": 0.80, "safety": 0.82},
    "deepseek":          {"accuracy": 0.85, "speed": 0.82, "cost_score": 0.95,
                          "creativity": 0.78, "reliability": 0.80, "context_score": 0.70, "safety": 0.80},
    "qwen":              {"accuracy": 0.83, "speed": 0.83, "cost_score": 0.88,
                          "creativity": 0.75, "reliability": 0.80, "context_score": 0.75, "safety": 0.80},
    "midjourney":        {"accuracy": 0.90, "speed": 0.60, "cost_score": 0.65,
                          "creativity": 0.97, "reliability": 0.88, "context_score": 0.50, "safety": 0.80},
    "dalle3":            {"accuracy": 0.87, "speed": 0.65, "cost_score": 0.60,
                          "creativity": 0.90, "reliability": 0.90, "context_score": 0.50, "safety": 0.85},
    "stable_diffusion":  {"accuracy": 0.82, "speed": 0.75, "cost_score": 0.95,
                          "creativity": 0.88, "reliability": 0.78, "context_score": 0.50, "safety": 0.75},
    "sora":              {"accuracy": 0.88, "speed": 0.30, "cost_score": 0.30,
                          "creativity": 0.95, "reliability": 0.80, "context_score": 0.50, "safety": 0.85},
    "runway":            {"accuracy": 0.85, "speed": 0.55, "cost_score": 0.50,
                          "creativity": 0.92, "reliability": 0.85, "context_score": 0.50, "safety": 0.82},
    "elevenlabs":        {"accuracy": 0.92, "speed": 0.80, "cost_score": 0.65,
                          "creativity": 0.85, "reliability": 0.90, "context_score": 0.50, "safety": 0.88},
    "whisper":           {"accuracy": 0.93, "speed": 0.82, "cost_score": 0.90,
                          "creativity": 0.50, "reliability": 0.88, "context_score": 0.50, "safety": 0.95},
    "perplexity":        {"accuracy": 0.87, "speed": 0.85, "cost_score": 0.80,
                          "creativity": 0.70, "reliability": 0.88, "context_score": 0.70, "safety": 0.88},
    "suno":              {"accuracy": 0.85, "speed": 0.70, "cost_score": 0.80,
                          "creativity": 0.93, "reliability": 0.82, "context_score": 0.50, "safety": 0.82},
    "alphafold":         {"accuracy": 0.97, "speed": 0.50, "cost_score": 0.80,
                          "creativity": 0.50, "reliability": 0.92, "context_score": 0.50, "safety": 0.95},
    "ms_copilot":        {"accuracy": 0.85, "speed": 0.82, "cost_score": 0.72,
                          "creativity": 0.78, "reliability": 0.90, "context_score": 0.80, "safety": 0.90},
    "zapier_ai":         {"accuracy": 0.85, "speed": 0.85, "cost_score": 0.70,
                          "creativity": 0.60, "reliability": 0.90, "context_score": 0.50, "safety": 0.88},
    "salesforce_einstein":{"accuracy": 0.85, "speed": 0.78, "cost_score": 0.45,
                           "creativity": 0.65, "reliability": 0.92, "context_score": 0.65, "safety": 0.88},
    "jasper":            {"accuracy": 0.82, "speed": 0.82, "cost_score": 0.65,
                          "creativity": 0.85, "reliability": 0.88, "context_score": 0.60, "safety": 0.85},
    "harvey_ai":         {"accuracy": 0.88, "speed": 0.70, "cost_score": 0.35,
                          "creativity": 0.70, "reliability": 0.88, "context_score": 0.85, "safety": 0.92},
    "bloomberg_gpt":     {"accuracy": 0.90, "speed": 0.72, "cost_score": 0.35,
                          "creativity": 0.65, "reliability": 0.90, "context_score": 0.75, "safety": 0.88},
    "crowdstrike_ai":    {"accuracy": 0.90, "speed": 0.85, "cost_score": 0.40,
                          "creativity": 0.50, "reliability": 0.93, "context_score": 0.60, "safety": 0.95},
    "enterprise_ai":        {"accuracy": 0.85, "speed": 0.75, "cost_score": 0.45,
                          "creativity": 0.60, "reliability": 0.90, "context_score": 0.70, "safety": 0.90},
    "nvidia_isaac":      {"accuracy": 0.90, "speed": 0.80, "cost_score": 0.30,
                          "creativity": 0.55, "reliability": 0.90, "context_score": 0.50, "safety": 0.90},
    "deepl":             {"accuracy": 0.94, "speed": 0.90, "cost_score": 0.80,
                          "creativity": 0.50, "reliability": 0.92, "context_score": 0.50, "safety": 0.92},
    "khanmigo":          {"accuracy": 0.88, "speed": 0.78, "cost_score": 0.85,
                          "creativity": 0.78, "reliability": 0.88, "context_score": 0.65, "safety": 0.95},
}


# ---------------------------------------------------------------------------
# Benchmark Engine
# ---------------------------------------------------------------------------

class BenchmarkEngine:
    """
    Maintains benchmark scores for all registered models and exposes
    helper methods for reporting and ranking.

    Designed to feed directly into :class:`TaskRouter.update_benchmark_scores`.
    """

    def __init__(self) -> None:
        self._records: dict[str, ModelBenchmark] = {}
        self._load_defaults()

    # ── Public API ────────────────────────────────────────────────────────

    def update(self, model_id: str, scores: dict[str, float]) -> ModelBenchmark:
        """
        Record new benchmark scores for *model_id*.

        Unknown model IDs are accepted (allows future/custom models).
        Returns the updated :class:`ModelBenchmark`.
        """
        if model_id not in self._records:
            self._records[model_id] = ModelBenchmark(model_id=model_id)
        record = self._records[model_id]
        record.update(scores)
        return record

    def get(self, model_id: str) -> Optional[ModelBenchmark]:
        """Return the benchmark record for *model_id*, or None."""
        return self._records.get(model_id)

    def scores_for_router(self) -> dict[str, dict[str, float]]:
        """
        Export scores in the format consumed by :class:`TaskRouter`.

        Returns
        -------
        dict[str, dict[str, float]]
            model_id → {accuracy, speed, cost_score, …}
        """
        return {mid: dict(rec.scores) for mid, rec in self._records.items()}

    def top_models(self, n: int = 10) -> list[tuple[str, float]]:
        """Return the top-n models by composite score."""
        ranked = sorted(
            self._records.items(),
            key=lambda kv: kv[1].composite_score,
            reverse=True,
        )
        return [(mid, rec.composite_score) for mid, rec in ranked[:n]]

    def rank_by_dimension(self, dimension: str, n: int = 10) -> list[tuple[str, float]]:
        """Rank models by a single benchmark dimension."""
        if dimension not in BENCHMARK_DIMENSIONS:
            raise ValueError(f"Unknown dimension '{dimension}'. Valid: {BENCHMARK_DIMENSIONS}")
        ranked = sorted(
            self._records.items(),
            key=lambda kv: kv[1].scores.get(dimension, 0.0),
            reverse=True,
        )
        return [(mid, rec.scores.get(dimension, 0.0)) for mid, rec in ranked[:n]]

    def summary(self) -> dict:
        """High-level summary for dashboards."""
        top = self.top_models(5)
        return {
            "total_models_benchmarked": len(self._records),
            "dimensions": list(BENCHMARK_DIMENSIONS),
            "top_5_overall": top,
            "best_coding":    self.rank_by_dimension("accuracy", 1),
            "best_speed":     self.rank_by_dimension("speed", 1),
            "best_cost":      self.rank_by_dimension("cost_score", 1),
            "best_creative":  self.rank_by_dimension("creativity", 1),
            "best_safety":    self.rank_by_dimension("safety", 1),
        }

    def run_daily_cycle(self, custom_scores: Optional[dict[str, dict[str, float]]] = None) -> dict:
        """
        Simulate a daily benchmark cycle.

        In production this would call each model's API with standardised
        test prompts and record real latency/quality scores.  Here it
        applies *custom_scores* if provided, otherwise refreshes from
        defaults (with a small jitter to represent continuous measurement).

        Returns a summary of the cycle results.
        """
        import random
        updated: list[str] = []
        scores_to_apply = custom_scores or {}

        for model_id, record in self._records.items():
            if model_id in scores_to_apply:
                self.update(model_id, scores_to_apply[model_id])
            else:
                # Apply a tiny random variation to simulate live measurement
                jittered = {
                    dim: max(0.0, min(1.0, record.scores.get(dim, 0.5) + random.uniform(-0.02, 0.02)))
                    for dim in BENCHMARK_DIMENSIONS
                }
                self.update(model_id, jittered)
            updated.append(model_id)

        return {
            "cycle_timestamp": datetime.now(timezone.utc).isoformat(),
            "models_updated": len(updated),
            "summary": self.summary(),
        }

    # ── Private helpers ───────────────────────────────────────────────────

    def _load_defaults(self) -> None:
        """Seed the engine with baseline scores for all known models."""
        # First, create a neutral baseline for every model in the registry
        for model_id in TOP_100_AI_MODELS:
            self._records[model_id] = ModelBenchmark(
                model_id=model_id,
                scores={dim: 0.5 for dim in BENCHMARK_DIMENSIONS},
                last_tested=None,
                test_count=0,
            )
            self._records[model_id].composite_score = 0.5

        # Then apply the curated defaults
        for model_id, scores in _DEFAULTS.items():
            self.update(model_id, scores)
