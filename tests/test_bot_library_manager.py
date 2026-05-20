"""Tests for bots.bot_library_manager.library_manager.BotLibraryManager."""

from bots.bot_library_manager.library_manager import BotLibraryManager


class _DummyFlow:
    def __init__(self):
        self.calls = []

    def run_pipeline(self, raw_data=None, learning_method="supervised"):
        self.calls.append({"raw_data": raw_data, "learning_method": learning_method})
        return {"pipeline_complete": True}


def test_register_and_summary_triggers_flow_pipeline():
    manager = BotLibraryManager(db_path=":memory:")
    dummy_flow = _DummyFlow()
    manager.flow = dummy_flow

    manager.register_library("bot.one", "requests", category="http")
    summary = manager.get_library_summary("bot.one")

    assert summary["bot_id"] == "bot.one"
    assert any(call["raw_data"]["action"] == "register_library" for call in dummy_flow.calls)
    assert any(call["raw_data"]["action"] == "get_library_summary" for call in dummy_flow.calls)
    manager.close()


def test_update_mastery_and_store_learning_triggers_flow_pipeline():
    manager = BotLibraryManager(db_path=":memory:")
    dummy_flow = _DummyFlow()
    manager.flow = dummy_flow

    manager.register_library("bot.two", "numpy", category="ml")
    manager.update_mastery("bot.two", "numpy", 88.5)
    manager.store_learning(
        "bot.two",
        "numeric_performance",
        "Vectorized paths reduce processing time",
        source="docs",
        relevance_score=92.0,
    )

    actions = [call["raw_data"]["action"] for call in dummy_flow.calls]
    assert "update_mastery" in actions
    assert "store_learning" in actions
    manager.close()
