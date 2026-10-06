"""Host-only secret store.

A secret is written only outside the repo, and only when the host key is set.
The file holds ciphertext. The repo never receives the value.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _key() -> bytes:
    value = os.environ.get("OWNER_SECRET_KEY", "")
    if len(value) < 16:
        raise PermissionError("set OWNER_SECRET_KEY on the host, at least 16 characters")
    return hashlib.sha256(value.encode("utf-8")).digest()


def store(name: str, secret: str, folder: Path) -> dict:
    if not name or "/" in name or name.startswith("."):
        raise PermissionError("invalid secret name")
    if ROOT in folder.resolve().parents or folder.resolve() == ROOT:
        raise PermissionError("secrets cannot be stored in the repo")
    folder.mkdir(parents=True, exist_ok=True)
    key = _key()
    raw = secret.encode("utf-8")
    stream = hmac.new(key, name.encode("utf-8"), hashlib.sha256).digest()
    stream = (stream * ((len(raw) // len(stream)) + 1))[: len(raw)]
    cipher = bytes(left ^ right for left, right in zip(raw, stream))
    path = folder / name
    path.write_bytes(cipher)
    return {"name": name, "stored": True, "in_repo": False, "plaintext_written": secret.encode("utf-8") not in path.read_bytes()}
