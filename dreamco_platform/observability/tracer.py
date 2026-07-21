"""
DreamCo Platform — Distributed Tracer
======================================

``Tracer`` provides span-based distributed tracing for capability executions.

Every ``CapabilityNode`` execution should create a span so that full
execution traces can be reconstructed across orchestrators and workers.

Design
------
* Spans are identified by ``span_id`` and linked to a parent via
  ``parent_span_id``.
* All spans belonging to the same request share a ``trace_id``
  (= ``correlation_id`` from the originating ``DreamCoEvent``).
* Completed spans are appended to a bounded in-memory store; export to an
  external backend (Jaeger, OTEL) is left to the application layer.

Usage::

    tracer = Tracer()
    with tracer.span("capability.lead_scrape", trace_id="t123") as span:
        span.set_tag("bot_id", "lead_gen_bot")
        result = do_work()
    # span is now finished and stored
"""

from __future__ import annotations

import contextlib
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Deque, Generator


# ---------------------------------------------------------------------------
# Span status
# ---------------------------------------------------------------------------

class SpanStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Span
# ---------------------------------------------------------------------------

@dataclass
class Span:
    span_id: str
    trace_id: str
    operation: str
    parent_span_id: str | None = None
    status: SpanStatus = SpanStatus.IN_PROGRESS
    tags: dict[str, Any] = field(default_factory=dict)
    logs: list[dict[str, Any]] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    error_message: str | None = None

    @property
    def duration_ms(self) -> float | None:
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000

    def set_tag(self, key: str, value: Any) -> None:
        self.tags[key] = value

    def log(self, message: str, **kwargs: Any) -> None:
        self.logs.append({"time": time.time(), "message": message, **kwargs})

    def finish(self, status: SpanStatus = SpanStatus.SUCCESS, error: str | None = None) -> None:
        self.end_time = time.time()
        self.status = status
        if error:
            self.error_message = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "operation": self.operation,
            "parent_span_id": self.parent_span_id,
            "status": self.status.value,
            "tags": self.tags,
            "logs": self.logs,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
        }


# ---------------------------------------------------------------------------
# Tracer
# ---------------------------------------------------------------------------

class Tracer:
    """Lightweight span-based distributed tracer."""

    def __init__(self, max_spans: int = 10_000) -> None:
        self._lock = threading.Lock()
        self._spans: Deque[Span] = deque(maxlen=max_spans)
        self._span_count: int = 0

    def start_span(
        self,
        operation: str,
        trace_id: str | None = None,
        parent_span_id: str | None = None,
    ) -> Span:
        span = Span(
            span_id=str(uuid.uuid4()),
            trace_id=trace_id or str(uuid.uuid4()),
            operation=operation,
            parent_span_id=parent_span_id,
        )
        return span

    def finish_span(self, span: Span, status: SpanStatus = SpanStatus.SUCCESS, error: str | None = None) -> None:
        span.finish(status=status, error=error)
        with self._lock:
            self._spans.append(span)
            self._span_count += 1

    @contextlib.contextmanager
    def span(
        self,
        operation: str,
        trace_id: str | None = None,
        parent_span_id: str | None = None,
    ) -> Generator[Span, None, None]:
        """Context manager that starts and finishes a span automatically."""
        s = self.start_span(operation, trace_id=trace_id, parent_span_id=parent_span_id)
        try:
            yield s
            self.finish_span(s, status=SpanStatus.SUCCESS)
        except Exception as exc:  # noqa: BLE001
            self.finish_span(s, status=SpanStatus.ERROR, error=str(exc))
            raise

    def trace_for(self, trace_id: str) -> list[Span]:
        with self._lock:
            return [s for s in self._spans if s.trace_id == trace_id]

    def recent_spans(self, n: int = 100) -> list[Span]:
        with self._lock:
            spans = list(self._spans)
        return spans[-n:]

    def stats(self) -> dict[str, Any]:
        with self._lock:
            spans = list(self._spans)
        status_counts: dict[str, int] = {}
        for s in spans:
            status_counts[s.status.value] = status_counts.get(s.status.value, 0) + 1
        return {
            "total_finished": self._span_count,
            "stored": len(spans),
            **status_counts,
        }
