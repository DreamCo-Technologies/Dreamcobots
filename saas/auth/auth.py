"""
DreamCo SaaS Authentication — User registry, login, signup, and role-based
access control.

This module provides:
    UserRegistry   — in-memory user store (replace with a DB in production)
    AuthService    — sign-up, login, token generation, and verification
    Tier           — subscription tier enum used across the platform

Environment variables
---------------------
AUTH_SECRET_KEY   HMAC key used to sign session tokens (default: dev key)
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# Subscription tiers
# ---------------------------------------------------------------------------


class Tier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# User model (lightweight in-memory version)
# ---------------------------------------------------------------------------


@dataclass
class User:
    user_id: str
    username: str
    email: str
    _password_hash: str
    tier: Tier = Tier.FREE
    created_at: float = field(default_factory=time.time)
    is_active: bool = True
    bot_quota: int = 5           # bots allowed to upload / run per day
    runs_today: int = 0          # reset daily
    stripe_customer_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "tier": self.tier.value,
            "created_at": self.created_at,
            "is_active": self.is_active,
            "bot_quota": self.bot_quota,
            "runs_today": self.runs_today,
            "stripe_customer_id": self.stripe_customer_id,
        }


# ---------------------------------------------------------------------------
# Token management
# ---------------------------------------------------------------------------

_SECRET_KEY: str = os.environ.get("AUTH_SECRET_KEY", "dreamco_dev_secret_key_change_me")
_TOKEN_TTL: int = 86_400  # 24 hours

_TIER_QUOTAS: Dict[Tier, int] = {
    Tier.FREE: 5,
    Tier.PRO: 100,
    Tier.ENTERPRISE: 10_000,
}


def _hash_password(password: str) -> str:
    """Return a salted PBKDF2-HMAC-SHA256 hash of *password*."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return f"{salt}:{dk.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    """Return True if *password* matches *stored_hash*."""
    try:
        salt, dk_hex = stored_hash.split(":", 1)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except Exception:
        return False


def _generate_token(user_id: str) -> str:
    """Generate a simple HMAC token embedding user_id and expiry."""
    expiry = int(time.time()) + _TOKEN_TTL
    payload = f"{user_id}:{expiry}"
    sig = hmac.new(_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def _verify_token(token: str) -> Optional[str]:
    """
    Verify *token* and return the user_id if valid and not expired.

    Returns
    -------
    str | None
        The user_id encoded in the token, or ``None`` if invalid.
    """
    try:
        parts = token.rsplit(":", 1)
        if len(parts) != 2:
            return None
        payload, sig = parts
        expected = hmac.new(_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        uid_part, expiry_str = payload.rsplit(":", 1)
        if int(expiry_str) < int(time.time()):
            return None
        return uid_part
    except Exception:
        return None


# ---------------------------------------------------------------------------
# User registry (in-memory; swap for SQLite/Postgres in production)
# ---------------------------------------------------------------------------


class UserRegistry:
    """In-memory user store with lookup by ID and by email."""

    def __init__(self) -> None:
        self._by_id: Dict[str, User] = {}
        self._by_email: Dict[str, str] = {}  # email -> user_id

    def add(self, user: User) -> None:
        self._by_id[user.user_id] = user
        self._by_email[user.email.lower()] = user.user_id

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._by_id.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        uid = self._by_email.get(email.lower())
        return self._by_id.get(uid) if uid else None

    def update_tier(self, user_id: str, tier: Tier) -> bool:
        user = self._by_id.get(user_id)
        if not user:
            return False
        user.tier = tier
        user.bot_quota = _TIER_QUOTAS[tier]
        return True

    def all_users(self) -> list:
        return list(self._by_id.values())

    def count(self) -> int:
        return len(self._by_id)


# ---------------------------------------------------------------------------
# AuthService
# ---------------------------------------------------------------------------


class AuthService:
    """
    Handles signup, login, token verification, and tier management.

    Parameters
    ----------
    registry : UserRegistry | None
        Shared user store.  A fresh registry is created if ``None``.
    """

    def __init__(self, registry: Optional[UserRegistry] = None) -> None:
        self.registry = registry or UserRegistry()

    # ------------------------------------------------------------------
    # Account management
    # ------------------------------------------------------------------

    def signup(self, username: str, email: str, password: str) -> dict:
        """
        Create a new FREE-tier user account.

        Returns
        -------
        dict
            ``{ success, user_id, token }`` on success or ``{ error }`` on
            failure.
        """
        if not username or not email or not password:
            return {"success": False, "error": "username, email and password are required"}
        if len(password) < 8:
            return {"success": False, "error": "password must be at least 8 characters"}
        if self.registry.get_by_email(email):
            return {"success": False, "error": "email already registered"}

        user_id = f"usr_{secrets.token_hex(8)}"
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            _password_hash=_hash_password(password),
            tier=Tier.FREE,
            bot_quota=_TIER_QUOTAS[Tier.FREE],
        )
        self.registry.add(user)
        token = _generate_token(user_id)
        return {"success": True, "user_id": user_id, "token": token}

    def login(self, email: str, password: str) -> dict:
        """
        Authenticate a user.

        Returns
        -------
        dict
            ``{ success, user_id, token, tier }`` or ``{ error }``.
        """
        user = self.registry.get_by_email(email)
        if not user or not _verify_password(password, user._password_hash):
            return {"success": False, "error": "invalid credentials"}
        if not user.is_active:
            return {"success": False, "error": "account is disabled"}

        token = _generate_token(user.user_id)
        return {
            "success": True,
            "user_id": user.user_id,
            "token": token,
            "tier": user.tier.value,
        }

    def verify_token(self, token: str) -> Optional[User]:
        """
        Verify *token* and return the corresponding User.

        Returns
        -------
        User | None
        """
        user_id = _verify_token(token)
        if not user_id:
            return None
        return self.registry.get_by_id(user_id)

    def upgrade_tier(self, user_id: str, tier) -> dict:
        """
        Upgrade a user's subscription tier.

        Parameters
        ----------
        tier : Tier | str
            The target tier, as a Tier enum value or its string name
            (``"free"``, ``"pro"``, ``"enterprise"``).

        Returns
        -------
        dict
            ``{ success, tier }`` or ``{ error }``.
        """
        if isinstance(tier, str):
            try:
                tier = Tier(tier)
            except ValueError:
                return {"success": False, "error": f"unknown tier: {tier!r}"}
        if not self.registry.update_tier(user_id, tier):
            return {"success": False, "error": "user not found"}
        return {"success": True, "tier": tier.value}

    # ------------------------------------------------------------------
    # Quota helpers
    # ------------------------------------------------------------------

    def check_quota(self, user_id: str) -> dict:
        """
        Return quota information for *user_id*.

        Returns
        -------
        dict
            ``{ allowed, runs_today, remaining }``.
        """
        user = self.registry.get_by_id(user_id)
        if not user:
            return {"allowed": False, "error": "user not found"}
        remaining = max(user.bot_quota - user.runs_today, 0)
        return {
            "allowed": remaining > 0,
            "runs_today": user.runs_today,
            "bot_quota": user.bot_quota,
            "remaining": remaining,
        }

    def consume_quota(self, user_id: str) -> bool:
        """
        Record a bot run for *user_id*.

        Returns
        -------
        bool
            ``True`` if the run was within quota, ``False`` otherwise.
        """
        user = self.registry.get_by_id(user_id)
        if not user:
            return False
        if user.runs_today >= user.bot_quota:
            return False
        user.runs_today += 1
        return True

    def reset_daily_quotas(self) -> int:
        """Reset run counters for all users.  Returns the number of users reset."""
        count = 0
        for user in self.registry.all_users():
            user.runs_today = 0
            count += 1
        return count
