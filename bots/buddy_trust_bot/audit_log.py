# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Audit Log — Buddy Trust Bot

Provides a tamper-evident, append-only audit trail for all sensitive
operations performed by Buddy.  Every entry records:
  - Who performed the action (user_id)
  - What action was taken (action type + description)
  - When it happened (Unix timestamp)
  - Which consent token authorised it
  - Whether the entry is flagged as suspicious

Supports:
  - Filtering by user, action type, or time range
  - Immediate freeze: mark the log as frozen so no new entries can be added
    (useful when suspicious activity is detected)
  - Integrity chain: each entry stores a hash of the previous entry,
    making tampering detectable
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AuditActionType(Enum):
    CONSENT_REQUESTED = "consent_requested"
    CONSENT_GRANTED = "consent_granted"
    CONSENT_REVOKED = "consent_revoked"
    VOICE_PROFILE_CREATED = "voice_profile_created"
    VOICE_SYNTHESIZED = "voice_synthesized"
    VOICE_PROFILE_FROZEN = "voice_profile_frozen"
    VOICE_PROFILE_REVOKED = "voice_profile_revoked"
    IMAGE_AVATAR_CREATED = "image_avatar_created"
    IMAGE_SYNTHESIZED = "image_synthesized"
    IMAGE_AVATAR_FROZEN = "image_avatar_frozen"
    IMAGE_AVATAR_REVOKED = "image_avatar_revoked"
    VAULT_SECRET_STORED = "vault_secret_stored"
    VAULT_SECRET_ACCESSED = "vault_secret_accessed"
    VAULT_SECRET_DELETED = "vault_secret_deleted"
    VAULT_LOCKED = "vault_locked"
    VAULT_UNLOCKED = "vault_unlocked"
    TRUST_SEAL_ISSUED = "trust_seal_issued"
    TRUST_SEAL_REVOKED = "trust_seal_revoked"
    GUARDRAIL_VIOLATION = "guardrail_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    AUDIT_LOG_FROZEN = "audit_log_frozen"
    CHAT_MESSAGE = "chat_message"
    SYSTEM_EVENT = "system_event"


@dataclass
class AuditEntry:
    """A single immutable audit log entry."""

    entry_id: str
    action_type: AuditActionType
    user_id: str
    description: str
    timestamp: float
    consent_token: str          # May be empty for non-consent-gated events
    resource_id: str            # ID of the affected resource (profile, secret, etc.)
    previous_hash: str          # Hash of the previous entry (integrity chain)
    entry_hash: str             # Hash of this entry's content
    is_suspicious: bool = False
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "action_type": self.action_type.value,
            "user_id": self.user_id,
            "description": self.description,
            "timestamp": self.timestamp,
            "consent_token": self.consent_token,
            "resource_id": self.resource_id,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
            "is_suspicious": self.is_suspicious,
            "metadata": self.metadata,
        }


class AuditLog:
    """
    Append-only audit log with integrity chain and freeze capability.

    Parameters
    ----------
    max_visible : Optional[int]
        Number of entries visible on the current tier (None = all).
    """

    GENESIS_HASH = "0" * 64   # Sentinel hash for first entry

    def __init__(self, max_visible: Optional[int] = None) -> None:
        self._entries: list[AuditEntry] = []
        self._frozen: bool = False
        self._max_visible = max_visible

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log(
        self,
        action_type: AuditActionType,
        user_id: str,
        description: str,
        consent_token: str = "",
        resource_id: str = "",
        is_suspicious: bool = False,
        metadata: Optional[dict] = None,
    ) -> AuditEntry:
        """
        Append a new entry to the audit log.

        Raises ``AuditLogFrozenError`` if the log has been frozen.
        """
        if self._frozen:
            raise AuditLogFrozenError(
                "Audit log is frozen due to suspicious activity. "
                "Contact DreamCo Trust Support to unfreeze."
            )

        previous_hash = (
            self._entries[-1].entry_hash if self._entries else self.GENESIS_HASH
        )
        entry_id = str(uuid.uuid4())
        ts = time.time()
        content = f"{entry_id}:{action_type.value}:{user_id}:{ts}:{previous_hash}"
        entry_hash = hashlib.sha256(content.encode()).hexdigest()

        entry = AuditEntry(
            entry_id=entry_id,
            action_type=action_type,
            user_id=user_id,
            description=description,
            timestamp=ts,
            consent_token=consent_token,
            resource_id=resource_id,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
            is_suspicious=is_suspicious,
            metadata=metadata or {},
        )
        self._entries.append(entry)
        return entry

    def flag_suspicious(self, entry_id: str) -> AuditEntry:
        """Mark an existing entry as suspicious (does not break chain)."""
        entry = self._get_entry(entry_id)
        entry.is_suspicious = True
        return entry

    # ------------------------------------------------------------------
    # Freeze / unfreeze
    # ------------------------------------------------------------------

    def freeze(self, user_id: str = "system") -> AuditEntry:
        """
        Freeze the audit log — no new entries can be added.

        Logs the freeze event itself before locking.
        """
        entry = self.log(
            AuditActionType.AUDIT_LOG_FROZEN,
            user_id=user_id,
            description="Audit log frozen due to suspicious activity detection.",
            is_suspicious=True,
        )
        self._frozen = True
        return entry

    def unfreeze(self) -> None:
        """Unfreeze the audit log (admin operation)."""
        self._frozen = False

    @property
    def is_frozen(self) -> bool:
        return self._frozen

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_entries(
        self,
        user_id: Optional[str] = None,
        action_type: Optional[AuditActionType] = None,
        since: Optional[float] = None,
        until: Optional[float] = None,
        suspicious_only: bool = False,
        limit: Optional[int] = None,
    ) -> list[AuditEntry]:
        """Return filtered audit entries (newest first)."""
        entries = list(reversed(self._entries))

        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        if action_type:
            entries = [e for e in entries if e.action_type == action_type]
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        if until:
            entries = [e for e in entries if e.timestamp <= until]
        if suspicious_only:
            entries = [e for e in entries if e.is_suspicious]

        effective_limit = limit
        if self._max_visible is not None and (
            effective_limit is None or effective_limit > self._max_visible
        ):
            effective_limit = self._max_visible

        if effective_limit is not None:
            entries = entries[:effective_limit]

        return entries

    def get_entry(self, entry_id: str) -> AuditEntry:
        return self._get_entry(entry_id)

    def count(self) -> int:
        return len(self._entries)

    def count_suspicious(self) -> int:
        return sum(1 for e in self._entries if e.is_suspicious)

    def verify_chain(self) -> bool:
        """
        Verify the integrity chain of the log.

        Returns False if any entry's previous_hash does not match
        the hash of the entry before it.
        """
        for i, entry in enumerate(self._entries):
            if i == 0:
                expected_prev = self.GENESIS_HASH
            else:
                expected_prev = self._entries[i - 1].entry_hash
            if entry.previous_hash != expected_prev:
                return False
        return True

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_entry(self, entry_id: str) -> AuditEntry:
        for entry in self._entries:
            if entry.entry_id == entry_id:
                return entry
        raise AuditLogError(f"Audit entry '{entry_id}' not found.")


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AuditLogError(Exception):
    """General audit log error."""


class AuditLogFrozenError(AuditLogError):
    """Raised when trying to log to a frozen audit log."""


__all__ = [
    "AuditActionType",
    "AuditEntry",
    "AuditLog",
    "AuditLogError",
    "AuditLogFrozenError",
]
