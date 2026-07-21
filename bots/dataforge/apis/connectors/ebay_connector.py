"""eBay Browse API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class EbayConnector:
    """EbayConnector for DataForge AI."""

    BASE_URL = "https://api.ebay.com/buy/browse/v1"

    def __init__(self):
        """Initialize connector, reading OAuth token from environment."""
        self.oauth_token = os.environ.get("EBAY_OAUTH_TOKEN", "")
        if not self.oauth_token:
            logger.warning("EBAY_OAUTH_TOKEN not set.")

    def search_items(self, query: str, limit: int = 10) -> dict:
        """Search eBay listings.

        Args:
            query: Search query string.
            limit: Max results (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.oauth_token}", "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"}
        params = {"q": query, "limit": limit}
        try:
            response = requests.get(f"{self.BASE_URL}/item_summary/search", params=params, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("eBay search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("eBay search_items error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_item(self, item_id: str) -> dict:
        """Get a specific eBay item by ID.

        Args:
            item_id: eBay item identifier.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.oauth_token}"}
        try:
            response = requests.get(f"{self.BASE_URL}/item/{item_id}", headers=headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("eBay get_item error: %s", e)
            return {"status": "error", "message": str(e)}
