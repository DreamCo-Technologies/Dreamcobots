"""Evidence-aware fusion of independent Buddy reasoning signals."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReasoningSignal:
    source: str
    claim: str
    confidence: float
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source.strip() or not self.claim.strip():
            raise ValueError("source and claim are required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class FusedClaim:
    claim: str
    confidence: float
    supporting_sources: tuple[str, ...]
    contradicting_claims: tuple[str, ...]
    evidence_ids: tuple[str, ...]


class ReasoningFusion:
    """Combine signals without treating agreement as proof."""

    def fuse(self, signals: tuple[ReasoningSignal, ...] | list[ReasoningSignal]) -> tuple[FusedClaim, ...]:
        if not signals:
            return ()
        groups: dict[str, list[ReasoningSignal]] = {}
        for signal in signals:
            groups.setdefault(signal.claim, []).append(signal)
        claims = []
        for claim, group in groups.items():
            confidence = 1.0
            for signal in group:
                confidence *= signal.confidence
            sources = tuple(sorted({signal.source for signal in group}))
            evidence = tuple(sorted({e for signal in group for e in signal.evidence_ids}))
            contradicting = tuple(sorted(c for c in groups if c != claim))
            claims.append(FusedClaim(claim, confidence, sources, contradicting, evidence))
        return tuple(sorted(claims, key=lambda item: (-item.confidence, item.claim)))
