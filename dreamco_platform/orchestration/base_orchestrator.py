"""
DreamCo Platform — Base Orchestrator Interface
===============================================

All orchestrators in the DreamCo platform (BuddyOrchestrator,
RevenueOrchestrator, GlobalLearningLoop, etc.) must implement this
interface so that the platform can:

* Track and introspect every active orchestrator from a single registry
* Route workflow → event bus → orchestrator → subscribers → analytics
* Support durable execution state (retries, resume, compensation) via the
  ``ExecutionContext`` abstraction

Design notes
------------
``BaseOrchestrator`` is an abstract base class.  Concrete orchestrators
subclass it and implement the three abstract methods: ``execute``,
``status``, and ``shutdown``.

``OrchestratorRegistry`` is a lightweight singleton-pattern class that
tracks every active orchestrator instance so that the Control Tower and
platform diagnostics can enumerate them.
"""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Orchestrator status
# ---------------------------------------------------------------------------

class OrchestratorStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


# ---------------------------------------------------------------------------
# Execution context — durable execution state
# ---------------------------------------------------------------------------

@dataclass
class ExecutionContext:
    """
    Durable execution state for a single orchestrator run.

    Carries all information needed to retry, resume, or replay an execution.

    Attributes
    ----------
    execution_id : str
        Unique run identifier.
    workflow_id : str
        The workflow or graph ID being executed.
    correlation_id : str
        End-to-end trace ID shared with all emitted events.
    inputs : dict
        Original inputs to this execution.
    outputs : dict
        Accumulated outputs from completed steps.
    status : str
        Current state: ``"pending"`` | ``"running"`` | ``"completed"`` |
        ``"failed"`` | ``"compensating"``.
    attempts : int
        How many times this execution has been attempted.
    max_attempts : int
        Maximum allowed attempts.
    started_at : float
        Unix timestamp of first attempt.
    completed_at : float | None
        Unix timestamp of completion/failure.
    error : str | None
        Last recorded error message.
    checkpoint : dict
        Arbitrary state saved between steps (enables resumability).
    metadata : dict
        Arbitrary extra metadata.
    """

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    attempts: int = 0
    max_attempts: int = 3
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    error: Optional[str] = None
    checkpoint: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def mark_started(self) -> None:
        """Increment attempt counter and set status to running."""
        self.attempts += 1
        self.status = "running"

    def mark_completed(self, outputs: Dict[str, Any]) -> None:
        """Record successful completion."""
        self.outputs = outputs
        self.status = "completed"
        self.completed_at = time.time()

    def mark_failed(self, error: str) -> None:
        """Record failure."""
        self.error = error
        self.status = "failed" if self.attempts >= self.max_attempts else "retrying"
        self.completed_at = time.time()

    def can_retry(self) -> bool:
        """Return ``True`` if another attempt is permitted."""
        return self.attempts < self.max_attempts and self.status not in (
            "completed",
            "compensating",
        )

    def save_checkpoint(self, state: Dict[str, Any]) -> None:
        """Persist intermediate state for resumability."""
        self.checkpoint.update(state)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "checkpoint": self.checkpoint,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Base orchestrator
# ---------------------------------------------------------------------------

