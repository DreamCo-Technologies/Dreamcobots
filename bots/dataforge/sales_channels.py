"""Sales channels for DataForge AI datasets."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

PRICING = {
    "voice_dataset_bundle": {"price": 5000.00, "tier": "enterprise"},
    "facial_synthetic_set": {"price": 10000.00, "tier": "enterprise"},
    "behavioral_ai_pack": {"price": 15000.00, "tier": "enterprise"},
    "api_subscription_monthly": {"price": 499.00, "tier": "subscription"},
    "research_license_annual": {"price": 999.00, "tier": "research"},
}


class SalesChannels:
    """Manages all sales channels for DataForge AI datasets."""

    def __init__(self):
        """Initialize the SalesChannels with an empty sales log."""
        self._sales_log: list = []

    def _log_sale(self, channel: str, product: str, price: float, metadata: dict = None) -> dict:
        """Log a sale record internally.

        Args:
            channel: The sales channel name.
            product: The product name.
            price: Sale price in USD.
            metadata: Optional additional metadata dict.

        Returns:
            The sale record dict.
        """
        record = {
            "channel": channel,
            "product": product,
            "price": price,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        self._sales_log.append(record)
        logger.info("Sale recorded: channel=%s product=%s price=%.2f", channel, product, price)
        return record

    def push_to_huggingface(self, dataset_name: str, data: list, token: str = None) -> dict:
        """Push a dataset to HuggingFace Hub for sale or free distribution.

        Args:
            dataset_name: Name of the dataset to push.
            data: List of records to push.
            token: Optional HuggingFace API token.

        Returns:
            Result dict with channel, dataset, records, status, and url.
        """
        logger.info("Pushing %s to HuggingFace (%d records).", dataset_name, len(data))
        result = {
            "channel": "huggingface",
            "dataset": dataset_name,
            "records": len(data),
            "status": "queued",
            "url": f"https://huggingface.co/datasets/dataforge/{dataset_name}",
        }
        self._log_sale("huggingface", dataset_name, 0.0, result)
        return result

    def push_to_kaggle(self, dataset_name: str, data: list, description: str = "") -> dict:
        """Push a dataset to Kaggle for sale or competition use.

        Args:
            dataset_name: Name of the dataset.
            data: List of records to push.
            description: Optional dataset description.

        Returns:
            Result dict with channel, dataset, records, status, and url.
        """
        logger.info("Pushing %s to Kaggle (%d records).", dataset_name, len(data))
        result = {
            "channel": "kaggle",
            "dataset": dataset_name,
            "records": len(data),
            "status": "queued",
            "url": f"https://www.kaggle.com/datasets/dataforge/{dataset_name}",
        }
        self._log_sale("kaggle", dataset_name, 0.0, result)
        return result

    def push_to_aws_marketplace(self, product_name: str, pricing_key: str) -> dict:
        """List a dataset product on AWS Marketplace.

        Args:
            product_name: Human-readable product name.
            pricing_key: Key from PRICING dict to determine price.

        Returns:
            Result dict with channel, product, price, tier, and status.
        """
        pricing = PRICING.get(pricing_key, {"price": 0.0, "tier": "unknown"})
        logger.info("Listing %s on AWS Marketplace at $%.2f", product_name, pricing["price"])
        result = {
            "channel": "aws_marketplace",
            "product": product_name,
            "price": pricing["price"],
            "tier": pricing["tier"],
            "status": "listing_submitted",
        }
        self._log_sale("aws_marketplace", product_name, pricing["price"], result)
        return result

    def sell_direct_api(self, product_name: str, pricing_key: str, buyer_id: str) -> dict:
        """Process a direct API sale for a dataset product.

        Args:
            product_name: Name of the product.
            pricing_key: Key from PRICING dict.
            buyer_id: Identifier for the buyer.

        Returns:
            Result dict with channel, product, buyer_id, price, tier, status, and access_url.
        """
        pricing = PRICING.get(pricing_key, {"price": 0.0, "tier": "unknown"})
        logger.info("Direct API sale: %s to buyer %s at $%.2f", product_name, buyer_id, pricing["price"])
        result = {
            "channel": "direct_api",
            "product": product_name,
            "buyer_id": buyer_id,
            "price": pricing["price"],
            "tier": pricing["tier"],
            "status": "sold",
            "access_url": f"https://api.dataforge.ai/v1/datasets/{product_name}",
        }
        self._log_sale("direct_api", product_name, pricing["price"], result)
        return result

    def get_pricing(self) -> dict:
        """Return current pricing tiers.

        Returns:
            The PRICING dict with all product pricing.
        """
        return PRICING

    def get_sales_log(self) -> list:
        """Return all recorded sales.

        Returns:
            List of all sale record dicts.
        """
        return self._sales_log
