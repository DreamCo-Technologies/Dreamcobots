"""Item/product dataset generator for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import random
import uuid
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

CATEGORIES = [
    "Electronics", "Clothing", "Home & Garden", "Sports", "Books",
    "Toys", "Automotive", "Health", "Beauty", "Food & Grocery",
]
ADJECTIVES = ["Premium", "Deluxe", "Professional", "Smart", "Ultra", "Classic", "Advanced"]
NOUNS = ["Widget", "Device", "Tool", "Gadget", "System", "Kit", "Bundle", "Pack"]


class ItemDatasetGenerator:
    """Generates synthetic product/item metadata for e-commerce AI training."""

    def _generate_price_history(self, base_price: float, num_points: int = 6) -> list:
        """Generate a price history for a product.

        Args:
            base_price: Starting price for history generation.
            num_points: Number of historical price points (default 6).

        Returns:
            List of dicts with 'date' and 'price' keys.
        """
        history = []
        price = base_price
        for i in range(num_points):
            date = (datetime.utcnow() - timedelta(days=30 * (num_points - i))).isoformat()
            price = round(price * random.uniform(0.85, 1.15), 2)
            history.append({"date": date, "price": price})
        return history

    def generate(self, num_items: int = 500) -> list:
        """Generate product metadata records.

        Args:
            num_items: Number of product records to generate (default 500).

        Returns:
            List of product metadata record dicts.
        """
        records = []
        for i in range(num_items):
            base_price = round(random.uniform(5.99, 999.99), 2)
            record = {
                "id": str(uuid.uuid4()),
                "index": i,
                "name": f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} {random.randint(100, 9999)}",
                "category": random.choice(CATEGORIES),
                "description": f"High-quality synthetic product for AI training dataset purposes.",
                "price": base_price,
                "price_history": self._generate_price_history(base_price),
                "sku": f"SKU-{uuid.uuid4().hex[:8].upper()}",
                "in_stock": random.choice([True, False]),
                "rating": round(random.uniform(1.0, 5.0), 1),
                "review_count": random.randint(0, 5000),
                "format": "JSON",
                "synthetic": True,
                "license": "CC-BY-4.0",
            }
            records.append(record)
        logger.info("Generated %d item dataset records.", num_items)
        return records
