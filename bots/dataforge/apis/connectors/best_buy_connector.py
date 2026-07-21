"""Best Buy products API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class BestBuyConnector:
    """BestBuyConnector for DataForge AI."""

    BASE_URL = "https://api.bestbuy.com/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("BESTBUY_API_KEY", "")
        if not self.api_key:
            logger.warning("BESTBUY_API_KEY not set.")

    def search_products(self, query: str, pageSize: int = 10) -> dict:
        """Search Best Buy products.

        Args:
            query: Search query string.
            pageSize: Results per page (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"format": "json", "apiKey": self.api_key, "pageSize": pageSize}
        try:
            response = requests.get(f"{self.BASE_URL}/products((search={query}))", params=params, timeout=30)
            response.raise_for_status()
            logger.info("Best Buy product search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Best Buy search_products error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_product(self, sku: str) -> dict:
        """Get a Best Buy product by SKU.

        Args:
            sku: Best Buy product SKU.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"format": "json", "apiKey": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/products/{sku}.json", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Best Buy get_product error: %s", e)
            return {"status": "error", "message": str(e)}
