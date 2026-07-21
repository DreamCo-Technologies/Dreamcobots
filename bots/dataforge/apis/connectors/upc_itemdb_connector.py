"""UPC ItemDB product lookup connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class UPCItemDBConnector:
    """UPCItemDBConnector for DataForge AI."""

    BASE_URL = "https://api.upcitemdb.com/prod/trial"

    def __init__(self):
        """Initialize connector (trial endpoint requires no key)."""
        self.user_key = os.environ.get("UPCITEMDB_USER_KEY", "")

    def lookup(self, upc: str) -> dict:
        """Look up a product by UPC barcode.

        Args:
            upc: UPC barcode string.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {}
        if self.user_key:
            headers["user_key"] = self.user_key
        try:
            response = requests.get(f"{self.BASE_URL}/lookup", params={"upc": upc}, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("UPC ItemDB lookup completed for: %s", upc)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("UPC ItemDB lookup error: %s", e)
            return {"status": "error", "message": str(e)}

    def search(self, query: str, type: str = "product") -> dict:
        """Search UPC ItemDB products.

        Args:
            query: Search query string.
            type: Search type (default 'product').

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {}
        if self.user_key:
            headers["user_key"] = self.user_key
        try:
            response = requests.get(f"{self.BASE_URL}/search", params={"s": query, "type": type}, headers=headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("UPC ItemDB search error: %s", e)
            return {"status": "error", "message": str(e)}
