"""
DreamCo Auth Middleware — Token-based access validation.

Provides helpers for validating Bearer tokens, enforcing tier-based
feature gates, and rate-limiting requests per user.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, Optional, Tuple

from saas.auth.auth import AuthService, User
from saas.auth.user_model import SubscriptionTier, TierFeatures, get_tier_features


# ---------------------------------------------------------------------------
# Middleware helpers
# ---------------------------------------------------------------------------


def extract_bearer_token(authorization_header: Optional[str]) -> Optional[str]:
    """
    Extract the raw token from an ``Authorization: Bearer <token>`` header.

    Returns
    -------
    str | None
    """
    if not authorization_header:
        return None
    parts = authorization_header.strip().split(None, 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


class AuthMiddleware:
    """
    Validates Bearer tokens and enforces access control.

    Parameters
    ----------
    auth_service : AuthService
        Shared auth service instance.
    """

    def __init__(self, auth_service: AuthService) -> None:
        self.auth = auth_service

    def authenticate(
        self, authorization_header: Optional[str]
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticate a request from its ``Authorization`` header.

        Returns
        -------
        (user, error_message)
            user is None and error_message is set on failure.
        """
        token = extract_bearer_token(authorization_header)
        if not token:
            return None, "missing or malformed Authorization header"

        user = self.auth.verify_token(token)
        if user is None:
            return None, "invalid or expired token"
        if not user.is_active:
            return None, "account is disabled"
        return user, None

    def require_tier(
        self, user: User, minimum_tier: SubscriptionTier
    ) -> Optional[str]:
        """
        Return an error string if *user* does not have *minimum_tier* or higher.

        Returns None if the user's tier is sufficient.
        """
        order = [
            SubscriptionTier.FREE,
            SubscriptionTier.PRO,
            SubscriptionTier.ENTERPRISE,
        ]
        user_tier = SubscriptionTier(user.tier.value)
        if order.index(user_tier) < order.index(minimum_tier):
            return (
                f"this feature requires {minimum_tier.value} tier; "
                f"your current tier is {user_tier.value}"
            )
        return None

    def get_user_features(self, user: User) -> TierFeatures:
        """Return the TierFeatures for *user*'s current subscription tier."""
        return get_tier_features(SubscriptionTier(user.tier.value))


# ---------------------------------------------------------------------------
# Per-user rate limiter (sliding window)
# ---------------------------------------------------------------------------


class RateLimiter:
    """
    Sliding-window per-user rate limiter.

    Parameters
    ----------
    max_requests : int
        Maximum number of requests allowed within *window_seconds*.
    window_seconds : int
        Length of the sliding window in seconds.
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._windows: Dict[str, list] = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        """
        Return True if *user_id* is within the rate limit.

        Side effect: records the current request timestamp.
        """
        now = time.time()
        window = self._windows[user_id]

        # Purge timestamps outside the current window
        cutoff = now - self.window_seconds
        self._windows[user_id] = [t for t in window if t > cutoff]

        if len(self._windows[user_id]) >= self.max_requests:
            return False

        self._windows[user_id].append(now)
        return True

    def remaining(self, user_id: str) -> int:
        """Return the number of remaining requests in the current window."""
        now = time.time()
        cutoff = now - self.window_seconds
        active = [t for t in self._windows.get(user_id, []) if t > cutoff]
        return max(self.max_requests - len(active), 0)

    def reset(self, user_id: str) -> None:
        """Clear the rate-limit window for *user_id*."""
        self._windows.pop(user_id, None)
