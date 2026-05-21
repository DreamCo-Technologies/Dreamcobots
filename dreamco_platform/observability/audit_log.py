"""
DreamCo Platform — Structured Audit Log
=========================================

Every security-relevant, governance-relevant, or compliance-relevant action
MUST be written to the audit log.  The audit log is append-only, immutable
within a session, and exportable to a persistent store.

Audit events capture: WHO did WHAT to WHICH resource, WHEN, with WHAT outcome.

Usage::

    log = AuditLog()
    log.record(
        actor="user:alice",
        action="capability.invoked",
        resource="lead.scrape",
        outcome="success",
        metadata={"cost_usd": 0.01},
    )
    entries = log.query(actor="user:alice", limit=10)
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque


# ---------------------------------------------------------------------------
# Audit entry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AuditEntry:
    entry_id: str
    timestamp: float
    actor: str           # e.g. "user:alice", "bot:lead_gen_bot", "system"
    action: str          # e.g. "capability.invoked", "policy.violated"
    resource: str        # e.g. "lead.scrape", "workspace:acme"
    outcome: str         # "success" | "failure" | "denied" | "pending"
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "action": self.action,
            "resource": self.resource,
            "outcome": self.outcome,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

class AuditLog:
    """Append-only in-memory audit log.

    Parameters
    ----------
    max_entries:
        Maximum number of entries kept in memory (FIFO eviction).
    """

    VALID_OUTCOMES: frozenset[str] = frozenset(
        {"success", "failure", "denied", "pending", "error"}
    )

    def __init__(self, max_entries: int = 100_000) -> None:
        self._lock = threading.Lock()
        self._log: Deque[AuditEntry] = deque(maxlen=max_entries)
        self._total: int = 0

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def record(
        self,
        actor: str,
        action: str,
        resource: str,
        outcome: str,
        metadata: dict[str, Any] | None = None,
        timestamp: float | None = None,
    ) -> AuditEntry:
        """Append an audit entry and return it."""
        if outcome not in self.VALID_OUTCOMES:
            raise ValueError(
                f"outcome '{outcome}' is invalid; must be one of {sorted(self.VALID_OUTCOMES)}"
            )
        entry = AuditEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=timestamp if timestamp is not None else time.time(),
            actor=actor,
            action=action,
            resource=resource,
            outcome=outcome,
            metadata=metadata or {},
        )
        with self._lock:
            self._log.append(entry)
            self._total += 1
        return entry

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(
        self,
        actor: str | None = None,
        action: str | None = None,
        resource: str | None = None,
        outcome: str | None = None,
        since: float | None = None,
        until: float | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Return entries matching all supplied filters, most-recent first."""
        with self._lock:
            entries = list(self._log)

        results = []
        for entry in reversed(entries):
            if actor and entry.actor != actor:
                continue
            if action and entry.action != action:
                continue
            if resource and entry.resource != resource:
                continue
            if outcome and entry.outcome != outcome:
                continue
            if since and entry.timestamp < since:
                continue
            if until and entry.timestamp > until:
                continue
            results.append(entry)
            if len(results) >= limit:
                break
        return results

    def all_entries(self) -> list[AuditEntry]:
        with self._lock:
            return list(self._log)

    def total_recorded(self) -> int:
        return self._total

    def stats(self) -> dict[str, Any]:
        with self._lock:
            entries = list(self._log)
        outcome_counts: dict[str, int] = {}
        for e in entries:
            outcome_counts[e.outcome] = outcome_counts.get(e.outcome, 0) + 1
        return {
            "total_recorded": self._total,
            "stored": len(entries),
            "by_outcome": outcome_counts,
        }
