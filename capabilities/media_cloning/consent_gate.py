"""Consent gate for voice and image cloning.

Nothing here clones a real person's voice or likeness without a signed consent
record whose reference_hash matches a sha256 of the exact reference file.
The subject must be confirmed as an adult. This stores JSON on disk so the
check is easy to audit. It does not verify identity by itself.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_CONSENT_DIR = Path("data/consent_records")


class ConsentError(RuntimeError):
    """Raised when a cloning request cannot proceed without valid consent."""


@dataclass(frozen=True)
class ConsentRecord:
    subject_name: str
    reference_hash: str
    signed_by: str
    signed_at: float
    scope: str
    adult_confirmed: bool
    expires_at: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ConsentRecord":
        return cls(
            subject_name=data["subject_name"],
            reference_hash=data["reference_hash"],
            signed_by=data["signed_by"],
            signed_at=data["signed_at"],
            scope=data["scope"],
            adult_confirmed=data["adult_confirmed"],
            expires_at=data.get("expires_at"),
        )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_consent(
    reference_path: str | Path,
    scope: str,
    consent_record_path: str | Path,
) -> ConsentRecord:
    """Validate a consent record against the actual reference file."""
    reference_path = Path(reference_path)
    consent_record_path = Path(consent_record_path)
    if not reference_path.exists():
        raise ConsentError(f"reference file not found: {reference_path}")
    if not consent_record_path.exists():
        raise ConsentError(
            f"no consent record at {consent_record_path}; refusing to clone "
            f"'{reference_path.name}' without one"
        )
    try:
        record = ConsentRecord.from_dict(json.loads(consent_record_path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, KeyError) as exc:
        raise ConsentError(f"malformed consent record: {exc}") from exc
    if record.adult_confirmed is not True:
        raise ConsentError("refusing to clone a voice or likeness unless the subject is confirmed to be an adult")
    if record.scope != scope:
        raise ConsentError(f"consent record scope '{record.scope}' does not cover '{scope}'")
    if record.expires_at is not None and time.time() > record.expires_at:
        raise ConsentError("consent record has expired")
    actual_hash = _sha256_file(reference_path)
    if actual_hash != record.reference_hash:
        raise ConsentError(
            "reference file does not match the file the consent record was signed for"
        )
    return record


def write_consent_record(
    subject_name: str,
    reference_path: str | Path,
    signed_by: str,
    scope: str,
    out_path: str | Path,
    adult_confirmed: bool = False,
    expires_in_seconds: Optional[float] = None,
) -> Path:
    """Record a hash binding after a person has actually given consent.

    This does not verify identity. Pass adult_confirmed=True only after a real
    intake step has established that the subject is an adult.
    """
    if adult_confirmed is not True:
        raise ConsentError("refusing to record consent unless the subject is confirmed to be an adult")
    reference_path = Path(reference_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    now = time.time()
    record = {
        "subject_name": subject_name,
        "reference_hash": _sha256_file(reference_path),
        "signed_by": signed_by,
        "signed_at": now,
        "scope": scope,
        "adult_confirmed": True,
        "expires_at": (now + expires_in_seconds) if expires_in_seconds else None,
    }
    out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return out_path
