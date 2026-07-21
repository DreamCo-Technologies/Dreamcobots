"""
Tests for global_learning_system/learning_loop.py — GlobalLearningLoop.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from global_learning_system.learning_loop import (
    BotDecision,
    GlobalLearningLoop,
    LearnedStrategy,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db(tmp_path):
    """Return a path to a fresh in-memory-ish SQLite DB per test."""
    return tmp_path / "test_learning.db"


@pytest.fixture
def loop(tmp_db, tmp_path):
    """Return a fresh GlobalLearningLoop backed by a temporary DB."""
    registry = tmp_path / "registry"
    return GlobalLearningLoop(db_path=tmp_db, model_registry_path=registry)


@pytest.fixture
def sample_decision():
    return BotDecision(
        decision_id="d001",
        bot_name="trading_bot",
        action_type="buy",
        action_params={"symbol": "BTC", "amount": 0.01},
        context={"price": 50000},
        prediction=0.8,
    )


# ---------------------------------------------------------------------------
# BotDecision
# ---------------------------------------------------------------------------


class TestBotDecision:
    def test_timestamp_auto_set(self, sample_decision):
        assert sample_decision.timestamp != ""

    def test_custom_timestamp(self):
        d = BotDecision(
            decision_id="d002",
            bot_name="bot",
            action_type="sell",
            action_params={},
            context={},
            prediction=0.5,
            timestamp="2025-01-01T00:00:00",
        )
        assert d.timestamp == "2025-01-01T00:00:00"

    def test_optional_fields_default_none(self, sample_decision):
        assert sample_decision.actual_outcome is None
        assert sample_decision.reward is None


# ---------------------------------------------------------------------------
# DB initialisation
# ---------------------------------------------------------------------------


class TestDBInit:
    def test_db_file_created(self, tmp_db, tmp_path):
        GlobalLearningLoop(db_path=tmp_db, model_registry_path=tmp_path / "reg")
        assert tmp_db.exists()

    def test_registry_dir_created(self, tmp_db, tmp_path):
        reg = tmp_path / "registry"
        GlobalLearningLoop(db_path=tmp_db, model_registry_path=reg)
        assert reg.is_dir()


# ---------------------------------------------------------------------------
# record_decision
# ---------------------------------------------------------------------------


class TestRecordDecision:
    def test_records_and_counts(self, loop, sample_decision):
        assert loop.count_decisions() == 0
        loop.record_decision(sample_decision)
        assert loop.count_decisions() == 1

    def test_upsert_replaces_existing(self, loop, sample_decision):
        loop.record_decision(sample_decision)
        # Same ID → should replace
        loop.record_decision(sample_decision)
        assert loop.count_decisions() == 1

    def test_multiple_decisions(self, loop):
        for i in range(5):
            d = BotDecision(
                decision_id=f"d{i}",
                bot_name="bot_a",
                action_type="run",
                action_params={},
                context={},
                prediction=0.5,
            )
            loop.record_decision(d)
        assert loop.count_decisions() == 5

    def test_count_per_bot(self, loop):
        for i in range(3):
            loop.record_decision(
                BotDecision(
                    decision_id=f"a{i}", bot_name="bot_a",
                    action_type="run", action_params={}, context={}, prediction=0.5,
                )
            )
        for i in range(2):
            loop.record_decision(
                BotDecision(
                    decision_id=f"b{i}", bot_name="bot_b",
                    action_type="run", action_params={}, context={}, prediction=0.5,
                )
            )
        assert loop.count_decisions("bot_a") == 3
        assert loop.count_decisions("bot_b") == 2


# ---------------------------------------------------------------------------
# record_outcome
# ---------------------------------------------------------------------------


class TestRecordOutcome:
    def test_updates_outcome(self, loop, sample_decision):
        loop.record_decision(sample_decision)
        loop.record_outcome(sample_decision.decision_id, actual_outcome=0.9, reward=25.0)
        rows = loop.get_training_data(bot_name="trading_bot")
        assert len(rows) == 1
        assert rows[0]["actual_outcome"] == 0.9
        assert rows[0]["reward"] == 25.0

    def test_outcome_for_unknown_id_does_not_raise(self, loop):
        loop.record_outcome("nonexistent", actual_outcome=0.0, reward=0.0)  # should not raise


# ---------------------------------------------------------------------------
# get_training_data
# ---------------------------------------------------------------------------


class TestGetTrainingData:
    def test_only_returns_decided_outcomes(self, loop):
        # Decision without outcome
        loop.record_decision(
            BotDecision(
                decision_id="no_outcome", bot_name="bot",
                action_type="run", action_params={}, context={}, prediction=0.5,
            )
        )
        # Decision with outcome
        loop.record_decision(
            BotDecision(
                decision_id="with_outcome", bot_name="bot",
                action_type="run", action_params={}, context={}, prediction=0.5,
            )
        )
        loop.record_outcome("with_outcome", actual_outcome=1.0, reward=10.0)

        rows = loop.get_training_data()
        assert len(rows) == 1
        assert rows[0]["decision_id"] == "with_outcome"

    def test_filter_by_bot_name(self, loop):
        for bot in ("bot_a", "bot_b"):
            loop.record_decision(
                BotDecision(
                    decision_id=bot, bot_name=bot,
                    action_type="run", action_params={}, context={}, prediction=0.5,
                )
            )
            loop.record_outcome(bot, actual_outcome=1.0, reward=5.0)

        rows = loop.get_training_data(bot_name="bot_a")
        assert all(r["bot_name"] == "bot_a" for r in rows)


# ---------------------------------------------------------------------------
# extract_successful_strategies
# ---------------------------------------------------------------------------


class TestExtractSuccessfulStrategies:
    def _seed(self, loop, count=5, bot="bot", action="buy", reward=10.0):
        for i in range(count):
            d = BotDecision(
                decision_id=f"{bot}_{action}_{i}",
                bot_name=bot, action_type=action,
                action_params={}, context={}, prediction=0.5,
            )
            loop.record_decision(d)
            loop.record_outcome(d.decision_id, actual_outcome=1.0, reward=reward)

    def test_returns_strategies_above_min_count(self, loop):
        self._seed(loop, count=5, bot="trade_bot", action="buy")
        strategies = loop.extract_successful_strategies(min_reward=0.0, min_count=3)
        assert len(strategies) == 1
        assert strategies[0].bot_name == "trade_bot"
        assert strategies[0].action_type == "buy"

    def test_below_min_count_excluded(self, loop):
        self._seed(loop, count=2, bot="rare_bot", action="buy")
        strategies = loop.extract_successful_strategies(min_reward=0.0, min_count=3)
        assert len(strategies) == 0

    def test_avg_reward_computed(self, loop):
        self._seed(loop, count=4, bot="r_bot", action="sell", reward=20.0)
        strategies = loop.extract_successful_strategies(min_count=1)
        assert abs(strategies[0].avg_reward - 20.0) < 0.01


# ---------------------------------------------------------------------------
# Model persistence
# ---------------------------------------------------------------------------


class TestModelPersistence:
    def test_save_and_load_model(self, loop):
        model = {"weights": [1, 2, 3], "version": 1}
        path = loop.save_model("test_bot", model, accuracy=0.95)
        assert path.exists()
        loaded = loop.load_latest_model("test_bot")
        assert loaded == model

    def test_version_increments(self, loop):
        loop.save_model("bot_v", {"v": 1})
        loop.save_model("bot_v", {"v": 2})
        loaded = loop.load_latest_model("bot_v")
        assert loaded == {"v": 2}

    def test_load_missing_returns_none(self, loop):
        assert loop.load_latest_model("nonexistent_bot") is None


# ---------------------------------------------------------------------------
# should_retrain
# ---------------------------------------------------------------------------


class TestShouldRetrain:
    def test_below_threshold_returns_false(self, loop):
        # Default threshold is 1000; we have 0 decisions
        assert loop.should_retrain("trading_bot") is False

    def test_at_threshold_returns_true(self, loop, monkeypatch):
        # Patch threshold to 2 so we can test without 1000 records
        import global_learning_system.learning_loop as ll_mod

        original = ll_mod._cfg

        def patched_cfg(key, default):
            if key == "learning.min_samples_to_retrain":
                return 2
            return original(key, default)

        monkeypatch.setattr(ll_mod, "_cfg", patched_cfg)

        for i in range(2):
            loop.record_decision(
                BotDecision(
                    decision_id=f"r{i}", bot_name="trading_bot",
                    action_type="run", action_params={}, context={}, prediction=0.5,
                )
            )
        assert loop.should_retrain("trading_bot") is True
