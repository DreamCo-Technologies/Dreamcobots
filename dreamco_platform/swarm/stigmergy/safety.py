from __future__ import annotations

import time


class SafetyViolation(RuntimeError):
    pass


class SwarmSafetyControls:
    def __init__(
        self,
        *,
        max_actions_per_window: int = 100,
        window_seconds: int = 60,
        required_approvals: int = 1,
    ) -> None:
        self.max_actions_per_window = max_actions_per_window
        self.window_seconds = window_seconds
        self.required_approvals = max(0, required_approvals)
        self._kill_switch = False
        self._circuit_open = False
        self._lock_owners: dict[str, tuple[str, float | None]] = {}
        self._action_timestamps: dict[str, list[float]] = {}
        self._approval_registry: dict[str, set[str]] = {}

    def activate_kill_switch(self) -> None:
        self._kill_switch = True

    def reset_kill_switch(self) -> None:
        self._kill_switch = False

    def open_circuit(self) -> None:
        self._circuit_open = True

    def close_circuit(self) -> None:
        self._circuit_open = False

    def acquire_lock(self, lock_name: str, owner_id: str, *, ttl_seconds: int | None = None) -> bool:
        self._expire_locks()
        current = self._lock_owners.get(lock_name)
        if current and current[0] != owner_id:
            return False
        expires_at = time.time() + ttl_seconds if ttl_seconds else None
        self._lock_owners[lock_name] = (owner_id, expires_at)
        return True

    def release_lock(self, lock_name: str, owner_id: str) -> None:
        self._expire_locks()
        current = self._lock_owners.get(lock_name)
        if current and current[0] == owner_id:
            self._lock_owners.pop(lock_name, None)

    def register_approval(self, action_key: str, approver_id: str) -> int:
        approvals = self._approval_registry.setdefault(action_key, set())
        approvals.add(approver_id)
        return len(approvals)

    def clear_approvals(self, action_key: str) -> None:
        self._approval_registry.pop(action_key, None)

    def approval_count(self, action_key: str | None) -> int:
        if not action_key:
            return 0
        return len(self._approval_registry.get(action_key, set()))

    def enforce(
        self,
        *,
        action: str,
        bot_id: str,
        high_impact: bool = False,
        approved: bool = False,
        action_key: str | None = None,
        approval_count: int = 0,
        required_approvals: int | None = None,
    ) -> None:
        if self._kill_switch:
            raise SafetyViolation("kill switch is active")
        if self._circuit_open:
            raise SafetyViolation("circuit breaker is open")
        needed = self.required_approvals if required_approvals is None else max(0, required_approvals)
        distributed_approval = approval_count >= needed and needed > 0
        if high_impact and not approved and not distributed_approval:
            raise SafetyViolation("high-impact action requires BuddyAI/SafetyBot approval")
        self._check_rate_limit(bot_id)
        if action_key:
            self.clear_approvals(action_key)

    def _check_rate_limit(self, bot_id: str) -> None:
        now = time.time()
        window_start = now - self.window_seconds
        timestamps = [ts for ts in self._action_timestamps.get(bot_id, []) if ts >= window_start]
        if len(timestamps) >= self.max_actions_per_window:
            raise SafetyViolation("rate limit exceeded")
        timestamps.append(now)
        self._action_timestamps[bot_id] = timestamps

    def _expire_locks(self) -> None:
        now = time.time()
        expired = [name for name, (_, expires_at) in self._lock_owners.items() if expires_at and expires_at <= now]
        for name in expired:
            self._lock_owners.pop(name, None)
