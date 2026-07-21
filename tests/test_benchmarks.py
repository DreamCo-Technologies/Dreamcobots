"""
DreamCobots — Benchmark / Stress Tests

Validates that critical paths meet latency and throughput production targets.

Run with::

    python -m pytest tests/test_benchmarks.py -v --tb=short

These tests do NOT require pytest-benchmark.  They use the stdlib ``time``
module so the suite can run in CI without extra dependencies.
"""

import os
import sys
import time
import threading
from typing import Any

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

from framework import GlobalAISourcesFlow  # noqa: E402
from bots.utils.logger import get_logger  # noqa: E402
from bots.utils.error_handler import BotError, retry, safe_run  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _elapsed(fn, *args: Any, **kwargs: Any) -> float:
    """Return wall-clock seconds for a single call to *fn*."""
    t0 = time.perf_counter()
    fn(*args, **kwargs)
    return time.perf_counter() - t0


# ─────────────────────────────────────────────────────────────────────────────
# GlobalAISourcesFlow benchmarks
# ─────────────────────────────────────────────────────────────────────────────

class TestFrameworkBenchmarks:
    """Ensure the GLOBAL AI SOURCES FLOW pipeline meets latency budgets."""

    _INSTANTIATION_BUDGET_S = 0.5
    _VALIDATE_BUDGET_S = 0.1
    _PIPELINE_BUDGET_S = 2.0

    def test_instantiation_within_budget(self):
        elapsed = _elapsed(GlobalAISourcesFlow, "benchmark_bot")
        assert elapsed < self._INSTANTIATION_BUDGET_S, (
            f"GlobalAISourcesFlow() took {elapsed:.3f}s "
            f"(budget: {self._INSTANTIATION_BUDGET_S}s)"
        )

    def test_validate_within_budget(self):
        flow = GlobalAISourcesFlow("benchmark_bot")
        elapsed = _elapsed(flow.validate)
        assert elapsed < self._VALIDATE_BUDGET_S, (
            f"validate() took {elapsed:.3f}s "
            f"(budget: {self._VALIDATE_BUDGET_S}s)"
        )

    def test_pipeline_within_budget(self):
        flow = GlobalAISourcesFlow("benchmark_bot")
        raw = {"source": "test", "records": list(range(100))}
        elapsed = _elapsed(flow.run_pipeline, raw, "supervised")
        assert elapsed < self._PIPELINE_BUDGET_S, (
            f"run_pipeline() took {elapsed:.3f}s "
            f"(budget: {self._PIPELINE_BUDGET_S}s)"
        )

    def test_repeated_pipeline_calls_are_stable(self):
        """100 consecutive pipeline calls should all finish within budget."""
        flow = GlobalAISourcesFlow("stability_bot")
        raw = {"source": "stability_test"}
        times = []
        for _ in range(100):
            t0 = time.perf_counter()
            flow.run_pipeline(raw, "supervised")
            times.append(time.perf_counter() - t0)

        avg = sum(times) / len(times)
        worst = max(times)
        assert worst < self._PIPELINE_BUDGET_S, (
            f"Worst-case pipeline call: {worst:.3f}s "
            f"(budget: {self._PIPELINE_BUDGET_S}s)"
        )
        assert avg < self._PIPELINE_BUDGET_S / 2, (
            f"Average pipeline call: {avg:.3f}s — unexpectedly slow"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Concurrency / stress tests
# ─────────────────────────────────────────────────────────────────────────────

class TestConcurrentAccess:
    """Verify that multiple bots can run their pipelines concurrently."""

    _N_THREADS = 10
    _BUDGET_TOTAL_S = 10.0

    def test_concurrent_pipeline_runs(self):
        errors: list[Exception] = []

        def _run(idx: int) -> None:
            try:
                flow = GlobalAISourcesFlow(f"concurrent_bot_{idx}")
                flow.run_pipeline({"thread": idx}, "supervised")
            except Exception as exc:
                errors.append(exc)

        threads = [
            threading.Thread(target=_run, args=(i,))
            for i in range(self._N_THREADS)
        ]
        t0 = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=self._BUDGET_TOTAL_S)
        elapsed = time.perf_counter() - t0

        assert not errors, f"Concurrent runs raised: {errors}"
        assert elapsed < self._BUDGET_TOTAL_S, (
            f"All {self._N_THREADS} concurrent runs took {elapsed:.2f}s "
            f"(budget: {self._BUDGET_TOTAL_S}s)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Logging benchmarks
# ─────────────────────────────────────────────────────────────────────────────

class TestLoggingBenchmarks:
    """Ensure structured logging overhead is negligible."""

    _LOG_CALLS = 1_000
    _BUDGET_S = 2.0

    def test_bulk_info_logging_within_budget(self, capsys):
        log = get_logger("bench_logger")
        t0 = time.perf_counter()
        for i in range(self._LOG_CALLS):
            log.info("benchmark message", iteration=i)
        elapsed = time.perf_counter() - t0
        assert elapsed < self._BUDGET_S, (
            f"{self._LOG_CALLS} log.info() calls took {elapsed:.3f}s "
            f"(budget: {self._BUDGET_S}s)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Error handling benchmarks
# ─────────────────────────────────────────────────────────────────────────────

class TestErrorHandlerBenchmarks:
    """Verify that retry / safe_run decorators add minimal overhead."""

    _BUDGET_OVERHEAD_S = 0.01   # 10 ms max decorator overhead for a no-op

    def test_retry_decorator_no_overhead_on_success(self):
        @retry(max_attempts=3)
        def noop() -> str:
            return "ok"

        elapsed = _elapsed(noop)
        assert elapsed < self._BUDGET_OVERHEAD_S, (
            f"retry() overhead on success: {elapsed:.4f}s "
            f"(budget: {self._BUDGET_OVERHEAD_S}s)"
        )

    def test_safe_run_decorator_no_overhead_on_success(self):
        @safe_run(fallback=None)
        def noop() -> str:
            return "ok"

        elapsed = _elapsed(noop)
        assert elapsed < self._BUDGET_OVERHEAD_S, (
            f"safe_run() overhead on success: {elapsed:.4f}s "
            f"(budget: {self._BUDGET_OVERHEAD_S}s)"
        )

    def test_safe_run_returns_fallback_without_raising(self):
        @safe_run(fallback="FALLBACK", log_errors=False)
        def always_fails() -> str:
            raise RuntimeError("deliberate test failure")

        result = always_fails()
        assert result == "FALLBACK"

    def test_retry_exhausts_and_raises(self):
        call_count = 0

        @retry(max_attempts=3, delay=0.0, exceptions=(ValueError,))
        def always_fails() -> None:
            nonlocal call_count
            call_count += 1
            raise ValueError("deliberate")

        with pytest.raises(ValueError):
            always_fails()
        assert call_count == 3
