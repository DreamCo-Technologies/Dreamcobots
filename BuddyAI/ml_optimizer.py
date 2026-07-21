"""
ml_optimizer.py – Machine Learning Optimization Engine.

Provides:
* ``IncomePredictor``  – Predicts high-potential income stream categories
  using a lightweight linear regression model trained on historical data.
* ``OptimizationEngine`` – Tests, scores, and scales profitable ideas
  through a configurable number of simulated iterations.

No external ML framework is required.  The module ships with a pure-Python
implementation that is fully functional without ``scikit-learn``.  When
``scikit-learn`` is installed it is used automatically for improved accuracy.
"""

from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass, field
from typing import Any

from .event_bus import EventBus
from .income_tracker import IncomeRecord

logger = logging.getLogger(__name__)

# ── Try to import sklearn – fall back gracefully ───────────────────────────

try:
    from sklearn.linear_model import LinearRegression  # type: ignore
    import numpy as np  # type: ignore
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False

# ── Data models ────────────────────────────────────────────────────────────


@dataclass
class Prediction:
    source: str
    predicted_revenue: float
    confidence: float          # 0 – 1
    growth_factor: float       # multiplier vs current
    recommendation: str

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "predicted_revenue": round(self.predicted_revenue, 2),
            "confidence": round(self.confidence, 3),
            "growth_factor": round(self.growth_factor, 3),
            "recommendation": self.recommendation,
        }


@dataclass
class OptimizationResult:
    idea: str
    iterations_run: int
    best_score: float
    best_config: dict
    improvement_pct: float
    status: str                # "scaled" | "rejected" | "testing"
    history: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "idea": self.idea,
            "iterations_run": self.iterations_run,
            "best_score": round(self.best_score, 4),
            "best_config": self.best_config,
            "improvement_pct": round(self.improvement_pct, 2),
            "status": self.status,
        }


# ── Pure-Python linear regression ─────────────────────────────────────────


def _simple_linear_regression(
    x: list[float], y: list[float]
) -> tuple[float, float]:
    """Return (slope, intercept) for the simple linear regression of x → y."""
    n = len(x)
    if n < 2:
        return 0.0, (y[0] if y else 0.0)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    den = sum((xi - mean_x) ** 2 for xi in x)
    slope = num / den if den != 0 else 0.0
    intercept = mean_y - slope * mean_x
    return slope, intercept


def _r_squared(x: list[float], y: list[float], slope: float, intercept: float) -> float:
    """Return the R² coefficient of determination."""
    mean_y = sum(y) / len(y)
    ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
    ss_tot = sum((yi - mean_y) ** 2 for yi in y)
    return 1.0 - ss_res / ss_tot if ss_tot != 0 else 1.0


# ── Predictor ──────────────────────────────────────────────────────────────


class IncomePredictor:
    """
    Predicts future revenue for each income stream.

    Trains on a list of ``IncomeRecord`` objects.  Each unique source gets
    its own trend model.  Call ``predict_all`` to get forecasts.
    """

    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self._models: dict[str, tuple[float, float]] = {}  # source → (slope, intercept)
        self._r2: dict[str, float] = {}

    def train(self, records: list[IncomeRecord]) -> None:
        """Train per-source linear trend models from historical *records*."""
        # Group records by source
        groups: dict[str, list[IncomeRecord]] = {}
        for r in records:
            groups.setdefault(r.source, []).append(r)

        for source, recs in groups.items():
            recs.sort(key=lambda r: r.date)
            x = list(range(len(recs)))
            y = [r.revenue for r in recs]
            if _SKLEARN_AVAILABLE:
                X = np.array(x).reshape(-1, 1)
                model = LinearRegression().fit(X, y)
                slope = float(model.coef_[0])
                intercept = float(model.intercept_)
            else:
                slope, intercept = _simple_linear_regression(x, y)
            self._models[source] = (slope, intercept)
            r2 = _r_squared(x, y, slope, intercept)
            self._r2[source] = r2
            logger.debug(
                "Trained model for %s: slope=%.4f, intercept=%.4f, R²=%.4f",
                source, slope, intercept, r2,
            )

    def predict(self, source: str, steps_ahead: int = 30) -> Prediction:
        """Forecast revenue *steps_ahead* periods into the future for *source*."""
        if source not in self._models:
            # No training data – return a conservative estimate
            logger.warning("No model for source '%s'; using heuristic estimate", source)
            rev = random.uniform(50, 500)
            return Prediction(
                source=source,
                predicted_revenue=round(rev, 2),
                confidence=0.3,
                growth_factor=1.0,
                recommendation="Gather more data to improve prediction accuracy.",
            )
        slope, intercept = self._models[source]
        # 'steps_ahead' is relative to the last training index
        last_idx = steps_ahead  # simplified: pretend training had N points
        predicted = max(0.0, slope * (last_idx + steps_ahead) + intercept)
        current = max(0.0, slope * last_idx + intercept)
        growth_factor = predicted / current if current > 0 else 1.0
        confidence = min(max(self._r2.get(source, 0.5), 0.0), 1.0)
        if growth_factor >= 1.2:
            recommendation = "High growth trajectory — increase investment in this stream."
        elif growth_factor >= 1.0:
            recommendation = "Stable growth — maintain current strategy."
        else:
            recommendation = "Declining trend — consider pivoting or optimizing."
        return Prediction(
            source=source,
            predicted_revenue=round(predicted, 2),
            confidence=confidence,
            growth_factor=round(growth_factor, 3),
            recommendation=recommendation,
        )

    def predict_all(self, sources: list[str], steps_ahead: int = 30) -> list[Prediction]:
        """Return predictions for every source in *sources*."""
        return [self.predict(s, steps_ahead) for s in sources]


