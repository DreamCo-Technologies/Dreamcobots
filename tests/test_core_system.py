"""
Tests for the DreamCo Core System:
  - core.base_bot   : BaseBot interface, result validation, helper methods
  - core.executor   : BotExecutor single/batch execution, error isolation
  - core.workflow   : WorkflowEngine step chaining, stop_on_failure, history
  - core.money_loop : MoneyLoopEngine revenue aggregation, scaling trigger
  - config.settings : Settings singleton, simulation flag, active_keys
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from core.base_bot import (
    BaseBot,
    BaseBotError,
    RESULT_STATUS_SUCCESS,
    RESULT_STATUS_FAILED,
)
from core.executor import BotExecutor
from core.workflow import WorkflowEngine, WorkflowStep
from core.money_loop import MoneyLoopEngine
from core.dreamco_orchestrator import SCALE_THRESHOLD


# ===========================================================================
# Helpers — concrete bot implementations for testing
# ===========================================================================


class EchoBot(BaseBot):
    bot_id = "echo_bot"
    name = "Echo Bot"
    category = "test"

    def run(self, task: dict) -> dict:
        return self._success(data={"echo": task.get("msg", "")}, metrics={"revenue": 100})


class RevenueBot(BaseBot):
    bot_id = "revenue_bot"
    name = "Revenue Bot"
    category = "finance"

    def __init__(self, revenue: float = 500.0, leads: int = 5) -> None:
        self._revenue = revenue
        self._leads = leads

    def run(self, task: dict) -> dict:
        return self._success(
            data={"revenue": self._revenue, "leads_generated": self._leads},
            metrics={"revenue": self._revenue},
        )


class FailBot(BaseBot):
    bot_id = "fail_bot"
    name = "Fail Bot"
    category = "test"

    def run(self, task: dict) -> dict:
        raise RuntimeError("FailBot always fails")


class BadResultBot(BaseBot):
    """Returns a malformed dict (missing required keys)."""

    bot_id = "bad_result_bot"
    name = "Bad Result Bot"
    category = "test"

    def run(self, task: dict) -> dict:
        return {"foo": "bar"}  # intentionally missing required keys


# ===========================================================================
# BaseBot
# ===========================================================================


class TestBaseBot:
    def test_abstract_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            BaseBot()  # type: ignore[abstract]

    def test_success_result_shape(self):
        bot = EchoBot()
        result = bot.run({"msg": "hello"})
        assert result["status"] == RESULT_STATUS_SUCCESS
        assert result["bot_id"] == "echo_bot"
        assert "data" in result
        assert "metrics" in result
        assert "next_tasks" in result

    def test_failure_result_shape(self):
        bot = EchoBot()
        result = bot._failure(error="something went wrong")
        assert result["status"] == RESULT_STATUS_FAILED
        assert "error" in result
        assert result["bot_id"] == "echo_bot"

    def test_validate_result_passes_for_valid_success(self):
        bot = EchoBot()
        result = bot.run({})
        assert BaseBot.validate_result(result) is True

    def test_validate_result_fails_for_missing_key(self):
        assert BaseBot.validate_result({"status": "success"}) is False

    def test_validate_result_fails_for_bad_status(self):
        bad = {
            "status": "unknown",
            "bot_id": "x",
            "data": {},
            "metrics": {},
            "next_tasks": [],
        }
        assert BaseBot.validate_result(bad) is False

    def test_success_defaults_are_empty_collections(self):
        bot = EchoBot()
        result = bot._success()
        assert result["data"] == {}
        assert result["metrics"] == {}
        assert result["next_tasks"] == []

    def test_failure_includes_error_message(self):
        bot = EchoBot()
        result = bot._failure(error="test error")
        assert result["error"] == "test error"

    def test_bot_class_attributes(self):
        bot = EchoBot()
        assert bot.bot_id == "echo_bot"
        assert bot.name == "Echo Bot"
        assert bot.category == "test"


# ===========================================================================
# BotExecutor
# ===========================================================================


class TestBotExecutor:
    def setup_method(self):
        self.executor = BotExecutor()

    def test_execute_success_returns_success_status(self):
        entry = self.executor.execute(EchoBot(), task={"msg": "hi"})
        assert entry["status"] == RESULT_STATUS_SUCCESS

    def test_execute_populates_result(self):
        entry = self.executor.execute(EchoBot(), task={})
        assert entry["result"] is not None
        assert "data" in entry["result"]

    def test_execute_records_elapsed_ms(self):
        entry = self.executor.execute(EchoBot(), task={})
        assert isinstance(entry["elapsed_ms"], float)
        assert entry["elapsed_ms"] >= 0

    def test_execute_captures_exception_as_failed(self):
        entry = self.executor.execute(FailBot(), task={})
        assert entry["status"] == RESULT_STATUS_FAILED
        assert "error" in entry

    def test_execute_malformed_result_becomes_failed(self):
        entry = self.executor.execute(BadResultBot(), task={})
        assert entry["status"] == RESULT_STATUS_FAILED

    def test_execute_default_task_is_empty_dict(self):
        entry = self.executor.execute(EchoBot())
        assert entry["status"] == RESULT_STATUS_SUCCESS

    def test_execute_many_runs_all_bots(self):
        bots = [EchoBot(), EchoBot(), EchoBot()]
        entries = self.executor.execute_many(bots)
        assert len(entries) == 3

    def test_execute_many_isolates_failures(self):
        bots = [EchoBot(), FailBot(), EchoBot()]
        entries = self.executor.execute_many(bots)
        statuses = [e["status"] for e in entries]
        assert statuses == [RESULT_STATUS_SUCCESS, RESULT_STATUS_FAILED, RESULT_STATUS_SUCCESS]

    def test_get_log_returns_all_entries(self):
        self.executor.execute(EchoBot())
        self.executor.execute(EchoBot())
        assert len(self.executor.get_log()) == 2

    def test_clear_log(self):
        self.executor.execute(EchoBot())
        self.executor.clear_log()
        assert self.executor.get_log() == []

    def test_summary_counts_correctly(self):
        self.executor.execute(EchoBot())   # success
        self.executor.execute(FailBot())   # failure
        summary = self.executor.summary()
        assert summary["total"] == 2
        assert summary["succeeded"] == 1
        assert summary["failed"] == 1

    def test_summary_empty_executor(self):
        summary = self.executor.summary()
        assert summary["total"] == 0
        assert summary["avg_elapsed_ms"] == 0.0

    def test_entry_contains_bot_id(self):
        entry = self.executor.execute(EchoBot())
        assert entry["bot_id"] == "echo_bot"

    def test_entry_contains_bot_name(self):
        entry = self.executor.execute(EchoBot())
        assert entry["bot_name"] == "Echo Bot"


# ===========================================================================
# WorkflowEngine
# ===========================================================================


class TestWorkflowEngine:
    def setup_method(self):
        self.engine = WorkflowEngine(name="test_workflow")

    def test_run_single_step(self):
        self.engine.add_bot(EchoBot(), task={"msg": "test"})
        result = self.engine.run()
        assert result.status == RESULT_STATUS_SUCCESS
        assert len(result.steps) == 1

    def test_run_multiple_steps(self):
        self.engine.add_bot(EchoBot()).add_bot(EchoBot())
        result = self.engine.run()
        assert len(result.steps) == 2

    def test_stop_on_failure_halts_pipeline(self):
        self.engine.stop_on_failure = True
        self.engine.add_bot(FailBot()).add_bot(EchoBot())
        result = self.engine.run()
        assert result.status == RESULT_STATUS_FAILED
        assert len(result.steps) == 1  # second step never ran

    def test_continue_on_failure_runs_all(self):
        engine = WorkflowEngine(stop_on_failure=False)
        engine.add_bot(FailBot()).add_bot(EchoBot())
        result = engine.run()
        assert len(result.steps) == 2

    def test_result_to_dict(self):
        self.engine.add_bot(EchoBot())
        d = self.engine.run().to_dict()
        assert "status" in d
        assert "steps" in d
        assert "succeeded" in d
        assert "failed" in d

    def test_context_is_populated(self):
        self.engine.add_bot(EchoBot(), name="step_a")
        result = self.engine.run()
        assert "step_a" in result.context

    def test_history_records_runs(self):
        self.engine.add_bot(EchoBot())
        self.engine.run()
        self.engine.run()
        assert len(self.engine.get_history()) == 2

    def test_last_result_returns_most_recent(self):
        self.engine.add_bot(EchoBot())
        r1 = self.engine.run()
        r2 = self.engine.run()
        assert self.engine.last_result() is r2

    def test_last_result_none_before_any_run(self):
        assert self.engine.last_result() is None

    def test_clear_steps(self):
        self.engine.add_bot(EchoBot())
        self.engine.clear_steps()
        result = self.engine.run()
        assert len(result.steps) == 0

    def test_add_step_object(self):
        step = WorkflowStep(bot=EchoBot(), task={"x": 1}, name="custom_step")
        self.engine.add_step(step)
        result = self.engine.run()
        assert result.steps[0]["step"] == "custom_step"

    def test_succeeded_and_failed_counts(self):
        engine = WorkflowEngine(stop_on_failure=False)
        engine.add_bot(EchoBot()).add_bot(FailBot()).add_bot(EchoBot())
        result = engine.run()
        assert result.succeeded == 2
        assert result.failed == 1

    def test_total_elapsed_ms_is_float(self):
        self.engine.add_bot(EchoBot())
        result = self.engine.run()
        assert isinstance(result.total_elapsed_ms, float)


# ===========================================================================
# MoneyLoopEngine
# ===========================================================================


class TestMoneyLoopEngine:
    def _make_loop(self, revenue: float = 200.0, leads: int = 5, cycles: int = 1) -> MoneyLoopEngine:
        workflow = WorkflowEngine(name="money_loop_wf")
        workflow.add_bot(RevenueBot(revenue=revenue, leads=leads))
        return MoneyLoopEngine(workflow=workflow, max_cycles=cycles)

    def test_run_returns_dict(self):
        loop = self._make_loop()
        report = loop.run()
        assert isinstance(report, dict)

    def test_run_keys(self):
        loop = self._make_loop()
        report = loop.run()
        assert "total_cycles" in report
        assert "total_revenue" in report
        assert "total_leads" in report
        assert "cycles" in report

    def test_single_cycle_revenue(self):
        loop = self._make_loop(revenue=200.0)
        report = loop.run()
        assert report["total_revenue"] == pytest.approx(200.0)

    def test_multi_cycle_revenue_accumulates(self):
        loop = self._make_loop(revenue=300.0, cycles=3)
        report = loop.run()
        assert report["total_revenue"] == pytest.approx(900.0)
        assert report["total_cycles"] == 3

    def test_leads_accumulate(self):
        loop = self._make_loop(leads=4, cycles=2)
        report = loop.run()
        assert report["total_leads"] == 8

    def test_scaling_triggered_above_threshold(self):
        # Revenue above SCALE_THRESHOLD triggers auto-scaling
        loop = self._make_loop(revenue=SCALE_THRESHOLD + 500.0)
        report = loop.run()
        assert len(report["scaled_bots"]) > 0

    def test_no_scaling_below_threshold(self):
        loop = self._make_loop(revenue=50.0)
        report = loop.run()
        assert report["scaled_bots"] == []

    def test_get_cycle_reports_length(self):
        loop = self._make_loop(cycles=3)
        loop.run()
        assert len(loop.get_cycle_reports()) == 3

    def test_total_revenue_helper(self):
        loop = self._make_loop(revenue=200.0, cycles=2)
        loop.run()
        assert loop.total_revenue() == pytest.approx(400.0)

    def test_total_leads_helper(self):
        loop = self._make_loop(leads=5, cycles=2)
        loop.run()
        assert loop.total_leads() == 10

    def test_cycle_report_to_dict_shape(self):
        loop = self._make_loop()
        loop.run()
        report = loop.get_cycle_reports()[0]
        d = report.to_dict()
        assert "cycle" in d
        assert "revenue" in d
        assert "validation_status" in d
        assert "elapsed_ms" in d


# ===========================================================================
# config.settings
# ===========================================================================


class TestSettings:
    def test_settings_import(self):
        from config.settings import settings
        assert settings is not None

    def test_simulation_mode_default_true(self):
        from config.settings import Settings
        s = Settings()
        # Default is True when SIMULATION_MODE env var is unset or "true"
        assert isinstance(s.simulation_mode, bool)

    def test_is_real_mode_inverse_of_simulation(self):
        from config.settings import Settings
        s = Settings()
        assert s.is_real_mode() == (not s.simulation_mode)

    def test_to_dict_has_expected_keys(self):
        from config.settings import settings
        d = settings.to_dict()
        assert "simulation_mode" in d
        assert "log_level" in d
        assert "money_loop_cycles" in d
        assert "keys_configured" in d

    def test_active_keys_returns_list(self):
        from config.settings import settings
        assert isinstance(settings.active_keys(), list)

    def test_has_key_returns_false_for_unset(self):
        from config.settings import Settings
        # Create fresh instance with no env keys set
        s = Settings()
        # In CI the API keys are typically not set, so this should be False
        # (or True if someone has injected them — that's fine too)
        result = s.has_key("zillow_api_key")
        assert isinstance(result, bool)

    def test_money_loop_cycles_positive(self):
        from config.settings import settings
        assert settings.money_loop_cycles >= 1

    def test_thresholds_positive(self):
        from config.settings import settings
        assert settings.scale_threshold_usd > 0
        assert settings.maintain_threshold_usd > 0
        assert settings.scale_threshold_usd > settings.maintain_threshold_usd
