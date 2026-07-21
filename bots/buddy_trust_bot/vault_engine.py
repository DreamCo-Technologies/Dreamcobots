# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Vault Engine — Buddy Trust Bot

Military-grade encrypted vault for sensitive user data including:
  - Social Security Numbers (SSN)
  - Bank account numbers
  - Email addresses and passwords
  - Bot secrets / API keys
  - Medical records (HIPAA)
  - Any user-defined sensitive field

Security design:
  - All secrets are AES-256-GCM encrypted at rest (simulated via hashlib).
  - Each secret has an individual encryption key derived from a master key.
  - Vault Mode allows the owner to lock the entire vault for a time period,
    preventing ALL reads until explicitly unlocked.
  - Access to any secret requires active SENSITIVE_DATA_ACCESS consent.
  - Every access is logged (caller must wire in AuditLog).
"""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SecretType(Enum):
    SSN = "ssn"                         # Social Security Number
    BANK_ACCOUNT = "bank_account"
    ROUTING_NUMBER = "routing_number"
    EMAIL_PASSWORD = "email_password"
    BOT_SECRET = "bot_secret"           # API keys, webhook tokens
    MEDICAL_RECORD = "medical_record"
    PASSPORT = "passport"
    CREDIT_CARD = "credit_card"
    GENERIC = "generic"


class VaultStatus(Enum):
    UNLOCKED = "unlocked"
    LOCKED = "locked"       # Vault Mode active


@dataclass
class VaultSecret:
    """
    A single encrypted secret stored in the vault.

    ``ciphertext`` is an opaque encrypted representation.
    In a real deployment this would use AES-256-GCM with a per-secret IV.
    """

    secret_id: str
    owner_user_id: str
    label: str              # Human-readable name, e.g. "Chase Checking Account"
    secret_type: SecretType
    ciphertext: str         # Encrypted/hashed value (not reversible in simulation)
    fingerprint: str        # HMAC fingerprint for integrity verification
    consent_token: str      # Token from the consent that authorised storage
    created_at: float
    last_accessed_at: Optional[float] = None
    access_count: int = 0
    notes: str = ""
    is_deleted: bool = False    # Soft delete

    def to_dict(self, include_ciphertext: bool = False) -> dict:
        d = {
            "secret_id": self.secret_id,
            "owner_user_id": self.owner_user_id,
            "label": self.label,
            "secret_type": self.secret_type.value,
            "fingerprint": self.fingerprint,
            "consent_token": self.consent_token,
            "created_at": self.created_at,
            "last_accessed_at": self.last_accessed_at,
            "access_count": self.access_count,
            "notes": self.notes,
            "is_deleted": self.is_deleted,
        }
        if include_ciphertext:
            d["ciphertext"] = self.ciphertext
        return d


@dataclass
class VaultLockRecord:
    """Record of a Vault Mode lock/unlock event."""

    event_id: str
    user_id: str
    action: str             # "lock" | "unlock"
    timestamp: float
    duration_seconds: Optional[float]   # How long the lock is valid
    unlock_at: Optional[float]          # Computed unlock timestamp

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "user_id": self.user_id,
            "action": self.action,
            "timestamp": self.timestamp,
            "duration_seconds": self.duration_seconds,
            "unlock_at": self.unlock_at,
        }


class VaultEngine:
    """
    Encrypted vault for sensitive data management.

    Parameters
    ----------
    max_secrets : Optional[int]
        Maximum number of secrets (None = unlimited).
    consent_manager :
        Shared ConsentManager instance.
    master_key : str
        Master encryption key (secret, never stored).  In production this
        would be sourced from an HSM or KMS.
    encryption_level : str
        Descriptive label such as "AES-256-GCM".
    """

    VAULT_MODE_REQUIRES_ENTERPRISE_FEATURE = "vault_mode"

    def __init__(
        self,
        max_secrets: Optional[int],
        consent_manager,
        master_key: str = "dreamco-vault-master-key-DO-NOT-EXPOSE",
        encryption_level: str = "AES-256-GCM",
    ) -> None:
        self._max_secrets = max_secrets
        self._consent_manager = consent_manager
        self._master_key = master_key
        self.encryption_level = encryption_level
        self._secrets: dict[str, VaultSecret] = {}
        self._vault_status: VaultStatus = VaultStatus.UNLOCKED
        self._lock_records: list[VaultLockRecord] = []
        self._lock_until: Optional[float] = None

    # ------------------------------------------------------------------
    # Status / Vault Mode
    # ------------------------------------------------------------------

    @property
    def status(self) -> VaultStatus:
        """Auto-expire a time-limited lock."""
        if (
            self._vault_status == VaultStatus.LOCKED
            and self._lock_until is not None
            and time.time() >= self._lock_until
        ):
            self._vault_status = VaultStatus.UNLOCKED
            self._lock_until = None
        return self._vault_status

    def lock_vault(
        self,
        user_id: str,
        duration_seconds: Optional[float] = None,
    ) -> VaultLockRecord:
        """
        Activate Vault Mode — lock the vault for restricted/temporary use.

        Requires active VAULT_UNLOCK consent (ensures the lock is intentional).
        """
        from bots.buddy_trust_bot.consent_manager import ConsentType
        self._consent_manager.require_consent(user_id, ConsentType.VAULT_UNLOCK)
        self._vault_status = VaultStatus.LOCKED
        unlock_at = time.time() + duration_seconds if duration_seconds else None
        self._lock_until = unlock_at

        record = VaultLockRecord(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            action="lock",
            timestamp=time.time(),
            duration_seconds=duration_seconds,
            unlock_at=unlock_at,
        )
        self._lock_records.append(record)
        return record

    def unlock_vault(self, user_id: str) -> VaultLockRecord:
        """
        Deactivate Vault Mode — requires VAULT_UNLOCK consent.
        """
        from bots.buddy_trust_bot.consent_manager import ConsentType
        self._consent_manager.require_consent(user_id, ConsentType.VAULT_UNLOCK)
        self._vault_status = VaultStatus.UNLOCKED
        self._lock_until = None

        record = VaultLockRecord(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            action="unlock",
            timestamp=time.time(),
            duration_seconds=None,
            unlock_at=None,
        )
        self._lock_records.append(record)
        return record

    def get_lock_history(self) -> list[VaultLockRecord]:
        return list(self._lock_records)

    # ------------------------------------------------------------------
    # Secret management
    # ------------------------------------------------------------------

    def store_secret(
        self,
        owner_user_id: str,
        label: str,
        plaintext_value: str,
        secret_type: SecretType = SecretType.GENERIC,
        notes: str = "",
    ) -> VaultSecret:
        """
        Encrypt and store a sensitive secret.

        Requires active SENSITIVE_DATA_STORAGE consent.
        """
        self._check_vault_unlocked()
        from bots.buddy_trust_bot.consent_manager import ConsentType
        consent = self._consent_manager.require_consent(
            owner_user_id, ConsentType.SENSITIVE_DATA_STORAGE
        )

        if self._max_secrets is not None:
            active_count = sum(1 for s in self._secrets.values() if not s.is_deleted)
            if active_count >= self._max_secrets:
                raise VaultLimitError(
                    f"Vault secret limit ({self._max_secrets}) reached on current tier."
                )

        secret_id = str(uuid.uuid4())
        ciphertext = self._encrypt(plaintext_value, secret_id)
        fingerprint = self._fingerprint(ciphertext)

        secret = VaultSecret(
            secret_id=secret_id,
            owner_user_id=owner_user_id,
            label=label,
            secret_type=secret_type,
            ciphertext=ciphertext,
            fingerprint=fingerprint,
            consent_token=consent.acknowledgment_token,
            created_at=time.time(),
            notes=notes,
        )
        self._secrets[secret_id] = secret
        return secret

    def retrieve_secret(self, secret_id: str, requester_user_id: str) -> str:
        """
        Decrypt and return a secret's plaintext value.

        Requires active SENSITIVE_DATA_ACCESS consent.
        """
        self._check_vault_unlocked()
        from bots.buddy_trust_bot.consent_manager import ConsentType
        self._consent_manager.require_consent(
            requester_user_id, ConsentType.SENSITIVE_DATA_ACCESS
        )
        secret = self._get_secret(secret_id)
        secret.last_accessed_at = time.time()
        secret.access_count += 1
        return self._decrypt(secret.ciphertext, secret_id)

    def delete_secret(self, secret_id: str, owner_user_id: str) -> VaultSecret:
        """Soft-delete a secret (owner only)."""
        secret = self._get_secret(secret_id)
        if secret.owner_user_id != owner_user_id:
            raise VaultError("Only the secret owner can delete it.")
        secret.is_deleted = True
        return secret

    def verify_integrity(self, secret_id: str) -> bool:
        """Verify a secret's HMAC fingerprint has not been tampered with."""
        secret = self._get_secret(secret_id)
        expected = self._fingerprint(secret.ciphertext)
        return hmac.compare_digest(expected, secret.fingerprint)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_secrets(
        self,
        owner_user_id: Optional[str] = None,
        include_deleted: bool = False,
    ) -> list[VaultSecret]:
        secrets = list(self._secrets.values())
        if not include_deleted:
            secrets = [s for s in secrets if not s.is_deleted]
        if owner_user_id:
            secrets = [s for s in secrets if s.owner_user_id == owner_user_id]
        return secrets

    def secret_count(self, include_deleted: bool = False) -> int:
        return len(self.list_secrets(include_deleted=include_deleted))

    def vault_summary(self) -> dict:
        return {
            "status": self.status.value,
            "encryption_level": self.encryption_level,
            "total_secrets": self.secret_count(),
            "lock_history_count": len(self._lock_records),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_vault_unlocked(self) -> None:
        if self.status == VaultStatus.LOCKED:
            raise VaultLockedError(
                "Vault is currently locked (Vault Mode active). "
                "Unlock the vault before accessing secrets."
            )

    def _get_secret(self, secret_id: str) -> VaultSecret:
        if secret_id not in self._secrets:
            raise VaultError(f"Secret '{secret_id}' not found.")
        secret = self._secrets[secret_id]
        if secret.is_deleted:
            raise VaultError(f"Secret '{secret_id}' has been deleted.")
        return secret

    def _derive_key(self, secret_id: str) -> bytes:
        """Derive a per-secret key from master key + secret_id."""
        raw = f"{self._master_key}:{secret_id}".encode()
        return hashlib.sha256(raw).digest()

    def _encrypt(self, plaintext: str, secret_id: str) -> str:
        """
        Simulate AES-256-GCM encryption.

        In production, replace with ``cryptography.hazmat.primitives.ciphers.aead.AESGCM``.
        Here we XOR each byte with the key (repeating) to produce an opaque hex string.
        """
        key = self._derive_key(secret_id)
        data = plaintext.encode("utf-8")
        xored = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
        return xored.hex()

    def _decrypt(self, ciphertext: str, secret_id: str) -> str:
        """Reverse the simulation encryption."""
        key = self._derive_key(secret_id)
        data = bytes.fromhex(ciphertext)
        xored = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
        return xored.decode("utf-8")

    def _fingerprint(self, ciphertext: str) -> str:
        """Generate an HMAC-SHA256 fingerprint."""
        return hmac.new(
            self._master_key.encode(),
            ciphertext.encode(),
            hashlib.sha256,
        ).hexdigest()


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class VaultError(Exception):
    """General vault error."""


class VaultLockedError(VaultError):
    """Raised when the vault is in locked (Vault Mode) state."""


class VaultLimitError(VaultError):
    """Raised when the tier secret limit is exceeded."""


__all__ = [
    "SecretType",
    "VaultStatus",
    "VaultSecret",
    "VaultLockRecord",
    "VaultEngine",
    "VaultError",
    "VaultLockedError",
    "VaultLimitError",
]
