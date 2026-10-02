"""Consent registry. A reference voice/face is only usable if a consent record is bound to that exact file."""
from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional, Sequence


class ConsentError(PermissionError):
    """Raised when a clone is requested without valid, matching consent."""


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class ConsentRecord:
    consent_id: str
    subject_name: str
    kind: str  # "voice" | "image"
    reference_sha256: str
    granted_by: str
    attestation: str
    scope: List[str]
    created_at: float
    expires_at: Optional[float] = None
    revoked: bool = False


class ConsentRegistry:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> List[ConsentRecord]:
        if not self.path.exists():
            return []
        return [ConsentRecord(**r) for r in json.loads(self.path.read_text())]

    def _save(self, records: List[ConsentRecord]) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps([asdict(r) for r in records], indent=2))
        tmp.replace(self.path)

    def register(
        self,
        reference_path,
        subject_name: str,
        kind: str,
        granted_by: str,
        attestation: str,
        scope: Sequence[str] = ("personal",),
        ttl_days: Optional[int] = None,
    ) -> ConsentRecord:
        if kind not in ("voice", "image"):
            raise ValueError("kind must be 'voice' or 'image'")
        if len(attestation.strip()) < 20:
            raise ConsentError(
                "Attestation must state, in words, that the subject consented to this use of their "
                f"{kind}. (This records a claim; it does not verify identity.)"
            )
        if re.search(r"\b(child|kid|minor|teen)\b", f"{subject_name} {attestation}", re.I):
            raise ConsentError("Buddy will not clone a child's voice or image.")
        now = time.time()
        rec = ConsentRecord(
            consent_id=uuid.uuid4().hex[:12],
            subject_name=subject_name,
            kind=kind,
            reference_sha256=sha256_file(reference_path),
            granted_by=granted_by,
            attestation=attestation.strip(),
            scope=list(scope),
            created_at=now,
            expires_at=(now + ttl_days * 86400) if ttl_days else None,
        )
        records = self._load()
        records.append(rec)
        self._save(records)
        return rec

    def require(self, reference_path, kind: str, purpose: str) -> ConsentRecord:
        digest = sha256_file(reference_path)
        now = time.time()
        for r in self._load():
            if (
                r.reference_sha256 == digest
                and r.kind == kind
                and not r.revoked
                and purpose in r.scope
                and (r.expires_at is None or r.expires_at > now)
            ):
                return r
        raise ConsentError(
            f"No valid consent for this {kind} reference (purpose='{purpose}'). "
            "Register consent for this exact file first, or the file was changed, revoked, or expired."
        )

    def revoke(self, consent_id: str) -> bool:
        records = self._load()
        hit = False
        for r in records:
            if r.consent_id == consent_id:
                r.revoked = True
                hit = True
        if hit:
            self._save(records)
        return hit
