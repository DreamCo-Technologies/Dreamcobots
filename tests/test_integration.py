"""Integration tests for BuddyBot."""

import pytest
from BuddyAI.buddy_bot import BuddyBot
from BuddyAI.plugins import productivity


@pytest.fixture
def buddy():
    """Provide a started BuddyBot instance, reset plugin state each test."""
    productivity._todo_list = productivity.TodoList()
    productivity._workflow_queue = productivity.WorkflowQueue()

    from BuddyAI.plugins import data_entry
    data_entry._stores.clear()

    bot = BuddyBot(enable_scheduler=False)
    bot.start()
    yield bot
    bot.stop()


def test_buddy_starts_and_stops():
    bot = BuddyBot(enable_scheduler=False)
    bot.start()
    assert bot._running is True
    bot.stop()
    assert bot._running is False


def test_chat_help(buddy):
    response = buddy.chat("help")
    assert response["success"] is True
    assert len(response["message"]) > 10


def test_chat_add_todo(buddy):
    response = buddy.chat("Add todo buy groceries")
    assert response["success"] is True
    assert "buy groceries" in response["message"].lower()


def test_chat_list_todos(buddy):
    buddy.chat("Add todo task one")
    buddy.chat("Add todo task two")
    response = buddy.chat("List my todos")
    assert response["success"] is True
    assert len(response["items"]) == 2


def test_chat_complete_todo(buddy):
    buddy.chat("Add todo write tests")
    response = buddy.chat("Complete write tests")
    assert response["success"] is True


def test_chat_unknown_command(buddy):
    response = buddy.chat("xyzzy plugh frobozz")
    assert response["success"] is False
    assert "message" in response


def test_chat_empty_input(buddy):
    response = buddy.chat("")
    assert response["success"] is False


def test_event_bus_receives_events(buddy):
    events = []
    buddy.event_bus.subscribe("buddy.input.text", lambda d: events.append(d))
    buddy.chat("help")
    assert len(events) == 1
    assert events[0]["text"] == "help"


def test_benchmark_task(buddy):
    result = buddy.benchmark_task("help", iterations=3)
    assert result["success"] is True
    assert "benchmark" in result
    assert result["benchmark"]["iterations"] == 3


def test_install_capability_blocked_package(buddy):
    result = buddy.install_capability("os")
    assert result["success"] is False


def test_capabilities_registered(buddy):
    caps = buddy.task_engine.list_capabilities()
    for expected in ["add_todo", "list_todos", "complete_todo", "help",
                     "fetch_api", "data_insert", "install_library"]:
        assert expected in caps, f"Missing capability: {expected}"
