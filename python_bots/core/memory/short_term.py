"""
DreamCo OS — Short-Term Memory (Redis)
========================================

Session-scoped memory backed by Redis with a configurable TTL (default 24 h).
Falls back gracefully to an in-process dict when Redis is unavailable so that
bots can run in development without an external Redis server.

Usage::

    mem = ShortTermMemory(bot_id="my_bot", redis_url="redis://localhost:6379")
    mem.save("last_task", {"result": "ok", "tokens": 123})
    value = mem.load("last_task")   # {"result": "ok", "tokens": 123}
    mem.forget("last_task")
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_TTL = 86_400  # 24 hours


class ShortTermMemory:
    """Redis-backed short-term memory with TTL and in-process fallback.

    Parameters
    ----------
    bot_id:
        Unique identifier for the owning bot — used as the Redis key namespace.
    redis_url:
        Redis connection string.  Reads ``REDIS_URL`` env-var when not supplied.
    ttl:
        Time-to-live in seconds for every key (default 86 400 = 24 h).
    """

    def __init__(
        self,
        bot_id: str,
        redis_url: str | None = None,
        ttl: int = _DEFAULT_TTL,
    ) -> None:
        self.bot_id = bot_id
        self.ttl = ttl
        self._redis: Any = None
        self._fallback: dict[str, tuple[Any, float]] = {}  # key → (value, expires_at)

        url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            import redis  # type: ignore

            self._redis = redis.from_url(url, socket_connect_timeout=2)
            self._redis.ping()
            logger.debug("ShortTermMemory connected to Redis at %s", url)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "ShortTermMemory: Redis unavailable (%s) — using in-process fallback",
                exc,
            )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _make_key(self, key: str) -> str:
        return f"dreamco:{self.bot_id}:{key}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, key: str, value: Any) -> None:
        """Persist *value* under *key* with the configured TTL."""
        encoded = json.dumps(value)
        if self._redis is not None:
            try:
                self._redis.setex(self._make_key(key), self.ttl, encoded)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("ShortTermMemory.save Redis error: %s", exc)
        # Fallback
        self._fallback[key] = (value, time.time() + self.ttl)

    def load(self, key: str) -> Any | None:
        """Return the value stored under *key*, or ``None`` if missing/expired."""
        if self._redis is not None:
            try:
                raw = self._redis.get(self._make_key(key))
                return json.loads(raw) if raw is not None else None
            except Exception as exc:  # noqa: BLE001
                logger.warning("ShortTermMemory.load Redis error: %s", exc)
        # Fallback
        entry = self._fallback.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self._fallback[key]
            return None
        return value

    def forget(self, key: str) -> None:
        """Delete *key* (GDPR-compliant selective deletion)."""
        if self._redis is not None:
            try:
                self._redis.delete(self._make_key(key))
            except Exception as exc:  # noqa: BLE001
                logger.warning("ShortTermMemory.forget Redis error: %s", exc)
        self._fallback.pop(key, None)

    def keys(self) -> list[str]:
        """Return all active keys for this bot."""
        if self._redis is not None:
            try:
                pattern = self._make_key("*")
                prefix = self._make_key("")
                return [
                    k.decode().removeprefix(prefix)
                    for k in self._redis.keys(pattern)
                ]
            except Exception as exc:  # noqa: BLE001
                logger.warning("ShortTermMemory.keys Redis error: %s", exc)
        # Fallback — prune expired
        now = time.time()
        expired = [k for k, (_, exp) in self._fallback.items() if now > exp]
        for k in expired:
            del self._fallback[k]
        return list(self._fallback)
