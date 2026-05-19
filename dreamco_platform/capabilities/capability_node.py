"""
DreamCo Platform — Capability Node Module
==========================================

Re-exports ``CapabilityNode``, ``ExecutionResult``, and ``EdgeCondition``
from ``capabilities.models`` under a dedicated module name, matching the
file layout prescribed by the Phase 2 blueprint.

Prefer importing from ``dreamco_platform.capabilities.models`` for the full
type set; use this module when you only need ``CapabilityNode``.
"""

from dreamco_platform.capabilities.models import (  # noqa: F401
    CapabilityNode,
    EdgeCondition,
    ExecutionResult,
    GovernancePolicy,
)

__all__ = ["CapabilityNode", "EdgeCondition", "ExecutionResult", "GovernancePolicy"]
