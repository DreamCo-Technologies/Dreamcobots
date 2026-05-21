"""
DreamCo Platform — Durable Execution Runtime
=============================================

``ExecutionRuntime`` provides durable execution semantics inspired by Temporal
and Prefect:

* **Retry** — configurable attempts with back-off
* **Checkpoint** — save/restore intermediate state
* **Compensation** — run compensating actions on terminal failure
* **Resume** — restart from last checkpoint rather than from scratch

All in-flight executions are tracked so the Control Tower can enumerate and
introspect them.

Usage::

    runtime = ExecutionRuntime()

    def my_step(ctx: RuntimeContext) -> dict:
        ctx.checkpoint({"step": "done"})
        return {"result": 42}

    result = runtime.run("job_1", my_step, max_attempts=3)
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

class RuntimeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


# ---------------------------------------------------------------------------
# Context injected into steps
# ---------------------------------------------------------------------------

@dataclass
class RuntimeContext:
    job_id: str
    attempt: int
    last_checkpoint: dict[str, Any] = field(default_factory=dict)
    _checkpoints: list[dict[str, Any]] = field(default_factory=list, repr=False)

    def checkpoint(self, state: dict[str, Any]) -> None:
        """Save *state* as the latest checkpoint for this execution."""
        self._checkpoints.append(dict(state))
        self.last_checkpoint = dict(state)

    def all_checkpoints(self) -> list[dict[str, Any]]:
        return list(self._checkpoints)


# ---------------------------------------------------------------------------
# Execution record
# ---------------------------------------------------------------------------

@dataclass
class ExecutionRecord:
    job_id: str
    status: RuntimeStatus = RuntimeStatus.PENDING
    result: Any = None
    error: str | None = None
    attempts: int = 0
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    checkpoints: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "attempts": self.attempts,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "checkpoints": self.checkpoints,
        }


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------

StepFn = Callable[[RuntimeContext], Any]
CompensationFn = Callable[[ExecutionRecord], None]


class ExecutionRuntime:
    """Durable execution runtime with retry, checkpoint, and compensation.

    Parameters
    ----------
    default_max_attempts:
        Default number of attempts if not specified per-call.
    default_backoff_seconds:
        Seconds to wait between attempts.
    """

    def __init__(
        self,
        default_max_attempts: int = 3,
        default_backoff_seconds: float = 1.0,
    ) -> None:
        self._lock = threading.Lock()
        self._records: dict[str, ExecutionRecord] = {}
        self._default_max_attempts = default_max_attempts
        self._default_backoff = default_backoff_seconds

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        job_id: str | None = None,
        step: StepFn | None = None,
        *,
        max_attempts: int | None = None,
        backoff_seconds: float | None = None,
        compensation: CompensationFn | None = None,
    ) -> ExecutionRecord:
        """Execute *step* with retry/compensation semantics.

        Parameters
        ----------
        job_id:
            Unique identifier for this execution.  Auto-generated if None.
        step:
            Callable ``(RuntimeContext) → Any``.
        max_attempts:
            Override default retry count.
        backoff_seconds:
            Override default back-off.
        compensation:
            Called on terminal failure with the failed ``ExecutionRecord``.
        """
        jid = job_id or str(uuid.uuid4())
        attempts = max_attempts if max_attempts is not None else self._default_max_attempts
        backoff = backoff_seconds if backoff_seconds is not None else self._default_backoff

        record = ExecutionRecord(job_id=jid, status=RuntimeStatus.RUNNING)
        with self._lock:
            self._records[jid] = record

        last_error: str | None = None
        for attempt in range(1, attempts + 1):
            record.attempts = attempt
            ctx = RuntimeContext(job_id=jid, attempt=attempt)
            if record.checkpoints:
                ctx.last_checkpoint = record.checkpoints[-1]

            try:
                if step is not None:
                    result = step(ctx)
                else:
                    result = None
                record.checkpoints.extend(ctx.all_checkpoints())
                record.status = RuntimeStatus.SUCCEEDED
                record.result = result
                record.finished_at = time.time()
                return record
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                record.checkpoints.extend(ctx.all_checkpoints())
                if attempt < attempts and backoff > 0:
                    time.sleep(backoff)

        record.status = RuntimeStatus.FAILED
        record.error = last_error
        record.finished_at = time.time()

        if compensation is not None:
            record.status = RuntimeStatus.COMPENSATING
            try:
                compensation(record)
                record.status = RuntimeStatus.COMPENSATED
            except Exception as exc:  # noqa: BLE001
                record.error = f"{last_error} | compensation failed: {exc}"
                record.status = RuntimeStatus.FAILED

        return record

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_record(self, job_id: str) -> ExecutionRecord | None:
        with self._lock:
            return self._records.get(job_id)

    def all_records(self) -> list[ExecutionRecord]:
        with self._lock:
            return list(self._records.values())

    def running_count(self) -> int:
        with self._lock:
            return sum(
                1 for r in self._records.values()
                if r.status == RuntimeStatus.RUNNING
            )

    def stats(self) -> dict[str, Any]:
        with self._lock:
            records = list(self._records.values())
        counts: dict[str, int] = {}
        for r in records:
            counts[r.status.value] = counts.get(r.status.value, 0) + 1
        return {"total": len(records), **counts}
