from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List


@dataclass
class AdaptiveWindow:
    alpha: float = 0.25
    ema_rate: float = 0.0
    last_seen: datetime = field(default_factory=datetime.utcnow)

    def update(self, now: datetime) -> float:
        delta = max((now - self.last_seen).total_seconds(), 1.0)
        instant_rate = 1.0 / delta
        self.ema_rate = self.alpha * instant_rate + (1 - self.alpha) * self.ema_rate
        self.last_seen = now
        return self.ema_rate


@dataclass
class RateDecision:
    allowed: bool
    applied_limit: int
    anomaly_flagged: bool
    reason: str


class AdaptiveRateLimiter:
    def __init__(self, base_limit_per_minute: int = 60) -> None:
        self.base_limit_per_minute = base_limit_per_minute
        self.windows: Dict[str, AdaptiveWindow] = {}
        self.request_log: Dict[str, List[datetime]] = {}
        self.security_flags: List[dict] = []

    def allow_request(self, api_key: str, now: datetime | None = None) -> RateDecision:
        now = now or datetime.utcnow()
        window = self.windows.setdefault(api_key, AdaptiveWindow())
        learned_rate = window.update(now)
        dynamic_limit = self._dynamic_limit(learned_rate)
        log = self.request_log.setdefault(api_key, [])
        horizon = now - timedelta(minutes=1)
        log[:] = [entry for entry in log if entry >= horizon]
        anomaly = len(log) > dynamic_limit * 1.5 or learned_rate > 3
        if anomaly:
            self.security_flags.append({'api_key': api_key, 'timestamp': now.isoformat(), 'rate': learned_rate})
        allowed = len(log) < dynamic_limit
        if allowed:
            log.append(now)
        reason = 'within learned burst pattern' if allowed else 'rate exceeded adaptive threshold'
        return RateDecision(allowed=allowed, applied_limit=dynamic_limit, anomaly_flagged=anomaly, reason=reason)

    def _dynamic_limit(self, learned_rate: float) -> int:
        expected_per_minute = max(1, int(learned_rate * 60))
        if expected_per_minute <= self.base_limit_per_minute:
            return self.base_limit_per_minute
        burst_headroom = int((expected_per_minute - self.base_limit_per_minute) * 0.5)
        return min(self.base_limit_per_minute * 3, self.base_limit_per_minute + burst_headroom)

def summarize_api_key(self, api_key: str) -> dict:
    log = self.request_log.get(api_key, [])
    window = self.windows.get(api_key)
    return {
        'api_key': api_key,
        'requests_last_minute': len(log),
        'ema_rate': round(window.ema_rate, 4) if window else 0.0,
        'flagged': any(flag['api_key'] == api_key for flag in self.security_flags),
    }


def reset_api_key(self, api_key: str) -> None:
    self.request_log.pop(api_key, None)
    self.windows.pop(api_key, None)


AdaptiveRateLimiter.summarize_api_key = summarize_api_key
AdaptiveRateLimiter.reset_api_key = reset_api_key
