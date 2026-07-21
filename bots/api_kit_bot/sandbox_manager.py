"""
Sandbox Manager — secure testing environments for the DreamCo API Kit Bot.

Each sandbox is an isolated testing context with its own secret key,
lifecycle management, analytics, and expiry controls.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import hashlib
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401

_SANDBOX_LIFETIME_DAYS = 30


def _generate_secret_key() -> str:
    """Generate a cryptographically strong sandbox secret key."""
    raw = (uuid.uuid4().hex + uuid.uuid4().hex).encode()
    digest = hashlib.sha256(raw).hexdigest()
    return f"sk_sandbox_{digest}"


class SandboxManager:
    """Create and manage isolated sandbox environments with secret key auth."""

    def __init__(self) -> None:
        self._sandboxes: dict = {}

    # ------------------------------------------------------------------
    # Core sandbox operations
    # ------------------------------------------------------------------

    def create_sandbox(
        self,
        owner_id: str,
        name: str,
        kit_id: Optional[str] = None,
    ) -> dict:
        """Create a new sandbox environment.

        Returns a sandbox record including a freshly generated secret key.
        """
        sandbox_id = f"sbx_{uuid.uuid4().hex[:12]}"
        secret_key = _generate_secret_key()
        now = datetime.now(tz=timezone.utc)
        expires_at = now + timedelta(days=_SANDBOX_LIFETIME_DAYS)

        record = {
            "sandbox_id": sandbox_id,
            "owner_id": owner_id,
            "name": name,
            "kit_id": kit_id,
            "secret_key": secret_key,
            "status": "ACTIVE",
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "requests_count": 0,
            "total_response_time_ms": 0,
            "success_count": 0,
            "error_count": 0,
            "endpoint_hits": {},
        }
        self._sandboxes[sandbox_id] = record
        return {k: v for k, v in record.items() if k != "endpoint_hits"}

    def get_sandbox(self, sandbox_id: str) -> dict:
        """Return sandbox metadata (excluding internal hit counters)."""
        record = self._sandboxes.get(sandbox_id)
        if record is None:
            return {"error": f"Sandbox '{sandbox_id}' not found."}
        return {k: v for k, v in record.items() if k not in ("endpoint_hits",)}

    def validate_secret_key(self, sandbox_id: str, secret_key: str) -> bool:
        """Return True if the secret key matches the sandbox."""
        record = self._sandboxes.get(sandbox_id)
        if record is None:
            return False
        return record["secret_key"] == secret_key

    def rotate_secret_key(self, sandbox_id: str) -> dict:
        """Generate and store a new secret key for the sandbox."""
        record = self._sandboxes.get(sandbox_id)
        if record is None:
            return {"error": f"Sandbox '{sandbox_id}' not found."}
        new_key = _generate_secret_key()
        record["secret_key"] = new_key
        return {"sandbox_id": sandbox_id, "secret_key": new_key, "rotated": True}

    def deactivate_sandbox(self, sandbox_id: str) -> dict:
        """Set sandbox status to INACTIVE."""
        record = self._sandboxes.get(sandbox_id)
        if record is None:
            return {"error": f"Sandbox '{sandbox_id}' not found."}
        record["status"] = "INACTIVE"
        return {"sandbox_id": sandbox_id, "status": "INACTIVE"}

    def list_sandboxes(self, owner_id: str) -> list:
        """Return all sandboxes owned by *owner_id*."""
        return [
            {k: v for k, v in rec.items() if k not in ("endpoint_hits",)}
            for rec in self._sandboxes.values()
            if rec["owner_id"] == owner_id
        ]

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def record_request(
        self,
        sandbox_id: str,
        endpoint: str,
        response_time_ms: int,
        success: bool,
    ) -> None:
        """Record a single API request against the sandbox (internal helper)."""
        record = self._sandboxes.get(sandbox_id)
        if record is None:
            return
        record["requests_count"] += 1
        record["total_response_time_ms"] += response_time_ms
        if success:
            record["success_count"] += 1
        else:
            record["error_count"] += 1
        hits = record["endpoint_hits"]
        hits[endpoint] = hits.get(endpoint, 0) + 1

    def get_sandbox_analytics(self, sandbox_id: str) -> dict:
        """Return request analytics for a sandbox."""
        record = self._sandboxes.get(sandbox_id)
        if record is None:
            return {"error": f"Sandbox '{sandbox_id}' not found."}
        total = record["requests_count"]
        avg_rt = (
            record["total_response_time_ms"] / total if total > 0 else 0
        )
        success_rate = record["success_count"] / total if total > 0 else 0.0
        error_rate = record["error_count"] / total if total > 0 else 0.0
        top_endpoints = sorted(
            record["endpoint_hits"].items(), key=lambda x: x[1], reverse=True
        )[:5]
        return {
            "sandbox_id": sandbox_id,
            "requests_count": total,
            "avg_response_time_ms": round(avg_rt, 2),
            "success_rate": round(success_rate, 4),
            "error_rate": round(error_rate, 4),
            "top_endpoints": [{"endpoint": e, "hits": h} for e, h in top_endpoints],
        }

    # ------------------------------------------------------------------
    # Expiry management
    # ------------------------------------------------------------------

    def check_expiry(self, sandbox_id: str) -> dict:
        """Return expiry information for the sandbox."""
        record = self._sandboxes.get(sandbox_id)
        if record is None:
            return {"error": f"Sandbox '{sandbox_id}' not found."}
        now = datetime.now(tz=timezone.utc)
        expires_at = datetime.fromisoformat(record["expires_at"])
        delta = expires_at - now
        is_expired = delta.total_seconds() <= 0
        days_remaining = max(0, delta.days)
        return {
            "sandbox_id": sandbox_id,
            "is_expired": is_expired,
            "days_remaining": days_remaining,
            "expires_at": record["expires_at"],
        }

    def auto_expire_sandboxes(self) -> list:
        """Deactivate all expired sandboxes and return their IDs."""
        expired_ids: list = []
        now = datetime.now(tz=timezone.utc)
        for sandbox_id, record in self._sandboxes.items():
            if record["status"] != "ACTIVE":
                continue
            expires_at = datetime.fromisoformat(record["expires_at"])
            if now >= expires_at:
                record["status"] = "INACTIVE"
                expired_ids.append(sandbox_id)
        return expired_ids
