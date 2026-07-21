"""Tests for productivity plugin."""

import pytest
from BuddyAI.task_engine import TaskEngine
from BuddyAI.plugins import productivity


@pytest.fixture(autouse=True)
def reset_todo_list():
    """Reset shared todo list state between tests."""
    productivity._todo_list = productivity.TodoList()
    productivity._workflow_queue = productivity.WorkflowQueue()
    yield


@pytest.fixture
def engine():
    e = TaskEngine()
    productivity.register(e)
    return e


# ------------------------------------------------------------------
# TodoList unit tests
# ------------------------------------------------------------------


def test_add_and_list():
    tl = productivity.TodoList()
    tl.add("buy milk")
    tl.add("write tests")
    items = tl.list_items()
    assert len(items) == 2
    assert items[0]["text"] == "buy milk"
    assert items[1]["text"] == "write tests"
    assert all(not i["done"] for i in items)


def test_complete_by_id():
    tl = productivity.TodoList()
    item = tl.add("task A")
    completed = tl.complete(item["id"])
    assert completed is not None
    assert completed["done"] is True


def test_complete_by_text():
    tl = productivity.TodoList()
    tl.add("buy groceries")
    completed = tl.complete("groceries")
    assert completed is not None
    assert completed["done"] is True


def test_complete_nonexistent():
    tl = productivity.TodoList()
    assert tl.complete("nothing") is None


def test_clear_all():
    tl = productivity.TodoList()
    tl.add("a")
    tl.add("b")
    removed = tl.clear()
    assert removed == 2
    assert tl.list_items() == []


def test_clear_done_only():
    tl = productivity.TodoList()
    a = tl.add("a")
    tl.add("b")
    tl.complete(a["id"])
    removed = tl.clear(done_only=True)
    assert removed == 1
    assert len(tl.list_items()) == 1


# ------------------------------------------------------------------
# WorkflowQueue unit tests
# ------------------------------------------------------------------


def test_workflow_queue():
    wq = productivity.WorkflowQueue()
    wq.enqueue("step 1")
    wq.enqueue("step 2")
    assert wq.peek() == "step 1"
    assert wq.dequeue() == "step 1"
    assert wq.dequeue() == "step 2"
    assert wq.dequeue() is None


# ------------------------------------------------------------------
# TaskEngine integration
# ------------------------------------------------------------------


def test_engine_add_todo(engine):
    result = engine.execute("add_todo", {"item": "buy milk"})
    assert result["success"] is True
    assert "buy milk" in result["message"]


def test_engine_list_todos_empty(engine):
    result = engine.execute("list_todos", {})
    assert result["success"] is True
    assert result["items"] == []


def test_engine_add_and_list(engine):
    engine.execute("add_todo", {"item": "task one"})
    result = engine.execute("list_todos", {})
    assert len(result["items"]) == 1


def test_engine_complete_todo(engine):
    engine.execute("add_todo", {"item": "do laundry"})
    result = engine.execute("complete_todo", {"item": "laundry"})
    assert result["success"] is True


def test_engine_add_todo_no_text(engine):
    result = engine.execute("add_todo", {"item": ""})
    assert result["success"] is False


def test_engine_help(engine):
    result = engine.execute("help", {})
    assert result["success"] is True
    assert len(result["message"]) > 0
