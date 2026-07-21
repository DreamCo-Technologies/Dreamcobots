"""
security_layer.py — Implements encryption and security functions.

Provides data encryption/decryption, key management, and access-control
helpers to secure sensitive data within the DreamCo governance layer.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class EncryptedPayload:
    """Holds an encrypted data payload and its associated key ID."""

    ciphertext: str  # Base64-encoded
    key_id: str
    algorithm: str


class SecurityLayer:
    """
    Lightweight encryption and HMAC-signing layer for the governance service.

    This implementation uses HMAC-SHA256 for integrity checking and a
    simple XOR + Base64 scheme **strictly as a placeholder**.

    .. warning::
        The XOR cipher is NOT cryptographically secure and MUST be replaced
        with a battle-tested library (e.g. ``cryptography.fernet``) before
        any production use.  Do not use this class to protect real secrets.

    Parameters
    ----------
    secret_key : bytes | None
        Secret key bytes. If ``None``, a random 32-byte key is generated.
    key_id : str
        Label for the current key (used for key-rotation tracking).
    """

    ALGORITHM = "HMAC-SHA256+XOR-B64"

    def __init__(self, secret_key: Optional[bytes] = None, key_id: str = "default"):
        self._key: bytes = secret_key if secret_key is not None else os.urandom(32)
        self.key_id = key_id

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def encrypt(self, plaintext: str) -> EncryptedPayload:
        """
        Encrypt *plaintext* and return an ``EncryptedPayload``.

        Parameters
        ----------
        plaintext : str
        """
        data = plaintext.encode()
        xored = bytes(b ^ self._key[i % len(self._key)] for i, b in enumerate(data))
        ciphertext = base64.urlsafe_b64encode(xored).decode()
        return EncryptedPayload(
            ciphertext=ciphertext,
            key_id=self.key_id,
            algorithm=self.ALGORITHM,
        )

    def decrypt(self, payload: EncryptedPayload) -> str:
        """
        Decrypt an ``EncryptedPayload`` and return the plaintext.

        Parameters
        ----------
        payload : EncryptedPayload
        """
        xored = base64.urlsafe_b64decode(payload.ciphertext.encode())
        data = bytes(b ^ self._key[i % len(self._key)] for i, b in enumerate(xored))
        return data.decode()

    def sign(self, message: str) -> str:
        """
        Produce an HMAC-SHA256 signature for *message*.

        Returns
        -------
        str
            Hex-encoded HMAC digest.
        """
        return hmac.new(self._key, message.encode(), hashlib.sha256).hexdigest()

    def verify(self, message: str, signature: str) -> bool:
        """
        Verify that *signature* is a valid HMAC for *message*.

        Returns
        -------
        bool
        """
        expected = self.sign(message)
        return hmac.compare_digest(expected, signature)

    def hash_data(self, data: str) -> str:
        """Return a SHA-256 hex digest of *data* (one-way hash)."""
        return hashlib.sha256(data.encode()).hexdigest()

    def rotate_key(self, new_key: bytes, new_key_id: str) -> None:
        """
        Replace the current encryption key.

        Parameters
        ----------
        new_key : bytes
            New secret key bytes.
        new_key_id : str
            Label for the new key.
        """
        self._key = new_key
        self.key_id = new_key_id
