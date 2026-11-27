"""Host-only authenticated secret store.

Secrets are encrypted with AES-256-GCM using a per-file scrypt-derived key.
Ciphertext is written outside the repository with owner-only file permissions.
The repository stores neither plaintext credentials nor encryption keys.
"""
from __future__ import annotations

import hashlib
import os
import re
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAGIC = b"DCOG2"
SALT_BYTES = 16
NONCE_BYTES = 12
MIN_MASTER_SECRET_LENGTH = 32
NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


def _aesgcm_type():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as exc:
        raise RuntimeError(
            "Install the cryptography package to use the authenticated secret store"
        ) from exc
    return AESGCM


def _master_secret() -> bytes:
    value = os.environ.get("OWNER_SECRET_KEY", "")
    if len(value) < MIN_MASTER_SECRET_LENGTH:
        raise PermissionError(
            "set OWNER_SECRET_KEY on the host to a randomly generated value of at least 32 characters"
        )
    return value.encode("utf-8")


def _derive_key(master: bytes, salt: bytes) -> bytes:
    return hashlib.scrypt(master, salt=salt, n=2**14, r=8, p=1, dklen=32)


def _target(name: str, folder: Path) -> tuple[Path, Path]:
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name) or name in {".", ".."}:
        raise PermissionError("invalid secret name")
    resolved = folder.expanduser().resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        raise PermissionError("secrets cannot be stored in the repo")
    return resolved, resolved / name


def store(name: str, secret: str, folder: Path) -> dict:
    """Encrypt and create a new secret file; refuse to overwrite existing files."""
    if not isinstance(secret, str) or not secret:
        raise PermissionError("secret must be a non-empty string")
    directory, path = _target(name, folder)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name == "posix":
        os.chmod(directory, 0o700)

    salt = os.urandom(SALT_BYTES)
    nonce = os.urandom(NONCE_BYTES)
    aad = MAGIC + name.encode("utf-8")
    ciphertext = _aesgcm_type()(_derive_key(_master_secret(), salt)).encrypt(
        nonce, secret.encode("utf-8"), aad
    )
    payload = MAGIC + salt + nonce + ciphertext

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink(missing_ok=True)
        finally:
            raise

    return {
        "name": name,
        "stored": True,
        "in_repo": False,
        "plaintext_written": secret.encode("utf-8") not in payload,
        "encryption": "AES-256-GCM",
        "key_derivation": "scrypt",
        "format": "DCOG2",
    }


def load(name: str, folder: Path) -> str:
    """Decrypt one secret file; authentication failures are surfaced, never ignored."""
    _directory, path = _target(name, folder)
    if path.is_symlink() or not path.is_file():
        raise PermissionError("secret file is missing or is not a regular file")
    if os.name == "posix" and stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise PermissionError("secret file permissions must be owner-only (0600)")
    payload = path.read_bytes()
    header_size = len(MAGIC) + SALT_BYTES + NONCE_BYTES
    if len(payload) <= header_size + 16 or not payload.startswith(MAGIC):
        raise ValueError("unsupported or truncated secret file")
    offset = len(MAGIC)
    salt = payload[offset:offset + SALT_BYTES]
    offset += SALT_BYTES
    nonce = payload[offset:offset + NONCE_BYTES]
    ciphertext = payload[offset + NONCE_BYTES:]
    aad = MAGIC + name.encode("utf-8")
    plaintext = _aesgcm_type()(_derive_key(_master_secret(), salt)).decrypt(
        nonce, ciphertext, aad
    )
    return plaintext.decode("utf-8")
