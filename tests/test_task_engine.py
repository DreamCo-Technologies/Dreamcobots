"""Tests for TaskEngine."""

import json
import pytest
from BuddyAI.task_engine import TaskEngine, UnknownIntentError
from BuddyAI.master_registry import MasterRegistryAdapter


@pytest.fixture
def engine():
    e = TaskEngine()
    e.register_capability("greet", lambda p: {"success": True, "message": "Hello!"})
    e.register_capability(
        "echo", lambda p: {"success": True, "message": p.get("text", "")}
    )
    return e


def test_execute_known_intent(engine):
    result = engine.execute("greet", {})
    assert result["success"] is True
    assert result["message"] == "Hello!"


def test_execute_unknown_intent_raises(engine):
    with pytest.raises(UnknownIntentError):
        engine.execute("nonexistent", {})


def test_list_capabilities(engine):
    caps = engine.list_capabilities()
    assert "greet" in caps
    assert "echo" in caps


def test_register_capability(engine):
    engine.register_capability("new_cap", lambda p: {"done": True})
    result = engine.execute("new_cap", {})
    assert result["done"] is True


def test_unregister_capability(engine):
    engine.register_capability("temp", lambda p: {})
    removed = engine.unregister_capability("temp")
    assert removed is True
    with pytest.raises(UnknownIntentError):
        engine.execute("temp", {})


def test_unregister_nonexistent(engine):
    assert engine.unregister_capability("ghost") is False


def test_process_text_known(engine):
    result = engine.process_text("help")
    # 'help' intent is not registered in this minimal engine
    # so we should get an informative failure
    assert "message" in result


def test_process_text_empty(engine):
    result = engine.process_text("")
    assert result["success"] is False


def test_process_text_with_registered_intent():
    e = TaskEngine()
    e.register_capability("add_todo", lambda p: {"success": True, "message": "added"})
    result = e.process_text("Add todo write tests")
    assert result["success"] is True


def test_handler_exception_returns_error(engine):
    engine.register_capability("explode", lambda p: (_ for _ in ()).throw(RuntimeError("boom")))
    result = engine.execute("explode", {})
    assert result["success"] is False
    assert "boom" in result["error"]


def test_registry_override_disables_capability(tmp_path):
    registry_path = tmp_path / "master_bot_registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "bots": [
                    {
                        "id": "governance_bot",
                        "capabilities": [
                            {
                                "intent": "restricted",
                                "enabled": False,
                                "risk_level": "medium",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    engine = TaskEngine(registry_adapter=MasterRegistryAdapter(registry_path))
    engine.register_capability("restricted", lambda p: {"success": True})

    result = engine.execute("restricted", {"_user_id": "u1"})
    assert result["success"] is False
    assert result["denied"] is True
    assert result["stage"] == "policy"


def test_approval_required_from_registry(tmp_path):
    registry_path = tmp_path / "master_bot_registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "bots": [
                    {
                        "id": "sales_bot",
                        "capabilities": [
                            {
                                "intent": "send_email",
                                "enabled": True,
                                "approval_required": True,
                                "risk_level": "medium",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    engine = TaskEngine(registry_adapter=MasterRegistryAdapter(registry_path))
    engine.register_capability("send_email", lambda p: {"success": True, "message": "sent"})

    denied = engine.execute("send_email", {"_user_id": "u1"})
    assert denied["success"] is False
    assert denied["stage"] == "permission"

    approved = engine.execute(
        "send_email", {"_user_id": "u1", "_approved": True, "_roles": ["admin"]}
    )
    assert approved["success"] is True
    assert "_execution" in approved


def test_event_bus_audit_and_telemetry_recorded():
    engine = TaskEngine()
    engine.register_capability("gated", lambda p: {"success": True}, approval_required=True)

    denied = engine.execute("gated", {"_user_id": "u1"})
    assert denied["success"] is False

    allowed = engine.execute(
        "gated", {"_user_id": "u1", "_approved": True, "_roles": ["admin"]}
    )
    assert allowed["success"] is True

    requested_events = engine.event_bus.get_events("capability.requested")
    denied_events = engine.event_bus.get_events("capability.denied")
    started_events = engine.event_bus.get_events("capability.started")
    succeeded_events = engine.event_bus.get_events("capability.succeeded")

    assert len(requested_events) == 2
    assert len(denied_events) == 1
    assert len(started_events) == 1
    assert len(succeeded_events) == 1

    audit_log = engine.get_audit_log()
    assert len(audit_log) == 2
    assert {entry["outcome"] for entry in audit_log} == {"denied", "succeeded"}

    telemetry = engine.get_telemetry()
    assert telemetry["executions"] == 2
    assert telemetry["denials"] == 1
    assert telemetry["successes"] == 1
