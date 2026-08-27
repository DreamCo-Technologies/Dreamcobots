"""Outcome-based reputation for reusable Buddy assets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class AssetReputation:
    asset_id: str
    attempts: int = 0
    successes: int = 0
    failures: int = 0
    verified: int = 0
    incidents: int = 0

    @property
    def success_rate(self) -> float:
        return self.successes / self.attempts if self.attempts else 0.0

    @property
    def verification_rate(self) -> float:
        return self.verified / self.attempts if self.attempts else 0.0

    @property
    risk_rate(self) -> float:
        return self.incidents / self.attempts if self.attempts else 0.0

    @property
    score(self) -> float:
        # Reputation is advisory; it never grants permission.
        return max(0.0, min(1.0, self.success_rate * .55 + self.verification_rate * .35 - self.risk_rate * .10))


class ReputationBook:
    def __init__(self) -> None:
        self._records: Dict[str, AssetReputation] = {}

    def record(self, asset_id: str, *, success: bool, verified: bool = False, incident: bool = False) -> AssetReputation:
        record = self._records.setdefault(asset_id, AssetReputation(asset_id))
        record.attempts += 1
        record.successes += int(success)
        record.failures += int(not success)
        record.verified += int(verified)
        record.incidents += int(incident)
        return record

    def get(self, asset_id: str) -> AssetReputation:
        return self._records.setdefault(asset_id, AssetReputation(asset_id))
