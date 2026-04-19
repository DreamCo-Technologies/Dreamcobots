"""
DreamCobots — Async Parallel Bot Runner

Enhances the original run_all_bots.py pipeline with:
  • asyncio-based concurrent bot execution (max_concurrency configurable)
  • Per-bot elapsed-time tracking
  • Centralised TimestampButton milestone logging
  • Redis + Celery task-queue scaffold for production deployments

Usage
-----
    # Sequential (original behaviour)
    python run_all_bots.py

    # Async parallel
    python -m bots.async_bot_runner

    # Programmatic
    from bots.async_bot_runner import AsyncBotRunner
    runner = AsyncBotRunner(max_concurrency=5)
    results = runner.run_all()
"""

from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
import time
from typing import Any, Callable, Dict, List, Optional

# Ensure repo root on path
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from core.timestamp_button import TimestampButton


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_bot(filename: str, module_name: str):
    """Load a standalone bot module by file path."""
    path = os.path.join(_REPO_ROOT, "bots", filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# AsyncBotRunner
# ---------------------------------------------------------------------------


class AsyncBotRunner:
    """
    Executes a fleet of bot callables concurrently using asyncio.

    Parameters
    ----------
    max_concurrency : int
        Maximum number of bots executed in parallel (default: 10).
    log_path : str
        Path for TimestampButton milestone log (default: ``logs.txt``).
    """

    def __init__(
        self,
        max_concurrency: int = 10,
        log_path: str = "logs.txt",
    ) -> None:
        self.max_concurrency = max_concurrency
        self._ts = TimestampButton(log_path=log_path, bot_name="AsyncBotRunner")
        self._results: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Core execution
    # ------------------------------------------------------------------

    def run_all(self, bot_callables: Optional[List[Callable]] = None) -> List[Dict[str, Any]]:
        """
        Run all provided bot callables concurrently.

        If *bot_callables* is ``None`` the default revenue pipeline
        (lead → outreach → real_estate → sales) is used.
        """
        if bot_callables is None:
            bot_callables = self._default_pipeline()

        self._ts.stamp(
            event="async_run_started",
            detail=f"bots={len(bot_callables)} concurrency={self.max_concurrency}",
        )
        start = time.monotonic()
        results = asyncio.run(self._run_parallel(bot_callables))
        elapsed = round((time.monotonic() - start) * 1000, 2)

        self._results = results
        self._ts.stamp(
            event="async_run_completed",
            detail=f"total={len(results)} elapsed_ms={elapsed}",
        )
        return results

    async def _run_parallel(
        self, bot_callables: List[Callable]
    ) -> List[Dict[str, Any]]:
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def _run_one(fn: Callable) -> Dict[str, Any]:
            name = getattr(fn, "__name__", str(fn))
            async with semaphore:
                start = time.monotonic()
                try:
                    if asyncio.iscoroutinefunction(fn):
                        result = await fn()
                    else:
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(None, fn)
                    elapsed = round((time.monotonic() - start) * 1000, 2)
                    return {"bot": name, "status": "success", "result": result, "elapsed_ms": elapsed}
                except Exception as exc:  # noqa: BLE001  # bot callables may raise any exception
                    elapsed = round((time.monotonic() - start) * 1000, 2)
                    return {"bot": name, "status": "failed", "error": str(exc), "elapsed_ms": elapsed}

        return list(await asyncio.gather(*[_run_one(fn) for fn in bot_callables]))

    # ------------------------------------------------------------------
    # Default revenue pipeline
    # ------------------------------------------------------------------

    def _default_pipeline(self) -> List[Callable]:
        """Load and return the original revenue pipeline bot callables."""
        _lead_bot = _load_bot("lead_bot.py", "_async_pipeline_lead_bot")
        _outreach_bot = _load_bot("outreach_bot.py", "_async_pipeline_outreach_bot")
        _sales_bot = _load_bot("sales_bot.py", "_async_pipeline_sales_bot")
        _real_estate_bot = _load_bot("real_estate_bot.py", "_async_pipeline_real_estate_bot")
        return [
            _lead_bot.run_leads,
            _outreach_bot.send_message,
            _sales_bot.close_sales,
            _real_estate_bot.find_deals,
        ]

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def print_report(self) -> None:
        """Print a summary of the last run to stdout."""
        print("\n── AsyncBotRunner Report ──────────────────────────")
        for r in self._results:
            status_icon = "✅" if r["status"] == "success" else "❌"
            print(f"  {status_icon}  {r['bot']:<30}  {r['elapsed_ms']} ms")
        passed = sum(1 for r in self._results if r["status"] == "success")
        print(f"\n  Passed: {passed}/{len(self._results)}")
        print("───────────────────────────────────────────────────\n")

    def get_milestone_dashboard(self) -> str:
        """Return the TimestampButton dashboard string."""
        return self._ts.dashboard()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    runner = AsyncBotRunner(max_concurrency=4)
    runner.run_all()
    runner.print_report()
    print(runner.get_milestone_dashboard())


if __name__ == "__main__":
    main()
