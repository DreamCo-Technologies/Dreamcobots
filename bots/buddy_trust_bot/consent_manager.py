# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Consent Manager — Buddy Trust Bot

Manages explicit, recorded consent for sensitive operations such as:
  - Voice mimicry (recording + synthesis)
  - Image/video synthesis (avatar creation)
  - Sensitive data storage (SSN, bank, email, etc.)

Every consent grant or revocation is timestamped, stored, and associated
with a unique acknowledgment token so operations can be audited at any time.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ConsentType(Enum):
    VOICE_MIMICRY = "voice_mimicry"
    IMAGE_SYNTHESIS = "image_synthesis"
    SENSITIVE_DATA_STORAGE = "sensitive_data_storage"
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"
    BIOMETRIC_COLLECTION = "biometric_collection"
    THIRD_PARTY_SHARING = "third_party_sharing"
    VAULT_UNLOCK = "vault_unlock"


class ConsentStatus(Enum):
    GRANTED = "granted"
    REVOKED = "revoked"
    PENDING = "pending"
    EXPIRED = "expired"


@dataclass
class ConsentRecord:
    """A single consent record with full audit details."""

    consent_id: str
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus
    granted_at: Optional[float]             # Unix timestamp
    revoked_at: Optional[float]
    expires_at: Optional[float]             # None = no expiry
    acknowledgment_token: str               # Cryptographic proof of consent
    details: str                            # Human-readable description
    ip_address: str = ""                    # Optional origin IP
    recorded_acknowledgment: bool = False   # True if user explicitly typed/confirmed

    def is_active(self) -> bool:
        if self.status != ConsentStatus.GRANTED:
            return False
        if self.expires_at is not None and time.time() > self.expires_at:
            return False
        return True

    def to_dict(self) -> dict:
        return {
            "consent_id": self.consent_id,
            "user_id": self.user_id,
            "consent_type": self.consent_type.value,
            "status": self.status.value,
            "granted_at": self.granted_at,
            "revoked_at": self.revoked_at,
            "expires_at": self.expires_at,
            "acknowledgment_token": self.acknowledgment_token,
            "details": self.details,
            "ip_address": self.ip_address,
            "recorded_acknowledgment": self.recorded_acknowledgment,
            "is_active": self.is_active(),
        }


class ConsentManager:
    """
    Manages user consent for sensitive operations.

    All sensitive operations (voice mimicry, image synthesis, vault access)
    MUST pass through ConsentManager before execution.
    """

    def __init__(self) -> None:
        self._records: dict[str, ConsentRecord] = {}   # consent_id -> record
        # user_id -> consent_type -> list of consent_ids
        self._user_index: dict[str, dict[str, list[str]]] = {}

    # ------------------------------------------------------------------
    # Consent lifecycle
    # ------------------------------------------------------------------

    def request_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        details: str,
        expires_in_seconds: Optional[float] = None,
        ip_address: str = "",
    ) -> ConsentRecord:
        """
        Create a PENDING consent request.

        The user must call ``grant_consent()`` to activate it.
        """
        consent_id = str(uuid.uuid4())
        expires_at = time.time() + expires_in_seconds if expires_in_seconds else None

        record = ConsentRecord(
            consent_id=consent_id,
            user_id=user_id,
            consent_type=consent_type,
            status=ConsentStatus.PENDING,
            granted_at=None,
            revoked_at=None,
            expires_at=expires_at,
            acknowledgment_token="",
            details=details,
            ip_address=ip_address,
        )
        self._records[consent_id] = record
        self._index(user_id, consent_type.value, consent_id)
        return record

    def grant_consent(
        self,
        consent_id: str,
        acknowledged: bool = True,
    ) -> ConsentRecord:
        """
        Activate a PENDING consent request.

        Parameters
        ----------
        consent_id : str
            The ID returned by ``request_consent()``.
        acknowledged : bool
            Must be ``True`` — represents the user's explicit confirmation.
        """
        if not acknowledged:
            raise ConsentError(
                "Consent cannot be granted without explicit acknowledgment (acknowledged=True)."
            )
        record = self._get_record(consent_id)
        if record.status == ConsentStatus.REVOKED:
            raise ConsentError(f"Consent {consent_id} has been revoked and cannot be re-activated.")
        record.status = ConsentStatus.GRANTED
        record.granted_at = time.time()
        record.recorded_acknowledgment = True
        record.acknowledgment_token = self._generate_token(record)
        return record

    def revoke_consent(self, consent_id: str) -> ConsentRecord:
        """Revoke a previously granted consent."""
        record = self._get_record(consent_id)
        record.status = ConsentStatus.REVOKED
        record.revoked_at = time.time()
        return record

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def has_active_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Return True if *user_id* has an active, un-expired consent for *consent_type*."""
        type_key = consent_type.value
        consent_ids = self._user_index.get(user_id, {}).get(type_key, [])
        for cid in consent_ids:
            if self._records[cid].is_active():
                return True
        return False

    def get_active_consent(self, user_id: str, consent_type: ConsentType) -> Optional[ConsentRecord]:
        """Return the most recent active consent record for the given user and type."""
        type_key = consent_type.value
        consent_ids = self._user_index.get(user_id, {}).get(type_key, [])
        for cid in reversed(consent_ids):
            rec = self._records[cid]
            if rec.is_active():
                return rec
        return None

    def list_user_consents(self, user_id: str) -> list[ConsentRecord]:
        """Return all consent records for a user."""
        all_ids: list[str] = []
        for ids in self._user_index.get(user_id, {}).values():
            all_ids.extend(ids)
        return [self._records[cid] for cid in all_ids]

    def list_all_consents(self) -> list[ConsentRecord]:
        """Return all consent records (admin view)."""
        return list(self._records.values())

    def count_active_by_type(self, consent_type: ConsentType) -> int:
        """Count active consents for a given type across all users."""
        return sum(
            1 for r in self._records.values()
            if r.consent_type == consent_type and r.is_active()
        )

    # ------------------------------------------------------------------
    # Require-or-raise helper (used by other engines)
    # ------------------------------------------------------------------

    def require_consent(self, user_id: str, consent_type: ConsentType) -> ConsentRecord:
        """
        Raise ``ConsentRequiredError`` if the user has no active consent for this type.
        Otherwise return the active consent record.
        """
        record = self.get_active_consent(user_id, consent_type)
        if record is None:
            raise ConsentRequiredError(
                f"User '{user_id}' has not granted consent for '{consent_type.value}'. "
                f"Please request and grant consent before proceeding."
            )
        return record

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_record(self, consent_id: str) -> ConsentRecord:
        if consent_id not in self._records:
            raise ConsentError(f"Consent record '{consent_id}' not found.")
        return self._records[consent_id]

    def _index(self, user_id: str, type_key: str, consent_id: str) -> None:
        self._user_index.setdefault(user_id, {}).setdefault(type_key, []).append(consent_id)

    @staticmethod
    def _generate_token(record: ConsentRecord) -> str:
        """Generate a deterministic acknowledgment token for auditing."""
        raw = f"{record.consent_id}:{record.user_id}:{record.consent_type.value}:{record.granted_at}"
        return "ACK-" + hashlib.sha256(raw.encode()).hexdigest()[:16].upper()


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ConsentError(Exception):
    """General consent operation error."""


class ConsentRequiredError(ConsentError):
    """Raised when a required consent is missing."""


__all__ = [
    "ConsentType",
    "ConsentStatus",
    "ConsentRecord",
    "ConsentManager",
    "ConsentError",
    "ConsentRequiredError",
]
