"""Turn CI/action failures into structured, reusable Buddy learning evidence.

The module is intentionally conservative: it records observations and proposed
remediation metadata; it does not execute arbitrary commands or automatically
change production code.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import re


@dataclass(frozen=True)
class FailureEvidence:
    workflow: str
    job: str
    failure_class: str
    signature: str
    remediation: str
    outcome: str
    commit: str = ""
    run_id: str = ""
    captured_at: str = ""

    def to_record(self) -> dict[str, str]:
        record = asdict(self)
        if not record["captured_at"]:
            record["captured_at"] = datetime.now(timezone.utc).isoformat()
        return record


def normalize_signature(log_text: str) -> str:
    """Create a stable failure signature while removing volatile values."""
    text = re.sub(r"0x[0-9a-fA-F]+", "0xADDR", log_text)
    text = re.sub(r"\b\d{5,}\b", "N", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def classify_failure(log_text: str) -> str:
    text = log_text.lower()
    if "typeerror" in text or "attributeerror" in text:
        return "python_runtime"
    if "assert" in text or "pytest" in text:
        return "test_failure"
    if "npm err" in text or "module not found" in text:
        return "dependency_or_build"
    if "lint" in text or "eslint" in text:
        return "lint"
    if "timeout" in text:
        return "timeout"
    if "permission denied" in text or "forbidden" in text:
        return "permissions"
    return "unknown"


def build_evidence(workflow: str, job: str, log_text: str, remediation: str,
                   outcome: str = "unresolved", commit: str = "", run_id: str = "") -> FailureEvidence:
    return FailureEvidence(
        workflow=workflow,
        job=job,
        failure_class=classify_failure(log_text),
        signature=normalize_signature(log_text),
        remediation=remediation,
        outcome=outcome,
        commit=commit,
        run_id=run_id,
    )
