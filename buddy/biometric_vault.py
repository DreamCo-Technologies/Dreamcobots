"""Encrypted, opt-in Buddy biometric template vault (no recognition engine).

Requires cryptography; fail closed if unavailable. Caller supplies a protected
32-byte key from a secret manager, never from a repository or model prompt.
Template bytes are embeddings, not photos/audio; embeddings remain sensitive.
"""
from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path

_ID = re.compile(r"^[A-Za-z0-9_-]{3,64}$")
_MODALITIES = {"face", "voice"}


def _validate(profile_id: str, modality: str) -> None:
    if not isinstance(profile_id, str) or not _ID.fullmatch(profile_id):
        raise ValueError("Invalid profile ID")
    if modality not in _MODALITIES:
        raise ValueError("Invalid modality")


def _aes(key: bytes):
    if not isinstance(key, bytes) or len(key) != 32:
        raise ValueError("32-byte vault key required")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    return AESGCM(key)


def _path(directory: Path, profile_id: str, modality: str) -> Path:
    _validate(profile_id, modality)
    return directory / f"{profile_id}.{modality}.enc"


def put_template(directory: Path, key: bytes, profile_id: str, modality: str,
                 template: bytes, *, consent: bool, adult_or_guardian_approved: bool) -> None:
    if consent is not True or adult_or_guardian_approved is not True:
        raise PermissionError("Explicit biometric consent required")
    if not isinstance(template, bytes) or not 1 <= len(template) <= 65536:
        raise ValueError("Invalid template")
    cipher = _aes(key)
    path = _path(directory, profile_id, modality)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.exists():
        raise FileExistsError("Existing biometric enrollment requires explicit replacement")
    nonce = os.urandom(12)
    aad = f"buddy:v1:{profile_id}:{modality}".encode()
    encrypted = cipher.encrypt(nonce, template, aad)
    payload = json.dumps({"v": 1, "nonce": base64.b64encode(nonce).decode(),
                          "ciphertext": base64.b64encode(encrypted).decode()}).encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(payload)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def get_template(directory: Path, key: bytes, profile_id: str, modality: str,
                 *, consent_active: bool) -> bytes:
    if consent_active is not True:
        raise PermissionError("Biometric consent revoked")
    cipher = _aes(key)
    payload = json.loads(_path(directory, profile_id, modality).read_text())
    if payload.get("v") != 1:
        raise ValueError("Unsupported vault format")
    nonce = base64.b64decode(payload["nonce"], validate=True)
    encrypted = base64.b64decode(payload["ciphertext"], validate=True)
    return cipher.decrypt(nonce, encrypted, f"buddy:v1:{profile_id}:{modality}".encode())


def delete_templates(directory: Path, profile_id: str) -> int:
    _validate(profile_id, "face")
    count = 0
    for modality in sorted(_MODALITIES):
        path = _path(directory, profile_id, modality)
        if path.exists():
            path.unlink()
            count += 1
    return count
