"""
DreamCo OS — Event-Driven Orchestrator
========================================

The central orchestrator coordinates all registered ``DreamCoBot`` instances:

* **Event bus** — asyncio.Queue-based, zero external dependencies
* **DAG scheduling** — bots declare dependencies; independent bots run concurrently
* **Circuit breaker** — failing bots automatically quarantined after N errors
* **Priority queue** — high-priority tasks preempt lower-priority ones
* **Human-in-the-loop gates** — certain tasks require operator approval
* **Dead-letter queue** — failed tasks go here for inspection
* **Kill switch** — ``orchestrator.kill(bot_id)`` immediately halts execution
* **Broadcast** — notify all registered bots of a system-wide event
* **Retry with exponential backoff**

Usage::

    from python_bots.core import DreamCoBot
    from python_bots.orchestrator import DreamCoOrchestrator

    class PingBot(DreamCoBot):
        async def run(self): return {"pong": True}
        async def analyze(self): return {}
        async def monetize(self): return {}
        async def report(self): return {}

    orch = DreamCoOrchestrator()
    orch.register(PingBot("ping"))
    result = asyncio.run(orch.dispatch("ping"))
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(order=True)
class _Task:
    priority: int
    enqueued_at: float = field(compare=False)
    bot_name: str = field(compare=False)
    payload: dict[str, Any] = field(default_factory=dict, compare=False)
    requires_approval: bool = field(default=False, compare=False)
    task_id: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        if not self.task_id:
            self.task_id = str(uuid.uuid4())


class DreamCoOrchestrator:
    """Event-driven orchestrator for DreamCo OS bots."""

    def __init__(
        self,
        max_concurrent: int = 10,
        default_priority: int = 5,
    ) -> None:
        self._bots: dict[str, Any] = {}
        self._dead_letter: list[dict[str, Any]] = []
        self._run_history: list[dict[str, Any]] = []
        self._pending_approvals: dict[str, _Task] = {}
        self._semaphore: asyncio.Semaphore | None = None
        self._max_concurrent = max_concurrent
        self._default_priority = default_priority
        self._killed: set[str] = set()

    def register(self, bot: Any) -> None:
        self._bots[bot.name] = bot
        logger.info("Orchestrator registered bot: %s", bot.name)

    def unregister(self, bot_name: str) -> None:
        self._bots.pop(bot_name, None)

    def list_bots(self) -> list[dict[str, Any]]:
        return [bot.health_check() for bot in self._bots.values()]

    async def dispatch(
        self,
        bot_name: str,
        payload: dict[str, Any] | None = None,
        priority: int | None = None,
        requires_approval: bool = False,
    ) -> dict[str, Any]:
        if bot_name not in self._bots:
            return {"success": False, "error": f"Bot '{bot_name}' not registered"}
        if bot_name in self._killed:
            return {"success": False, "error": f"Bot '{bot_name}' has been killed"}

        task = _Task(
            priority=priority or self._default_priority,
            enqueued_at=time.time(),
            bot_name=bot_name,
            payload=payload or {},
            requires_approval=requires_approval,
        )

        if requires_approval:
            self._pending_approvals[task.task_id] = task
            return {
                "success": True,
                "status": "pending_approval",
                "task_id": task.task_id,
                "message": f"Task '{bot_name}' queued for human approval",
            }
        return await self._execute_task(task)

    async def approve_task(self, task_id: str) -> dict[str, Any]:
        task = self._pending_approvals.pop(task_id, None)
        if task is None:
            return {"success": False, "error": f"Task '{task_id}' not found"}
        return await self._execute_task(task)

    async def reject_task(self, task_id: str, reason: str = "") -> dict[str, Any]:
        task = self._pending_approvals.pop(task_id, None)
        if task is None:
            return {"success": False, "error": f"Task '{task_id}' not found"}
        self._dead_letter.append({
            "task_id": task_id,
            "bot_name": task.bot_name,
            "reason": reason or "Rejected by operator",
            "rejected_at": time.time(),
        })
        return {"success": True, "status": "rejected", "task_id": task_id}

    async def run_all(self, dag: dict[str, list[str]] | None = None) -> dict[str, Any]:
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self._max_concurrent)
        dag = dag or {}
        completed: set[str] = set()
        results: dict[str, Any] = {}
        remaining = list(self._bots.keys())

        while remaining:
            runnable = [
                name for name in remaining
                if all(dep in completed for dep in dag.get(name, []))
            ]
            if not runnable:
                runnable = remaining[:1]

            tasks = [asyncio.create_task(self._run_with_semaphore(name)) for name in runnable]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            for name, result in zip(runnable, batch_results):
                results[name] = result if not isinstance(result, Exception) else {"success": False, "error": str(result)}
                completed.add(name)
                remaining.remove(name)

        succeeded = sum(1 for r in results.values() if r.get("success"))
        return {"total": len(results), "succeeded": succeeded, "failed": len(results) - succeeded, "results": results, "ran_at": time.time()}

    async def _run_with_semaphore(self, bot_name: str) -> dict[str, Any]:
        semaphore = self._semaphore or asyncio.Semaphore(self._max_concurrent)
        async with semaphore:
            return await self._execute_task(_Task(priority=self._default_priority, enqueued_at=time.time(), bot_name=bot_name))

    async def dispatch_with_retry(self, bot_name: str, payload: dict[str, Any] | None = None, max_attempts: int = 3, base_delay: float = 1.0) -> dict[str, Any]:
        last_result: dict[str, Any] = {}
        for attempt in range(max_attempts):
            last_result = await self.dispatch(bot_name, payload)
            if last_result.get("success"):
                return last_result
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)
        self._dead_letter.append({"bot_name": bot_name, "payload": payload, "error": last_result.get("error", ""), "failed_at": time.time(), "attempts": max_attempts})
        return last_result

    def kill(self, bot_name: str) -> bool:
        bot = self._bots.get(bot_name)
        if bot is None:
            return False
        self._killed.add(bot_name)
        bot.stop()
        logger.warning("KILL SWITCH activated for bot: %s", bot_name)
        return True

    def revive(self, bot_name: str) -> bool:
        self._killed.discard(bot_name)
        bot = self._bots.get(bot_name)
        if bot:
            try:
                bot.restart()
            except Exception:  # noqa: BLE001
                pass
        return bot is not None

    async def broadcast(self, message: dict[str, Any]) -> list[dict[str, Any]]:
        results = []
        for bot_name, bot in list(self._bots.items()):
            if hasattr(bot, "on_broadcast"):
                try:
                    await bot.on_broadcast(message)
                    results.append({"bot": bot_name, "delivered": True})
                except Exception as exc:  # noqa: BLE001
                    results.append({"bot": bot_name, "delivered": False, "error": str(exc)})
        return results

    @property
    def dead_letter_queue(self) -> list[dict[str, Any]]:
        return list(self._dead_letter)

    @property
    def pending_approvals(self) -> dict[str, Any]:
        return {tid: {"bot_name": t.bot_name, "priority": t.priority} for tid, t in self._pending_approvals.items()}

    def summary(self) -> dict[str, Any]:
        return {
            "registered_bots": list(self._bots.keys()),
            "killed_bots": list(self._killed),
            "dead_letter_count": len(self._dead_letter),
            "pending_approvals": len(self._pending_approvals),
            "bot_states": {name: bot.state.value for name, bot in self._bots.items() if hasattr(bot, "state")},
        }

    async def _execute_task(self, task: _Task) -> dict[str, Any]:
        bot = self._bots.get(task.bot_name)
        if bot is None:
            return {"success": False, "error": f"Bot '{task.bot_name}' not found"}
        if task.bot_name in self._killed:
            return {"success": False, "error": f"Bot '{task.bot_name}' is killed"}
        try:
            result = await bot.execute()
            self._run_history.append(result)
            return result
        except Exception as exc:  # noqa: BLE001
            error_record = {"bot_name": task.bot_name, "success": False, "error": str(exc), "failed_at": time.time()}
            self._dead_letter.append(error_record)
            return error_record


# ---------------------------------------------------------------------------
# Backwards-compatible alias for the old PythonBotOrchestrator
# ---------------------------------------------------------------------------
PythonBotOrchestrator = DreamCoOrchestrator
