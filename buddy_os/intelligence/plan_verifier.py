"""Preflight verification for Buddy plans.

Verification is advisory and does not grant authorization to execute actions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Mapping


@dataclass(frozen=True)
class VerificationIssue:
    code: str
    message: str
    severity: str = "error"


@dataclass(frozen=True)
class PlanCheck:
    plan_id: str
    required_assets: List[str] = field(default_factory=list)
    known_assets: List[str] = field(default_factory=list)
    simulated: bool = False
    issues: List[VerificationIssue] = field(default_factory=list)

    @property
    def approved_for_authorization(self) -> bool:
        return self.simulated and not any(i.severity == "error" for i in self.issues)


class PlanVerifier:
    def verify(
        self,
        plan_id: str,
        required_assets: Iterable[str],
        known_assets: Iterable[str],
        simulated: bool,
    ) -> PlanCheck:
        required = list(dict.fromkeys(required_assets))
        known = set(known_assets)
        issues: List[VerificationIssue] = []
        missing = [asset for asset in required if asset not in known]
        if missing:
            issues.append(VerificationIssue("missing_asset", f"Missing assets: {', '.join(missing)}"))
        if not simulated:
            issues.append(VerificationIssue("not_simulated", "Plan has not completed a simulation preflight"))
        return PlanCheck(plan_id, required, sorted(known), simulated, issues)
