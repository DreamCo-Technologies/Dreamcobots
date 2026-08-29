"""Measure progress toward solving tasks without external model assistance."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapabilitySample:
    native_success: bool
    external_assistance: bool
    verified: bool


def native_solve_rate(samples: list[CapabilitySample]) -> float:
    verified = [s for s in samples if s.verified]
    if not verified:
        return 0.0
    return sum(s.native_success and not s.external_assistance for s in verified) / len(verified)


def external_assistance_rate(samples: list[CapabilitySample]) -> float:
    verified = [s for s in samples if s.verified]
    if not verified:
        return 0.0
    return sum(s.external_assistance for s in verified) / len(verified)
