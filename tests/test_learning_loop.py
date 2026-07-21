"""Tests for bots/ai_learning_system/learning_loop.py"""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.ai_learning_system.learning_loop import (
    LearningLoop,
    BotPerformanceRecord,
    DEFAULT_KPIS,
)


# ---------------------------------------------------------------------------
# BotPerformanceRecord
# ---------------------------------------------------------------------------

class TestBotPerformanceRecord:
    def test_instantiates(self):
        rec = BotPerformanceRecord("test_bot")
        assert rec.bot_name == "test_bot"
        assert rec.total_runs == 0

    def test_efficiency_with_no_runs_is_one(self):
        rec = BotPerformanceRecord("bot")
        assert rec.efficiency == 1.0

    def test_efficiency_after_all_successes(self):
        rec = BotPerformanceRecord("bot")
        rec.record_run(success=True)
        rec.record_run(success=True)
        assert rec.efficiency == 1.0

    def test_efficiency_after_mixed_runs(self):
        rec = BotPerformanceRecord("bot")
        rec.record_run(success=True)
        rec.record_run(success=False)
        assert rec.efficiency == 0.5

    def test_revenue_per_run(self):
        rec = BotPerformanceRecord("bot")
        rec.record_run(success=True, revenue=100.0)
        rec.record_run(success=True, revenue=200.0)
        assert rec.revenue_per_run == 150.0

    def test_record_run_increments_total(self):
        rec = BotPerformanceRecord("bot")
        rec.record_run(True)
        rec.record_run(True)
        assert rec.total_runs == 2

    def test_record_failure_increments_failed(self):
        rec = BotPerformanceRecord("bot")
        rec.record_run(False)
        assert rec.failed_runs == 1

    def test_to_dict_contains_expected_keys(self):
        rec = BotPerformanceRecord("bot")
        d = rec.to_dict()
        for key in ("bot_name", "total_runs", "successful_runs", "failed_runs",
                    "efficiency", "total_revenue_usd", "revenue_per_run", "last_updated"):
            assert key in d


# ---------------------------------------------------------------------------
# LearningLoop instantiation
# ---------------------------------------------------------------------------

class TestLearningLoopInstantiation:
    def test_instantiates(self):
        ll = LearningLoop()
        assert ll is not None

    def test_initial_cycle_count_zero(self):
        ll = LearningLoop()
        assert ll._cycle_count == 0

    def test_default_kpis_present(self):
        ll = LearningLoop()
        for key in DEFAULT_KPIS:
            assert key in ll.kpis

    def test_custom_kpis_override_defaults(self):
        ll = LearningLoop(kpis={"min_efficiency": 0.99})
        assert ll.kpis["min_efficiency"] == 0.99

    def test_initial_performance_empty(self):
        ll = LearningLoop()
        assert ll._performance == {}


# ---------------------------------------------------------------------------
# Performance tracking
# ---------------------------------------------------------------------------

class TestPerformanceTracking:
    def test_record_run_creates_record(self):
        ll = LearningLoop()
        ll.record_run("bot_a", success=True)
        assert "bot_a" in ll._performance

    def test_record_multiple_runs(self):
        ll = LearningLoop()
        ll.record_run("bot_a", success=True)
        ll.record_run("bot_a", success=False)
        assert ll._performance["bot_a"].total_runs == 2

    def test_record_run_returns_record(self):
        ll = LearningLoop()
        rec = ll.record_run("bot_x", success=True)
        assert isinstance(rec, BotPerformanceRecord)

    def test_ingest_cycle_results_ok_run(self):
        ll = LearningLoop()
        cycle_results = [{"bot_results": {"bot_a": {"status": "ok"}}}]
        ll.ingest_cycle_results(cycle_results)
        assert ll._performance["bot_a"].successful_runs == 1

    def test_ingest_cycle_results_error_run(self):
        ll = LearningLoop()
        cycle_results = [{"bot_results": {"bot_b": {"status": "error"}}}]
        ll.ingest_cycle_results(cycle_results)
        assert ll._performance["bot_b"].failed_runs == 1

    def test_ingest_multiple_cycles(self):
        ll = LearningLoop()
        cycles = [
            {"bot_results": {"bot_a": {"status": "ok"}}},
            {"bot_results": {"bot_a": {"status": "ok"}}},
        ]
        ll.ingest_cycle_results(cycles)
        assert ll._performance["bot_a"].total_runs == 2


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

