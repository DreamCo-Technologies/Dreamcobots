"""
GlobalLearningLoop — Persistent SQLite-backed learning system for DreamCobots.

Every bot records decisions and observed outcomes here.  The loop
periodically extracts successful strategies and exposes training data
so that models can be retrained automatically.

Usage
-----
    from global_learning_system.learning_loop import learning_loop, BotDecision

    decision = BotDecision(
        decision_id="abc123",
        bot_name="trading_bot",
        action_type="buy",
        action_params={"symbol": "BTC", "amount": 0.01},
        context={"price": 50000},
        prediction=0.75,
    )
    learning_loop.record_decision(decision)
    learning_loop.record_outcome("abc123", actual_outcome=0.9, reward=25.0)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import pickle
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional config import (gracefully degraded when running standalone)
# ---------------------------------------------------------------------------

try:
    from config.config_manager import config as _master_config
except Exception:  # pragma: no cover
    _master_config = None  # type: ignore[assignment]


def _cfg(key: str, default: Any) -> Any:
    if _master_config is not None:
        return _master_config.get(key, default)
    return default


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class BotDecision:
    """A single decision recorded by a bot before it acts."""

    decision_id: str
    bot_name: str
    action_type: str
    action_params: Dict[str, Any]
    context: Dict[str, Any]
    prediction: float
    actual_outcome: Optional[float] = None
    reward: Optional[float] = None
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class LearnedStrategy:
    """A strategy that has been proven profitable by observed outcomes."""

    strategy_id: str
    bot_name: str
    action_type: str
    avg_reward: float
    success_count: int
    conditions: Dict[str, Any]
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# GlobalLearningLoop
# ---------------------------------------------------------------------------


class GlobalLearningLoop:
    """
    Singleton-style persistent learning engine backed by SQLite.

    The database is created lazily on first access.
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        model_registry_path: Optional[Path] = None,
    ) -> None:
        configured_db = os.environ.get("DREAMCO_LEARNING_DB", "database/learning.db")
        self.db_path = db_path or Path(configured_db)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

        registry_str = _cfg("learning.model_registry_path", "models/registry")
        self.model_registry = model_registry_path or Path(registry_str)
        self.model_registry.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id   TEXT PRIMARY KEY,
                    bot_name      TEXT NOT NULL,
                    action_type   TEXT NOT NULL,
                    action_params TEXT NOT NULL,
                    context       TEXT NOT NULL,
                    prediction    REAL NOT NULL,
                    actual_outcome REAL,
                    reward        REAL,
                    timestamp     TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS learned_strategies (
                    strategy_id   TEXT PRIMARY KEY,
                    bot_name      TEXT NOT NULL,
                    action_type   TEXT NOT NULL,
                    avg_reward    REAL NOT NULL,
                    success_count INTEGER NOT NULL,
                    conditions    TEXT NOT NULL,
                    created_at    TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS model_versions (
                    model_id      TEXT PRIMARY KEY,
                    bot_name      TEXT NOT NULL,
                    version       INTEGER NOT NULL,
                    path          TEXT NOT NULL,
                    accuracy      REAL,
                    created_at    TEXT NOT NULL
                );
                """
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_decision(self, decision: BotDecision) -> None:
        """Persist a bot decision to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO decisions
                (decision_id, bot_name, action_type, action_params,
                 context, prediction, actual_outcome, reward, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.decision_id,
                    decision.bot_name,
                    decision.action_type,
                    json.dumps(decision.action_params),
                    json.dumps(decision.context),
                    decision.prediction,
                    decision.actual_outcome,
                    decision.reward,
                    decision.timestamp,
                ),
            )
            conn.commit()
        logger.debug("Recorded decision %s for bot %s", decision.decision_id, decision.bot_name)

    def record_outcome(
        self,
        decision_id: str,
        actual_outcome: float,
        reward: float,
    ) -> None:
        """Update a previously recorded decision with its observed outcome."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE decisions
                SET actual_outcome = ?, reward = ?
                WHERE decision_id = ?
                """,
                (actual_outcome, reward, decision_id),
            )
            conn.commit()
        logger.debug("Updated outcome for decision %s", decision_id)

    # ------------------------------------------------------------------
    # Data retrieval
    # ------------------------------------------------------------------

    def get_training_data(
        self,
        bot_name: Optional[str] = None,
        since_days: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Return decisions that have observed outcomes for training."""
        retention = _cfg("learning.feedback_retention_days", 90)
        effective_days = since_days or int(retention)
        cutoff = (datetime.now(timezone.utc) - timedelta(days=effective_days)).isoformat()

        query = "SELECT * FROM decisions WHERE actual_outcome IS NOT NULL AND timestamp >= ?"
        params: List[Any] = [cutoff]
        if bot_name:
            query += " AND bot_name = ?"
            params.append(bot_name)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()

        return [dict(r) for r in rows]

    def extract_successful_strategies(
        self,
        min_reward: float = 0.0,
        min_count: int = 3,
    ) -> List[LearnedStrategy]:
        """
        Aggregate decisions with positive rewards into learned strategies.

        Groups by (bot_name, action_type) and returns those with
        at least *min_count* successful observations.
        """
        query = """
            SELECT
                bot_name,
                action_type,
                AVG(reward)   AS avg_reward,
                COUNT(*)      AS success_count
            FROM decisions
            WHERE reward > ?
            GROUP BY bot_name, action_type
            HAVING COUNT(*) >= ?
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, (min_reward, min_count)).fetchall()

        strategies: List[LearnedStrategy] = []
        for row in rows:
            sid = hashlib.md5(
                f"{row['bot_name']}:{row['action_type']}".encode()
            ).hexdigest()
            strategies.append(
                LearnedStrategy(
                    strategy_id=sid,
                    bot_name=row["bot_name"],
                    action_type=row["action_type"],
                    avg_reward=round(row["avg_reward"], 4),
                    success_count=row["success_count"],
                    conditions={},
                )
            )
        return strategies

    def count_decisions(self, bot_name: Optional[str] = None) -> int:
        """Return the total number of recorded decisions (optionally per bot)."""
        if bot_name:
            query = "SELECT COUNT(*) FROM decisions WHERE bot_name = ?"
            params: tuple = (bot_name,)
        else:
            query = "SELECT COUNT(*) FROM decisions"
            params = ()
        with sqlite3.connect(self.db_path) as conn:
            (count,) = conn.execute(query, params).fetchone()
        return count

    def get_recent_outcomes(self, n: int = 50) -> List[Dict[str, Any]]:
        """Return the newest completed decisions in a workflow-friendly shape."""
        if n < 1:
            return []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT decision_id, bot_name, action_type, actual_outcome,
                       reward, timestamp
                FROM decisions
                WHERE actual_outcome IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (n,),
            ).fetchall()

        outcomes = []
        for row in rows:
            item = dict(row)
            item["outcome"] = "success" if float(item["actual_outcome"]) > 0 else "failure"
            outcomes.append(item)
        return outcomes

    # ------------------------------------------------------------------
    # Model persistence
    # ------------------------------------------------------------------

    def save_model(
        self,
        bot_name: str,
        model: Any,
        accuracy: float = 0.0,
    ) -> Path:
        """Pickle *model* into the model registry and record the version."""
        existing = self._latest_version(bot_name)
        version = (existing or 0) + 1
        model_id = hashlib.md5(f"{bot_name}:{version}".encode()).hexdigest()
        model_path = self.model_registry / f"{bot_name}_v{version}.pkl"
        with open(model_path, "wb") as fh:
            pickle.dump(model, fh)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO model_versions
                (model_id, bot_name, version, path, accuracy, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    model_id,
                    bot_name,
                    version,
                    str(model_path),
                    accuracy,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
        logger.info("Saved model for %s at %s (v%d)", bot_name, model_path, version)
        return model_path

    def load_latest_model(self, bot_name: str) -> Optional[Any]:
        """Return the most recently saved model for *bot_name*, or ``None``."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT path FROM model_versions WHERE bot_name = ? ORDER BY version DESC LIMIT 1",
                (bot_name,),
            ).fetchone()
        if not row:
            return None
        model_path = Path(row[0])
        if not model_path.exists():
            logger.warning("Model file missing: %s", model_path)
            return None
        with open(model_path, "rb") as fh:
            return pickle.load(fh)

    def _latest_version(self, bot_name: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT MAX(version) FROM model_versions WHERE bot_name = ?",
                (bot_name,),
            ).fetchone()
        return row[0] or 0

    # ------------------------------------------------------------------
    # Retraining gate
    # ------------------------------------------------------------------

    def should_retrain(self, bot_name: str) -> bool:
        """
        Return ``True`` when there are enough new samples to justify retraining.

        The threshold is read from ``learning.min_samples_to_retrain`` in the
        master config (default: 1 000).
        """
        threshold = int(_cfg("learning.min_samples_to_retrain", 1000))
        count = self.count_decisions(bot_name)
        return count >= threshold


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

learning_loop = GlobalLearningLoop()
