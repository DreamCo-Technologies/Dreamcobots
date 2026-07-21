"""
DreamCo BotExecutor — Runs a single bot with error isolation, timing,
and structured result validation.

Usage
-----
    from core.executor import BotExecutor
    from core.base_bot import BaseBot

    executor = BotExecutor()
    result = executor.execute(my_bot, task={"target": "austin"})
"""

from __future__ import annotations

import time
import traceback
from typing import Any, Dict, Optional

from core.base_bot import BaseBot, RESULT_STATUS_FAILED, RESULT_STATUS_SUCCESS


# ---------------------------------------------------------------------------
# BotExecutor
# ---------------------------------------------------------------------------


class BotExecutor:
    """
    Runs a ``BaseBot`` instance with error isolation and timing.

    Parameters
    ----------
    timeout_seconds : float | None
        If provided, execution time is recorded but no hard timeout is
        enforced (hard timeouts require threading; this is a lightweight
        executor suitable for single-threaded pipelines).
    """

    def __init__(self, timeout_seconds: Optional[float] = None) -> None:
        self.timeout_seconds = timeout_seconds
        self._execution_log: list[dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute(self, bot: BaseBot, task: dict | None = None) -> dict:
        """
        Execute *bot* with *task* and return a log entry dict.

        Parameters
        ----------
        bot : BaseBot
            The bot instance to run.
        task : dict | None
            Task payload forwarded to ``bot.run()``.  Defaults to ``{}``.

        Returns
        -------
        dict
            ``{ bot_id, bot_name, status, result, elapsed_ms, error? }``
        """
        if task is None:
            task = {}

        start = time.monotonic()
        entry: dict[str, Any] = {
            "bot_id": bot.bot_id,
            "bot_name": bot.name,
            "category": bot.category,
        }

        try:
            result = bot.run(task)
            elapsed_ms = round((time.monotonic() - start) * 1000, 2)

            if not BaseBot.validate_result(result):
                entry.update(
                    {
                        "status": RESULT_STATUS_FAILED,
                        "error": "Bot returned a malformed result dict",
                        "result": result,
                        "elapsed_ms": elapsed_ms,
                    }
                )
            else:
                entry.update(
                    {
                        "status": result["status"],
                        "result": result,
                        "elapsed_ms": elapsed_ms,
                    }
                )
        except Exception as exc:  # pylint: disable=broad-except
            elapsed_ms = round((time.monotonic() - start) * 1000, 2)
            entry.update(
                {
                    "status": RESULT_STATUS_FAILED,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "result": None,
                    "elapsed_ms": elapsed_ms,
                }
            )

        self._execution_log.append(entry)
        return entry

    def execute_many(
        self, bots: list[BaseBot], task: dict | None = None
    ) -> list[dict]:
        """
        Execute a list of bots sequentially and return all log entries.

        Parameters
        ----------
        bots : list[BaseBot]
            Bots to run in order.
        task : dict | None
            Shared task payload forwarded to each ``bot.run()``.

        Returns
        -------
        list[dict]
        """
        return [self.execute(bot, task) for bot in bots]

    # ------------------------------------------------------------------
    # Execution log
    # ------------------------------------------------------------------

    def get_log(self) -> list[dict]:
        """Return all execution log entries recorded by this executor."""
        return list(self._execution_log)

    def clear_log(self) -> None:
        """Clear the internal execution log."""
        self._execution_log.clear()

    # ------------------------------------------------------------------
    # Summary helpers
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """
        Return an aggregate summary of all executions recorded so far.

        Returns
        -------
        dict
            ``{ total, succeeded, failed, avg_elapsed_ms }``
        """
        total = len(self._execution_log)
        succeeded = sum(
            1 for e in self._execution_log if e["status"] == RESULT_STATUS_SUCCESS
        )
        failed = total - succeeded
        if total:
            avg_elapsed = round(
                sum(e.get("elapsed_ms", 0) for e in self._execution_log) / total, 2
            )
        else:
            avg_elapsed = 0.0

        return {
            "total": total,
            "succeeded": succeeded,
            "failed": failed,
            "avg_elapsed_ms": avg_elapsed,
        }
