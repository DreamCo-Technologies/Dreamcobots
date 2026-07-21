"""Tests for bots/control_center/controller.py"""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.control_center.controller import Controller, TaskMessage


# ---------------------------------------------------------------------------
# Simple mock bot for testing
# ---------------------------------------------------------------------------

class _MockBot:
    def __init__(self):
        self.tier = None
        self._runs = 0

    def run(self) -> str:
        self._runs += 1
        return f"mock_run_{self._runs}"

    def get_status(self) -> dict:
        return {"runs": self._runs}


class _ErrorBot:
    def run(self):
        raise RuntimeError("intentional error")


# ---------------------------------------------------------------------------
# TaskMessage
# ---------------------------------------------------------------------------

class TestTaskMessage:
    def test_creates_with_required_fields(self):
        msg = TaskMessage("sender_bot", "recipient_bot", "run")
        assert msg.sender == "sender_bot"
        assert msg.recipient == "recipient_bot"
        assert msg.action == "run"
        assert msg.payload == {}
        assert msg.created_at is not None

    def test_to_dict_contains_all_keys(self):
        msg = TaskMessage("a", "b", "run", {"key": "val"})
        d = msg.to_dict()
        for key in ("sender", "recipient", "action", "payload", "created_at"):
            assert key in d

    def test_payload_default_is_empty_dict(self):
        msg = TaskMessage("a", "b", "status")
        assert isinstance(msg.payload, dict)
        assert len(msg.payload) == 0


# ---------------------------------------------------------------------------
# Controller instantiation
# ---------------------------------------------------------------------------

class TestControllerInstantiation:
    def test_instantiates(self):
        ctrl = Controller()
        assert ctrl is not None

    def test_initial_status(self):
        ctrl = Controller()
        status = ctrl.get_status()
        assert status["controller"]["loop_count"] == 0
        assert status["controller"]["running"] is False
        assert status["control_center"]["total_bots"] == 0

    def test_initial_pending_tasks_zero(self):
        ctrl = Controller()
        assert ctrl.get_status()["controller"]["pending_tasks"] == 0


# ---------------------------------------------------------------------------
# Bot registration
# ---------------------------------------------------------------------------

class TestBotRegistration:
    def test_register_bot(self):
        ctrl = Controller()
        ctrl.register_bot("mock", _MockBot())
        status = ctrl.get_status()
        assert status["control_center"]["total_bots"] == 1

    def test_register_multiple_bots(self):
        ctrl = Controller()
        ctrl.register_bot("bot1", _MockBot())
        ctrl.register_bot("bot2", _MockBot())
        assert ctrl.get_status()["control_center"]["total_bots"] == 2


# ---------------------------------------------------------------------------
# Task assignment & processing
# ---------------------------------------------------------------------------

class TestTaskAssignment:
    def test_assign_task_adds_to_queue(self):
        ctrl = Controller()
        ctrl.register_bot("mock", _MockBot())
        msg = ctrl.assign_task("mock", "run")
        assert isinstance(msg, TaskMessage)
        assert ctrl.get_status()["controller"]["pending_tasks"] == 1

    def test_process_tasks_drains_queue(self):
        ctrl = Controller()
        ctrl.register_bot("mock", _MockBot())
        ctrl.assign_task("mock", "run")
        ctrl.process_tasks()
        assert ctrl.get_status()["controller"]["pending_tasks"] == 0

    def test_process_task_run_action(self):
        ctrl = Controller()
        ctrl.register_bot("mock", _MockBot())
        ctrl.assign_task("mock", "run")
        results = ctrl.process_tasks()
        assert len(results) == 1
        assert results[0]["status"] == "ok"

    def test_process_task_status_action(self):
        ctrl = Controller()
        ctrl.register_bot("mock", _MockBot())
        ctrl.assign_task("mock", "status")
        results = ctrl.process_tasks()
        assert results[0]["status"] == "ok"

    def test_process_task_unknown_bot(self):
        ctrl = Controller()
        ctrl.assign_task("nonexistent_bot", "run")
        results = ctrl.process_tasks()
        assert results[0]["status"] == "error"
        assert "not registered" in results[0]["error"]

    def test_process_task_error_bot(self):
        ctrl = Controller()
        ctrl.register_bot("error_bot", _ErrorBot())
        ctrl.assign_task("error_bot", "run")
        results = ctrl.process_tasks()
        assert results[0]["status"] == "error"

    def test_broadcast_task_targets_all_bots(self):
        ctrl = Controller()
        ctrl.register_bot("bot1", _MockBot())
        ctrl.register_bot("bot2", _MockBot())
        msgs = ctrl.broadcast_task("run")
        assert len(msgs) == 2
        recipients = {m.recipient for m in msgs}
        assert "bot1" in recipients
        assert "bot2" in recipients


# ---------------------------------------------------------------------------
# Inter-bot messaging
# ---------------------------------------------------------------------------

class TestInterBotMessaging:
    def test_send_message_ok(self):
        ctrl = Controller()
        ctrl.register_bot("target", _MockBot())
        result = ctrl.send_message("sender", "target", "run")
        assert result["status"] == "ok"

    def test_send_message_logged(self):
        ctrl = Controller()
        ctrl.register_bot("target", _MockBot())
        ctrl.send_message("sender", "target", "run")
        log = ctrl.get_message_log()
        assert len(log) == 1
        assert log[0]["sender"] == "sender"
        assert log[0]["recipient"] == "target"

    def test_send_message_to_unknown_bot(self):
        ctrl = Controller()
        result = ctrl.send_message("a", "ghost", "run")
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# Automation loop
# ---------------------------------------------------------------------------

class TestAutomationLoop:
    def test_run_loop_one_iteration(self):
        ctrl = Controller()
        ctrl.register_bot("mock", _MockBot())
        results = ctrl.run_loop(iterations=1)
        assert len(results) == 1
        assert results[0]["cycle"] == 1

    def test_run_loop_increments_loop_count(self):
        ctrl = Controller()
        ctrl.register_bot("mock", _MockBot())
        ctrl.run_loop(iterations=3)
        assert ctrl.get_status()["controller"]["loop_count"] == 3

    def test_run_loop_returns_bot_results(self):
        ctrl = Controller()
        ctrl.register_bot("mock", _MockBot())
        results = ctrl.run_loop(iterations=1)
        assert "bot_results" in results[0]
        assert "mock" in results[0]["bot_results"]

    def test_run_loop_no_bots(self):
        ctrl = Controller()
        results = ctrl.run_loop(iterations=1)
        assert len(results) == 1
        assert results[0]["bot_results"] == {}

    def test_stop_sets_running_false(self):
        ctrl = Controller()
        ctrl.stop()
        assert ctrl.get_status()["controller"]["running"] is False


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class TestDashboard:
    def test_get_dashboard_returns_dict(self):
        ctrl = Controller()
        dash = ctrl.get_dashboard()
        assert isinstance(dash, dict)
        assert "dashboard" in dash
