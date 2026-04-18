"""
Buddy OS — Security Manager

Provides robust security infrastructure for Buddy OS:
  • Device authentication  — token-based device trust / revocation
  • Encryption layer       — symmetric AES-style key management
                             (pure-Python simulation; swap for cryptography lib
                              in production)
  • Secure pairing         — PIN / passkey exchange workflow
  • Sync mode              — cloud-sync vs. local-only operation
  • Audit log              — tamper-evident event log

GLOBAL AI SOURCES FLOW: participates via buddy_os.py pipeline.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class SyncMode(Enum):
    CLOUD = "cloud"
    LOCAL = "local"


class AuthStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REVOKED = "revoked"
    EXPIRED = "expired"


class EncryptionAlgorithm(Enum):
    AES_256_GCM = "aes_256_gcm"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    RSA_OAEP = "rsa_oaep"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class DeviceToken:
    """A short-lived authentication token issued to a paired device."""

    token_id: str
    device_name: str
    token_hash: str          # SHA-256 hash of the raw token
    status: AuthStatus = AuthStatus.APPROVED
    scopes: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def is_valid(self) -> bool:
        return self.status == AuthStatus.APPROVED

    def to_dict(self) -> dict:
        return {
            "token_id": self.token_id,
            "device_name": self.device_name,
            "status": self.status.value,
            "scopes": self.scopes,
        }


@dataclass
class EncryptionKey:
    """Represents a managed symmetric encryption key."""

    key_id: str
    algorithm: EncryptionAlgorithm
    key_bytes: bytes         # raw key material (never serialized to disk)
    active: bool = True
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "key_id": self.key_id,
            "algorithm": self.algorithm.value,
            "active": self.active,
            "key_length_bytes": len(self.key_bytes),
        }


@dataclass
class PairingSession:
    """Tracks a secure-pairing handshake."""

    session_id: str
    device_name: str
    pin: str                # 6-digit PIN exchanged out-of-band
    confirmed: bool = False
    token_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "device_name": self.device_name,
            "confirmed": self.confirmed,
            "token_id": self.token_id,
        }


@dataclass
class AuditEvent:
    """An entry in the tamper-evident audit log."""

    event_id: str
    event_type: str
    actor: str
    details: dict
    checksum: str   # HMAC-SHA256 of event data (keyed with internal secret)

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "actor": self.actor,
            "details": self.details,
            "checksum": self.checksum,
        }


# ---------------------------------------------------------------------------
# Security Manager
# ---------------------------------------------------------------------------

class SecurityManager:
    """
    Central security subsystem for Buddy OS.

    Manages device authentication, encryption keys, secure pairing, sync mode,
    and an append-only audit log.
    """

    def __init__(self, sync_mode: SyncMode = SyncMode.LOCAL) -> None:
        self.sync_mode: SyncMode = sync_mode
        self._tokens: dict[str, DeviceToken] = {}
        self._keys: dict[str, EncryptionKey] = {}
        self._pairing_sessions: dict[str, PairingSession] = {}
        self._audit_log: list[AuditEvent] = []
        # Internal HMAC secret — never exposed
        self._hmac_secret: bytes = os.urandom(32)

    # ------------------------------------------------------------------
    # Sync mode
    # ------------------------------------------------------------------

    def set_sync_mode(self, mode: SyncMode) -> None:
        """Switch between cloud-sync and local-only operation."""
        old = self.sync_mode
        self.sync_mode = mode
        self._log_event("sync_mode_changed", "system", {"from": old.value, "to": mode.value})

    def is_cloud_mode(self) -> bool:
        return self.sync_mode == SyncMode.CLOUD

    def is_local_mode(self) -> bool:
        return self.sync_mode == SyncMode.LOCAL

    # ------------------------------------------------------------------
    # Device authentication (token management)
    # ------------------------------------------------------------------

    def issue_token(
        self,
        device_name: str,
        scopes: Optional[list] = None,
        metadata: Optional[dict] = None,
    ) -> tuple[str, DeviceToken]:
        """
        Issue a new authentication token for *device_name*.

        Returns (raw_token, DeviceToken).  Store the raw_token securely;
        only the hash is retained internally.
        """
        raw_token = uuid.uuid4().hex + uuid.uuid4().hex   # 64-char hex
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token_id = f"tok_{uuid.uuid4().hex[:8]}"
        dt = DeviceToken(
            token_id=token_id,
            device_name=device_name,
            token_hash=token_hash,
            status=AuthStatus.APPROVED,
            scopes=list(scopes or []),
            metadata=dict(metadata or {}),
        )
        self._tokens[token_id] = dt
        self._log_event("token_issued", device_name, {"token_id": token_id})
        return raw_token, dt

    def verify_token(self, token_id: str, raw_token: str) -> bool:
        """Verify a raw token against the stored hash."""
        if token_id not in self._tokens:
            return False
        dt = self._tokens[token_id]
        if not dt.is_valid():
            return False
        expected = hashlib.sha256(raw_token.encode()).hexdigest()
        return hmac.compare_digest(expected, dt.token_hash)

    def revoke_token(self, token_id: str) -> DeviceToken:
        dt = self._get_token(token_id)
        dt.status = AuthStatus.REVOKED
        self._log_event("token_revoked", "system", {"token_id": token_id})
        return dt

    def list_tokens(self, active_only: bool = False) -> list[DeviceToken]:
        tokens = list(self._tokens.values())
        if active_only:
            tokens = [t for t in tokens if t.is_valid()]
        return tokens

    def get_token(self, token_id: str) -> DeviceToken:
        return self._get_token(token_id)

    # ------------------------------------------------------------------
    # Encryption key management
    # ------------------------------------------------------------------

    def generate_key(
        self,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
    ) -> EncryptionKey:
        """Generate a new encryption key."""
        key_length = 32  # 256-bit for AES-256 / ChaCha20
        if algorithm == EncryptionAlgorithm.RSA_OAEP:
            key_length = 256   # 2048-bit RSA modulus placeholder
        key_id = f"key_{uuid.uuid4().hex[:8]}"
        key = EncryptionKey(
            key_id=key_id,
            algorithm=algorithm,
            key_bytes=os.urandom(key_length),
        )
        self._keys[key_id] = key
        self._log_event("key_generated", "system", {"key_id": key_id, "algo": algorithm.value})
        return key

    def rotate_key(self, key_id: str) -> EncryptionKey:
        """Deactivate the current key and generate a replacement."""
        old_key = self._get_key(key_id)
        old_key.active = False
        new_key = self.generate_key(old_key.algorithm)
        self._log_event("key_rotated", "system", {"old": key_id, "new": new_key.key_id})
        return new_key

    def revoke_key(self, key_id: str) -> EncryptionKey:
        key = self._get_key(key_id)
        key.active = False
        self._log_event("key_revoked", "system", {"key_id": key_id})
        return key

    def list_keys(self, active_only: bool = False) -> list[EncryptionKey]:
        keys = list(self._keys.values())
        if active_only:
            keys = [k for k in keys if k.active]
        return keys

    def get_key(self, key_id: str) -> EncryptionKey:
        return self._get_key(key_id)

    def encrypt(self, key_id: str, plaintext: bytes) -> bytes:
        """
        Simulate encryption.

        Production code should replace this with a proper call to
        the `cryptography` library (e.g., AES-GCM via Fernet).
        """
        key = self._get_active_key(key_id)
        # XOR-based simulation — not cryptographically secure
        key_stream = (key.key_bytes * ((len(plaintext) // len(key.key_bytes)) + 1))[: len(plaintext)]
        return bytes(p ^ k for p, k in zip(plaintext, key_stream))

    def decrypt(self, key_id: str, ciphertext: bytes) -> bytes:
        """Simulate decryption (mirrors encrypt for XOR)."""
        return self.encrypt(key_id, ciphertext)  # XOR is self-inverse

    # ------------------------------------------------------------------
    # Secure pairing
    # ------------------------------------------------------------------

    def initiate_pairing(self, device_name: str) -> PairingSession:
        """Start a secure-pairing session and generate a PIN."""
        pin = str(secrets.randbelow(1_000_000)).zfill(6)
        session_id = f"pair_{uuid.uuid4().hex[:8]}"
        session = PairingSession(
            session_id=session_id,
            device_name=device_name,
            pin=pin,
        )
        self._pairing_sessions[session_id] = session
        self._log_event("pairing_initiated", device_name, {"session_id": session_id})
        return session

    def confirm_pairing(self, session_id: str, pin: str) -> DeviceToken:
        """Confirm the pairing with the correct PIN and return an access token."""
        session = self._get_pairing_session(session_id)
        if session.confirmed:
            raise RuntimeError(f"Pairing session '{session_id}' already confirmed.")
        if not hmac.compare_digest(pin, session.pin):
            raise ValueError("Incorrect PIN — pairing confirmation failed.")
        session.confirmed = True
        _raw, token = self.issue_token(session.device_name, scopes=["device_control"])
        session.token_id = token.token_id
        self._log_event("pairing_confirmed", session.device_name, {"token_id": token.token_id})
        return token

    def get_pairing_session(self, session_id: str) -> PairingSession:
        return self._get_pairing_session(session_id)

    def list_pairing_sessions(self, confirmed_only: bool = False) -> list[PairingSession]:
        sessions = list(self._pairing_sessions.values())
        if confirmed_only:
            sessions = [s for s in sessions if s.confirmed]
        return sessions

    # ------------------------------------------------------------------
    # Audit log
    # ------------------------------------------------------------------

    def get_audit_log(self) -> list[AuditEvent]:
        """Return a copy of the append-only audit log."""
        return list(self._audit_log)

    def verify_audit_log(self) -> bool:
        """Re-compute checksums to detect tampering."""
        for event in self._audit_log:
            expected = self._compute_checksum(
                event.event_type, event.actor, event.details
            )
            if not hmac.compare_digest(expected, event.checksum):
                return False
        return True

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _log_event(self, event_type: str, actor: str, details: dict) -> None:
        checksum = self._compute_checksum(event_type, actor, details)
        event = AuditEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            actor=actor,
            details=details,
            checksum=checksum,
        )
        self._audit_log.append(event)

    def _compute_checksum(self, event_type: str, actor: str, details: dict) -> str:
        payload = f"{event_type}:{actor}:{sorted(details.items())}".encode()
        return hmac.new(self._hmac_secret, payload, hashlib.sha256).hexdigest()

    def _get_token(self, token_id: str) -> DeviceToken:
        if token_id not in self._tokens:
            raise KeyError(f"Token '{token_id}' not found.")
        return self._tokens[token_id]

    def _get_key(self, key_id: str) -> EncryptionKey:
        if key_id not in self._keys:
            raise KeyError(f"Encryption key '{key_id}' not found.")
        return self._keys[key_id]

    def _get_active_key(self, key_id: str) -> EncryptionKey:
        key = self._get_key(key_id)
        if not key.active:
            raise RuntimeError(f"Key '{key_id}' is inactive.")
        return key

    def _get_pairing_session(self, session_id: str) -> PairingSession:
        if session_id not in self._pairing_sessions:
            raise KeyError(f"Pairing session '{session_id}' not found.")
        return self._pairing_sessions[session_id]
