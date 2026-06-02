from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class PatchCandidate:
    cve_id: str
    severity: str
    affected_package: str
    patch_version: str


@dataclass
class ApprovedPatch:
    cve_id: str
    affected_package: str
    patch_version: str
    approved: bool
    reason: str


class AutoPatcher:
    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    def evaluate(self, candidates: Iterable[PatchCandidate]) -> List[ApprovedPatch]:
        approved = []
        for candidate in candidates:
            severity = candidate.severity.upper()
            if severity == 'CRITICAL':
                approved.append(ApprovedPatch(candidate.cve_id, candidate.affected_package, candidate.patch_version, False, 'Human approval required for CRITICAL patch'))
            elif severity in {'HIGH', 'MEDIUM'}:
                action = 'Dry-run approved' if self.dry_run else 'Auto-apply approved'
                approved.append(ApprovedPatch(candidate.cve_id, candidate.affected_package, candidate.patch_version, True, action))
            else:
                approved.append(ApprovedPatch(candidate.cve_id, candidate.affected_package, candidate.patch_version, False, 'Severity too low for automatic patching'))
        return approved

def summarize(self, patches: Iterable[ApprovedPatch]) -> dict:
    patches = list(patches)
    return {
        'approved': sum(1 for patch in patches if patch.approved),
        'manual_review': sum(1 for patch in patches if 'Human approval' in patch.reason),
        'rejected': sum(1 for patch in patches if not patch.approved and 'Human approval' not in patch.reason),
    }


def dry_run_report(self, candidates: Iterable[PatchCandidate]) -> List[str]:
    decisions = self.evaluate(candidates)
    return [f"{decision.cve_id}:{decision.reason}" for decision in decisions]


AutoPatcher.summarize = summarize
AutoPatcher.dry_run_report = dry_run_report

def requires_human(self, candidate: PatchCandidate) -> bool:
    return candidate.severity.upper() == 'CRITICAL'


AutoPatcher.requires_human = requires_human
