"""
DreamCo Platform — Universal Correlation Chain
===============================================

Every request flowing through the DreamCo platform carries a
``CorrelationChain`` — an immutable bundle of IDs that links together:

* the originating HTTP/gRPC/event request (``request_id``)
* the distributed trace it belongs to (``trace_id``)
* the workflow being executed (``workflow_id``)
* the learning decision that triggered or was triggered by it (``decision_id``)
* the atomic execution unit (``execution_id``)
* the user/agent session (``session_id``)

Having all six IDs in every log line, telemetry event, and audit entry
enables full replay, causal analysis, learning attribution, ROI attribution,
debugging, and autonomous optimisation.

Usage
-----
::

    chain = CorrelationChain.new()
    # propagate into a child span
    child = chain.derive(workflow_id="wf_abc123")
    headers = child.to_headers()          # inject into HTTP call
    received = CorrelationChain.from_headers(headers)   # extract on the other side
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Header names — keep in sync with any API gateway / load-balancer config
# ---------------------------------------------------------------------------

_H_REQUEST_ID  = "x-dreamco-request-id"
_H_TRACE_ID    = "x-dreamco-trace-id"
_H_WORKFLOW_ID = "x-dreamco-workflow-id"
_H_DECISION_ID = "x-dreamco-decision-id"
_H_EXEC_ID     = "x-dreamco-execution-id"
_H_SESSION_ID  = "x-dreamco-session-id"

HEADER_MAP: Dict[str, str] = {
    "request_id":   _H_REQUEST_ID,
    "trace_id":     _H_TRACE_ID,
    "workflow_id":  _H_WORKFLOW_ID,
    "decision_id":  _H_DECISION_ID,
    "execution_id": _H_EXEC_ID,
    "session_id":   _H_SESSION_ID,
}


def _new_id() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# CorrelationChain
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CorrelationChain:
    """
    Immutable bundle of cross-system correlation IDs.

    Every subsystem (orchestrator, learning loop, event router, gateway)
    should accept a ``CorrelationChain`` and pass it — or a :meth:`derive`
    variant — to all downstream calls.

    Attributes
    ----------
    request_id : str
        Unique ID for the originating HTTP / event request.
    trace_id : str
        Distributed trace ID shared across all spans of one logical trace.
    workflow_id : str
        ID of the workflow being executed (may be empty for non-workflow ops).
    decision_id : str
        ID of the learning decision that produced or was produced by this op.
    execution_id : str
        ID of the atomic execution unit (single capability invocation, etc.).
    session_id : str
        ID of the user/agent session that initiated the operation.
    """

    request_id:   str = field(default_factory=_new_id)
    trace_id:     str = field(default_factory=_new_id)
    workflow_id:  str = ""
    decision_id:  str = ""
    execution_id: str = field(default_factory=_new_id)
    session_id:   str = ""

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    @classmethod
    def new(
        cls,
        *,
        workflow_id: str = "",
        decision_id: str = "",
        session_id: str = "",
    ) -> "CorrelationChain":
        """Create a brand-new chain, optionally seeding optional IDs."""
        return cls(
            request_id=_new_id(),
            trace_id=_new_id(),
            workflow_id=workflow_id,
            decision_id=decision_id,
            execution_id=_new_id(),
            session_id=session_id,
        )

    def derive(self, **overrides: str) -> "CorrelationChain":
        """
        Produce a child chain that inherits the trace / session context but
        gets a fresh ``request_id`` and ``execution_id`` (unless overridden).

        Useful when fanning out to sub-workflows or child capabilities.

        Example::

            child = chain.derive(workflow_id="wf_sub_123")
        """
        import dataclasses
        base = dataclasses.asdict(self)
        base["request_id"] = _new_id()
        base["execution_id"] = _new_id()
        base.update(overrides)
        return CorrelationChain(**base)

    # ------------------------------------------------------------------
    # Header injection / extraction
    # ------------------------------------------------------------------

    def to_headers(self) -> Dict[str, str]:
        """Serialise the chain as HTTP header key-value pairs."""
        headers: Dict[str, str] = {}
        for field_name, header_name in HEADER_MAP.items():
            value = getattr(self, field_name, "")
            if value:
                headers[header_name] = value
        return headers

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> "CorrelationChain":
        """
        Reconstruct a ``CorrelationChain`` from HTTP headers.

        Unknown / missing headers are replaced with fresh IDs or empty strings
        so the chain is always valid.
        """
        reverse = {v: k for k, v in HEADER_MAP.items()}
        kwargs: Dict[str, Any] = {}
        for header_name, field_name in reverse.items():
            kwargs[field_name] = headers.get(header_name, "") or ""
        # Ensure mandatory IDs always exist
        if not kwargs.get("request_id"):
            kwargs["request_id"] = _new_id()
        if not kwargs.get("trace_id"):
            kwargs["trace_id"] = _new_id()
        if not kwargs.get("execution_id"):
            kwargs["execution_id"] = _new_id()
        return cls(**kwargs)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain dict of all IDs (useful for log injection)."""
        return {
            "request_id":   self.request_id,
            "trace_id":     self.trace_id,
            "workflow_id":  self.workflow_id,
            "decision_id":  self.decision_id,
            "execution_id": self.execution_id,
            "session_id":   self.session_id,
        }

    def __repr__(self) -> str:
        return (
            f"CorrelationChain(req={self.request_id[:8]}, "
            f"trace={self.trace_id[:8]}, wf={self.workflow_id[:8] or '-'})"
        )
