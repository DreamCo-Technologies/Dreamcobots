"""
DreamCo Client API Key Registry — generate, list, revoke, and categorise
per-user developer API keys.

Keys are structured tokens of the form:
    dc_<tier_prefix>_<random_hex_32>

Supported categories (for lookup / filtering):
    read_only    — GET endpoints only
    full_access  — all endpoints
    bot_runner   — bot execution endpoints only
    webhook      — webhook delivery only
    analytics    — stats / revenue endpoints only

The registry is intentionally kept in-memory for development; swap
``_store`` for a database-backed store in production.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Valid categories
# ---------------------------------------------------------------------------

API_KEY_CATEGORIES = frozenset(
    {"read_only", "full_access", "bot_runner", "webhook", "analytics"}
)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class ClientApiKey:
    """A single issued developer API key.

    Attributes
    ----------
    key_id : str
        Short unique identifier (``kid_<hex8>``).  Used for lookup / revoke.
    key : str
        The actual secret token shown to the client on creation only.
    user_id : str
        Owner of this key.
    label : str
        Human-readable name chosen by the user.
    category : str
        One of :data:`API_KEY_CATEGORIES`.
    tier : str
        Tier copied from the owning user (``free`` / ``pro`` / ``enterprise``).
    created_at : float
        Unix timestamp of creation.
    last_used_at : float | None
        Unix timestamp of last successful use (updated externally).
    is_active : bool
        ``False`` once the key has been revoked.
    call_count : int
        Cumulative number of successful API calls authenticated with this key.
    """

    key_id: str
    key: str
    user_id: str
    label: str
    category: str
    tier: str
    created_at: float = field(default_factory=time.time)
    last_used_at: Optional[float] = None
    is_active: bool = True
    call_count: int = 0

    def to_dict(self, *, include_key: bool = False) -> dict:
        """Serialise to a plain dict.

        Parameters
        ----------
        include_key:
            When ``True`` the raw secret key is included.  Only pass
            ``True`` immediately after key creation — never return it again.
        """
        d = {
            "key_id": self.key_id,
            "user_id": self.user_id,
            "label": self.label,
            "category": self.category,
            "tier": self.tier,
            "created_at": self.created_at,
            "last_used_at": self.last_used_at,
            "is_active": self.is_active,
            "call_count": self.call_count,
        }
        if include_key:
            d["key"] = self.key
        return d


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class ClientApiKeyRegistry:
    """In-memory registry for per-user developer API keys.

    Methods
    -------
    generate_key(user_id, label, category, tier)
        Create and store a new key; returns the full :class:`ClientApiKey`.
    list_keys(user_id, *, category, active_only)
        List keys owned by *user_id* with optional filters.
    revoke_key(user_id, key_id)
        Soft-delete a key; raises ``KeyError`` if not found or not owned.
    get_key_by_value(key)
        Look up a key record by its raw token value (used during auth).
    record_usage(key_id)
        Increment call count and update last_used_at.
    usage_summary(user_id)
        Aggregate usage statistics across all keys owned by *user_id*.
    """

    def __init__(self) -> None:
        # key_id -> ClientApiKey
        self._store: Dict[str, ClientApiKey] = {}
        # raw key value -> key_id (for O(1) auth lookup)
        self._value_index: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def generate_key(
        self,
        user_id: str,
        label: str,
        category: str,
        tier: str = "free",
    ) -> ClientApiKey:
        """Generate and store a new API key.

        Parameters
        ----------
        user_id:
            Owning user identifier.
        label:
            Human-readable name (e.g. "My Bot Runner Key").
        category:
            Must be one of :data:`API_KEY_CATEGORIES`.
        tier:
            The user's current subscription tier string.

        Returns
        -------
        ClientApiKey
            The newly created key record.  The ``key`` field is the raw
            secret — expose it to the user once and discard.

        Raises
        ------
        ValueError
            If *category* is not a recognised value.
        """
        if not label or not label.strip():
            raise ValueError("label must be a non-empty string")
        category = category.lower()
        if category not in API_KEY_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. "
                f"Choose from: {sorted(API_KEY_CATEGORIES)}"
            )

        tier_prefix = _tier_prefix(tier)
        raw_key = f"dc_{tier_prefix}_{secrets.token_hex(16)}"
        key_id = f"kid_{secrets.token_hex(4)}"

        record = ClientApiKey(
            key_id=key_id,
            key=raw_key,
            user_id=user_id,
            label=label.strip(),
            category=category,
            tier=tier,
        )
        self._store[key_id] = record
        self._value_index[raw_key] = key_id
        return record

    # ------------------------------------------------------------------
    # Listing / filtering
    # ------------------------------------------------------------------

    def list_keys(
        self,
        user_id: str,
        *,
        category: Optional[str] = None,
        active_only: bool = True,
    ) -> List[ClientApiKey]:
        """Return all keys for *user_id* with optional filters.

        Parameters
        ----------
        user_id:
            Owner to filter by.
        category:
            When set, only keys in this category are returned.
        active_only:
            When ``True`` (default) revoked keys are excluded.
        """
        results = []
        for rec in self._store.values():
            if rec.user_id != user_id:
                continue
            if active_only and not rec.is_active:
                continue
            if category and rec.category != category.lower():
                continue
            results.append(rec)
        results.sort(key=lambda r: r.created_at, reverse=True)
        return results

    # ------------------------------------------------------------------
    # Revocation
    # ------------------------------------------------------------------

    def revoke_key(self, user_id: str, key_id: str) -> ClientApiKey:
        """Revoke (soft-delete) a key.

        Parameters
        ----------
        user_id:
            Must match the key's owner — prevents cross-user revocation.
        key_id:
            The ``key_id`` of the key to revoke.

        Returns
        -------
        ClientApiKey
            The (now-revoked) key record.

        Raises
        ------
        KeyError
            If the key does not exist or is not owned by *user_id*.
        """
        rec = self._store.get(key_id)
        if rec is None or rec.user_id != user_id:
            raise KeyError(f"API key '{key_id}' not found for user '{user_id}'")
        rec.is_active = False
        return rec

    # ------------------------------------------------------------------
    # Auth lookup
    # ------------------------------------------------------------------

    def get_key_by_value(self, key: str) -> Optional[ClientApiKey]:
        """Return the active :class:`ClientApiKey` for *key*, or ``None``."""
        key_id = self._value_index.get(key)
        if key_id is None:
            return None
        rec = self._store.get(key_id)
        if rec is None or not rec.is_active:
            return None
        return rec

    # ------------------------------------------------------------------
    # Usage tracking
    # ------------------------------------------------------------------

    def record_usage(self, key_id: str) -> None:
        """Increment call count and update last_used_at for *key_id*."""
        rec = self._store.get(key_id)
        if rec:
            rec.call_count += 1
            rec.last_used_at = time.time()

    def usage_summary(self, user_id: str) -> dict:
        """Return aggregate usage stats for all keys owned by *user_id*.

        Returns
        -------
        dict
            Keys: ``total_keys``, ``active_keys``, ``total_calls``,
            ``by_category`` (dict of category → call count).
        """
        all_keys = list(self._store[k] for k in self._store if self._store[k].user_id == user_id)
        by_category: Dict[str, int] = {}
        total_calls = 0
        active = 0
        for rec in all_keys:
            if rec.is_active:
                active += 1
            total_calls += rec.call_count
            by_category[rec.category] = by_category.get(rec.category, 0) + rec.call_count
        return {
            "user_id": user_id,
            "total_keys": len(all_keys),
            "active_keys": active,
            "total_calls": total_calls,
            "by_category": by_category,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _tier_prefix(tier: str) -> str:
    mapping = {"enterprise": "ent", "pro": "pro", "free": "free"}
    return mapping.get(tier.lower(), "free")
