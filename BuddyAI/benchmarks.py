"""
Benchmarks - Performance benchmarking and auto-optimization for Buddy.

Provides tools to measure Buddy's execution time, compare it against
baseline solutions, and surface optimization opportunities.
"""

import functools
import logging
import statistics
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run.

    Attributes:
        name: Human-readable benchmark name.
        iterations: Number of times the function was executed.
        timings: Raw per-iteration elapsed times in seconds.
        mean: Mean elapsed time across all iterations (seconds).
        median: Median elapsed time (seconds).
        stdev: Standard deviation of timings (0.0 when iterations < 2).
        min_time: Fastest iteration time (seconds).
        max_time: Slowest iteration time (seconds).
    """

    name: str
    iterations: int
    timings: List[float] = field(default_factory=list)
    mean: float = 0.0
    median: float = 0.0
    stdev: float = 0.0
    min_time: float = 0.0
    max_time: float = 0.0

    def summary(self) -> str:
        """Return a human-readable summary string."""
        return (
            f"[{self.name}] "
            f"iterations={self.iterations} "
            f"mean={self.mean * 1000:.3f}ms "
            f"median={self.median * 1000:.3f}ms "
            f"stdev={self.stdev * 1000:.3f}ms "
            f"min={self.min_time * 1000:.3f}ms "
            f"max={self.max_time * 1000:.3f}ms"
        )


class Benchmarks:
    """Utility for measuring and comparing callable performance.

    Example::

        bm = Benchmarks()
        result = bm.benchmark(my_function, iterations=100)
        print(result.summary())

        comparison = bm.compare(buddy_fn, external_fn, iterations=50)
        print(comparison["winner"])
    """

    def benchmark(
        self,
        func: Callable,
        *args: Any,
        iterations: int = 10,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> BenchmarkResult:
        """Run *func* repeatedly and collect timing statistics.

        Args:
            func: Callable to benchmark.
            *args: Positional arguments passed to *func*.
            iterations: Number of executions (default 10).
            name: Optional display name (defaults to ``func.__name__``).
            **kwargs: Keyword arguments passed to *func*.

        Returns:
            A :class:`BenchmarkResult` with aggregated statistics.
        """
        label = name or getattr(func, "__name__", str(func))
        timings: List[float] = []

        for _ in range(iterations):
            start = time.perf_counter()
            try:
                func(*args, **kwargs)
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning("Exception during benchmark of '%s': %s", label, exc)
            elapsed = time.perf_counter() - start
            timings.append(elapsed)

        result = BenchmarkResult(
            name=label,
            iterations=iterations,
            timings=timings,
            mean=statistics.mean(timings),
            median=statistics.median(timings),
            stdev=statistics.stdev(timings) if len(timings) > 1 else 0.0,
            min_time=min(timings),
            max_time=max(timings),
        )
        logger.info(result.summary())
        return result

    def compare(
        self,
        buddy_func: Callable,
        external_func: Callable,
        *args: Any,
        iterations: int = 10,
        buddy_name: str = "Buddy",
        external_name: str = "External",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Benchmark two callables and return a comparison report.

        Args:
            buddy_func: Buddy's implementation.
            external_func: External/baseline implementation.
            *args: Positional arguments passed to both functions.
            iterations: Number of executions for each function.
            buddy_name: Display name for *buddy_func*.
            external_name: Display name for *external_func*.
            **kwargs: Keyword arguments passed to both functions.

        Returns:
            Dict with keys ``"buddy"``, ``"external"``, ``"winner"``,
            ``"speedup"`` (ratio of means; > 1 means Buddy is faster).
        """
        buddy_result = self.benchmark(
            buddy_func, *args, iterations=iterations, name=buddy_name, **kwargs
        )
        external_result = self.benchmark(
            external_func, *args, iterations=iterations, name=external_name, **kwargs
        )

        if external_result.mean > 0:
            speedup = external_result.mean / buddy_result.mean
        else:
            speedup = 1.0

        winner = buddy_name if speedup >= 1.0 else external_name

        report = {
            "buddy": buddy_result,
            "external": external_result,
            "winner": winner,
            "speedup": round(speedup, 3),
        }
        logger.info(
            "Comparison: %s vs %s → winner=%s (speedup=%.3fx)",
            buddy_name,
            external_name,
            winner,
            speedup,
        )
        return report

    @staticmethod
    def timed(func: Callable) -> Callable:
        """Decorator that logs elapsed time for every call to *func*.

        Usage::

            @Benchmarks.timed
            def my_slow_function():
                time.sleep(1)
        """

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            logger.debug("%s took %.3fms", func.__name__, elapsed * 1000)
            return result

        return wrapper
