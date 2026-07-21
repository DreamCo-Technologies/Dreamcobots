"""Tests for shared core modules."""
import pytest

from core.bot_base import AbstractBotBase as BotBase, BotStatus
from core.revenue_engine import RevenueEngine
from core.crash_guard import crash_guard, safe_run
from core.monetization_hooks import MonetizationHooks
from core.dream_core import DreamCore


# ---------------------------------------------------------------------------
# BotBase tests
# ---------------------------------------------------------------------------

class ConcreteBot(BotBase):
    """Minimal concrete bot for testing BotBase lifecycle."""

    def __init__(self):
        super().__init__(name="TestBot")
        self.started = False
        self.stopped = False
        self.executed = False

    def on_start(self):
        self.started = True

    def on_stop(self):
        self.stopped = True

    def execute(self):
        self.executed = True


class ErrorBot(BotBase):
    def __init__(self):
        super().__init__(name="ErrorBot")

    def on_start(self): pass
    def on_stop(self): pass
    def execute(self):
        raise ValueError("boom")


class TestBotBase:
    def test_initial_status_is_idle(self):
        bot = ConcreteBot()
        assert bot.status == BotStatus.IDLE

    def test_start_transitions_to_running(self):
        bot = ConcreteBot()
        bot.start()
        assert bot.status == BotStatus.RUNNING
        assert bot.started is True

    def test_stop_transitions_to_stopped(self):
        bot = ConcreteBot()
        bot.start()
        bot.stop()
        assert bot.status == BotStatus.STOPPED
        assert bot.stopped is True

    def test_run_full_lifecycle(self):
        bot = ConcreteBot()
        bot.run()
        assert bot.started
        assert bot.executed
        assert bot.stopped
        assert bot.status == BotStatus.STOPPED

    def test_run_sets_error_on_exception(self):
        bot = ErrorBot()
        with pytest.raises(ValueError):
            bot.run()
        assert bot.status == BotStatus.ERROR


# ---------------------------------------------------------------------------
# RevenueEngine tests
# ---------------------------------------------------------------------------

class TestRevenueEngine:
    def test_record_and_total(self):
        engine = RevenueEngine()
        engine.record("test_source", 50.0)
        assert engine.total() == 50.0

    def test_multiple_records(self):
        engine = RevenueEngine()
        engine.record("s1", 25.0)
        engine.record("s2", 75.0)
        assert engine.total() == 100.0

    def test_currency_filter(self):
        engine = RevenueEngine()
        engine.record("usd_source", 100.0, currency="USD")
        engine.record("eur_source", 50.0, currency="EUR")
        assert engine.total("USD") == 100.0
        assert engine.total("EUR") == 50.0

    def test_report_returns_all_entries(self):
        engine = RevenueEngine()
        engine.record("a", 10.0)
        engine.record("b", 20.0)
        report = engine.report()
        assert len(report) == 2

    def test_reset_clears_entries(self):
        engine = RevenueEngine()
        engine.record("src", 99.0)
        engine.reset()
        assert engine.total() == 0.0
        assert engine.report() == []


# ---------------------------------------------------------------------------
# CrashGuard tests
# ---------------------------------------------------------------------------

class TestCrashGuard:
    def test_crash_guard_decorator_swallows_exception(self):
        @crash_guard
        def risky():
            raise RuntimeError("oops")

        result = risky()
        assert result is None

    def test_crash_guard_decorator_returns_value_on_success(self):
        @crash_guard
        def safe():
            return 42

        assert safe() == 42

    def test_safe_run_context_manager_swallows_exception(self):
        executed = []
        with safe_run("test_op"):
            raise ValueError("context error")
        # No exception propagated; test reaches here

    def test_safe_run_executes_body_on_success(self):
        result = []
        with safe_run("ok_op"):
            result.append(1)
        assert result == [1]


# ---------------------------------------------------------------------------
# MonetizationHooks tests
# ---------------------------------------------------------------------------

class TestMonetizationHooks:
    def test_track_records_stage(self):
        hooks = MonetizationHooks()
        hooks.track("gig_started", {"id": 1})
        report = hooks.funnel_report()
        assert len(report) == 1
        assert report[0]["stage"] == "gig_started"

    def test_on_stage_callback_fires(self):
        hooks = MonetizationHooks()
        fired = []
        hooks.on_stage("purchase", lambda e: fired.append(e))
        hooks.track("purchase", {"amount": 25})
        assert len(fired) == 1

    def test_conversion_rate_calculation(self):
        hooks = MonetizationHooks()
        hooks.track("lead")
        hooks.track("lead")
        hooks.track("purchase")
        rate = hooks.conversion_rate("lead", "purchase")
        assert rate == 0.5

    def test_conversion_rate_zero_denominator(self):
        hooks = MonetizationHooks()
        rate = hooks.conversion_rate("nonexistent", "also_nonexistent")
        assert rate == 0.0

    def test_reset_clears_funnel(self):
        hooks = MonetizationHooks()
        hooks.track("step1")
        hooks.reset()
        assert hooks.funnel_report() == []


# ---------------------------------------------------------------------------
# DreamCore tests
# ---------------------------------------------------------------------------

class TestDreamCore:
    def test_generate_email_structure(self):
        dc = DreamCore()
        email = dc.generate_email("Alice", "Hello", "Test body")
        assert email["to"] == "Alice"
        assert email["subject"] == "Hello"
        assert "Alice" in email["body"]
        assert "Test body" in email["body"]

    def test_generate_lead_outreach(self):
        dc = DreamCore()
        lead = {"name": "Bob", "email": "bob@example.com"}
        email = dc.generate_lead_outreach(lead)
        assert email["to"] == "Bob"
        assert "DreamCo" in email["subject"] or "Opportunity" in email["subject"]

    def test_generate_lead_outreach_missing_name(self):
        dc = DreamCore()
        email = dc.generate_lead_outreach({"email": "no-name@example.com"})
        assert "there" in email["body"] or email["to"] == "there"
