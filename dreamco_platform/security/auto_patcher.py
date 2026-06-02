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
