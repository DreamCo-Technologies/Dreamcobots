"""A bounded, approval-aware task runner with a 24-hour maximum window."""

from __future__ import annotations

import heapq
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


class TaskRunnerError(ValueError):
    """Raised when a task exceeds runtime, concurrency, or approval rules."""


class TaskAdapter(Protocol):
    name: str

    def execute(self, task: "ScheduledTask") -> dict[str, Any]:
        raise NotImplementedError


@dataclass(order=True)
class ScheduledTask:
    run_at: float
    task_id: str = field(compare=False)
    owner_user_id: str = field(compare=False)
    bot_slug: str = field(compare=False)
    objective: str = field(compare=False)
    max_runtime_seconds: int = field(default=3600, compare=False)
    live_external_action: bool = field(default=False, compare=False)
    approval_id: str | None = field(default=None, compare=False)
    status: str = field(default="scheduled", compare=False)
    created_at: float = field(default_factory=time.time, compare=False)

    def validate(self, *, now: float | None = None) -> None:
        current = time.time() if now is None else now
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{2,80}", self.owner_user_id):
            raise TaskRunnerError("A stable owner id is required.")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,79}", self.bot_slug):
            raise TaskRunnerError("A valid Buddy bot slug is required.")
        if len(self.objective.strip()) < 10 or len(self.objective) > 4000:
            raise TaskRunnerError("Task objective must contain 10 to 4,000 characters.")
        if self.max_runtime_seconds < 1 or self.max_runtime_seconds > 86_400:
            raise TaskRunnerError("Tasks can run for at most 24 hours.")
        if self.run_at < current - 1:
            raise TaskRunnerError("A task cannot be scheduled in the past.")
        if self.live_external_action and not self.approval_id:
            raise TaskRunnerError("Live external tasks require a one-action approval id.")


class BuddyTaskRunner:
    """Schedule multiple tasks and execute due work through injected adapters."""

    def __init__(self, *, max_concurrency: int = 4, max_tasks: int = 1000):
        if max_concurrency < 1 or max_concurrency > 32:
            raise TaskRunnerError("Concurrency must be between 1 and 32.")
        self.max_concurrency = max_concurrency
        self.max_tasks = min(max(max_tasks, 1), 10_000)
        self._queue: list[ScheduledTask] = []
        self._tasks: dict[str, ScheduledTask] = {}
        self._approval_claims: set[str] = set()

    def schedule(
        self,
        *,
        owner_user_id: str,
        bot_slug: str,
        objective: str,
        run_at: float | None = None,
        max_runtime_seconds: int = 3600,
        live_external_action: bool = False,
        approval_id: str | None = None,
    ) -> ScheduledTask:
        if len(self._tasks) >= self.max_tasks:
            raise TaskRunnerError("Task queue capacity reached.")
        task = ScheduledTask(
            run_at=time.time() if run_at is None else run_at,
            task_id=f"task-{uuid.uuid4().hex[:16]}",
            owner_user_id=owner_user_id,
            bot_slug=bot_slug,
            objective=objective,
            max_runtime_seconds=max_runtime_seconds,
            live_external_action=live_external_action,
            approval_id=approval_id,
        )
        task.validate()
        if approval_id and approval_id in self._approval_claims:
            raise TaskRunnerError("An approval can authorize only one task.")
        if approval_id:
            self._approval_claims.add(approval_id)
        self._tasks[task.task_id] = task
        heapq.heappush(self._queue, task)
        return task

    def run_due(self, adapter: TaskAdapter, *, now: float | None = None) -> list[dict[str, Any]]:
        current = time.time() if now is None else now
        due: list[ScheduledTask] = []
        while self._queue and self._queue[0].run_at <= current and len(due) < self.max_concurrency:
            task = heapq.heappop(self._queue)
            if task.status == "scheduled":
                due.append(task)
        results = []
        for task in due:
            task.status = "running"
            started = time.monotonic()
            try:
                payload = adapter.execute(task)
                elapsed = time.monotonic() - started
                if elapsed > task.max_runtime_seconds:
                    raise TaskRunnerError("Task exceeded its approved runtime.")
                task.status = "completed"
                results.append({
                    "task": asdict(task),
                    "status": "completed",
                    "adapter": adapter.name,
                    "result": payload,
                    "live_external_action": task.live_external_action,
                })
            except Exception as error:
                task.status = "failed"
                results.append({
                    "task": asdict(task),
                    "status": "failed",
                    "adapter": adapter.name,
                    "error": str(error)[:300],
                })
        return results

    def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task is None or task.status not in {"scheduled", "running"}:
            return False
        task.status = "cancelled"
        return True

    def dashboard(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for task in self._tasks.values():
            counts[task.status] = counts.get(task.status, 0) + 1
        return {
            "schema": "dreamco.buddy_task_runner.v1",
            "max_task_runtime_seconds": 86_400,
            "max_concurrency": self.max_concurrency,
            "counts": counts,
            "tasks": [asdict(task) for task in sorted(self._tasks.values(), key=lambda item: item.created_at)],
        }
