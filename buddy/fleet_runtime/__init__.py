"""Shared DreamCo fleet runtime.

Bots are manifests (config/bots/bot-manifests.generated.json) executed by a
small set of shared capability engines. This package is the canonical Python
executor; it reuses Buddy's existing pieces instead of forking them:

- model routing: ``buddy.openrouter.gateway.BuddyGateway`` (live, opt-in only)
- local routing heuristics: ``buddy.local_core``
- guardrails: ``buddy.safety.guardrails.review``
- permission levels: ``buddy_os/governance/approval_policy.yaml``
- readiness ladder: ``buddy_os/governance/release_readiness.yaml``

Offline/deterministic mode is the default so smoke tests run in CI without
secrets. Offline output is a deterministic engine result, never a claim that a
model or an external service was used.
"""
from __future__ import annotations

from .contract import CONTRACT_PIECES, ENGINES, READINESS_STATES, load_manifests
from .executor import FleetExecutor, run_bot

__all__ = [
    "CONTRACT_PIECES",
    "ENGINES",
    "READINESS_STATES",
    "FleetExecutor",
    "load_manifests",
    "run_bot",
]
