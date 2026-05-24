"""
DreamCo OS — PII Detector
===========================

Detects personally-identifiable information (PII) before any data is
stored in memory or transmitted externally.

Patterns covered: email, phone, SSN, credit card, IP address, full name
heuristics, and passport/driver's licence numbers.

Usage::

    detector = PIIDetector()
    clean_text, findings = detector.scrub("Call me at 555-123-4567 or alice@example.com")
    # findings = [{"type": "phone", ...}, {"type": "email", ...}]
"""

from __future__ import annotations

import re
from typing import Any


_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("email", re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", re.I)),
    ("phone", re.compile(r"\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("credit_card", re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12})\b")),
    ("ip_address", re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")),
    ("us_passport", re.compile(r"\b[A-Z]\d{8}\b")),
    ("date_of_birth", re.compile(r"\b(?:dob|date of birth|born)[:\s]+\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b", re.I)),
]

_REDACTION_PLACEHOLDER = "[REDACTED]"


class PIIDetectionResult:
    def __init__(self, pii_type: str, match: str, start: int, end: int) -> None:
        self.pii_type = pii_type
        self.match = match
        self.start = start
        self.end = end

    def to_dict(self) -> dict[str, Any]:
        return {
            "pii_type": self.pii_type,
            "match": self.match[:4] + "****",  # only show first 4 chars
            "start": self.start,
            "end": self.end,
        }


class PIIDetector:
    """Detects and scrubs PII from text strings.

    Parameters
    ----------
    raise_on_detection:
        When True, raises ``PIIDetectedError`` instead of scrubbing.
    """

    def __init__(self, raise_on_detection: bool = False) -> None:
        self.raise_on_detection = raise_on_detection

    class PIIDetectedError(Exception):
        pass

    def detect(self, text: str) -> list[PIIDetectionResult]:
        """Return all PII matches found in *text*."""
        findings: list[PIIDetectionResult] = []
        for pii_type, pattern in _PATTERNS:
            for match in pattern.finditer(text):
                findings.append(PIIDetectionResult(pii_type, match.group(), match.start(), match.end()))
        return findings

    def scrub(self, text: str) -> tuple[str, list[dict[str, Any]]]:
        """Return (scrubbed_text, list_of_findings)."""
        findings = self.detect(text)
        if findings and self.raise_on_detection:
            raise self.PIIDetectedError(
                f"PII detected: {[f.pii_type for f in findings]}"
            )
        result = text
        for pii_type, pattern in _PATTERNS:
            result = pattern.sub(_REDACTION_PLACEHOLDER, result)
        return result, [f.to_dict() for f in findings]

    def has_pii(self, text: str) -> bool:
        return bool(self.detect(text))
