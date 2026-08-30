"""Conservative promotion decision for Buddy capabilities."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MasteryEvidence:
    native_passes: int
    holdout_passed: bool
    regression_passed: bool
    repeated_signature_stable: bool
    external_assistance_used: bool


def eligible_for_mastery(evidence: MasteryEvidence, minimum_native_passes: int = 3) -> bool:
    """Return true only when all independent promotion gates are satisfied."""
    return (
        evidence.native_passes >= minimum_native_passes
        and evidence.holdout_passed
        and evidence.regression_passed
        and evidence.repeated_signature_stable
    )


def should_keep_external_fallback(evidence: MasteryEvidence) -> bool:
    """Keep external help available until native mastery is independently proven."""
    return not eligible_for_mastery(evidence)