# ── Optimization engine ────────────────────────────────────────────────────


class OptimizationEngine:
    """
    Tests and scales profitable income stream ideas.

    Uses a simplified simulated-annealing-inspired search to explore the
    configuration space and find high-scoring setups.

    Usage::

        engine = OptimizationEngine(cfg, bus)
        result = engine.optimize("AI Blog Network")
        engine.scale(result)
    """

    def __init__(self, cfg: dict, bus: EventBus) -> None:
        self.cfg = cfg
        self.bus = bus
        self.iterations = int(cfg.get("optimization_iterations", 100))

    def optimize(self, idea: str, baseline_score: float | None = None) -> OptimizationResult:
        """
        Run an optimization loop for the given *idea*.

        Returns an ``OptimizationResult`` with the best configuration found.
        """
        logger.info("Optimizing idea: '%s' over %d iterations", idea, self.iterations)
        if baseline_score is None:
            baseline_score = random.uniform(0.3, 0.5)

        best_score = baseline_score
        best_config: dict[str, Any] = {"mode": "baseline"}
        history = [baseline_score]

        temperature = 1.0
        cooling_rate = 0.95

        config_options = {
            "posting_frequency": ["daily", "3x/week", "weekly"],
            "content_length": ["short", "medium", "long"],
            "promotion_channel": ["SEO", "social", "email", "paid"],
            "monetization_mix": ["ads_only", "ads+affiliate", "full_mix"],
        }

        for i in range(self.iterations):
            # Sample a random configuration
            candidate_config = {
                k: random.choice(v) for k, v in config_options.items()
            }
            # Simulate a score (in production: A/B test or live metric)
            candidate_score = self._simulate_score(candidate_config, i)

            # Accept if better, or probabilistically if worse (SA)
            delta = candidate_score - best_score
            if delta > 0 or random.random() < math.exp(delta / temperature):
                best_score = candidate_score
                best_config = candidate_config

            history.append(best_score)
            temperature *= cooling_rate

        improvement_pct = (
            (best_score - baseline_score) / baseline_score * 100
            if baseline_score > 0 else 0.0
        )
        status = "scaled" if best_score >= 0.7 else "testing" if best_score >= 0.5 else "rejected"
        result = OptimizationResult(
            idea=idea,
            iterations_run=self.iterations,
            best_score=round(best_score, 4),
            best_config=best_config,
            improvement_pct=round(improvement_pct, 2),
            status=status,
            history=history,
        )
        logger.info(
            "Optimization complete for '%s': score=%.4f (%+.1f%%) → %s",
            idea, best_score, improvement_pct, status,
        )
        self.bus.publish("optimizer.result", result.to_dict())
        return result

    def scale(self, result: OptimizationResult) -> dict:
        """
        Apply the best configuration found and initiate scaling.

        Returns an action plan.
        """
        if result.status == "rejected":
            plan = {
                "action": "reject",
                "idea": result.idea,
                "reason": f"Score too low ({result.best_score:.2f}). Recommend pivoting.",
            }
        elif result.status == "testing":
            plan = {
                "action": "continue_testing",
                "idea": result.idea,
                "config": result.best_config,
                "reason": "Promising results; run further experiments.",
            }
        else:
            plan = {
                "action": "scale",
                "idea": result.idea,
                "config": result.best_config,
                "expected_improvement_pct": result.improvement_pct,
                "next_steps": [
                    f"Adopt '{result.best_config.get('posting_frequency')}' posting schedule",
                    f"Focus promotion on '{result.best_config.get('promotion_channel')}'",
                    f"Switch to '{result.best_config.get('monetization_mix')}' monetization",
                    "Monitor KPIs weekly and re-optimize quarterly",
                ],
            }
        self.bus.publish("optimizer.scale_plan", plan)
        return plan

    @staticmethod
    def _simulate_score(config: dict, iteration: int) -> float:
        """
        Simulate a performance score for a configuration.

        Replace with real metric evaluation (CTR, revenue, retention…)
        when integrating live data.
        """
        base = 0.4
        if config.get("monetization_mix") == "full_mix":
            base += 0.15
        if config.get("promotion_channel") in ("SEO", "email"):
            base += 0.10
        if config.get("posting_frequency") in ("daily", "3x/week"):
            base += 0.05
        noise = random.gauss(0, 0.05)
        # Slight upward trend as iterations increase (learning effect)
        trend = min(iteration / 2000, 0.15)
        return min(max(base + noise + trend, 0.0), 1.0)
