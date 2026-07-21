"""Direct API seller for DataForge AI datasets."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import hashlib
import logging
import os
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

PRICING_TIERS = {
    "standard": {"price": 499.00, "billing": "monthly", "description": "Standard API access"},
    "research": {"price": 999.00, "billing": "annual", "description": "Research license"},
    "enterprise": {"price": None, "billing": "custom", "description": "Enterprise custom pricing"},
}


class DirectAPISeller:
    """Manages direct API subscriptions and access key sales."""

    def __init__(self):
        """Initialize the seller with empty subscription and API key stores."""
        self._subscriptions: dict = {}
        self._api_keys: dict = {}

    def create_subscription(self, user_id: str, tier: str = "standard") -> dict:
        """Create a new subscription for a user.

        Args:
            user_id: The user identifier.
            tier: Pricing tier ('standard', 'research', 'enterprise').

        Returns:
            Subscription record dict with API key and details.

        Raises:
            ValueError: If tier is not valid.
        """
        if tier not in PRICING_TIERS:
            raise ValueError(f"Unknown tier: {tier}. Valid tiers: {list(PRICING_TIERS.keys())}")
        api_key = self.generate_api_key(user_id)
        subscription = {
            "subscription_id": str(uuid.uuid4()),
            "user_id": user_id,
            "tier": tier,
            "price": PRICING_TIERS[tier]["price"],
            "billing": PRICING_TIERS[tier]["billing"],
            "api_key": api_key,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
        }
        self._subscriptions[user_id] = subscription
        logger.info("Subscription created: user=%s tier=%s", user_id, tier)
        return subscription

    def verify_subscription(self, api_key: str) -> dict:
        """Verify that an API key has an active subscription.

        Args:
            api_key: The API key to verify.

        Returns:
            Dict with valid status, user_id, and tier.
        """
        user_id = self._api_keys.get(api_key)
        if not user_id:
            logger.warning("API key not found: %s", api_key[:8] + "***")
            return {"valid": False, "message": "API key not found."}
        subscription = self._subscriptions.get(user_id, {})
        active = subscription.get("status") == "active"
        logger.info("API key verification: user=%s active=%s", user_id, active)
        return {"valid": active, "user_id": user_id, "tier": subscription.get("tier")}

    def generate_api_key(self, user_id: str) -> str:
        """Generate a unique API key for a user.

        Args:
            user_id: The user identifier.

        Returns:
            A unique API key string prefixed with 'dfai_'.
        """
        raw = f"{user_id}-{uuid.uuid4()}-{os.urandom(16).hex()}"
        api_key = "dfai_" + hashlib.sha256(raw.encode()).hexdigest()[:40]
        self._api_keys[api_key] = user_id
        logger.info("API key generated for user %s.", user_id)
        return api_key

    def get_pricing_tiers(self) -> dict:
        """Return available pricing tiers.

        Returns:
            The PRICING_TIERS dict.
        """
        return PRICING_TIERS
