"""User-configurable, non-financial training points and reward ledger.

No cryptocurrency, transferable assets, payouts, or model weight updates.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from datetime import datetime, timezone
from typing import Dict, List
import uuid

@dataclass(frozen=True)
class Rules:
    owner_id: str
    point_name: str = "Buddy XP"
    points_per_pass: int = 10
    points_per_improvement: int = 5
    daily_cap: int = 200
    rewards: Dict[str, int] = field(default_factory=lambda: {"Study badge": 100})

    def __post_init__(self):
        if not self.owner_id or len(self.owner_id) > 128:
            raise ValueError("owner_id required")
        if not 1 <= len(self.point_name) <= 40:
            raise ValueError("point name length invalid")
        if not all(isinstance(n, int) and not isinstance(n, bool) and 0 <= n <= 1000
                   for n in (self.points_per_pass, self.points_per_improvement)):
            raise ValueError("invalid award amounts")
        if not isinstance(self.daily_cap, int) or not 1 <= self.daily_cap <= 100000:
            raise ValueError("invalid daily cap")
        if len(self.rewards) > 100 or any(not isinstance(k, str) or not k.strip() or
                                          not isinstance(v, int) or isinstance(v, bool) or v < 1
                                          for k, v in self.rewards.items()):
            raise ValueError("invalid reward catalog")
        object.__setattr__(self, "rewards", MappingProxyType(dict(self.rewards)))

class Ledger:
    def __init__(self, rules: Rules):
        self.rules = rules
        self.balance = 0
        self.events: List[dict] = []
        self.seen = set()

    def _record(self, event_id: str, amount: int, kind: str, day: str):
        if event_id in self.seen:
            return False
        self.seen.add(event_id)
        self.balance += amount
        self.events.append({"id": event_id, "amount": amount, "kind": kind,
                            "day": day, "balance": self.balance})
        return True

    def award(self, event_id: str, *, passed: bool, improved: bool,
              verified: bool, day: str = None) -> int:
        if not event_id or len(event_id) > 128:
            raise ValueError("event ID required")
        if not verified:
            raise ValueError("verified benchmark evidence required")
        day = day or datetime.now(timezone.utc).date().isoformat()
        if event_id in self.seen:
            return 0
        requested = (self.rules.points_per_pass if passed else 0) + (
            self.rules.points_per_improvement if improved else 0)
        already = sum(e["amount"] for e in self.events if e["day"] == day and e["amount"] > 0)
        amount = max(0, min(requested, self.rules.daily_cap - already))
        self._record(event_id, amount, "benchmark", day)
        return amount

    def redeem(self, event_id: str, reward: str, day: str = None) -> int:
        if event_id in self.seen:
            return 0
        if reward not in self.rules.rewards:
            raise ValueError("unknown reward")
        cost = self.rules.rewards[reward]
        if cost > self.balance:
            raise ValueError("insufficient points")
        self._record(event_id, -cost, "redeem:" + reward,
                     day or datetime.now(timezone.utc).date().isoformat())
        return cost
