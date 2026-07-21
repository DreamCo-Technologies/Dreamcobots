"""
Scheduler - Task scheduling capability for Buddy.

Provides lightweight in-process task scheduling using Python's
standard ``sched`` module.  Jobs can be one-off or recurring.
"""

import logging
import sched
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTask:
    """A task waiting to be executed.

    Attributes:
        task_id: Unique string identifier for the task.
        name: Human-readable task label.
        callback: Callable to invoke when the task fires.
        run_at: Unix timestamp when the task should run.
        recurring: Whether to reschedule after execution.
        interval: Seconds between recurrences (only used when recurring=True).
        params: Extra keyword arguments passed to the callback.
    """

    task_id: str
    name: str
    callback: Callable
    run_at: float
    recurring: bool = False
    interval: float = 0.0
    params: Dict[str, Any] = field(default_factory=dict)
    _event: Optional[object] = field(default=None, repr=False)


class Scheduler:
    """Lightweight task scheduler backed by ``sched.scheduler``.

    Runs in a background daemon thread so that scheduled callbacks
    fire even while the caller is blocked.

    Example::

        scheduler = Scheduler()
        scheduler.start()

        def greet():
            print("Hello from Buddy!")

        scheduler.schedule_task("greet", greet, delay=5)
        # … greet() will fire in 5 seconds
    """

    def __init__(self) -> None:
        self._sched = sched.scheduler(time.time, time.sleep)
        self._tasks: Dict[str, ScheduledTask] = {}
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._running = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the background scheduler thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Scheduler started.")

    def stop(self) -> None:
        """Stop the background scheduler thread."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        logger.info("Scheduler stopped.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def schedule_task(
        self,
        name: str,
        callback: Callable,
        *,
        delay: float = 0.0,
        run_at: Optional[float] = None,
        recurring: bool = False,
        interval: float = 0.0,
        **params: Any,
    ) -> str:
        """Schedule *callback* to run in the future.

        Args:
            name: Human-readable task name.
            callback: Callable to execute.
            delay: Seconds from now until the task fires (mutually exclusive
                   with *run_at*).
            run_at: Absolute Unix timestamp to run the task.
            recurring: If ``True``, reschedule the task every *interval* seconds
                       after it fires.
            interval: Seconds between recurring executions.
            **params: Extra keyword arguments forwarded to *callback*.

        Returns:
            Unique task ID string.
        """
        if run_at is None:
            run_at = time.time() + delay

        task_id = str(uuid.uuid4())
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            callback=callback,
            run_at=run_at,
            recurring=recurring,
            interval=interval,
            params=params,
        )

        with self._lock:
            event = self._sched.enterabs(run_at, 1, self._fire, argument=(task,))
            task._event = event
            self._tasks[task_id] = task

        logger.info(
            "Scheduled task '%s' (id=%s) at %.1f (delay=%.1fs)",
            name,
            task_id,
            run_at,
            run_at - time.time(),
        )
        return task_id

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task by *task_id*.

        Args:
            task_id: ID returned by :meth:`schedule_task`.

        Returns:
            ``True`` if the task was found and cancelled, ``False`` otherwise.
        """
        with self._lock:
            task = self._tasks.pop(task_id, None)
            if task is None:
                logger.warning("Task %s not found; cannot cancel.", task_id)
                return False
            if task._event is not None:
                try:
                    self._sched.cancel(task._event)
                except ValueError:
                    pass  # already fired
            logger.info("Cancelled task '%s' (id=%s).", task.name, task_id)
            return True

    def get_upcoming(self) -> List[Dict[str, Any]]:
        """Return a list of all pending tasks sorted by their scheduled time.

        Returns:
            List of dicts with keys ``task_id``, ``name``, ``run_at``.
        """
        with self._lock:
            return sorted(
                [
                    {
                        "task_id": t.task_id,
                        "name": t.name,
                        "run_at": t.run_at,
                        "recurring": t.recurring,
                    }
                    for t in self._tasks.values()
                ],
                key=lambda x: x["run_at"],
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fire(self, task: ScheduledTask) -> None:
        """Execute *task* and reschedule if recurring."""
        logger.debug("Firing task '%s' (id=%s)", task.name, task.task_id)
        try:
            task.callback(**task.params)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(
                "Task '%s' raised an exception: %s", task.name, exc
            )
        finally:
            with self._lock:
                self._tasks.pop(task.task_id, None)
                if task.recurring and task.interval > 0 and self._running:
                    next_run = time.time() + task.interval
                    task.run_at = next_run
                    event = self._sched.enterabs(
                        next_run, 1, self._fire, argument=(task,)
                    )
                    task._event = event
                    self._tasks[task.task_id] = task
                    logger.debug(
                        "Rescheduled recurring task '%s' in %.1fs",
                        task.name,
                        task.interval,
                    )

    def _run_loop(self) -> None:
        """Main loop for the background thread."""
        while self._running:
            self._sched.run(blocking=False)
            time.sleep(0.1)
