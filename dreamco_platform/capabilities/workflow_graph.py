"""
DreamCo Platform — WorkflowGraph Module
========================================

Re-exports ``WorkflowGraph`` and ``ExecutionEdge`` from
``capabilities.models`` under a dedicated module name, matching the Phase 2
blueprint file layout.
"""

from dreamco_platform.capabilities.models import (  # noqa: F401
    ExecutionEdge,
    WorkflowGraph,
)

__all__ = ["WorkflowGraph", "ExecutionEdge"]
