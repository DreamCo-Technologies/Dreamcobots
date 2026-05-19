"""
DreamCo Platform — Execution Edge Module
=========================================

Re-exports ``ExecutionEdge`` and ``EdgeCondition`` from
``capabilities.models`` under a dedicated module name, matching the Phase 2
blueprint layout.

Additional helper ``EdgeBuilder`` provides a fluent API for constructing
edges without importing from ``models`` directly.
"""

from __future__ import annotations

from dreamco_platform.capabilities.models import (  # noqa: F401
    EdgeCondition,
    ExecutionEdge,
)


class EdgeBuilder:
    """Fluent builder for ``ExecutionEdge`` objects.

    Usage::

        edge = EdgeBuilder("scrape").to("enrich").on_success().build()
    """

    def __init__(self, from_id: str) -> None:
        self._from = from_id
        self._to: str = ""
        self._condition: EdgeCondition = EdgeCondition.ON_SUCCESS
        self._weight: float = 1.0
        self._metadata: dict = {}

    def to(self, to_id: str) -> "EdgeBuilder":
        self._to = to_id
        return self

    def on_success(self) -> "EdgeBuilder":
        self._condition = EdgeCondition.ON_SUCCESS
        return self

    def on_failure(self) -> "EdgeBuilder":
        self._condition = EdgeCondition.ON_FAILURE
        return self

    def always(self) -> "EdgeBuilder":
        self._condition = EdgeCondition.ALWAYS
        return self

    def weight(self, w: float) -> "EdgeBuilder":
        self._weight = w
        return self

    def with_metadata(self, key: str, value) -> "EdgeBuilder":
        self._metadata[key] = value
        return self

    def build(self) -> ExecutionEdge:
        if not self._to:
            raise ValueError("Edge target (to) must be set before calling build()")
        return ExecutionEdge(
            from_id=self._from,
            to_id=self._to,
            condition=self._condition,
            metadata=self._metadata,
        )


__all__ = ["ExecutionEdge", "EdgeCondition", "EdgeBuilder"]
