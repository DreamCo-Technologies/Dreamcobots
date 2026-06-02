from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AbusePattern:
    type: str
    signature: str
    severity: str
    detection_method: str


@dataclass
class ImmunityVerdict:
    outcome: str
    matched_patterns: List[str]
    adaptive_update: str


class ImmunitySystem:
    def __init__(self) -> None:
        self.patterns: List[AbusePattern] = [
            AbusePattern('rate_limit', 'burst', 'medium', 'velocity'),
            AbusePattern('content_filter', 'DROP TABLE', 'high', 'signature'),
            AbusePattern('behavior_analysis', 'credential-stuffing', 'critical', 'heuristic'),
        ]
        self.learned_patterns: List[AbusePattern] = []

    def analyze(self, request: Dict[str, str]) -> ImmunityVerdict:
        matched = []
        payload = ' '.join(str(value) for value in request.values())
        for pattern in self.patterns + self.learned_patterns:
            if pattern.signature.lower() in payload.lower():
                matched.append(pattern.type)
        outcome = 'BLOCK' if matched else 'ALLOW'
        adaptive = 'stored new abuse fingerprint' if matched else 'no update'
        if matched:
            self.learned_patterns.append(AbusePattern('adaptive', payload[:40], 'medium', 'feedback'))
        return ImmunityVerdict(outcome, matched, adaptive)

def known_signatures(self) -> List[str]:
    return [pattern.signature for pattern in self.patterns + self.learned_patterns]


def layer_summary(self) -> Dict[str, int]:
    summary: Dict[str, int] = {}
    for pattern in self.patterns + self.learned_patterns:
        summary[pattern.type] = summary.get(pattern.type, 0) + 1
    return summary


ImmunitySystem.known_signatures = known_signatures
ImmunitySystem.layer_summary = layer_summary

def relearn(self, signature: str, severity: str = 'medium') -> None:
    self.learned_patterns.append(AbusePattern('adaptive', signature, severity, 'manual-feedback'))


ImmunitySystem.relearn = relearn
