"""
DreamCo Payments — API Manager

Manages API keys, rotation, revocation, validation, and usage analytics.
The DREAMCO_STRIPE_KEY is loaded from the environment (placeholder only —
no real Stripe credentials are stored or transmitted).

Key generation uses hashlib.sha256; no external crypto libraries required.
"""

import hashlib
import hmac
import os
import uuid
import datetime
from typing import Optional

from bots.dreamco_payments.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    FEATURE_API_KEY_MANAGEMENT,
)
from framework import GlobalAISourcesFlow  # noqa: F401


class APITierError(Exception):
    """Raised when an API-management feature is not available on the current tier."""


# Placeholder Stripe key — loaded from environment, never hard-coded.
DREAMCO_STRIPE_KEY: str = (
    os.environ.get("STRIPE_SECRET_KEY")
    or os.environ.get("DREAMCO_STRIPE_KEY")
    or "sk_test_placeholder_dreamco_stripe_key"
)


class APIManager:
    """
    Tier-aware API key manager for DreamCo Payments.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature access.
    """

    def __init__(self, tier: Tier = Tier.STARTER) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        # key_id -> metadata record
        self._keys: dict[str, dict] = {}
        # key_id -> usage stats
        self._usage: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise APITierError(
                f"Feature '{feature}' is not available on the "
                f"{self.config.name} tier.  Please upgrade."
            )

    @staticmethod
    def _now_iso() -> str:
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _generate_raw_key() -> str:
        """Return a hex string derived from a UUID and sha256."""
        raw = uuid.uuid4().hex + uuid.uuid4().hex
        return hashlib.sha256(raw.encode()).hexdigest()

    # ------------------------------------------------------------------
    # Key lifecycle
    # ------------------------------------------------------------------

    def generate_api_key(self, name: str, permissions: list) -> dict:
        """
        Generate a new API key.

        Parameters
        ----------
        name : str
            Human-readable label for the key.
        permissions : list[str]
            List of permission scopes (e.g. ["payments:read", "payments:write"]).

        Returns
        -------
        dict
            key_id, key (sha256-hashed hex), created_at, permissions, name.
        """
        self._require_feature(FEATURE_API_KEY_MANAGEMENT)

        key_id = f"kid_{uuid.uuid4().hex[:10]}"
        raw_key = self._generate_raw_key()
        created_at = self._now_iso()

        record = {
            "key_id": key_id,
            "key": raw_key,
            "name": name,
            "permissions": list(permissions),
            "created_at": created_at,
            "status": "active",
        }
        self._keys[key_id] = record
        self._usage[key_id] = {
            "request_count": 0,
            "last_used": None,
            "key_id": key_id,
        }
        return dict(record)

    def rotate_api_key(self, key_id: str) -> dict:
        """
        Rotate (regenerate) an existing API key.

        Parameters
        ----------
        key_id : str
            Key to rotate.

        Returns
        -------
        dict
            Updated key record with a new key value.
        """
        self._require_feature(FEATURE_API_KEY_MANAGEMENT)

        if key_id not in self._keys:
            raise KeyError(f"API key '{key_id}' not found.")

        new_raw = self._generate_raw_key()
        self._keys[key_id]["key"] = new_raw
        self._keys[key_id]["rotated_at"] = self._now_iso()
        return dict(self._keys[key_id])

    def revoke_api_key(self, key_id: str) -> dict:
        """
        Revoke an API key, preventing further use.

        Parameters
        ----------
        key_id : str
            Key to revoke.

        Returns
        -------
        dict
            Updated key record with status 'revoked'.
        """
        self._require_feature(FEATURE_API_KEY_MANAGEMENT)

        if key_id not in self._keys:
            raise KeyError(f"API key '{key_id}' not found.")

        self._keys[key_id]["status"] = "revoked"
        self._keys[key_id]["revoked_at"] = self._now_iso()
        return dict(self._keys[key_id])

    def validate_api_key(self, key: str) -> bool:
        """
        Validate that a raw key value is active.

        Parameters
        ----------
        key : str
            Raw key string to validate.

        Returns
        -------
        bool
            True if the key matches an active record, False otherwise.
        """
        for record in self._keys.values():
            if record["status"] == "active" and hmac.compare_digest(
                record["key"], key
            ):
                return True
        return False

    # ------------------------------------------------------------------
    # Usage analytics
    # ------------------------------------------------------------------

    def record_api_call(self, key_id: str) -> None:
        """
        Increment the request counter for *key_id*.

        Parameters
        ----------
        key_id : str
            The key that was used.
        """
        if key_id not in self._usage:
            raise KeyError(f"API key '{key_id}' not found.")

        self._usage[key_id]["request_count"] += 1
        self._usage[key_id]["last_used"] = self._now_iso()

    def get_usage_analytics(self, key_id: str) -> dict:
        """
        Return usage statistics for *key_id*.

        Parameters
        ----------
        key_id : str
            Key to query.

        Returns
        -------
        dict
            request_count, last_used, key_id, and key metadata.
        """
        if key_id not in self._usage:
            raise KeyError(f"API key '{key_id}' not found.")

        usage = dict(self._usage[key_id])
        key_meta = self._keys[key_id]
        usage["name"] = key_meta["name"]
        usage["status"] = key_meta["status"]
        usage["permissions"] = key_meta["permissions"]
        return usage

    def list_api_keys(self) -> list:
        """
        Return metadata for all managed API keys (key values omitted).

        Returns
        -------
        list[dict]
            Key records without the raw key value.
        """
        result = []
        for kid, record in self._keys.items():
            entry = {k: v for k, v in record.items() if k != "key"}
            entry["request_count"] = self._usage[kid]["request_count"]
            result.append(entry)
        return result
