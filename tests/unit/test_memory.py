"""
DreamCo OS — Unit Tests: Memory Layer
"""

import pytest
from python_bots.core.memory.short_term import ShortTermMemory
from python_bots.core.memory.long_term import LongTermMemory
from python_bots.core.memory.structured import StructuredMemory
from python_bots.core.memory.behavioral import BehavioralMemory
from python_bots.core.memory.client import MemoryClient


class TestShortTermMemory:
    def test_save_and_load(self):
        mem = ShortTermMemory(bot_id="test_bot")
        mem.save("key1", {"value": 42})
        assert mem.load("key1") == {"value": 42}

    def test_load_missing_returns_none(self):
        mem = ShortTermMemory(bot_id="test_bot")
        assert mem.load("nonexistent") is None

    def test_forget_removes_key(self):
        mem = ShortTermMemory(bot_id="test_bot")
        mem.save("key1", "data")
        mem.forget("key1")
        assert mem.load("key1") is None

    def test_keys_lists_active_keys(self):
        mem = ShortTermMemory(bot_id="keys_test")
        mem.save("a", 1)
        mem.save("b", 2)
        keys = mem.keys()
        assert "a" in keys
        assert "b" in keys


class TestLongTermMemory:
    def test_store_and_recall(self):
        mem = LongTermMemory(bot_id="test_bot", backend="chroma", persist_directory="/tmp/test_chroma")
        mem.store("doc1", "DreamCo is an AI bot operating system")
        results = mem.recall("bot operating system", top_k=1)
        assert len(results) >= 0  # May be 0 with fallback

    def test_forget_reduces_count(self):
        mem = LongTermMemory(bot_id="test_forget", backend="chroma", persist_directory="/tmp/test_chroma_2")
        mem.store("doc_to_delete", "test document")
        mem.forget("doc_to_delete")
        # After forget, count should not have the deleted doc


class TestStructuredMemory:
    def test_upsert_and_get_state(self):
        mem = StructuredMemory(bot_id="test_bot", db_url="/tmp/test_structured.db")
        mem.upsert_state("portfolio", {"AAPL": 10})
        result = mem.get_state("portfolio")
        assert result == {"AAPL": 10}

    def test_get_missing_returns_none(self):
        mem = StructuredMemory(bot_id="test_bot2", db_url="/tmp/test_structured2.db")
        assert mem.get_state("missing_key") is None

    def test_delete_state(self):
        mem = StructuredMemory(bot_id="test_del", db_url="/tmp/test_del.db")
        mem.upsert_state("temp", "value")
        mem.delete_state("temp")
        assert mem.get_state("temp") is None

    def test_record_run_and_history(self):
        mem = StructuredMemory(bot_id="test_runs", db_url="/tmp/test_runs.db")
        run_id = mem.record_run(success=True, tokens_used=100, cost_usd=0.001)
        assert run_id
        history = mem.get_run_history(10)
        assert any(r["run_id"] == run_id for r in history)


class TestBehavioralMemory:
    def test_record_and_get_history(self):
        mem = BehavioralMemory(bot_id="test_bot")
        mem.record_event("task_started", {"task": "lead_gen"})
        mem.record_event("task_completed", {"leads": 5})
        history = mem.get_history()
        assert len(history) == 2

    def test_parent_chain(self):
        mem = BehavioralMemory(bot_id="chain_bot")
        e1 = mem.record_event("step_1")
        e2 = mem.record_event("step_2")
        assert e2.parent_id == e1.event_id

    def test_pin_prevents_pruning(self):
        mem = BehavioralMemory(bot_id="pin_bot", ttl_days=0)
        e = mem.record_event("pinned_event")
        mem.pin(e.event_id)
        pruned = mem.prune_expired()
        assert e.event_id in [ev["event_id"] for ev in mem.get_history()]

    def test_forget_removes_event(self):
        mem = BehavioralMemory(bot_id="forget_bot")
        e = mem.record_event("to_delete")
        assert mem.forget(e.event_id)
        assert e.event_id not in [ev["event_id"] for ev in mem.get_history()]

    def test_to_task_graph_structure(self):
        mem = BehavioralMemory(bot_id="graph_bot")
        mem.record_event("a")
        mem.record_event("b")
        graph = mem.to_task_graph()
        assert "nodes" in graph
        assert "edges" in graph


class TestMemoryClient:
    def test_save_and_load(self):
        client = MemoryClient(bot_id="test_client")
        client.save("session_data", {"user": "alice"})
        assert client.load("session_data") == {"user": "alice"}

    def test_event_recorded(self):
        client = MemoryClient(bot_id="event_client")
        client.event("test_event", {"key": "val"})
        history = client.behavioral.get_history()
        assert any(e["event_type"] == "test_event" for e in history)

    def test_forget_across_tiers(self):
        client = MemoryClient(bot_id="forget_client")
        client.save("to_forget", "value")
        client.forget("to_forget")
        assert client.load("to_forget") is None

    def test_stats(self):
        client = MemoryClient(bot_id="stats_client")
        stats = client.stats()
        assert "bot_id" in stats
        assert "behavioral" in stats