class TestAnalysis:
    def test_analyse_returns_dict(self):
        ll = LearningLoop()
        result = ll.analyse()
        assert isinstance(result, dict)

    def test_analyse_has_expected_keys(self):
        ll = LearningLoop()
        result = ll.analyse()
        for key in ("underperforming", "healthy", "suggestions", "kpis", "timestamp"):
            assert key in result

    def test_healthy_bot_classified_correctly(self):
        ll = LearningLoop(kpis={"min_efficiency": 0.5, "min_revenue_usd": 0.0,
                                 "target_efficiency": 0.9, "target_revenue_usd": 100.0})
        ll.record_run("good_bot", success=True)
        ll.record_run("good_bot", success=True)
        result = ll.analyse()
        healthy_names = [r["bot_name"] for r in result["healthy"]]
        assert "good_bot" in healthy_names

    def test_underperforming_bot_classified_correctly(self):
        ll = LearningLoop(kpis={"min_efficiency": 0.9, "min_revenue_usd": 0.0,
                                 "target_efficiency": 0.95, "target_revenue_usd": 100.0})
        ll.record_run("bad_bot", success=False)
        ll.record_run("bad_bot", success=False)
        result = ll.analyse()
        under_names = [r["bot_name"] for r in result["underperforming"]]
        assert "bad_bot" in under_names

    def test_underperforming_bot_has_issues_field(self):
        ll = LearningLoop(kpis={"min_efficiency": 0.9, "min_revenue_usd": 0.0,
                                 "target_efficiency": 0.95, "target_revenue_usd": 100.0})
        ll.record_run("bad_bot", success=False)
        result = ll.analyse()
        under = result["underperforming"][0]
        assert "issues" in under
        assert len(under["issues"]) > 0

    def test_suggestions_generated_for_underperforming(self):
        ll = LearningLoop(kpis={"min_efficiency": 0.9, "min_revenue_usd": 0.0,
                                 "target_efficiency": 0.95, "target_revenue_usd": 100.0})
        ll.record_run("bad_bot", success=False)
        result = ll.analyse()
        suggestion_types = [s["type"] for s in result["suggestions"]]
        assert "refactor" in suggestion_types

    def test_new_bot_suggestion_when_few_healthy(self):
        ll = LearningLoop()
        # No bots tracked = 0 healthy < 3
        result = ll.analyse()
        suggestion_types = [s["type"] for s in result["suggestions"]]
        assert "new_bot" in suggestion_types

    def test_no_new_bot_suggestion_when_sufficient_healthy(self):
        ll = LearningLoop(kpis={"min_efficiency": 0.0, "min_revenue_usd": 0.0,
                                 "target_efficiency": 0.9, "target_revenue_usd": 100.0})
        for name in ("bot_1", "bot_2", "bot_3"):
            ll.record_run(name, success=True)
        result = ll.analyse()
        suggestion_types = [s["type"] for s in result["suggestions"]]
        assert "new_bot" not in suggestion_types


# ---------------------------------------------------------------------------
# Refactor underperforming
# ---------------------------------------------------------------------------

class TestRefactorUnderperforming:
    def test_refactor_returns_list(self):
        ll = LearningLoop()
        actions = ll.refactor_underperforming()
        assert isinstance(actions, list)

    def test_refactor_logs_action(self):
        ll = LearningLoop(kpis={"min_efficiency": 0.9, "min_revenue_usd": 0.0,
                                 "target_efficiency": 0.95, "target_revenue_usd": 100.0})
        ll.record_run("slow_bot", success=False)
        actions = ll.refactor_underperforming()
        assert len(actions) == 1
        assert actions[0]["bot_name"] == "slow_bot"
        assert actions[0]["action"] == "refactor"

    def test_refactor_log_updated(self):
        ll = LearningLoop(kpis={"min_efficiency": 0.9, "min_revenue_usd": 0.0,
                                 "target_efficiency": 0.95, "target_revenue_usd": 100.0})
        ll.record_run("slow_bot", success=False)
        ll.refactor_underperforming()
        assert len(ll._refactor_log) == 1


# ---------------------------------------------------------------------------
# KPI updates
# ---------------------------------------------------------------------------

class TestKPIUpdates:
    def test_update_kpi(self):
        ll = LearningLoop()
        ll.update_kpis(min_efficiency=0.75)
        assert ll.kpis["min_efficiency"] == 0.75

    def test_update_multiple_kpis(self):
        ll = LearningLoop()
        ll.update_kpis(min_efficiency=0.8, target_revenue_usd=500.0)
        assert ll.kpis["min_efficiency"] == 0.8
        assert ll.kpis["target_revenue_usd"] == 500.0

    def test_update_unknown_kpi_ignored(self):
        ll = LearningLoop()
        original_keys = set(ll.kpis.keys())
        ll.update_kpis(nonexistent_kpi=99.0)
        assert set(ll.kpis.keys()) == original_keys


# ---------------------------------------------------------------------------
# Performance report
# ---------------------------------------------------------------------------

class TestPerformanceReport:
    def test_report_returns_dict(self):
        ll = LearningLoop()
        report = ll.get_performance_report()
        assert isinstance(report, dict)

    def test_report_has_expected_keys(self):
        ll = LearningLoop()
        report = ll.get_performance_report()
        for key in ("cycle_count", "kpis", "bots", "refactor_log", "suggestions", "timestamp"):
            assert key in report

    def test_report_includes_tracked_bots(self):
        ll = LearningLoop()
        ll.record_run("tracked_bot", success=True)
        report = ll.get_performance_report()
        assert "tracked_bot" in report["bots"]


# ---------------------------------------------------------------------------
# run_cycle (no controller, no generator)
# ---------------------------------------------------------------------------

class TestRunCycle:
    def test_run_cycle_returns_dict(self):
        ll = LearningLoop()
        result = ll.run_cycle()
        assert isinstance(result, dict)

    def test_run_cycle_increments_cycle_count(self):
        ll = LearningLoop()
        ll.run_cycle()
        assert ll._cycle_count == 1

    def test_run_cycle_has_analysis(self):
        ll = LearningLoop()
        result = ll.run_cycle()
        assert "analysis" in result

    def test_run_cycle_has_refactor_actions(self):
        ll = LearningLoop()
        result = ll.run_cycle()
        assert "refactor_actions" in result

    def test_run_cycle_has_auto_generated_bots(self):
        ll = LearningLoop()
        result = ll.run_cycle()
        assert "auto_generated_bots" in result

    def test_multiple_cycles_accumulate(self):
        ll = LearningLoop()
        ll.run_cycle()
        ll.run_cycle()
        assert ll._cycle_count == 2
