"""A recurring, approval-aware task runner with bounded individual runs."""

from __future__ import annotations

import heapq
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


class TaskRunnerError(ValueError):
    """Raised when a task exceeds runtime, concurrency, schedule, or approval rules."""


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
    recurrence: str = field(default="once", compare=False)
    interval_seconds: int | None = field(default=None, compare=False)
    ends_at: float | None = field(default=None, compare=False)
    max_runs: int | None = field(default=None, compare=False)
    max_consecutive_failures: int = field(default=3, compare=False)
    live_external_action: bool = field(default=False, compare=False)
    approval_id: str | None = field(default=None, compare=False)
    status: str = field(default="scheduled", compare=False)
    run_count: int = field(default=0, compare=False)
    consecutive_failures: int = field(default=0, compare=False)
    last_run_at: float | None = field(default=None, compare=False)
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
            raise TaskRunnerError("Each individual run can use at most 24 hours before a checkpoint.")
        if self.run_at < current - 1:
            raise TaskRunnerError("A task cannot be scheduled in the past.")
        if self.recurrence not in {"once", "interval"}:
            raise TaskRunnerError("Recurrence must be once or interval.")
        if self.recurrence == "once" and self.interval_seconds is not None:
            raise TaskRunnerError("One-time tasks cannot define a recurring interval.")
        if self.recurrence == "interval" and (self.interval_seconds is None or self.interval_seconds < 60):
            raise TaskRunnerError("Recurring tasks require an interval of at least 60 seconds.")
        if self.ends_at is not None and self.ends_at <= self.run_at:
            raise TaskRunnerError("The schedule end must be after the first run.")
        if self.max_runs is not None and (self.max_runs < 1 or self.max_runs > 10_000):
            raise TaskRunnerError("Maximum runs must be between 1 and 10,000.")
        if self.max_consecutive_failures < 1 or self.max_consecutive_failures > 20:
            raise TaskRunnerError("Failure pause threshold must be between 1 and 20.")
        if self.live_external_action and not self.approval_id:
            raise TaskRunnerError("Live external tasks require a one-action approval id.")
        if self.live_external_action and self.recurrence != "once":
            raise TaskRunnerError("Recurring external actions require fresh approval for every run.")

    @property
    def indefinite(self) -> bool:
        return self.recurrence == "interval" and self.ends_at is None and self.max_runs is None


class BuddyTaskRunner:
    """Schedule one-time or indefinitely recurring work through injected adapters."""

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
        recurrence: str = "once",
        interval_seconds: int | None = None,
        ends_at: float | None = None,
        max_runs: int | None = None,
        max_consecutive_failures: int = 3,
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
            recurrence=recurrence,
            interval_seconds=interval_seconds,
            ends_at=ends_at,
            max_runs=max_runs,
            max_consecutive_failures=max_consecutive_failures,
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

    @staticmethod
    def _has_finished_schedule(task: ScheduledTask, next_run_at: float) -> bool:
        if task.recurrence == "once":
            return True
        if task.max_runs is not None and task.run_count >= task.max_runs:
            return True
        return task.ends_at is not None and next_run_at > task.ends_at

    def _reschedule(self, task: ScheduledTask, current: float) -> bool:
        if task.recurrence != "interval" or task.interval_seconds is None:
            return False
        next_run_at = max(task.run_at + task.interval_seconds, current + 1)
        if self._has_finished_schedule(task, next_run_at):
            return False
        task.run_at = next_run_at
        task.status = "scheduled"
        heapq.heappush(self._queue, task)
        return True

    def _remove_from_queue(self, task_id: str) -> None:
        self._queue = [task for task in self._queue if task.task_id != task_id]
        heapq.heapify(self._queue)

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
            task.last_run_at = current
            task.run_count += 1
            started = time.monotonic()
            try:
                payload = adapter.execute(task)
                elapsed = time.monotonic() - started
                if elapsed > task.max_runtime_seconds:
                    raise TaskRunnerError("Task exceeded its approved per-run runtime.")
                task.consecutive_failures = 0
                repeated = self._reschedule(task, current)
                if not repeated:
                    task.status = "completed"
                results.append({
                    "task": asdict(task),
                    "status": "completed_and_rescheduled" if repeated else "completed",
                    "adapter": adapter.name,
                    "result": payload,
                    "next_run_at": task.run_at if repeated else None,
                    "live_external_action": task.live_external_action,
                })
            except Exception as error:
                task.consecutive_failures += 1
                repeated = task.consecutive_failures < task.max_consecutive_failures and self._reschedule(task, current)
                task.status = "scheduled" if repeated else "paused" if task.recurrence == "interval" else "failed"
                results.append({
                    "task": asdict(task),
                    "status": "failed_and_rescheduled" if repeated else "paused_after_failures" if task.recurrence == "interval" else "failed",
                    "adapter": adapter.name,
                    "error": str(error)[:300],
                    "next_run_at": task.run_at if repeated else None,
                })
        return results

    def pause(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task is None or task.status not in {"scheduled", "running"}:
            return False
        task.status = "paused"
        self._remove_from_queue(task_id)
        return True

    def resume(self, task_id: str, *, run_at: float | None = None) -> bool:
        task = self._tasks.get(task_id)
        if task is None or task.status != "paused":
            return False
        task.run_at = time.time() if run_at is None else run_at
        task.consecutive_failures = 0
        task.status = "scheduled"
        task.validate()
        heapq.heappush(self._queue, task)
        return True

    def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task is None or task.status not in {"scheduled", "running", "paused"}:
            return False
        task.status = "cancelled"
        self._remove_from_queue(task_id)
        return True

    def dashboard(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for task in self._tasks.values():
            counts[task.status] = counts.get(task.status, 0) + 1
        return {
            "schema": "dreamco.buddy_task_runner.v2",
            "schedule_duration": "indefinite_until_paused_or_end_condition",
            "max_individual_run_runtime_seconds": 86_400,
            "max_concurrency": self.max_concurrency,
            "counts": counts,
            "indefinite_recurring_tasks": sum(1 for task in self._tasks.values() if task.indefinite),
            "tasks": [asdict(task) for task in sorted(self._tasks.values(), key=lambda item: item.created_at)],
        }
