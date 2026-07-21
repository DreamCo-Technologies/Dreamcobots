"""Tests for TextHandler."""

import pytest
from BuddyAI.text_handler import TextHandler, ParsedCommand


@pytest.fixture
def handler():
    return TextHandler()


def test_add_todo(handler):
    cmd = handler.parse("Add todo buy groceries")
    assert cmd.intent == "add_todo"
    assert "buy groceries" in cmd.params["item"]


def test_list_todos(handler):
    cmd = handler.parse("List my todos")
    assert cmd.intent == "list_todos"


def test_complete_todo(handler):
    cmd = handler.parse("Complete buy groceries")
    assert cmd.intent == "complete_todo"
    assert "buy groceries" in cmd.params["item"]


def test_schedule_task(handler):
    cmd = handler.parse("Schedule meeting at 3pm")
    assert cmd.intent == "schedule_task"
    assert "meeting" in cmd.params["task"]
    assert "3pm" in cmd.params["when"]


def test_set_reminder(handler):
    cmd = handler.parse("Remind me to call John at 5pm")
    assert cmd.intent == "set_reminder"
    assert "call John" in cmd.params["message"]


def test_fetch_api(handler):
    cmd = handler.parse("Fetch data from https://api.example.com/data")
    assert cmd.intent == "fetch_api"
    assert "https://api.example.com/data" in cmd.params["url"]


def test_search(handler):
    cmd = handler.parse("Search for Python tutorials")
    assert cmd.intent == "search"
    assert "Python tutorials" in cmd.params["query"]


def test_install_library(handler):
    cmd = handler.parse("Install library requests")
    assert cmd.intent == "install_library"
    assert cmd.params["package"] == "requests"


def test_benchmark(handler):
    cmd = handler.parse("Benchmark my todo list function")
    assert cmd.intent == "benchmark"


def test_help(handler):
    cmd = handler.parse("help")
    assert cmd.intent == "help"


def test_unknown_intent(handler):
    cmd = handler.parse("xyzzy plugh")
    assert cmd.intent == "unknown"
    assert cmd.confidence == 0.0


def test_empty_string(handler):
    cmd = handler.parse("")
    assert cmd.intent == "unknown"
    assert cmd.confidence == 0.0


def test_raw_text_preserved(handler):
    text = "Add todo something important"
    cmd = handler.parse(text)
    assert cmd.raw_text == text


def test_extract_entities_time(handler):
    entities = handler.extract_entities("Remind me at 3pm to water the plants")
    assert "time" in entities
    assert "3pm" in entities["time"].lower()


def test_extract_entities_date(handler):
    entities = handler.extract_entities("Schedule meeting for tomorrow")
    assert "date" in entities
    assert "tomorrow" in entities["date"].lower()


def test_extract_entities_url(handler):
    entities = handler.extract_entities("Fetch data from https://example.com/api")
    assert "url" in entities
    assert entities["url"] == "https://example.com/api"
