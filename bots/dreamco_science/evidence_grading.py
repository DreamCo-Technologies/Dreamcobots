# GLOBAL AI SOURCES FLOW
"""Evidence grading utilities for DreamCo science workflows."""
import sys
import os
_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
from enum import Enum


class EvidenceLevel(str, Enum):
    PROVEN = "proven"
    STRONG = "strong_evidence"
    EARLY = "early_evidence"
    EXPERIMENTAL = "experimental"
    UNVERIFIED = "unverified"
    UNSAFE = "unsafe"


EVIDENCE_RANK = {e: i for i, e in enumerate(EvidenceLevel)}


SAFETY_DISCLAIMER = (
    "DISCLAIMER: These findings are for informational/research purposes only. "
    "Not medical advice. Always consult qualified healthcare professionals."
)


_ALIAS_MAP = {
    "strong": EvidenceLevel.STRONG,
    "strong_evidence": EvidenceLevel.STRONG,
    "early": EvidenceLevel.EARLY,
    "early_evidence": EvidenceLevel.EARLY,
    "experimental": EvidenceLevel.EXPERIMENTAL,
    "unverified": EvidenceLevel.UNVERIFIED,
    "unsafe": EvidenceLevel.UNSAFE,
    "proven": EvidenceLevel.PROVEN,
}


def grade_evidence(level: str) -> EvidenceLevel:
    """Parse string to EvidenceLevel."""
    if isinstance(level, EvidenceLevel):
        return level
    normalized = str(level or '').strip().lower()
    if normalized in _ALIAS_MAP:
        return _ALIAS_MAP[normalized]
    raise ValueError(f"Unsupported evidence level: {level}")
