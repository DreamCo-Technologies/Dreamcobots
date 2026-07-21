# BuddyAI Stress Test Runner
# Measures system performance under simulated load to inform capacity planning
# and surfaced on the client dashboard.

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional


@dataclass
class StressTestResult:
    """Holds the outcome of a single stress test run."""

    test_id: str
    test_name: str
    iterations: int
    concurrency: int
    total_duration_seconds: float
    successful_ops: int
    failed_ops: int
    avg_latency_seconds: float
    max_latency_seconds: float
    min_latency_seconds: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def success_rate(self) -> float:
        """Fraction of operations that completed successfully (0.0 – 1.0)."""
        total = self.successful_ops + self.failed_ops
        if total == 0:
            return 0.0
        return round(self.successful_ops / total, 4)

    @property
    def ops_per_second(self) -> float:
        """Throughput: operations per second."""
        if self.total_duration_seconds == 0:
            return 0.0
        return round((self.successful_ops + self.failed_ops) / self.total_duration_seconds, 2)

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "iterations": self.iterations,
            "concurrency": self.concurrency,
            "total_duration_seconds": self.total_duration_seconds,
            "successful_ops": self.successful_ops,
            "failed_ops": self.failed_ops,
            "avg_latency_seconds": self.avg_latency_seconds,
            "max_latency_seconds": self.max_latency_seconds,
            "min_latency_seconds": self.min_latency_seconds,
            "success_rate": self.success_rate,
            "ops_per_second": self.ops_per_second,
            "timestamp": self.timestamp.isoformat(),
        }


class StressTestRunner:
    """
    Runs configurable stress tests against a callable target and stores results.

    Usage::

        runner = StressTestRunner()
        result = runner.run(
            target=my_function,
            test_name="payment_processing",
            iterations=1000,
        )
        print(result.to_dict())
    """

    def __init__(self) -> None:
        self._results: Dict[str, StressTestResult] = {}

    def run(
        self,
        target: Callable,
        test_name: str,
        iterations: int = 100,
        concurrency: int = 1,
        target_args: Optional[tuple] = None,
        target_kwargs: Optional[dict] = None,
    ) -> StressTestResult:
        """
        Execute *target* the specified number of times and collect latency/error stats.

        Args:
            target: The callable to benchmark.
            test_name: Human-readable label for the test.
            iterations: Total number of calls to make.
            concurrency: Placeholder for future parallel execution support.
                         Currently executes serially.
            target_args: Positional arguments forwarded to *target*.
            target_kwargs: Keyword arguments forwarded to *target*.

        Returns:
            A :class:`StressTestResult` capturing aggregate statistics.
        """
        if iterations <= 0:
            raise ValueError("iterations must be greater than zero.")

        args = target_args or ()
        kwargs = target_kwargs or {}
        latencies: List[float] = []
        failed = 0

        overall_start = time.perf_counter()

        for _ in range(iterations):
            start = time.perf_counter()
            try:
                target(*args, **kwargs)
            except Exception:
                failed += 1
            finally:
                latencies.append(time.perf_counter() - start)

        total_duration = time.perf_counter() - overall_start
        successful = iterations - failed

        result = StressTestResult(
            test_id=str(uuid.uuid4()),
            test_name=test_name,
            iterations=iterations,
            concurrency=concurrency,
            total_duration_seconds=round(total_duration, 6),
            successful_ops=successful,
            failed_ops=failed,
            avg_latency_seconds=round(sum(latencies) / len(latencies), 6),
            max_latency_seconds=round(max(latencies), 6),
            min_latency_seconds=round(min(latencies), 6),
        )

        self._results[result.test_id] = result
        return result

    def get_result(self, test_id: str) -> Optional[StressTestResult]:
        """Return a single stress test result by its ID."""
        return self._results.get(test_id)

    def list_results(self) -> List[StressTestResult]:
        """Return all stress test results sorted by timestamp descending."""
        return sorted(
            self._results.values(),
            key=lambda r: r.timestamp,
            reverse=True,
        )
