from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math
from typing import Dict, Optional


class HealingStrategy(Enum):
    RESTART = 'restart'
    ROLLBACK = 'rollback'
    SCALE_OUT = 'scale_out'
    CIRCUIT_BREAK = 'circuit_break'


class CircuitBreakerState(Enum):
    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half_open'


@dataclass
class HealingAction:
    bot_id: str
    strategy: HealingStrategy
    retry_in_seconds: int
    attempt: int
    reason: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BotHealthSnapshot:
    bot_id: str
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    failures: int = 0
    consecutive_errors: int = 0
    restart_count: int = 0
    status: str = 'healthy'


class CircuitBreaker:
    def __init__(self, threshold: int = 3, reset_timeout: int = 60) -> None:
        self.threshold = threshold
        self.reset_timeout = timedelta(seconds=reset_timeout)
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.opened_at: Optional[datetime] = None

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.opened_at = None

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.threshold:
            self.state = CircuitBreakerState.OPEN
            self.opened_at = datetime.utcnow()

    def allow_request(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True
        if self.state == CircuitBreakerState.OPEN and self.opened_at:
            if datetime.utcnow() - self.opened_at >= self.reset_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        return self.state == CircuitBreakerState.HALF_OPEN


class SelfHealingRuntime:
    def __init__(self, max_retries: int = 6, heartbeat_timeout: int = 90) -> None:
        self.max_retries = max_retries
        self.heartbeat_timeout = timedelta(seconds=heartbeat_timeout)
        self.health: Dict[str, BotHealthSnapshot] = {}
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.history: list[HealingAction] = []

    def register_bot(self, bot_id: str) -> None:
        self.health.setdefault(bot_id, BotHealthSnapshot(bot_id=bot_id))
        self.breakers.setdefault(bot_id, CircuitBreaker())

    def record_heartbeat(self, bot_id: str) -> None:
        self.register_bot(bot_id)
        snapshot = self.health[bot_id]
        snapshot.last_heartbeat = datetime.utcnow()
        snapshot.status = 'healthy'
        snapshot.consecutive_errors = 0
        self.breakers[bot_id].record_success()

    def detect_failures(self) -> list[str]:
        now = datetime.utcnow()
        failed = []
        for bot_id, snapshot in self.health.items():
            if now - snapshot.last_heartbeat > self.heartbeat_timeout:
                snapshot.status = 'heartbeat_timeout'
                failed.append(bot_id)
        return failed

    def heal(self, bot_id: str, failure_type: str) -> HealingAction:
        self.register_bot(bot_id)
        snapshot = self.health[bot_id]
        snapshot.failures += 1
        snapshot.consecutive_errors += 1
        breaker = self.breakers[bot_id]
        strategy = self._choose_strategy(snapshot, failure_type, breaker)
        if strategy == HealingStrategy.CIRCUIT_BREAK:
            breaker.record_failure()
        delay = min(300, int(math.pow(2, min(snapshot.consecutive_errors, self.max_retries))))
        action = HealingAction(
            bot_id=bot_id,
            strategy=strategy,
            retry_in_seconds=delay,
            attempt=snapshot.failures,
            reason=failure_type,
        )
        if strategy == HealingStrategy.RESTART:
            snapshot.restart_count += 1
            snapshot.status = 'restarting'
        elif strategy == HealingStrategy.ROLLBACK:
            snapshot.status = 'rollback_pending'
        elif strategy == HealingStrategy.SCALE_OUT:
            snapshot.status = 'scaling_out'
        else:
            snapshot.status = breaker.state.value
        self.history.append(action)
        return action

    def _choose_strategy(self, snapshot: BotHealthSnapshot, failure_type: str, breaker: CircuitBreaker) -> HealingStrategy:
        if failure_type in {'oom', 'crash_loop'}:
            return HealingStrategy.RESTART if snapshot.restart_count < 3 else HealingStrategy.SCALE_OUT
        if failure_type in {'bad_release', 'migration_error'}:
            return HealingStrategy.ROLLBACK
        if failure_type in {'dependency_outage', 'downstream_5xx'}:
            return HealingStrategy.CIRCUIT_BREAK if breaker.allow_request() else HealingStrategy.SCALE_OUT
        if snapshot.consecutive_errors >= 4:
            return HealingStrategy.CIRCUIT_BREAK
        return HealingStrategy.RESTART
