"""Tests for data_entry plugin."""

import pytest
from BuddyAI.task_engine import TaskEngine
from BuddyAI.plugins import data_entry


@pytest.fixture(autouse=True)
def reset_stores():
    """Clear shared data store state between tests."""
    data_entry._stores.clear()
    yield


@pytest.fixture
def engine():
    e = TaskEngine()
    data_entry.register(e)
    return e


# ------------------------------------------------------------------
# DataStore unit tests
# ------------------------------------------------------------------


def test_insert_and_list():
    store = data_entry.DataStore("test")
    r1 = store.insert({"name": "Alice", "age": "30"})
    r2 = store.insert({"name": "Bob", "age": "25"})
    assert store.count() == 2
    assert r1["_id"] == 1
    assert r2["_id"] == 2


def test_find_by_field():
    store = data_entry.DataStore("test")
    store.insert({"status": "open", "title": "task1"})
    store.insert({"status": "closed", "title": "task2"})
    results = store.find(status="open")
    assert len(results) == 1
    assert results[0]["title"] == "task1"


def test_search():
    store = data_entry.DataStore("test")
    store.insert({"name": "Alice"})
    store.insert({"name": "Bob"})
    results = store.search("ali")
    assert len(results) == 1


def test_update():
    store = data_entry.DataStore("test")
    r = store.insert({"value": "old"})
    updated = store.update(r["_id"], {"value": "new"})
    assert updated["value"] == "new"


def test_delete():
    store = data_entry.DataStore("test")
    r = store.insert({"x": 1})
    assert store.delete(r["_id"]) is True
    assert store.count() == 0


def test_csv_export_import():
    store = data_entry.DataStore("test")
    store.insert({"name": "Alice", "score": "95"})
    store.insert({"name": "Bob", "score": "80"})
    csv_text = store.to_csv()
    assert "Alice" in csv_text

    new_store = data_entry.DataStore("import")
    count = new_store.from_csv(csv_text)
    assert count == 2
    assert new_store.count() == 2


def test_csv_export_empty():
    store = data_entry.DataStore("empty")
    assert store.to_csv() == ""


# ------------------------------------------------------------------
# TaskEngine integration
# ------------------------------------------------------------------


def test_engine_insert(engine):
    result = engine.execute("data_insert", {"name": "Alice", "age": "30"})
    assert result["success"] is True
    assert result["record"]["name"] == "Alice"


def test_engine_list(engine):
    engine.execute("data_insert", {"name": "Alice"})
    result = engine.execute("data_list", {})
    assert result["success"] is True
    assert len(result["records"]) == 1


def test_engine_search(engine):
    engine.execute("data_insert", {"name": "Alice"})
    engine.execute("data_insert", {"name": "Bob"})
    result = engine.execute("data_search", {"query": "ali"})
    assert len(result["records"]) == 1


def test_engine_insert_no_data(engine):
    result = engine.execute("data_insert", {})
    assert result["success"] is False


def test_engine_export_csv(engine):
    engine.execute("data_insert", {"name": "Alice"})
    result = engine.execute("data_export_csv", {})
    assert result["success"] is True
    assert "Alice" in result["csv"]


def test_engine_import_csv(engine):
    csv_text = "name,score\nAlice,95\nBob,80\n"
    result = engine.execute("data_import_csv", {"csv": csv_text})
    assert result["success"] is True
    assert "2" in result["message"]
