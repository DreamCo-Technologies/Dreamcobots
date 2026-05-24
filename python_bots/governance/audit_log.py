"""
DreamCo OS — Governance Audit Log
====================================

Append-only, tamper-evident audit log for all governance events.
Wraps the platform audit log with bot-governance-specific helpers.
"""

from __future__ import annotations

import json
import os
import threading
import time
import uuid
from typing import Any


class GovernanceAuditLog:
    """File-backed append-only audit log.

    Parameters
    ----------
    log_file:
        Path to the JSONL audit log file.  Reads ``AUDIT_LOG_FILE`` env-var;
        defaults to ``"dreamco_audit.jsonl"``.
    """

    def __init__(self, log_file: str | None = None) -> None:
        self._path = log_file or os.getenv("AUDIT_LOG_FILE", "dreamco_audit.jsonl")
        self._lock = threading.Lock()
        self._in_memory: list[dict[str, Any]] = []

    def record(
        self,
        actor: str,
        action: str,
        resource: str,
        outcome: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Append an audit entry and return its entry_id."""
        entry = {
            "entry_id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "actor": actor,
            "action": action,
            "resource": resource,
            "outcome": outcome,
            "metadata": metadata or {},
        }
        with self._lock:
            self._in_memory.append(entry)
            try:
                with open(self._path, "a") as f:
                    f.write(json.dumps(entry) + "\n")
            except OSError:
                pass  # in-memory log still records it
        return entry["entry_id"]

    def query(
        self,
        actor: str | None = None,
        action: str | None = None,
        outcome: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return matching entries from the in-memory log, most-recent first."""
        with self._lock:
            entries = list(reversed(self._in_memory))
        results = []
        for e in entries:
            if actor and e["actor"] != actor:
                continue
            if action and e["action"] != action:
                continue
            if outcome and e["outcome"] != outcome:
                continue
            results.append(e)
            if len(results) >= limit:
                break
        return results

    def stats(self) -> dict[str, Any]:
        with self._lock:
            total = len(self._in_memory)
        return {"total_entries": total, "log_file": self._path}
