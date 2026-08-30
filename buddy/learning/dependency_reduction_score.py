"""Score evidence that Buddy is reducing external dependency without losing quality."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Cohort:
    native_pass_rate: float
    external_assistance_rate: float


def reduction_score(previous: Cohort, current: Cohort) -> float:
    """Return combined progress: native gain plus external-assistance reduction."""
    native_gain = current.native_pass_rate - previous.native_pass_rate
    external_drop = previous.external_assistance_rate - current.external_assistance_rate
    return native_gain + external_drop


def is_improving(previous: Cohort, current: Cohort, tolerance: float = 0.0) -> bool:
    """Require native quality to hold/improve and external reliance to fall."""
    native_gain = current.native_pass_rate - previous.native_pass_rate
    external_drop = previous.external_assistance_rate - current.external_assistance_rate
    return native_gain >= -tolerance and external_drop > tolerance
