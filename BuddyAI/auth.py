"""
BuddyAI Authentication Module
------------------------------
Provides shared authentication and authorization utilities for all bots
in the DreamCobots ecosystem.
"""

import hashlib
import hmac
import secrets
from typing import Optional


class AuthError(Exception):
    """Raised when authentication or authorization fails."""


class AuthModule:
    """Handles bot authentication and permission management.

    Each bot registers with a unique token.  Callers may then verify
    tokens and check whether a given bot holds a required permission.

    Example::

        auth = AuthModule()
        token = auth.register_bot("dreamcobot", permissions=["task:run"])
        auth.verify_token("dreamcobot", token)          # OK
        auth.require_permission("dreamcobot", "task:run")  # OK
    """

    def __init__(self) -> None:
        # Maps bot_id -> {"token_hash": str, "permissions": set[str]}
        self._registry: dict = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_bot(self, bot_id: str, permissions: Optional[list] = None) -> str:
        """Register *bot_id* and return a fresh secret token.

        Parameters
        ----------
        bot_id:
            Unique identifier for the bot.
        permissions:
            List of permission strings granted to the bot (e.g.
            ``["task:run", "knowledge:read"]``).

        Returns
        -------
        str
            The plain-text token the bot should keep secret.
        """
        if not bot_id:
            raise ValueError("bot_id must not be empty")
        token = secrets.token_hex(32)
        token_hash = self._hash_token(token)
        self._registry[bot_id] = {
            "token_hash": token_hash,
            "permissions": set(permissions or []),
        }
        return token

    def unregister_bot(self, bot_id: str) -> None:
        """Remove *bot_id* from the registry."""
        self._registry.pop(bot_id, None)

    # ------------------------------------------------------------------
    # Token verification
    # ------------------------------------------------------------------

    def verify_token(self, bot_id: str, token: str) -> bool:
        """Return ``True`` when *token* is valid for *bot_id*.

        Raises
        ------
        AuthError
            If *bot_id* is not registered or the token is wrong.
        """
        entry = self._registry.get(bot_id)
        if entry is None:
            raise AuthError(f"Bot '{bot_id}' is not registered")
        expected = entry["token_hash"]
        actual = self._hash_token(token)
        if not hmac.compare_digest(expected, actual):
            raise AuthError(f"Invalid token for bot '{bot_id}'")
        return True

    # ------------------------------------------------------------------
    # Permission checks
    # ------------------------------------------------------------------

    def require_permission(self, bot_id: str, permission: str) -> None:
        """Raise :class:`AuthError` if *bot_id* does not hold *permission*.

        Parameters
        ----------
        bot_id:
            The bot to check.
        permission:
            Permission string, e.g. ``"task:run"``.
        """
        entry = self._registry.get(bot_id)
        if entry is None:
            raise AuthError(f"Bot '{bot_id}' is not registered")
        if permission not in entry["permissions"]:
            raise AuthError(
                f"Bot '{bot_id}' does not have permission '{permission}'"
            )

    def has_permission(self, bot_id: str, permission: str) -> bool:
        """Return ``True`` when *bot_id* holds *permission*."""
        entry = self._registry.get(bot_id)
        if entry is None:
            return False
        return permission in entry["permissions"]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
