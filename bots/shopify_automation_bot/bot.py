"""
Dreamcobots ShopifyAutomationBot — tier-aware Shopify store automation.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.shopify_automation_bot.tiers import SHOPIFY_AUTOMATION_FEATURES, get_shopify_automation_tier_info
import uuid
from datetime import datetime


class ShopifyAutomationBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class ShopifyAutomationBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class ShopifyAutomationBot:
    """Tier-aware Shopify store automation bot."""

    ORDER_LIMITS = {
        "free": 100,
        "pro": 10000,
        "enterprise": None,
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._stores: list = []
        self._orders_processed: int = 0

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise ShopifyAutomationBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_order_limit(self) -> None:
        limit = self.ORDER_LIMITS[self.tier.value]
        if limit is not None and self._orders_processed >= limit:
            raise ShopifyAutomationBotRequestLimitError(
                f"Monthly order limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_feature(self, feature: str) -> None:
        features = SHOPIFY_AUTOMATION_FEATURES[self.tier.value]
        if not any(feature.lower() in f.lower() for f in features):
            raise ShopifyAutomationBotTierError(
                f"'{feature}' is not available on the {self.config.name} tier. "
                f"Please upgrade to access this feature."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    def sync_inventory(self, store_id: str) -> dict:
        """
        Sync inventory for a Shopify store.

        Args:
            store_id: The store identifier.

        Returns:
            {"store_id": str, "synced_items": int, "status": str, "tier": str}
        """
        self._check_request_limit()
        self._request_count += 1

        if self.tier == Tier.FREE:
            store_limit = 1
            if store_id not in self._stores:
                if len(self._stores) >= store_limit:
                    raise ShopifyAutomationBotTierError(
                        f"Store limit of {store_limit} reached on the Free tier. "
                        "Please upgrade to connect more stores."
                    )
                self._stores.append(store_id)
            synced_items = 10
            status = "basic_sync_complete"

        elif self.tier == Tier.PRO:
            store_limit = 3
            if store_id not in self._stores:
                if len(self._stores) >= store_limit:
                    raise ShopifyAutomationBotTierError(
                        f"Store limit of {store_limit} reached on the Pro tier. "
                        "Please upgrade to Enterprise to connect unlimited stores."
                    )
                self._stores.append(store_id)
            synced_items = 100
            status = "full_sync_complete"

        else:  # ENTERPRISE
            if store_id not in self._stores:
                self._stores.append(store_id)
            synced_items = 1000
            status = "bulk_sync_complete"

        return {
            "store_id": store_id,
            "synced_items": synced_items,
            "status": status,
            "tier": self.tier.value,
        }

    def process_order(self, order: dict) -> dict:
        """
        Process a Shopify order with automated actions.

        Args:
            order: {"order_id": str, "items": list, "customer": dict}

        Returns:
            {"order_id": str, "status": str, "automated_actions": list, "tier": str}
        """
        self._check_request_limit()
        self._check_order_limit()
        self._request_count += 1
        self._orders_processed += 1

        order_id = order.get("order_id", str(uuid.uuid4()))

        if self.tier == Tier.FREE:
            automated_actions = ["send_confirmation"]
        elif self.tier == Tier.PRO:
            automated_actions = ["send_confirmation", "update_inventory", "notify_fulfillment"]
        else:  # ENTERPRISE
            automated_actions = [
                "send_confirmation",
                "update_inventory",
                "notify_fulfillment",
                "trigger_workflow",
                "update_crm",
            ]

        return {
            "order_id": order_id,
            "status": "processed",
            "automated_actions": automated_actions,
            "tier": self.tier.value,
        }

    def automate_workflow(self, workflow: dict) -> dict:
        """
        Create an automated workflow for store operations.

        Args:
            workflow: {"name": str, "trigger": str, "actions": list}

        Returns:
            {"workflow_id": str, "name": str, "status": str, "tier": str}
        """
        if self.tier == Tier.FREE:
            raise ShopifyAutomationBotTierError(
                "Custom workflow automation is not available on the Free tier. "
                "Please upgrade to PRO or ENTERPRISE."
            )

        workflow_id = str(uuid.uuid4())
        name = workflow.get("name", "unnamed_workflow")

        return {
            "workflow_id": workflow_id,
            "name": name,
            "status": "active",
            "tier": self.tier.value,
        }

    def get_stats(self) -> dict:
        return {
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
            "stores_connected": len(self._stores),
            "orders_processed": self._orders_processed,
            "buddy_integration": True,
        }
