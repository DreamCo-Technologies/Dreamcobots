"""
sandbox_runner.py — Orchestrates sandboxed AI experiments.

Provides an isolated execution context for A/B tests, adversarial tests,
and other experiment types managed by the DreamCo sandbox lab.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional


@dataclass
class SandboxResult:
    """Result produced by a single sandbox run."""

    run_id: str
    experiment_name: str
    status: str  # "success" | "failed" | "timeout"
    output: Any
    duration_ms: float
    started_at: str
    completed_at: str
    error: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)


class SandboxRunner:
    """
    Orchestrates sandboxed experiment execution.

    Parameters
    ----------
    timeout_ms : float
        Maximum allowed run duration in milliseconds (informational).
    enable_logging : bool
        When ``True``, each run is appended to the run history.
    """

    def __init__(self, timeout_ms: float = 30_000.0, enable_logging: bool = True):
        self.timeout_ms = timeout_ms
        self.enable_logging = enable_logging
        self._history: List[SandboxResult] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        experiment_name: str,
        fn: Callable[[], Any],
        metrics_fn: Optional[Callable[[Any], Dict[str, float]]] = None,
    ) -> SandboxResult:
        """
        Execute *fn* inside the sandbox and return a ``SandboxResult``.

        Parameters
        ----------
        experiment_name : str
            Human-readable name for this run.
        fn : callable
            Zero-argument callable containing the experiment logic.
        metrics_fn : callable | None
            Optional callable that receives the function output and
            returns a dict of metric name → value.
        """
        run_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc).isoformat()
        start_ns = self._now_ns()

        try:
            output = fn()
            status = "success"
            error = None
        except Exception as exc:  # noqa: BLE001
            output = None
            status = "failed"
            error = str(exc)

        end_ns = self._now_ns()
        duration_ms = (end_ns - start_ns) / 1_000_000
        completed_at = datetime.now(timezone.utc).isoformat()

        metrics: Dict[str, float] = {}
        if status == "success" and metrics_fn is not None:
            try:
                metrics = metrics_fn(output) or {}
            except Exception:  # noqa: BLE001
                pass

        result = SandboxResult(
            run_id=run_id,
            experiment_name=experiment_name,
            status=status,
            output=output,
            duration_ms=round(duration_ms, 3),
            started_at=started_at,
            completed_at=completed_at,
            error=error,
            metrics=metrics,
        )

        if self.enable_logging:
            self._history.append(result)

        return result

    def get_history(self) -> List[SandboxResult]:
        """Return all recorded run results."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear the run history."""
        self._history = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _now_ns() -> int:
        """Return a monotonic-like nanosecond timestamp."""
        import time
        return time.perf_counter_ns()
