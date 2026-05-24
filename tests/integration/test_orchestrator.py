"""
DreamCo OS — Integration Tests: Orchestrator + Memory
"""

import asyncio
import pytest
from python_bots.core.base_bot import DreamCoBot
from python_bots.core.lifecycle import BotState
from python_bots.orchestrator import DreamCoOrchestrator


class EchoBot(DreamCoBot):
    async def run(self): return {"echo": "pong", "config": self.config}
    async def analyze(self): return {"analyzed": True}
    async def monetize(self): return {"revenue": 0.01}
    async def report(self): return {"runs": self.memory.structured.get_run_history(3)}


class CounterBot(DreamCoBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_count = 0

    async def run(self):
        self.run_count += 1
        return {"count": self.run_count}

    async def analyze(self): return {}
    async def monetize(self): return {}
    async def report(self): return {}


class AlwaysFailBot(DreamCoBot):
    async def run(self): raise RuntimeError("Always fails")
    async def analyze(self): return {}
    async def monetize(self): return {}
    async def report(self): return {}


class TestOrchestrator:
    @pytest.mark.asyncio
    async def test_register_and_dispatch(self):
        orch = DreamCoOrchestrator()
        bot = EchoBot("echo")
        orch.register(bot)
        result = await orch.dispatch("echo")
        assert result["success"] is True
        assert result["result"]["echo"] == "pong"

    @pytest.mark.asyncio
    async def test_dispatch_unknown_bot_returns_error(self):
        orch = DreamCoOrchestrator()
        result = await orch.dispatch("nonexistent")
        assert result["success"] is False
        assert "not registered" in result["error"]

    @pytest.mark.asyncio
    async def test_kill_switch_prevents_execution(self):
        orch = DreamCoOrchestrator()
        bot = EchoBot("killable")
        orch.register(bot)
        orch.kill("killable")
        result = await orch.dispatch("killable")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_run_all_runs_all_bots(self):
        orch = DreamCoOrchestrator(max_concurrent=5)
        for i in range(3):
            orch.register(EchoBot(f"echo_{i}"))
        results = await orch.run_all()
        assert results["total"] == 3
        assert results["succeeded"] == 3

    @pytest.mark.asyncio
    async def test_dag_ordering(self):
        orch = DreamCoOrchestrator()
        execution_order = []

        class OrderedBot(DreamCoBot):
            def __init__(self, name, order_list, **kwargs):
                super().__init__(name, **kwargs)
                self._order = order_list
            async def run(self):
                self._order.append(self.name)
                return {"order": len(self._order)}
            async def analyze(self): return {}
            async def monetize(self): return {}
            async def report(self): return {}

        bot_a = OrderedBot("a", execution_order)
        bot_b = OrderedBot("b", execution_order)
        orch.register(bot_a)
        orch.register(bot_b)
        # b depends on a
        await orch.run_all(dag={"a": [], "b": ["a"]})
        assert execution_order.index("a") < execution_order.index("b")

    @pytest.mark.asyncio
    async def test_circuit_breaker_quarantines_failing_bot(self):
        orch = DreamCoOrchestrator()
        bot = AlwaysFailBot("fail_bot", max_retries=1)
        orch.register(bot)
        await orch.dispatch("fail_bot")
        assert bot.state == BotState.QUARANTINED

    @pytest.mark.asyncio
    async def test_retry_with_eventual_success(self):
        orch = DreamCoOrchestrator()
        bot = EchoBot("retry_echo")
        orch.register(bot)
        result = await orch.dispatch_with_retry("retry_echo", max_attempts=3, base_delay=0.01)
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_human_in_the_loop_pending(self):
        orch = DreamCoOrchestrator()
        bot = EchoBot("approval_bot")
        orch.register(bot)
        result = await orch.dispatch("approval_bot", requires_approval=True)
        assert result["status"] == "pending_approval"
        task_id = result["task_id"]
        assert task_id in orch.pending_approvals

    @pytest.mark.asyncio
    async def test_approve_and_execute(self):
        orch = DreamCoOrchestrator()
        bot = EchoBot("approve_me")
        orch.register(bot)
        pend_result = await orch.dispatch("approve_me", requires_approval=True)
        approved = await orch.approve_task(pend_result["task_id"])
        assert approved["success"] is True

    @pytest.mark.asyncio
    async def test_broadcast_to_all_bots(self):
        received = []

        class BroadcastBot(DreamCoBot):
            def __init__(self, name, log):
                super().__init__(name)
                self._log = log
            async def on_broadcast(self, msg): self._log.append(msg)
            async def run(self): return {}
            async def analyze(self): return {}
            async def monetize(self): return {}
            async def report(self): return {}

        orch = DreamCoOrchestrator()
        orch.register(BroadcastBot("b1", received))
        orch.register(BroadcastBot("b2", received))
        await orch.broadcast({"msg": "system_alert"})
        assert len(received) == 2

    def test_summary(self):
        orch = DreamCoOrchestrator()
        bot = EchoBot("summary_bot")
        orch.register(bot)
        s = orch.summary()
        assert "summary_bot" in s["registered_bots"]
        assert "dead_letter_count" in s
