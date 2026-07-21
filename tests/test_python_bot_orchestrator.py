"""
Tests for PythonBotOrchestrator in python_bots/orchestrator.py.

Test coverage:
  1. Registration and unregistration of sub-bots
  2. run_bot — success, error, not found
  3. run_all — aggregation
  4. summary and run_history
  5. Integration with LearningLoop
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

from python_bots.orchestrator import PythonBotOrchestrator
from python_bots.base_bot import BaseBot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _OKBot(BaseBot):
    """A bot that always succeeds and publishes a revenue event."""

    def run(self, event_bus) -> None:
        event_bus.publish("ok_bot.done", {"revenue": 10.0})


class _ErrorBot(BaseBot):
    """A bot that always raises."""

    def run(self, event_bus) -> None:  # noqa: ARG002
        raise RuntimeError("intentional error")


class _SilentBot(BaseBot):
    """A bot that succeeds but emits no events."""

    def run(self, event_bus) -> None:  # noqa: ARG002
        pass


# ---------------------------------------------------------------------------
# Registration / unregistration
# ---------------------------------------------------------------------------

def test_register_single_bot() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("my_bot"))
    assert "my_bot" in orch.summary()["registered_bots"]


def test_register_multiple_bots() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("bot_a"))
    orch.register(_OKBot("bot_b"))
    s = orch.summary()
    assert "bot_a" in s["registered_bots"]
    assert "bot_b" in s["registered_bots"]


def test_register_replaces_existing_bot() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("dup"))
    orch.register(_ErrorBot("dup"))
    # After replacement, running the bot should fail (ErrorBot)
    result = orch.run_bot("dup")
    assert result["success"] is False


def test_unregister_removes_bot() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("to_remove"))
    orch.unregister("to_remove")
    assert "to_remove" not in orch.summary()["registered_bots"]


def test_unregister_nonexistent_is_silent() -> None:
    orch = PythonBotOrchestrator()
    orch.unregister("ghost")  # should not raise


# ---------------------------------------------------------------------------
# run_bot — success
# ---------------------------------------------------------------------------

def test_run_bot_success_flag() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("ok"))
    result = orch.run_bot("ok")
    assert result["success"] is True
    assert result["error"] == ""


def test_run_bot_captures_events() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("ok"))
    result = orch.run_bot("ok")
    assert len(result["events"]) == 1
    assert result["events"][0]["topic"] == "ok_bot.done"


def test_run_bot_timestamps_present() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("ok"))
    result = orch.run_bot("ok")
    assert result["started_at"]
    assert result["finished_at"]


# ---------------------------------------------------------------------------
# run_bot — error
# ---------------------------------------------------------------------------

def test_run_bot_error_flag() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_ErrorBot("err"))
    result = orch.run_bot("err")
    assert result["success"] is False
    assert "intentional error" in result["error"]


def test_run_bot_error_no_events() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_ErrorBot("err"))
    result = orch.run_bot("err")
    assert result["events"] == []


# ---------------------------------------------------------------------------
# run_bot — not found
# ---------------------------------------------------------------------------

def test_run_bot_not_found_returns_failure() -> None:
    orch = PythonBotOrchestrator()
    result = orch.run_bot("nonexistent")
    assert result["success"] is False
    assert "nonexistent" in result["error"]


# ---------------------------------------------------------------------------
# run_all — aggregation
# ---------------------------------------------------------------------------

def test_run_all_empty_orchestrator() -> None:
    orch = PythonBotOrchestrator()
    summary = orch.run_all()
    assert summary["total"] == 0
    assert summary["succeeded"] == 0
    assert summary["failed"] == 0


def test_run_all_counts_correct() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("ok1"))
    orch.register(_OKBot("ok2"))
    orch.register(_ErrorBot("err1"))
    summary = orch.run_all()
    assert summary["total"] == 3
    assert summary["succeeded"] == 2
    assert summary["failed"] == 1


def test_run_all_results_list() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("a"))
    orch.register(_OKBot("b"))
    summary = orch.run_all()
    assert len(summary["results"]) == 2
    names = {r["bot_name"] for r in summary["results"]}
    assert names == {"a", "b"}


# ---------------------------------------------------------------------------
# summary and run_history
# ---------------------------------------------------------------------------

def test_summary_initial_state() -> None:
    orch = PythonBotOrchestrator()
    s = orch.summary()
    assert s["total_runs"] == 0
    assert s["total_succeeded"] == 0
    assert s["total_failed"] == 0


def test_summary_after_runs() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("ok"))
    orch.register(_ErrorBot("err"))
    orch.run_bot("ok")
    orch.run_bot("err")
    s = orch.summary()
    assert s["total_runs"] == 2
    assert s["total_succeeded"] == 1
    assert s["total_failed"] == 1


def test_run_history_grows() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("ok"))
    orch.run_bot("ok")
    orch.run_bot("ok")
    assert len(orch.run_history) == 2


def test_run_history_is_copy() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("ok"))
    orch.run_bot("ok")
    h = orch.run_history
    h.clear()
    assert len(orch.run_history) == 1  # original unchanged


# ---------------------------------------------------------------------------
# Integration with LearningLoop
# ---------------------------------------------------------------------------

class _FakeLearningLoop:
    def __init__(self) -> None:
        self.calls: list = []

    def record_run(self, bot_name: str, success: bool, revenue: float) -> None:
        self.calls.append({"bot_name": bot_name, "success": success, "revenue": revenue})


def test_learning_loop_called_on_success() -> None:
    loop = _FakeLearningLoop()
    orch = PythonBotOrchestrator(learning_loop=loop)
    orch.register(_OKBot("ok"))
    orch.run_bot("ok")
    assert len(loop.calls) == 1
    call = loop.calls[0]
    assert call["bot_name"] == "ok"
    assert call["success"] is True
    assert call["revenue"] == 10.0


def test_learning_loop_called_on_error() -> None:
    loop = _FakeLearningLoop()
    orch = PythonBotOrchestrator(learning_loop=loop)
    orch.register(_ErrorBot("err"))
    orch.run_bot("err")
    assert len(loop.calls) == 1
    assert loop.calls[0]["success"] is False
    assert loop.calls[0]["revenue"] == 0.0


def test_learning_loop_error_does_not_crash_orchestrator() -> None:
    class _BrokenLoop:
        def record_run(self, bot_name: str, success: bool, revenue: float) -> None:
            raise RuntimeError("loop broken")

    orch = PythonBotOrchestrator(learning_loop=_BrokenLoop())
    orch.register(_OKBot("ok"))
    result = orch.run_bot("ok")
    # Orchestrator should still report success
    assert result["success"] is True


def test_no_learning_loop_runs_fine() -> None:
    orch = PythonBotOrchestrator()
    orch.register(_OKBot("ok"))
    result = orch.run_bot("ok")
    assert result["success"] is True
