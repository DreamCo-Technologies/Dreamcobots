"""Validate bot event declarations against the shared DreamCo contract."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


class ContractViolation(Exception):
    """Raised when a bot declares events outside the platform contract."""


@dataclass
class ValidationResult:
    bot: str
    valid: bool
    diff: dict[str, Any]


class EventContractValidator:
    """Compare profile-declared events to config/shared_event_contract.json."""

    def __init__(self, contract_path: Path | None = None) -> None:
        self.contract_path = contract_path or ROOT / "config" / "shared_event_contract.json"
        self.contract = json.loads(self.contract_path.read_text())

    def validate_profile(self, profile_path: Path) -> ValidationResult:
        profile = json.loads(profile_path.read_text())
        declared = set(profile.get("events_emitted", []) + profile.get("events_consumed", []))
        required = set(self.contract.get("required_fields", []))
        metadata_fields = set(profile.keys())
        missing = sorted(required - metadata_fields)
        diff = {"missing_fields": missing, "declared_events": sorted(declared)}
        valid = not missing
        if not valid:
            raise ContractViolation(f"{profile_path.parent.name} violates contract: {diff}")
        return ValidationResult(bot=profile_path.parent.name, valid=valid, diff=diff)

    def validate_all(self) -> list[ValidationResult]:
        results = []
        for path in sorted((ROOT / "bots").glob("*/replit_profile.json")):
            try:
                results.append(self.validate_profile(path))
            except ContractViolation as exc:
                results.append(ValidationResult(bot=path.parent.name, valid=False, diff={"error": str(exc)}))
        return results
