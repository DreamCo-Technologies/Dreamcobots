"""
DreamCo WorkflowEngine — Chains bots into sequential or parallel
execution pipelines.

A *workflow* is an ordered list of steps, each pointing to a ``BaseBot``
subclass and an optional task override.  Steps are executed in order;
the output of each step is available to subsequent steps via the shared
*context* dict.

Parallel execution is supported via :attr:`WorkflowStep.parallel_group`.
Steps that share the same ``parallel_group`` label are executed
concurrently inside a thread pool.

Priority-level execution is supported by optionally sorting steps via
:meth:`WorkflowEngine.run` with ``sort_by_priority=True``.

Usage
-----
    from core.workflow import WorkflowEngine, WorkflowStep

    engine = WorkflowEngine()
    engine.add_step(WorkflowStep(bot=RealEstateBot(), task={"location": "austin"}))
    engine.add_step(WorkflowStep(bot=DealFinderBot(), task={}))
    result = engine.run()
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.base_bot import BaseBot, RESULT_STATUS_SUCCESS, RESULT_STATUS_FAILED
from core.executor import BotExecutor

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# WorkflowStep
# ---------------------------------------------------------------------------


@dataclass
class WorkflowStep:
    """
    A single step in a workflow.

    Attributes
    ----------
    bot : BaseBot
        The bot instance to run for this step.
    task : dict
        Task payload forwarded to ``bot.run()``.
    name : str
        Optional human-readable step name.  Defaults to the bot's name.
    priority : int
        Execution priority (lower numbers run first when sorting is enabled).
        Defaults to 0 (highest priority).
    parallel_group : str
        When non-empty, steps sharing the same ``parallel_group`` value are
        executed concurrently.  Empty string (default) means sequential.
    max_retries : int
        Number of times to retry this step on failure before marking it
        as failed.  Defaults to 0 (no retries).
    retry_delay_seconds : float
        Seconds to wait between retry attempts.  Defaults to 1.0.
    """

    bot: BaseBot
    task: dict = field(default_factory=dict)
    name: str = ""
    priority: int = 0
    parallel_group: str = ""
    max_retries: int = 0
    retry_delay_seconds: float = 1.0

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.bot.name or self.bot.bot_id


# ---------------------------------------------------------------------------
# WorkflowResult
# ---------------------------------------------------------------------------


@dataclass
class WorkflowResult:
    """Aggregated result returned by :meth:`WorkflowEngine.run`."""

    steps: List[dict]
    status: str
    total_elapsed_ms: float
    context: Dict[str, Any]

    @property
    def succeeded(self) -> int:
        return sum(1 for s in self.steps if s["status"] == RESULT_STATUS_SUCCESS)

    @property
    def failed(self) -> int:
        return sum(1 for s in self.steps if s["status"] == RESULT_STATUS_FAILED)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "steps": self.steps,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "total_elapsed_ms": self.total_elapsed_ms,
            "context": self.context,
        }


# ---------------------------------------------------------------------------
# WorkflowEngine
# ---------------------------------------------------------------------------


class WorkflowEngine:
    """
    Chains ``BaseBot`` instances into sequential or parallel execution
    pipelines with priority-level scheduling and failure recovery.

    Parameters
    ----------
    name : str
        Human-readable workflow name (useful for logging).
    stop_on_failure : bool
        If ``True`` (default), halt the pipeline when a step fails.
        If ``False``, continue running remaining steps.
    max_workers : int
        Maximum number of threads used for parallel step groups.
        Defaults to 4.
    """

    def __init__(
        self,
        name: str = "default_workflow",
        stop_on_failure: bool = True,
        max_workers: int = 4,
    ) -> None:
        self.name = name
        self.stop_on_failure = stop_on_failure
        self.max_workers = max_workers
        self._steps: List[WorkflowStep] = []
        self._executor = BotExecutor()
        self._history: List[WorkflowResult] = []

    # ------------------------------------------------------------------
    # Step management
    # ------------------------------------------------------------------

    def add_step(self, step: WorkflowStep) -> "WorkflowEngine":
        """Append *step* to the workflow and return *self* for chaining."""
        self._steps.append(step)
        return self

    def add_bot(
        self,
        bot: BaseBot,
        task: dict | None = None,
        name: str = "",
        priority: int = 0,
        parallel_group: str = "",
        max_retries: int = 0,
    ) -> "WorkflowEngine":
        """Convenience method — wrap *bot* in a WorkflowStep and add it."""
        return self.add_step(
            WorkflowStep(
                bot=bot,
                task=task or {},
                name=name,
                priority=priority,
                parallel_group=parallel_group,
                max_retries=max_retries,
            )
        )

    def clear_steps(self) -> None:
        """Remove all steps from the workflow."""
        self._steps.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _execute_step_with_retry(
        self,
        step: WorkflowStep,
        context: Dict[str, Any],
    ) -> dict:
        """Execute a single step, retrying up to ``step.max_retries`` times."""
        merged_task = {**step.task, "_context": context}
        attempts = 0
        last_entry: dict = {}

        while attempts <= step.max_retries:
            if attempts > 0:
                logger.warning(
                    "[%s] Step '%s' failed — retry %d/%d in %.1fs",
                    self.name,
                    step.name,
                    attempts,
                    step.max_retries,
                    step.retry_delay_seconds,
                )
                time.sleep(step.retry_delay_seconds)

            last_entry = self._executor.execute(step.bot, task=merged_task)
            attempts += 1

            if last_entry.get("status") == RESULT_STATUS_SUCCESS:
                if attempts > 1:
                    logger.info(
                        "[%s] Step '%s' recovered after %d retries",
                        self.name,
                        step.name,
                        attempts - 1,
                    )
                break

        last_entry["retries"] = attempts - 1
        return last_entry

    def _run_parallel_group(
        self,
        steps: List[WorkflowStep],
        context: Dict[str, Any],
    ) -> List[dict]:
        """Execute a list of steps concurrently and collect results."""
        step_results: List[dict] = [{} for _ in steps]
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(steps))) as pool:
            future_to_index = {
                pool.submit(self._execute_step_with_retry, step, dict(context)): idx
                for idx, step in enumerate(steps)
            }
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                step = steps[idx]
                try:
                    entry = future.result()
                except Exception as exc:  # pragma: no cover
                    logger.error(
                        "[%s] Parallel step '%s' raised unexpectedly: %s",
                        self.name,
                        step.name,
                        exc,
                    )
                    entry = {
                        "status": RESULT_STATUS_FAILED,
                        "error": str(exc),
                        "retries": 0,
                    }
                step_results[idx] = {"step": step.name, **entry}
        return step_results

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(
        self,
        context: Dict[str, Any] | None = None,
        sort_by_priority: bool = False,
    ) -> WorkflowResult:
        """
        Execute all steps, respecting priority ordering and parallel groups.

        Parameters
        ----------
        context : dict | None
            Shared mutable context that each step can read and write.
            The result of each step is stored under the step name key.
        sort_by_priority : bool
            When ``True``, steps are sorted by ascending ``priority`` before
            execution (lower priority number = runs first).

        Returns
        -------
        WorkflowResult
        """
        if context is None:
            context = {}

        steps = list(self._steps)
        if sort_by_priority:
            steps = sorted(steps, key=lambda s: s.priority)

        logger.info("[%s] Starting workflow with %d step(s)", self.name, len(steps))
        start = time.monotonic()
        step_results: List[dict] = []
        overall_status = RESULT_STATUS_SUCCESS

        # Group consecutive steps that share the same parallel_group label.
        # Sequential steps (parallel_group="") are each their own singleton group.
        i = 0
        while i < len(steps):
            current_step = steps[i]
            group_label = current_step.parallel_group

            if group_label:
                # Collect all consecutive steps with the same group label
                group: List[WorkflowStep] = []
                while i < len(steps) and steps[i].parallel_group == group_label:
                    group.append(steps[i])
                    i += 1

                logger.info(
                    "[%s] Executing parallel group '%s' (%d steps)",
                    self.name,
                    group_label,
                    len(group),
                )
                group_results = self._run_parallel_group(group, context)
                step_results.extend(group_results)

                for entry, step in zip(group_results, group):
                    context[step.name] = entry.get("result")
                    if entry.get("status") == RESULT_STATUS_FAILED:
                        overall_status = RESULT_STATUS_FAILED
                        logger.error(
                            "[%s] Parallel step '%s' failed",
                            self.name,
                            step.name,
                        )

                if overall_status == RESULT_STATUS_FAILED and self.stop_on_failure:
                    logger.warning(
                        "[%s] Stopping workflow after parallel group failure",
                        self.name,
                    )
                    break
            else:
                # Sequential step
                entry = self._execute_step_with_retry(current_step, context)
                step_results.append({"step": current_step.name, **entry})
                context[current_step.name] = entry.get("result")

                if entry.get("status") == RESULT_STATUS_FAILED:
                    overall_status = RESULT_STATUS_FAILED
                    logger.error(
                        "[%s] Step '%s' failed (retries=%d)",
                        self.name,
                        current_step.name,
                        entry.get("retries", 0),
                    )
                    if self.stop_on_failure:
                        logger.warning(
                            "[%s] Stopping workflow after step failure",
                            self.name,
                        )
                        break
                else:
                    logger.debug("[%s] Step '%s' succeeded", self.name, current_step.name)

                i += 1

        total_elapsed = round((time.monotonic() - start) * 1000, 2)
        logger.info(
            "[%s] Workflow finished — status=%s elapsed=%.2fms",
            self.name,
            overall_status,
            total_elapsed,
        )
        result = WorkflowResult(
            steps=step_results,
            status=overall_status,
            total_elapsed_ms=total_elapsed,
            context=context,
        )
        self._history.append(result)
        return result

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def get_history(self) -> List[WorkflowResult]:
        """Return all past :class:`WorkflowResult` instances."""
        return list(self._history)

    def last_result(self) -> Optional[WorkflowResult]:
        """Return the most recent :class:`WorkflowResult`, or ``None``."""
        return self._history[-1] if self._history else None
