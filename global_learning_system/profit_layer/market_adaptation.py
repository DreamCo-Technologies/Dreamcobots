"""
market_adaptation.py — Monitors market-based performance.

Tracks how well deployed AI strategies adapt to shifting market conditions
by measuring performance drift, triggering re-evaluation alerts, and
surfacing adaptation recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class MarketSignal:
    """A single market performance signal for a deployed strategy."""

    strategy_id: str
    signal_type: str  # "performance_drift" | "volume_change" | "accuracy_drop" | "custom"
    value: float
    threshold: float
    alert: bool
    recorded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    notes: Optional[str] = None


class MarketAdaptation:
    """
    Monitors market-based performance signals for deployed AI strategies.

    Parameters
    ----------
    drift_threshold : float
        Minimum absolute change in performance score that triggers a
        drift alert.
    """

    VALID_SIGNAL_TYPES = {"performance_drift", "volume_change", "accuracy_drop", "custom"}

    def __init__(self, drift_threshold: float = 0.05):
        if drift_threshold <= 0:
            raise ValueError("drift_threshold must be positive.")
        self.drift_threshold = drift_threshold
        self._signals: List[MarketSignal] = []
        self._baselines: Dict[str, float] = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def set_baseline(self, strategy_id: str, baseline_score: float) -> None:
        """
        Record the baseline performance score for *strategy_id*.

        Parameters
        ----------
        strategy_id : str
        baseline_score : float
        """
        self._baselines[strategy_id] = baseline_score

    def observe(
        self,
        strategy_id: str,
        current_score: float,
        signal_type: str = "performance_drift",
        notes: Optional[str] = None,
    ) -> MarketSignal:
        """
        Record a current performance observation and detect drift.

        Parameters
        ----------
        strategy_id : str
        current_score : float
        signal_type : str
        notes : str | None

        Returns
        -------
        MarketSignal
        """
        if signal_type not in self.VALID_SIGNAL_TYPES:
            raise ValueError(
                f"Unknown signal type '{signal_type}'. "
                f"Valid: {sorted(self.VALID_SIGNAL_TYPES)}"
            )
        baseline = self._baselines.get(strategy_id, current_score)
        drift = abs(current_score - baseline)
        alert = drift >= self.drift_threshold

        signal = MarketSignal(
            strategy_id=strategy_id,
            signal_type=signal_type,
            value=current_score,
            threshold=self.drift_threshold,
            alert=alert,
            notes=notes,
        )
        self._signals.append(signal)
        return signal

    def get_alerts(self, strategy_id: Optional[str] = None) -> List[MarketSignal]:
        """Return all signals that triggered an alert."""
        signals = [s for s in self._signals if s.alert]
        if strategy_id is not None:
            signals = [s for s in signals if s.strategy_id == strategy_id]
        return signals

    def get_signals(self, strategy_id: Optional[str] = None) -> List[MarketSignal]:
        """Return all recorded signals, optionally filtered by *strategy_id*."""
        if strategy_id is not None:
            return [s for s in self._signals if s.strategy_id == strategy_id]
        return list(self._signals)

    def adaptation_report(self, strategy_id: str) -> Dict[str, Any]:
        """
        Produce an adaptation status report for *strategy_id*.

        Returns
        -------
        dict with keys: ``strategy_id``, ``baseline``, ``latest_score``,
        ``drift``, ``alert_count``, ``recommendation``.
        """
        baseline = self._baselines.get(strategy_id)
        signals = self.get_signals(strategy_id)
        alerts = self.get_alerts(strategy_id)
        latest_score = signals[-1].value if signals else baseline

        drift = abs(latest_score - baseline) if baseline is not None and latest_score is not None else 0.0
        recommendation = (
            "Re-evaluate and retrain strategy."
            if len(alerts) > 0
            else "Strategy performing within acceptable bounds."
        )

        return {
            "strategy_id": strategy_id,
            "baseline": baseline,
            "latest_score": latest_score,
            "drift": round(drift, 6),
            "alert_count": len(alerts),
            "recommendation": recommendation,
        }
