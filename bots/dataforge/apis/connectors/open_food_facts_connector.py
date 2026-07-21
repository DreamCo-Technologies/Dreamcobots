"""Open Food Facts nutrition data connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class OpenFoodFactsConnector:
    """OpenFoodFactsConnector for DataForge AI."""

    BASE_URL = "https://world.openfoodfacts.org/api/v0"

    def __init__(self):
        """Initialize connector (no API key required)."""
        self.headers = {"User-Agent": "DataForge-AI-Bot/1.0 (dataforge@example.com)"}

    def get_product(self, barcode: str) -> dict:
        """Get food product data by barcode.

        Args:
            barcode: Product barcode string.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/product/{barcode}.json", headers=self.headers, timeout=30)
            response.raise_for_status()
            logger.info("Open Food Facts product fetched for barcode: %s", barcode)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Open Food Facts get_product error: %s", e)
            return {"status": "error", "message": str(e)}

    def search_products(self, query: str, page: int = 1) -> dict:
        """Search Open Food Facts products.

        Args:
            query: Search query string.
            page: Page number (default 1).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"search_terms": query, "search_simple": 1, "json": 1, "page": page}
        try:
            response = requests.get("https://world.openfoodfacts.org/cgi/search.pl", params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Open Food Facts search_products error: %s", e)
            return {"status": "error", "message": str(e)}
