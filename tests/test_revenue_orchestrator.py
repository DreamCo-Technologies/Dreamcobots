"""
Tests for dreamco/revenue_orchestrator.py — RevenueOrchestrator.
"""

from __future__ import annotations

import asyncio
import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from dreamco.revenue_orchestrator import BotInstance, RevenueOrchestrator


# ---------------------------------------------------------------------------
# BotInstance
# ---------------------------------------------------------------------------


class TestBotInstance:
    def test_defaults(self):
        bot = BotInstance(name="my_bot")
        assert bot.status == "idle"
        assert bot.profit_7d == 0.0
        assert bot.runs_total == 0

    def test_success_rate_no_runs(self):
        bot = BotInstance(name="bot")
        assert bot.success_rate == 1.0

    def test_success_rate_after_runs(self):
        bot = BotInstance(name="bot", runs_total=4, runs_success=3)
        assert abs(bot.success_rate - 0.75) < 1e-6

    def test_priority_from_known_category(self):
        bot = BotInstance(name="t", category="trading")
        # trading priority = 1 per master_config.yaml
        assert bot.priority == 1

    def test_priority_for_unknown_category(self):
        bot = BotInstance(name="x", category="unknown_xyz")
        assert bot.priority == 99


# ---------------------------------------------------------------------------
# RevenueOrchestrator construction
# ---------------------------------------------------------------------------


class TestRevenueOrchestratorInit:
    def test_instantiates(self):
        orch = RevenueOrchestrator()
        assert isinstance(orch, RevenueOrchestrator)

    def test_default_bots_registered(self):
        orch = RevenueOrchestrator()
        assert len(orch._bots) >= 1

    def test_status_returns_dict(self):
        orch = RevenueOrchestrator()
        s = orch.status()
        assert "orchestrator" in s
        assert s["orchestrator"] == "RevenueOrchestrator"
        assert "registered_bots" in s
        assert "total_profit_today_usd" in s


# ---------------------------------------------------------------------------
# Bot registration
# ---------------------------------------------------------------------------


class TestRegisterBot:
    def test_register_adds_bot(self):
        orch = RevenueOrchestrator()
        initial = len(orch._bots)
        orch.register_bot("new_bot", category="trading")
        assert len(orch._bots) == initial + 1

    def test_register_returns_instance(self):
        orch = RevenueOrchestrator()
        bot = orch.register_bot("bot_x", category="general")
        assert isinstance(bot, BotInstance)
        assert bot.name == "bot_x"

    def test_register_with_runner(self):
        orch = RevenueOrchestrator()
        runner = lambda name, task: {"revenue_usd": 10.0}
        bot = orch.register_bot("runner_bot", runner=runner)
        assert bot.runner is runner


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------


class TestRankedBots:
    def test_ranked_by_priority(self):
        orch = RevenueOrchestrator()
        orch._bots.clear()
        orch.register_bot("low_p", category="government_contracts")  # priority 4
        orch.register_bot("high_p", category="trading")              # priority 1
        ranked = orch.ranked_bots()
        assert ranked[0].name == "high_p"
        assert ranked[-1].name == "low_p"

    def test_same_priority_sorted_by_profit(self):
        orch = RevenueOrchestrator()
        orch._bots.clear()
        orch.register_bot("rich", category="general", initial_profit_7d=1000.0)
        orch.register_bot("poor", category="general", initial_profit_7d=10.0)
        ranked = orch.ranked_bots()
        assert ranked[0].name == "rich"


# ---------------------------------------------------------------------------
# Budget allocation
# ---------------------------------------------------------------------------


class TestAllocateBudgets:
    def test_total_allocated_equals_daily_budget(self):
        orch = RevenueOrchestrator()
        orch.allocate_budgets()
        total = sum(b.budget_allocated for b in orch._bots.values())
        # Allow for floating-point rounding (per_bot = budget/n, rounded to 2dp)
        daily = 200.0
        assert abs(total - daily) <= 0.10

    def test_all_bots_get_allocation(self):
        orch = RevenueOrchestrator()
        orch.allocate_budgets()
        for bot in orch._bots.values():
            assert bot.budget_allocated > 0


# ---------------------------------------------------------------------------
# run_profitable_bots (async)
# ---------------------------------------------------------------------------


class TestRunProfitableBots:
    def test_returns_list_of_results(self):
        orch = RevenueOrchestrator()
        results = asyncio.run(orch.run_profitable_bots())
        assert isinstance(results, list)
        assert len(results) == len(orch._bots)

    def test_result_keys_present(self):
        orch = RevenueOrchestrator()
        results = asyncio.run(orch.run_profitable_bots())
        for r in results:
            assert "bot_name" in r
            assert "success" in r
            assert "revenue_usd" in r

    def test_cycle_count_increments(self):
        orch = RevenueOrchestrator()
        assert orch._cycle_count == 0
        asyncio.run(orch.run_profitable_bots())
        assert orch._cycle_count == 1

    def test_runner_revenue_accumulated(self):
        orch = RevenueOrchestrator()
        orch._bots.clear()
        orch.register_bot("profit_bot", runner=lambda n, t: {"revenue_usd": 99.0})
        asyncio.run(orch.run_profitable_bots())
        assert orch.total_profit_today == 99.0

    def test_runner_error_does_not_raise(self):
        orch = RevenueOrchestrator()
        orch._bots.clear()

        def bad_runner(name, task):
            raise RuntimeError("explode")

        orch.register_bot("bad_bot", runner=bad_runner)
        results = asyncio.run(orch.run_profitable_bots())
        assert results[0]["success"] is False
        assert "error" in results[0]["result"]


# ---------------------------------------------------------------------------
# summary()
# ---------------------------------------------------------------------------


class TestSummary:
    def test_returns_list(self):
        orch = RevenueOrchestrator()
        s = orch.summary()
        assert isinstance(s, list)

    def test_contains_all_bots(self):
        orch = RevenueOrchestrator()
        s = orch.summary()
        assert len(s) == len(orch._bots)

    def test_keys_present(self):
        orch = RevenueOrchestrator()
        for entry in orch.summary():
            for key in ("name", "category", "status", "profit_7d", "priority"):
                assert key in entry
