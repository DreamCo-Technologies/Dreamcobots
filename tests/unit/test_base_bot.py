"""
DreamCo OS — Unit Tests: Core Base Bot
"""

import asyncio
import pytest
from python_bots.core.base_bot import DreamCoBot
from python_bots.core.lifecycle import BotState, IllegalStateTransitionError


class MinimalBot(DreamCoBot):
    async def run(self): return {"status": "ok"}
    async def analyze(self): return {"analyzed": True}
    async def monetize(self): return {"revenue": 0.0}
    async def report(self): return {"report": "ok"}


class FailingBot(DreamCoBot):
    async def run(self): raise ValueError("Intentional failure")
    async def analyze(self): return {}
    async def monetize(self): return {}
    async def report(self): return {}


class TestDreamCoBot:
    def test_initial_state_is_idle(self):
        bot = MinimalBot("test")
        assert bot.state == BotState.IDLE

    def test_health_check_returns_dict(self):
        bot = MinimalBot("test")
        h = bot.health_check()
        assert h["state"] == "IDLE"
        assert "bot_id" in h
        assert "name" in h

    def test_capability_whitelist_empty_means_all_allowed(self):
        bot = MinimalBot("test", capabilities=[])
        assert bot.can_use("any_tool")

    def test_capability_whitelist_enforced(self):
        bot = MinimalBot("test", capabilities=["web_search"])
        assert bot.can_use("web_search")
        assert not bot.can_use("file_write")

    def test_assert_can_use_raises_permission_error(self):
        bot = MinimalBot("test", capabilities=["web_search"])
        with pytest.raises(PermissionError):
            bot.assert_can_use("file_write")

    @pytest.mark.asyncio
    async def test_execute_transitions_to_idle_on_success(self):
        bot = MinimalBot("test")
        result = await bot.execute()
        assert result["success"] is True
        assert bot.state == BotState.IDLE

    @pytest.mark.asyncio
    async def test_execute_increments_error_count_on_failure(self):
        bot = FailingBot("fail_bot", max_retries=5)
        result = await bot.execute()
        assert result["success"] is False
        assert bot._error_count == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_quarantines_after_max_retries(self):
        bot = FailingBot("fail_bot", max_retries=1)
        result = await bot.execute()
        assert bot.state == BotState.QUARANTINED

    @pytest.mark.asyncio
    async def test_stopped_bot_returns_error(self):
        bot = MinimalBot("test")
        bot.stop()
        result = await bot.execute()
        assert result["success"] is False
        assert "STOPPED" in result["error"]

    @pytest.mark.asyncio
    async def test_quarantined_bot_returns_error(self):
        bot = FailingBot("fail_bot", max_retries=1)
        await bot.execute()  # quarantine it
        result = await bot.execute()
        assert result["success"] is False
        assert "QUARANTINED" in result["error"]

    def test_stop_and_restart(self):
        bot = MinimalBot("test")
        bot.stop()
        assert bot.state == BotState.STOPPED
        bot.restart()
        assert bot.state == BotState.IDLE

    def test_repr(self):
        bot = MinimalBot("test")
        assert "MinimalBot" in repr(bot)
        assert "IDLE" in repr(bot)
