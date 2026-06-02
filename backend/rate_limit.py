"""Redis-backed sliding-window rate limiting middleware for FastAPI."""

from __future__ import annotations

import os
import time
from collections import defaultdict
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from redis.asyncio import Redis
except ImportError:  # pragma: no cover - optional runtime dependency
    Redis = None

try:
    from slowapi.errors import RateLimitExceeded
except ImportError:  # pragma: no cover - fallback when slowapi is unavailable
    class RateLimitExceeded(Exception):
        def __init__(self, detail: str) -> None:
            super().__init__(detail)
            self.detail = detail


RATE_LIMITS = {
    "free": 100,
    "pro": 1000,
    "enterprise": 10000,
    "elite": 0,
}


class SlidingWindowRateLimiter:
    """Track request timestamps in Redis ZSETs with in-memory fallback."""

    def __init__(self, redis_url: str | None = None, window_seconds: int = 3600) -> None:
        self.window_seconds = window_seconds
        self.redis = Redis.from_url(redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")) if Redis else None
        self._memory_store: dict[str, list[float]] = defaultdict(list)

    async def _redis_eval(self, key: str, now: float) -> tuple[int, float]:
        assert self.redis is not None
        pipeline = self.redis.pipeline()
        min_score = now - self.window_seconds
        pipeline.zremrangebyscore(key, 0, min_score)
        pipeline.zadd(key, {f"{now}:{time.monotonic_ns()}": now})
        pipeline.zcard(key)
        pipeline.expire(key, self.window_seconds)
        _, _, count, _ = await pipeline.execute()
        return int(count), now + self.window_seconds

    async def _memory_eval(self, key: str, now: float) -> tuple[int, float]:
        window_start = now - self.window_seconds
        active = [timestamp for timestamp in self._memory_store[key] if timestamp > window_start]
        active.append(now)
        self._memory_store[key] = active
        return len(active), now + self.window_seconds

    async def check(self, key: str, limit: int) -> dict[str, Any]:
        if limit == 0:
            return {"allowed": True, "limit": "unlimited", "remaining": "unlimited", "reset_at": None}
        now = time.time()
        count, reset_at = await (self._redis_eval(key, now) if self.redis is not None else self._memory_eval(key, now))
        remaining = max(limit - count, 0)
        return {"allowed": count <= limit, "limit": limit, "remaining": remaining, "reset_at": reset_at}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware enforcing per-API-key usage tiers."""

    def __init__(self, app, limiter: SlidingWindowRateLimiter | None = None) -> None:
        super().__init__(app)
        self.limiter = limiter or SlidingWindowRateLimiter()

    @staticmethod
    def _resolve_tier(request: Request) -> tuple[str, str]:
        api_key = request.headers.get("x-api-key", "anonymous")
        tier = request.headers.get("x-api-tier", "free").lower()
        return api_key, tier if tier in RATE_LIMITS else "free"

    async def dispatch(self, request: Request, call_next):
        api_key, tier = self._resolve_tier(request)
        result = await self.limiter.check(f"rate_limit:{tier}:{api_key}", RATE_LIMITS[tier])
        if not result["allowed"]:
            exc = RateLimitExceeded(f"Rate limit exceeded for tier {tier}")
            return JSONResponse(
                status_code=429,
                content={"detail": getattr(exc, "detail", str(exc)), "tier": tier, "reset_at": result["reset_at"]},
                headers={"Retry-After": str(int(self.limiter.window_seconds))},
            )
        response = await call_next(request)
        response.headers["X-RateLimit-Tier"] = tier
        response.headers["X-RateLimit-Limit"] = str(result["limit"])
        response.headers["X-RateLimit-Remaining"] = str(result["remaining"])
        if result["reset_at"] is not None:
            response.headers["X-RateLimit-Reset"] = str(int(result["reset_at"]))
        return response


def install_rate_limiting(app) -> SlidingWindowRateLimiter:
    """Attach middleware to a FastAPI application and return the limiter."""
    limiter = SlidingWindowRateLimiter()
    app.add_middleware(RateLimitMiddleware, limiter=limiter)
    app.state.rate_limiter = limiter
    return limiter
