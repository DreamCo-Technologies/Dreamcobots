"""
retraining_optimizer.py – Model retraining decision engine for DreamCobots.

Determines whether a bot model should be retrained based on accuracy drift,
and selects the most appropriate retraining strategy.

Usage
-----
    from framework.retraining_optimizer import RetrainingOptimizer

    optimizer = RetrainingOptimizer(threshold=0.05)
    if optimizer.should_retrain(current_accuracy=0.84, baseline_accuracy=0.92):
        method = optimizer.select_retraining_method(0.84, 0.92)
        print(f"Retraining recommended: {method}")
"""

from __future__ import annotations

from typing import Optional


# ---------------------------------------------------------------------------
# Retraining strategy constants
# ---------------------------------------------------------------------------

STRATEGY_FULL_RETRAIN = "full_retrain"
STRATEGY_FINE_TUNE = "fine_tune"
STRATEGY_INCREMENTAL = "incremental_update"
STRATEGY_NO_RETRAIN = "no_retrain"


class RetrainingOptimizer:
    """
    Evaluates model accuracy drift and recommends retraining strategies.

    Parameters
    ----------
    threshold : float
        Minimum absolute accuracy drop that triggers a retraining recommendation.
        Default is ``0.05`` (5 percentage points).
    critical_threshold : float
        Accuracy drop above which a full retrain is recommended (default 0.15).
    """

    def __init__(
        self,
        threshold: float = 0.05,
        critical_threshold: float = 0.15,
    ) -> None:
        if not 0.0 < threshold <= 1.0:
            raise ValueError(f"threshold must be in (0, 1], got {threshold!r}")
        if not threshold < critical_threshold <= 1.0:
            raise ValueError(
                f"critical_threshold ({critical_threshold!r}) must be "
                f"greater than threshold ({threshold!r}) and ≤ 1"
            )
        self.threshold = threshold
        self.critical_threshold = critical_threshold

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def should_retrain(
        self,
        baseline_accuracy: float,
        current_accuracy: float,
    ) -> bool:
        """
        Return ``True`` when the accuracy drop exceeds ``self.threshold``.

        Parameters
        ----------
        baseline_accuracy : float
            Reference accuracy the model achieved after its last training run.
        current_accuracy : float
            Most recently measured model accuracy (0–1).
        """
        drop = self._accuracy_drop(current_accuracy, baseline_accuracy)
        return drop >= self.threshold

    def select_retraining_method(
        self,
        baseline_accuracy: float,
        current_accuracy: float,
    ) -> str:
        """
        Choose a retraining strategy based on the magnitude of accuracy drift.

        Parameters
        ----------
        baseline_accuracy : float
            Reference accuracy from the last training run.
        current_accuracy : float
            Most recently measured model accuracy.

        Returns one of:
        - ``"no_retrain"``         — drop < threshold
        - ``"incremental_update"`` — threshold ≤ drop < critical_threshold / 2
        - ``"fine_tune"``          — critical_threshold / 2 ≤ drop < critical_threshold
        - ``"full_retrain"``       — drop ≥ critical_threshold
        """
        drop = self._accuracy_drop(current_accuracy, baseline_accuracy)

        if drop < self.threshold:
            return STRATEGY_NO_RETRAIN
        if drop >= self.critical_threshold:
            return STRATEGY_FULL_RETRAIN
        mid = self.critical_threshold / 2
        if drop >= mid:
            return STRATEGY_FINE_TUNE
        return STRATEGY_INCREMENTAL

    def drift_summary(
        self,
        baseline_accuracy: float,
        current_accuracy: float,
        label: Optional[str] = None,
    ) -> dict:
        """
        Return a summary dict with drift details and retraining recommendation.

        Useful for monitoring reports and JSON artifact generation.
        """
        drop = self._accuracy_drop(current_accuracy, baseline_accuracy)
        retrain = drop >= self.threshold
        method = self.select_retraining_method(baseline_accuracy, current_accuracy)

        return {
            "label": label or "model",
            "baseline_accuracy": baseline_accuracy,
            "current_accuracy": current_accuracy,
            "accuracy_drop": round(drop, 6),
            "threshold": self.threshold,
            "drift_detected": retrain,
            "recommended_method": method,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _accuracy_drop(current: float, baseline: float) -> float:
        """Absolute accuracy reduction (clamped to 0 – no negative drift)."""
        return max(0.0, baseline - current)
