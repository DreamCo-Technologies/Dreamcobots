"""
DreamCo Control Plane — Learning Gateway
==========================================

Surfaces key learning-system signals:

* recent decisions and outcomes
* reward statistics (mean, max, total)
* drift indicator (std-dev of recent rewards vs baseline)
* retraining status stub (extensible via ``set_retraining_status``)
"""

from __future__ import annotations

import statistics
import time
from typing import Any, Dict, List, Optional


class LearningGateway:
    """
    Aggregates signals from the Global Learning System for dashboard display.

    The gateway is intentionally decoupled from the ``GlobalLearningLoop``
    singleton so that it can be used in tests without touching the SQLite DB.
    Plug in a real loop via ``attach_loop()``.
    """

    def __init__(self) -> None:
        self._loop: Any = None
        self._retraining_status: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Loop attachment
    # ------------------------------------------------------------------

    def attach_loop(self, loop: Any) -> None:
        """Attach a ``GlobalLearningLoop`` (or compatible object) instance."""
        self._loop = loop

    # ------------------------------------------------------------------
    # Retraining status
    # ------------------------------------------------------------------

    def set_retraining_status(
        self, model_id: str, status: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record the current retraining status of a model."""
        self._retraining_status[model_id] = {
            "model_id": model_id,
            "status": status,
            "recorded_at": time.time(),
            "metadata": metadata or {},
        }

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Return a learning-system snapshot for the dashboard."""
        recent_decisions: List[Dict[str, Any]] = []
        reward_stats: Dict[str, Any] = {
            "count": 0,
            "mean": 0.0,
            "max": 0.0,
            "total": 0.0,
            "drift_indicator": 0.0,
        }
        strategies: List[Dict[str, Any]] = []

        if self._loop is not None:
            try:
                recent_decisions = [
                    {
                        "decision_id": d.decision_id,
                        "bot_name": d.bot_name,
                        "action_type": d.action_type,
                        "prediction": d.prediction,
                        "reward": d.reward,
                        "timestamp": d.timestamp,
                    }
                    for d in self._loop.get_recent_decisions(limit=20)
                ]
            except Exception:  # pragma: no cover
                pass

            try:
                rewards = [
                    d.reward
                    for d in self._loop.get_recent_decisions(limit=100)
                    if d.reward is not None
                ]
                if rewards:
                    reward_stats["count"] = len(rewards)
                    reward_stats["mean"] = round(sum(rewards) / len(rewards), 4)
                    reward_stats["max"] = round(max(rewards), 4)
                    reward_stats["total"] = round(sum(rewards), 4)
                    if len(rewards) > 1:
                        reward_stats["drift_indicator"] = round(
                            statistics.stdev(rewards), 4
                        )
            except Exception:  # pragma: no cover
                pass

            try:
                strategies = [
                    {
                        "strategy_id": s.strategy_id,
                        "bot_name": s.bot_name,
                        "action_type": s.action_type,
                        "avg_reward": s.avg_reward,
                        "success_count": s.success_count,
                    }
                    for s in self._loop.get_top_strategies(limit=10)
                ]
            except Exception:  # pragma: no cover
                pass

        return {
            "recent_decisions": recent_decisions,
            "reward_stats": reward_stats,
            "top_strategies": strategies,
            "retraining_status": list(self._retraining_status.values()),
            "snapshot_at": time.time(),
        }
