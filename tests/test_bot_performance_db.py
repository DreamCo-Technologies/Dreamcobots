"""
Tests for bots/ai_learning_system/database.py

Covers:
  1. Database initialization
  2. Recording bot runs
  3. KPI score computation (efficiency, ROI, reliability, composite)
  4. Run history retrieval
  5. Leaderboard
  6. Underperformer detection
  7. Aggregate stats
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.ai_learning_system.database import BotPerformanceDB


# ===========================================================================
# 1. Initialization
# ===========================================================================

class TestDBInitialization:
    def test_creates_in_memory_db(self):
        db = BotPerformanceDB()
        assert db is not None
        db.close()

    def test_empty_scores_initially(self):
        db = BotPerformanceDB()
        scores = db.get_all_scores()
        assert scores == []
        db.close()

    def test_get_stats_empty_db(self):
        db = BotPerformanceDB()
        stats = db.get_stats()
        assert stats["tracked_bots"] == 0
        assert stats["total_runs"] == 0
        db.close()


# ===========================================================================
# 2. Recording runs
# ===========================================================================

class TestRecordRun:
    def setup_method(self):
        self.db = BotPerformanceDB()

    def teardown_method(self):
        self.db.close()

    def test_record_run_returns_dict(self):
        entry = self.db.record_run("test_bot")
        assert isinstance(entry, dict)
        assert entry["bot_name"] == "test_bot"

    def test_record_run_has_run_at(self):
        entry = self.db.record_run("test_bot")
        assert "run_at" in entry
        assert entry["run_at"] is not None

    def test_record_run_with_kpis(self):
        kpis = {"revenue_usd": 50.0, "tasks_completed": 5, "error_count": 0}
        entry = self.db.record_run("revenue_bot", kpis=kpis)
        assert entry["kpis"]["revenue_usd"] == 50.0

    def test_record_run_error_status(self):
        entry = self.db.record_run("error_bot", status="error")
        assert entry["status"] == "error"

    def test_multiple_runs_same_bot(self):
        self.db.record_run("my_bot")
        self.db.record_run("my_bot")
        self.db.record_run("my_bot")
        summary = self.db.get_kpi_summary("my_bot")
        assert summary["total_runs"] == 3

    def test_record_run_creates_score_entry(self):
        self.db.record_run("new_bot")
        summary = self.db.get_kpi_summary("new_bot")
        assert summary["total_runs"] == 1


# ===========================================================================
# 3. KPI score computation
# ===========================================================================

class TestKPIScores:
    def setup_method(self):
        self.db = BotPerformanceDB()

    def teardown_method(self):
        self.db.close()

    def test_composite_score_range(self):
        self.db.record_run("bot_a", kpis={"revenue_usd": 100.0, "tasks_completed": 5})
        summary = self.db.get_kpi_summary("bot_a")
        assert 0.0 <= summary["composite_score"] <= 100.0

    def test_efficiency_score_increases_with_tasks(self):
        self.db.record_run("bot_task", kpis={"tasks_completed": 10, "error_count": 0})
        summary = self.db.get_kpi_summary("bot_task")
        assert summary["efficiency_score"] > 0.0

    def test_errors_reduce_efficiency(self):
        self.db.record_run("bot_err", kpis={"tasks_completed": 5, "error_count": 10})
        summary = self.db.get_kpi_summary("bot_err")
        self.db.record_run("bot_ok", kpis={"tasks_completed": 5, "error_count": 0})
        summary_ok = self.db.get_kpi_summary("bot_ok")
        assert summary_ok["efficiency_score"] >= summary["efficiency_score"]

    def test_roi_score_increases_with_revenue(self):
        self.db.record_run("rich_bot", kpis={"revenue_usd": 500.0})
        summary = self.db.get_kpi_summary("rich_bot")
        assert summary["roi_score"] >= 99.0  # $500 = cap

    def test_reliability_100_for_successful_runs(self):
        self.db.record_run("reliable_bot", status="ok")
        summary = self.db.get_kpi_summary("reliable_bot")
        assert summary["reliability_score"] == 100.0

    def test_reliability_drops_on_errors(self):
        self.db.record_run("flaky_bot", status="ok")
        self.db.record_run("flaky_bot", status="error")
        summary = self.db.get_kpi_summary("flaky_bot")
        assert summary["reliability_score"] == 50.0

    def test_composite_higher_for_better_bots(self):
        self.db.record_run("good_bot", kpis={
            "revenue_usd": 400.0, "tasks_completed": 8, "error_count": 0,
            "response_time_ms": 100.0,
        })
        self.db.record_run("bad_bot", kpis={
            "revenue_usd": 0.0, "tasks_completed": 0, "error_count": 5,
            "response_time_ms": 5000.0,
        }, status="error")
        good = self.db.get_kpi_summary("good_bot")
        bad = self.db.get_kpi_summary("bad_bot")
        assert good["composite_score"] > bad["composite_score"]

    def test_unknown_bot_returns_zero_scores(self):
        summary = self.db.get_kpi_summary("nonexistent_bot")
        assert summary["composite_score"] == 0.0
        assert summary["total_runs"] == 0


# ===========================================================================
# 4. Run history
# ===========================================================================

class TestRunHistory:
    def setup_method(self):
        self.db = BotPerformanceDB()

    def teardown_method(self):
        self.db.close()

    def test_history_is_list(self):
        self.db.record_run("hist_bot")
        history = self.db.get_run_history("hist_bot")
        assert isinstance(history, list)

    def test_history_has_correct_count(self):
        for _ in range(5):
            self.db.record_run("hist_bot")
        history = self.db.get_run_history("hist_bot")
        assert len(history) == 5

    def test_history_limit(self):
        for _ in range(10):
            self.db.record_run("hist_bot")
        history = self.db.get_run_history("hist_bot", limit=3)
        assert len(history) == 3

    def test_history_kpis_parsed(self):
        self.db.record_run("hist_bot", kpis={"revenue_usd": 42.0})
        history = self.db.get_run_history("hist_bot")
        assert history[0]["kpis"]["revenue_usd"] == 42.0

    def test_empty_history_for_new_bot(self):
        history = self.db.get_run_history("no_runs_bot")
        assert history == []


# ===========================================================================
# 5. Leaderboard
# ===========================================================================

class TestLeaderboard:
    def setup_method(self):
        self.db = BotPerformanceDB()
        self.db.record_run("bot_a", kpis={"revenue_usd": 200.0, "tasks_completed": 5})
        self.db.record_run("bot_b", kpis={"revenue_usd": 50.0, "tasks_completed": 2})
        self.db.record_run("bot_c", kpis={"revenue_usd": 400.0, "tasks_completed": 8})

    def teardown_method(self):
        self.db.close()

    def test_leaderboard_is_list(self):
        lb = self.db.get_leaderboard()
        assert isinstance(lb, list)

    def test_leaderboard_sorted_descending(self):
        lb = self.db.get_leaderboard()
        for i in range(len(lb) - 1):
            assert lb[i]["composite_score"] >= lb[i + 1]["composite_score"]

    def test_leaderboard_top_n(self):
        lb = self.db.get_leaderboard(top_n=2)
        assert len(lb) == 2

    def test_leaderboard_bot_c_first(self):
        lb = self.db.get_leaderboard()
        assert lb[0]["bot_name"] == "bot_c"


# ===========================================================================
# 6. Underperformer detection
# ===========================================================================

class TestUnderperformers:
    def setup_method(self):
        self.db = BotPerformanceDB()
        # Good bot
        self.db.record_run("strong_bot", kpis={"revenue_usd": 400.0, "tasks_completed": 8})
        # Weak bot
        self.db.record_run("weak_bot", kpis={"revenue_usd": 0.0, "tasks_completed": 0}, status="error")

    def teardown_method(self):
        self.db.close()

    def test_underperformers_is_list(self):
        result = self.db.get_underperformers()
        assert isinstance(result, list)

    def test_weak_bot_in_underperformers(self):
        result = self.db.get_underperformers(threshold=50.0)
        names = [r["bot_name"] for r in result]
        assert "weak_bot" in names

    def test_strong_bot_not_in_default_underperformers(self):
        result = self.db.get_underperformers(threshold=30.0)
        names = [r["bot_name"] for r in result]
        assert "strong_bot" not in names

    def test_custom_threshold(self):
        result = self.db.get_underperformers(threshold=100.0)
        # Every bot is below 100
        assert len(result) >= 2


# ===========================================================================
# 7. Aggregate stats
# ===========================================================================

class TestAggregateStats:
    def setup_method(self):
        self.db = BotPerformanceDB()

    def teardown_method(self):
        self.db.close()

    def test_stats_keys(self):
        stats = self.db.get_stats()
        for key in ("tracked_bots", "total_runs", "avg_composite_score",
                    "underperformers_below_30"):
            assert key in stats

    def test_stats_after_runs(self):
        self.db.record_run("bot_x")
        self.db.record_run("bot_x")
        self.db.record_run("bot_y")
        stats = self.db.get_stats()
        assert stats["tracked_bots"] == 2
        assert stats["total_runs"] == 3

    def test_avg_composite_score_is_float(self):
        self.db.record_run("bot_a", kpis={"revenue_usd": 100.0})
        stats = self.db.get_stats()
        assert isinstance(stats["avg_composite_score"], float)
