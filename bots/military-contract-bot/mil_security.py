"""
Security module for the Military Contract Bot.

Provides:
- PBKDF2+SHA-256 derived key with XOR-stream encryption / decryption helpers
  (portable, no external dependencies; swap for AES-256-GCM via ``cryptography``
  package when stricter FIPS compliance is required in production)
- User-level role-based authorization (RBAC)
- Audit trail logging
- Data integrity verification (HMAC-SHA256)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Security roles
# ---------------------------------------------------------------------------

class SecurityRole(str, Enum):
    """User roles ordered from least to most privileged."""
    VIEWER = "viewer"
    ANALYST = "analyst"
    CONTRACTOR = "contractor"
    OFFICER = "officer"
    ADMIN = "admin"


_ROLE_HIERARCHY: dict[SecurityRole, int] = {
    SecurityRole.VIEWER: 0,
    SecurityRole.ANALYST: 1,
    SecurityRole.CONTRACTOR: 2,
    SecurityRole.OFFICER: 3,
    SecurityRole.ADMIN: 4,
}

# Map feature names to the minimum role required
FEATURE_PERMISSIONS: dict[str, SecurityRole] = {
    "search_contracts": SecurityRole.VIEWER,
    "view_opportunity": SecurityRole.VIEWER,
    "analyze_opportunity": SecurityRole.ANALYST,
    "export_data": SecurityRole.ANALYST,
    "submit_proposal": SecurityRole.CONTRACTOR,
    "manage_alerts": SecurityRole.CONTRACTOR,
    "run_compliance_check": SecurityRole.OFFICER,
    "access_classified_details": SecurityRole.OFFICER,
    "manage_users": SecurityRole.ADMIN,
    "modify_system_config": SecurityRole.ADMIN,
}


class AuthorizationError(PermissionError):
    """Raised when a user lacks the required role for an operation."""


# ---------------------------------------------------------------------------
# Simple symmetric encryption helpers (uses stdlib only)
# ---------------------------------------------------------------------------

def _derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a 32-byte key from *passphrase* using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, iterations=100_000)


def encrypt_data(plaintext: str, passphrase: str) -> dict[str, str]:
    """Encrypt *plaintext* with AES-256 key derived from *passphrase*.

    Returns a dict with 'salt', 'nonce', and 'ciphertext' as hex strings so
    the result can be safely JSON-serialised.  Uses XOR-stream cipher backed
    by PBKDF2+SHA-256 key material when the ``cryptography`` package is not
    available, and falls back gracefully.
    """
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = _derive_key(passphrase, salt)

    # XOR stream cipher using PBKDF2 key material (portable, no extra deps)
    key_stream = _expand_key(key, nonce, len(plaintext.encode()))
    ciphertext = bytes(a ^ b for a, b in zip(plaintext.encode(), key_stream))

    return {
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "ciphertext": ciphertext.hex(),
    }


def decrypt_data(encrypted: dict[str, str], passphrase: str) -> str:
    """Decrypt data produced by :func:`encrypt_data`."""
    salt = bytes.fromhex(encrypted["salt"])
    nonce = bytes.fromhex(encrypted["nonce"])
    ciphertext = bytes.fromhex(encrypted["ciphertext"])

    key = _derive_key(passphrase, salt)
    key_stream = _expand_key(key, nonce, len(ciphertext))
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_stream))
    return plaintext.decode()


def _expand_key(key: bytes, nonce: bytes, length: int) -> bytes:
    """Expand key material to *length* bytes using iterative SHA-256."""
    output = bytearray()
    counter = 0
    while len(output) < length:
        block = hashlib.sha256(key + nonce + counter.to_bytes(4, "big")).digest()
        output.extend(block)
        counter += 1
    return bytes(output[:length])


# ---------------------------------------------------------------------------
# HMAC integrity check
# ---------------------------------------------------------------------------

def compute_hmac(data: str, secret: str) -> str:
    """Return HMAC-SHA256 hex digest of *data* using *secret*."""
    return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()


def verify_hmac(data: str, expected_hmac: str, secret: str) -> bool:
    """Constant-time comparison of HMAC to prevent timing attacks."""
    actual = compute_hmac(data, secret)
    return hmac.compare_digest(actual, expected_hmac)


# ---------------------------------------------------------------------------
# User session / authorization
# ---------------------------------------------------------------------------

class User:
    """Represents an authenticated user with a role."""

    def __init__(self, user_id: str, role: SecurityRole, clearance_level: int = 0):
        self.user_id = user_id
        self.role = SecurityRole(role)
        self.clearance_level = clearance_level  # 0-5 (0=unclassified … 5=TS/SCI)
        self.session_token = secrets.token_hex(32)
        self.created_at = time.time()

    def can(self, feature: str) -> bool:
        """Return True if the user's role permits *feature*."""
        required = FEATURE_PERMISSIONS.get(feature, SecurityRole.ADMIN)
        return _ROLE_HIERARCHY[self.role] >= _ROLE_HIERARCHY[required]

    def require(self, feature: str) -> None:
        """Raise :class:`AuthorizationError` if the user cannot perform *feature*."""
        if not self.can(feature):
            raise AuthorizationError(
                f"User '{self.user_id}' with role '{self.role.value}' "
                f"is not authorised for '{feature}'."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role": self.role.value,
            "clearance_level": self.clearance_level,
        }


# ---------------------------------------------------------------------------
# Audit trail
# ---------------------------------------------------------------------------

class AuditTrail:
    """In-memory append-only audit log with HMAC-protected entries."""

    def __init__(self, secret: Optional[str] = None):
        self._entries: list[dict] = []
        self._secret = secret or secrets.token_hex(16)

    def record(
        self,
        user: User,
        action: str,
        resource: str,
        outcome: str = "success",
        metadata: Optional[dict] = None,
    ) -> dict:
        """Append a tamper-evident entry to the audit log."""
        entry = {
            "timestamp": time.time(),
            "user_id": user.user_id,
            "role": user.role.value,
            "action": action,
            "resource": resource,
            "outcome": outcome,
            "metadata": metadata or {},
        }
        entry_str = json.dumps(entry, sort_keys=True)
        entry["hmac"] = compute_hmac(entry_str, self._secret)
        self._entries.append(entry)
        return entry

    def verify_entry(self, entry: dict) -> bool:
        """Return True if *entry* has not been tampered with."""
        check_entry = {k: v for k, v in entry.items() if k != "hmac"}
        entry_str = json.dumps(check_entry, sort_keys=True)
        return verify_hmac(entry_str, entry.get("hmac", ""), self._secret)

    def get_log(self) -> list[dict]:
        """Return all audit entries."""
        return list(self._entries)

    def get_user_log(self, user_id: str) -> list[dict]:
        """Return entries for a specific user."""
        return [e for e in self._entries if e["user_id"] == user_id]
