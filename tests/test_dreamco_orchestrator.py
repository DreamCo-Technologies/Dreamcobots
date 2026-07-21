"""
Tests for the DreamCo Orchestrator, Revenue Validator, Auto Scaler,
Scheduler, and Optimizer.

Covers:
  1. RevenueValidator — scale / maintain / underperforming logic
  2. AutoScaler — clone notification
  3. DreamCoOrchestrator — process_bot, run_bot (mocked), run_all_bots (mocked), summary
  4. Scheduler — single cycle, max_cycles, cycle counter
  5. Optimizer — improve recommendations, analyse_all
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import types
from unittest.mock import MagicMock, patch

import pytest

from core.dreamco_orchestrator import (
    DreamCoOrchestrator,
    RevenueValidator,
    AutoScaler,
    SCALE_THRESHOLD,
    MAINTAIN_THRESHOLD,
)
from core.optimizer import Optimizer, HIGH_REVENUE_THRESHOLD, LOW_CONVERSION_THRESHOLD
from core.scheduler import Scheduler


# ===========================================================================
# RevenueValidator
# ===========================================================================


class TestRevenueValidator:
    def setup_method(self):
        self.validator = RevenueValidator()

    # --- scale threshold ---

    def test_scale_when_revenue_exceeds_threshold(self):
        result = self.validator.validate({"revenue": SCALE_THRESHOLD + 1})
        assert result["scale"] is True
        assert result["status"] == "scale"

    def test_scale_at_exact_threshold(self):
        result = self.validator.validate({"revenue": SCALE_THRESHOLD})
        assert result["scale"] is True

    # --- maintain threshold ---

    def test_maintain_above_lower_threshold(self):
        result = self.validator.validate({"revenue": MAINTAIN_THRESHOLD + 50})
        assert result["scale"] is False
        assert result["status"] == "maintain"

    def test_maintain_at_exact_lower_threshold(self):
        result = self.validator.validate({"revenue": MAINTAIN_THRESHOLD})
        assert result["scale"] is False
        assert result["status"] == "maintain"

    # --- underperforming ---

    def test_underperforming_below_maintain(self):
        result = self.validator.validate({"revenue": MAINTAIN_THRESHOLD - 1})
        assert result["scale"] is False
        assert result["status"] == "underperforming"

    def test_underperforming_zero_revenue(self):
        result = self.validator.validate({"revenue": 0})
        assert result["status"] == "underperforming"

    # --- passthrough fields ---

    def test_passthrough_fields(self):
        result = self.validator.validate(
            {"revenue": 200, "conversion_rate": 0.25, "leads_generated": 10}
        )
        assert result["conversion_rate"] == pytest.approx(0.25)
        assert result["leads_generated"] == 10
        assert result["revenue"] == pytest.approx(200.0)

    def test_missing_fields_default_to_zero(self):
        result = self.validator.validate({})
        assert result["revenue"] == 0
        assert result["conversion_rate"] == 0.0
        assert result["leads_generated"] == 0

    def test_message_contains_scale_emoji_when_scaling(self):
        result = self.validator.validate({"revenue": 9999})
        assert "🚀" in result["message"]

    def test_message_contains_status_when_not_scaling(self):
        result = self.validator.validate({"revenue": 50})
        assert "📊" in result["message"]


# ===========================================================================
# AutoScaler
# ===========================================================================


class TestAutoScaler:
    def setup_method(self):
        self.scaler = AutoScaler()

    def test_clone_bot_returns_string(self):
        msg = self.scaler.clone_bot("real_estate_bot")
        assert isinstance(msg, str)

    def test_clone_bot_contains_bot_name(self):
        msg = self.scaler.clone_bot("my_bot")
        assert "my_bot" in msg

    def test_clone_bot_mentions_niche(self):
        msg = self.scaler.clone_bot("job_bot")
        assert "niche" in msg.lower()


# ===========================================================================
# DreamCoOrchestrator — process_bot
# ===========================================================================


class TestDreamCoOrchestratorProcessBot:
    def setup_method(self):
        self.orch = DreamCoOrchestrator()

    def test_process_bot_returns_dict(self):
        result = self.orch.process_bot("test_bot", {"revenue": 50})
        assert isinstance(result, dict)

    def test_process_bot_scale_false_below_threshold(self):
        result = self.orch.process_bot("low_bot", {"revenue": 50})
        assert result["scale"] is False

    def test_process_bot_scale_true_above_threshold(self):
        result = self.orch.process_bot("big_bot", {"revenue": SCALE_THRESHOLD + 100})
        assert result["scale"] is True

    def test_process_bot_passthrough_conversion_rate(self):
        result = self.orch.process_bot("b", {"revenue": 200, "conversion_rate": 0.4})
        assert result["conversion_rate"] == pytest.approx(0.4)


# ===========================================================================
# DreamCoOrchestrator — run_bot (mocked module)
# ===========================================================================


class TestDreamCoOrchestratorRunBot:
    def setup_method(self):
        self.orch = DreamCoOrchestrator()

    def _register_mock_module(self, module_path: str, output: dict):
        """Register a fake module in sys.modules that has a run() function."""
        mod = types.ModuleType(module_path)
        mod.run = lambda: output  # type: ignore[attr-defined]
        sys.modules[module_path] = mod
        return mod

    def teardown_method(self):
        # Clean up any mock modules we added
        for key in list(sys.modules.keys()):
            if key.startswith("mock_dreamco_"):
                del sys.modules[key]

    def test_run_bot_success(self):
        path = "mock_dreamco_success"
        self._register_mock_module(path, {"revenue": 300, "leads_generated": 5, "conversion_rate": 0.2})
        result = self.orch.run_bot(path, "success_bot")
        assert "output" in result
        assert result["output"]["revenue"] == 300
        assert "validation" in result
        assert "error" not in result or result.get("error") is None

    def test_run_bot_error_captured(self):
        path = "mock_dreamco_missing"
        # Don't register — importlib will raise ModuleNotFoundError
        result = self.orch.run_bot(path, "missing_bot")
        assert "error" in result
        assert isinstance(result["error"], str)

    def test_run_bot_returns_bot_name(self):
        path = "mock_dreamco_named"
        self._register_mock_module(path, {"revenue": 100})
        result = self.orch.run_bot(path, "named_bot")
        assert result["bot"] == "named_bot"

    def test_run_bot_scale_true_when_high_revenue(self):
        path = "mock_dreamco_high"
        self._register_mock_module(path, {"revenue": 5000, "leads_generated": 2, "conversion_rate": 0.1})
        result = self.orch.run_bot(path, "high_bot")
        assert result["validation"]["scale"] is True


# ===========================================================================
# DreamCoOrchestrator — summary
# ===========================================================================


class TestDreamCoOrchestratorSummary:
    def setup_method(self):
        self.orch = DreamCoOrchestrator()

    def _make_results(self):
        return [
            {
                "bot": "bot_a",
                "output": {"revenue": 500, "leads_generated": 3, "conversion_rate": 0.2},
                "validation": {"scale": False, "status": "maintain"},
            },
            {
                "bot": "bot_b",
                "output": {"revenue": 1500, "leads_generated": 2, "conversion_rate": 0.1},
                "validation": {"scale": True, "status": "scale"},
            },
            {
                "bot": "bot_err",
                "error": "import failed",
            },
        ]

    def test_summary_total_revenue(self):
        s = self.orch.summary(self._make_results())
        assert s["total_revenue"] == pytest.approx(2000.0)

    def test_summary_total_leads(self):
        s = self.orch.summary(self._make_results())
        assert s["total_leads"] == 5

    def test_summary_scaling_bots(self):
        s = self.orch.summary(self._make_results())
        assert "bot_b" in s["scaling_bots"]
        assert "bot_a" not in s["scaling_bots"]

    def test_summary_failed_bots(self):
        s = self.orch.summary(self._make_results())
        assert "bot_err" in s["failed_bots"]

    def test_summary_bots_run_count(self):
        s = self.orch.summary(self._make_results())
        assert s["bots_run"] == 3

    def test_summary_empty_results(self):
        s = self.orch.summary([])
        assert s["total_revenue"] == 0
        assert s["total_leads"] == 0
        assert s["scaling_bots"] == []
        assert s["failed_bots"] == []
        assert s["bots_run"] == 0


# ===========================================================================
# Optimizer
# ===========================================================================


class TestOptimizer:
    def setup_method(self):
        self.opt = Optimizer()

    def test_scale_aggressively_high_revenue(self):
        rec = self.opt.improve({"revenue": HIGH_REVENUE_THRESHOLD + 1, "conversion_rate": 0.3, "leads_generated": 5})
        assert rec == "Scale aggressively"

    def test_change_strategy_low_conversion(self):
        rec = self.opt.improve({
            "revenue": 200,
            "conversion_rate": LOW_CONVERSION_THRESHOLD - 0.01,
            "leads_generated": 5,
        })
        assert rec == "Change strategy"

    def test_expand_reach_few_leads(self):
        rec = self.opt.improve({"revenue": 100, "conversion_rate": 0.2, "leads_generated": 1})
        assert rec == "Expand reach"

    def test_maintain_middle_ground(self):
        rec = self.opt.improve({"revenue": 300, "conversion_rate": 0.15, "leads_generated": 5})
        assert rec == "Maintain"

    def test_expand_reach_when_no_leads(self):
        # An empty output dict has 0 leads (< threshold) → "Expand reach"
        rec = self.opt.improve({})
        assert rec == "Expand reach"

    def test_analyse_all_returns_list(self):
        results = [
            {"bot": "bot_a", "output": {"revenue": 200, "conversion_rate": 0.1, "leads_generated": 5}},
            {"bot": "bot_b", "output": {"revenue": 2000, "conversion_rate": 0.3, "leads_generated": 10}},
        ]
        enriched = self.opt.analyse_all(results)
        assert len(enriched) == 2

    def test_analyse_all_includes_recommendation(self):
        results = [{"bot": "test", "output": {"revenue": 500, "conversion_rate": 0.1, "leads_generated": 5}}]
        enriched = self.opt.analyse_all(results)
        assert "recommendation" in enriched[0]

    def test_analyse_all_missing_output(self):
        results = [{"bot": "broken", "error": "failed"}]
        enriched = self.opt.analyse_all(results)
        # No output key → output falls back to {} (falsy) → "Insufficient data"
        assert enriched[0]["recommendation"] == "Insufficient data"


# ===========================================================================
# Scheduler
# ===========================================================================


class _MockOrchestrator:
    """Minimal mock orchestrator for Scheduler tests."""

    def __init__(self, revenue: float = 500):
        self.revenue = revenue
        self.call_count = 0

    def run_all_bots(self):
        self.call_count += 1
        return [
            {
                "bot": "mock_bot",
                "output": {
                    "revenue": self.revenue,
                    "leads_generated": 3,
                    "conversion_rate": 0.2,
                },
                "validation": {"scale": False, "status": "maintain"},
            }
        ]

    def summary(self, results):
        return {
            "total_revenue": self.revenue,
            "total_leads": 3,
            "scaling_bots": [],
            "failed_bots": [],
            "bots_run": 1,
        }


class TestScheduler:
    def test_run_cycle_increments_counter(self):
        sched = Scheduler(interval_seconds=0, orchestrator=_MockOrchestrator())
        sched.run_cycle()
        assert sched.cycles_run == 1

    def test_run_cycle_returns_summary(self):
        sched = Scheduler(interval_seconds=0, orchestrator=_MockOrchestrator(revenue=750))
        result = sched.run_cycle()
        assert result["total_revenue"] == 750

    def test_run_forever_stops_at_max_cycles(self):
        mock_orch = _MockOrchestrator()
        sched = Scheduler(interval_seconds=0, max_cycles=3, orchestrator=mock_orch)
        sched.run_forever()
        assert sched.cycles_run == 3
        assert mock_orch.call_count == 3

    def test_default_interval(self):
        sched = Scheduler(orchestrator=_MockOrchestrator())
        assert sched.interval_seconds == 3600

    def test_custom_interval(self):
        sched = Scheduler(interval_seconds=300, orchestrator=_MockOrchestrator())
        assert sched.interval_seconds == 300

    def test_cycles_run_starts_at_zero(self):
        sched = Scheduler(orchestrator=_MockOrchestrator())
        assert sched.cycles_run == 0

    def test_multiple_cycles(self):
        mock_orch = _MockOrchestrator()
        sched = Scheduler(interval_seconds=0, max_cycles=5, orchestrator=mock_orch)
        sched.run_forever()
        assert sched.cycles_run == 5
