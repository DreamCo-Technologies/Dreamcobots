"""
DreamCo Platform — Workflow Memory
=====================================

``WorkflowMemory`` stores per-workflow operational context:
* Step results and checkpoints
* Profitability by execution path
* Retry histories
* Learning signals

Built on top of ``MemoryStore``.

Usage::

    wm = WorkflowMemory()
    wm.record_step_result("wf:lead_pipeline", "lead.scrape", success=True, cost_usd=0.01)
    wm.record_profitability("wf:lead_pipeline", path="fast_path", value_usd=12.50)
    wm.get_profitability_history("wf:lead_pipeline")
"""

from __future__ import annotations

from typing import Any

from dreamco_platform.memory.memory_store import MemoryRecord, MemoryStore, MemoryType


class WorkflowMemory:
    """Per-workflow persistent memory layer."""

    def __init__(self, store: MemoryStore | None = None) -> None:
        self._store = store or MemoryStore()

    def _subject(self, workflow_id: str) -> str:
        return f"workflow:{workflow_id}"

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    def record_step_result(
        self,
        workflow_id: str,
        step_id: str,
        success: bool,
        cost_usd: float = 0.0,
        duration_ms: float = 0.0,
        importance: float = 0.4,
        context: dict[str, Any] | None = None,
    ) -> MemoryRecord:
        ctx = dict(context or {})
        ctx.update({"step_id": step_id, "success": success, "cost_usd": cost_usd, "duration_ms": duration_ms})
        record = MemoryRecord(
            subject=self._subject(workflow_id),
            memory_type=MemoryType.OUTCOME,
            content=f"step={step_id} success={success} cost={cost_usd:.4f}",
            importance=importance,
            context=ctx,
            tags=["step_result"],
        )
        self._store.write(record)
        return record

    def record_profitability(
        self,
        workflow_id: str,
        path: str,
        value_usd: float,
        importance: float = 0.7,
        context: dict[str, Any] | None = None,
    ) -> MemoryRecord:
        ctx = dict(context or {})
        ctx.update({"path": path, "value_usd": value_usd})
        record = MemoryRecord(
            subject=self._subject(workflow_id),
            memory_type=MemoryType.PROFITABILITY,
            content=f"path={path} value={value_usd:.4f}",
            importance=importance,
            context=ctx,
            tags=["profitability"],
        )
        self._store.write(record)
        return record

    def record_retry(
        self,
        workflow_id: str,
        step_id: str,
        attempt: int,
        reason: str,
        importance: float = 0.6,
    ) -> MemoryRecord:
        record = MemoryRecord(
            subject=self._subject(workflow_id),
            memory_type=MemoryType.ANOMALY,
            content=f"retry step={step_id} attempt={attempt} reason={reason}",
            importance=importance,
            context={"step_id": step_id, "attempt": attempt, "reason": reason},
            tags=["retry"],
        )
        self._store.write(record)
        return record

    def record_learning_signal(
        self,
        workflow_id: str,
        signal: str,
        strength: float = 0.5,
        context: dict[str, Any] | None = None,
    ) -> MemoryRecord:
        ctx = dict(context or {})
        ctx["strength"] = strength
        record = MemoryRecord(
            subject=self._subject(workflow_id),
            memory_type=MemoryType.LEARNING_SIGNAL,
            content=signal,
            importance=strength,
            context=ctx,
            tags=["learning"],
        )
        self._store.write(record)
        return record

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def get_step_results(self, workflow_id: str, limit: int = 50) -> list[MemoryRecord]:
        return [
            r for r in self._store.recall(self._subject(workflow_id), limit=limit)
            if "step_result" in r.tags
        ]

    def get_profitability_history(self, workflow_id: str, limit: int = 20) -> list[MemoryRecord]:
        return self._store.recall(
            self._subject(workflow_id),
            memory_type=MemoryType.PROFITABILITY,
            limit=limit,
        )

    def get_retry_history(self, workflow_id: str, limit: int = 20) -> list[MemoryRecord]:
        return [
            r for r in self._store.recall(self._subject(workflow_id), limit=limit)
            if "retry" in r.tags
        ]

    def get_learning_signals(self, workflow_id: str, limit: int = 20) -> list[MemoryRecord]:
        return self._store.recall(
            self._subject(workflow_id),
            memory_type=MemoryType.LEARNING_SIGNAL,
            limit=limit,
        )

    def total_cost(self, workflow_id: str) -> float:
        results = self.get_step_results(workflow_id, limit=10_000)
        return sum(r.context.get("cost_usd", 0.0) for r in results)