class BaseOrchestrator(ABC):
    """
    Abstract base class for all DreamCo orchestrators.

    Every orchestrator (BuddyOrchestrator, RevenueOrchestrator, etc.)
    must subclass ``BaseOrchestrator`` and implement the three abstract
    methods so that the platform registry and Control Tower can interact
    with all orchestrators uniformly.

    Attributes
    ----------
    orchestrator_id : str
        Unique identifier for this orchestrator instance.
    name : str
        Human-readable name.
    """

    def __init__(self, orchestrator_id: str = "", name: str = "") -> None:
        self.orchestrator_id: str = orchestrator_id or str(uuid.uuid4())
        self.name: str = name or self.__class__.__name__
        self._status: OrchestratorStatus = OrchestratorStatus.IDLE
        self._executions: Dict[str, ExecutionContext] = {}
        self._created_at: float = time.time()

    # ------------------------------------------------------------------
    # Abstract interface — must be implemented by subclasses
    # ------------------------------------------------------------------

    @abstractmethod
    def execute(self, context: ExecutionContext) -> ExecutionContext:
        """
        Execute the workflow described by *context*.

        Implementations should:
        1. Call ``context.mark_started()`` at the top.
        2. Perform the orchestration work.
        3. Call ``context.mark_completed(outputs)`` on success or
           ``context.mark_failed(error)`` on failure.
        4. Return the modified context.

        Parameters
        ----------
        context : ExecutionContext
            Durable execution state for this run.

        Returns
        -------
        ExecutionContext
            Updated context with outcome recorded.
        """
        ...

    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """
        Return a status snapshot of this orchestrator.

        Must include at minimum:
        ``{"orchestrator_id": ..., "name": ..., "status": ..., "uptime_s": ...}``
        """
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """Gracefully stop the orchestrator and release resources."""
        ...

    # ------------------------------------------------------------------
    # Execution management helpers
    # ------------------------------------------------------------------

    def create_context(
        self,
        workflow_id: str = "",
        inputs: Dict[str, Any] | None = None,
        max_attempts: int = 3,
        correlation_id: str | None = None,
    ) -> ExecutionContext:
        """Create and register a new ``ExecutionContext`` for *workflow_id*."""
        ctx = ExecutionContext(
            workflow_id=workflow_id,
            inputs=inputs or {},
            max_attempts=max_attempts,
        )
        if correlation_id:
            ctx.correlation_id = correlation_id
        self._executions[ctx.execution_id] = ctx
        return ctx

    def get_context(self, execution_id: str) -> Optional[ExecutionContext]:
        """Return the context for *execution_id*, or ``None``."""
        return self._executions.get(execution_id)

    def list_contexts(self, status_filter: str | None = None) -> List[ExecutionContext]:
        """Return all registered contexts, optionally filtered by status."""
        contexts = list(self._executions.values())
        if status_filter:
            contexts = [c for c in contexts if c.status == status_filter]
        return contexts

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def orchestrator_status(self) -> OrchestratorStatus:
        return self._status

    @orchestrator_status.setter
    def orchestrator_status(self, value: OrchestratorStatus) -> None:
        self._status = value

    def uptime_seconds(self) -> float:
        return time.time() - self._created_at

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self.orchestrator_id!r}, "
            f"name={self.name!r}, "
            f"status={self._status.value!r})"
        )


# ---------------------------------------------------------------------------
# Orchestrator registry
# ---------------------------------------------------------------------------

class OrchestratorRegistry:
    """
    Lightweight registry for all active orchestrator instances.

    The Control Tower and platform diagnostics query this registry to
    enumerate running orchestrators without hard-coding imports.
    """

    def __init__(self) -> None:
        self._orchestrators: Dict[str, BaseOrchestrator] = {}

    def register(self, orchestrator: BaseOrchestrator) -> None:
        """Register *orchestrator* by its ``orchestrator_id``."""
        self._orchestrators[orchestrator.orchestrator_id] = orchestrator

    def unregister(self, orchestrator_id: str) -> Optional[BaseOrchestrator]:
        """Remove and return the orchestrator, or ``None``."""
        return self._orchestrators.pop(orchestrator_id, None)

    def get(self, orchestrator_id: str) -> Optional[BaseOrchestrator]:
        """Return the orchestrator for *orchestrator_id*, or ``None``."""
        return self._orchestrators.get(orchestrator_id)

    def list_all(self) -> List[BaseOrchestrator]:
        """Return all registered orchestrators sorted by name."""
        return sorted(self._orchestrators.values(), key=lambda o: o.name)

    def status_summary(self) -> List[Dict[str, Any]]:
        """Return a status snapshot for every registered orchestrator."""
        return [o.status() for o in self.list_all()]

    def __len__(self) -> int:
        return len(self._orchestrators)

    def __contains__(self, orchestrator_id: str) -> bool:
        return orchestrator_id in self._orchestrators

    def __repr__(self) -> str:
        return f"OrchestratorRegistry({len(self._orchestrators)} orchestrators)"
