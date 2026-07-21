from __future__ import annotations

import time


class SafetyViolation(RuntimeError):
    pass


class SwarmSafetyControls:
    def __init__(self, *, max_actions_per_window: int = 100, window_seconds: int = 60) -> None:
        self.max_actions_per_window = max_actions_per_window
        self.window_seconds = window_seconds
        self._kill_switch = False
        self._circuit_open = False
        self._lock_owners: dict[str, str] = {}
        self._action_timestamps: dict[str, list[float]] = {}

    def activate_kill_switch(self) -> None:
        self._kill_switch = True

    def reset_kill_switch(self) -> None:
        self._kill_switch = False

    def open_circuit(self) -> None:
        self._circuit_open = True

    def close_circuit(self) -> None:
        self._circuit_open = False

    def acquire_lock(self, lock_name: str, owner_id: str) -> bool:
        current = self._lock_owners.get(lock_name)
        if current and current != owner_id:
            return False
        self._lock_owners[lock_name] = owner_id
        return True

    def release_lock(self, lock_name: str, owner_id: str) -> None:
        if self._lock_owners.get(lock_name) == owner_id:
            self._lock_owners.pop(lock_name, None)

    def enforce(self, *, action: str, bot_id: str, high_impact: bool = False, approved: bool = False) -> None:
        if self._kill_switch:
            raise SafetyViolation("kill switch is active")
        if self._circuit_open:
            raise SafetyViolation("circuit breaker is open")
        if high_impact and not approved:
            raise SafetyViolation("high-impact action requires BuddyAI/SafetyBot approval")
        self._check_rate_limit(bot_id)

    def _check_rate_limit(self, bot_id: str) -> None:
        now = time.time()
        window_start = now - self.window_seconds
        timestamps = [ts for ts in self._action_timestamps.get(bot_id, []) if ts >= window_start]
        if len(timestamps) >= self.max_actions_per_window:
            raise SafetyViolation("rate limit exceeded")
        timestamps.append(now)
        self._action_timestamps[bot_id] = timestamps
