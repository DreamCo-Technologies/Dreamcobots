"""Etsy Open API v3 connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class EtsyConnector:
    """EtsyConnector for DataForge AI."""

    BASE_URL = "https://openapi.etsy.com/v3"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("ETSY_API_KEY", "")
        if not self.api_key:
            logger.warning("ETSY_API_KEY not set.")

    def find_all_listings_active(self, keywords: str, limit: int = 25) -> dict:
        """Search active Etsy listings.

        Args:
            keywords: Search keywords.
            limit: Max results (default 25).

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"x-api-key": self.api_key}
        params = {"keywords": keywords, "limit": limit}
        try:
            response = requests.get(f"{self.BASE_URL}/application/listings/active", params=params, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Etsy listings search completed for: %s", keywords)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Etsy find_all_listings_active error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_listing(self, listing_id: int) -> dict:
        """Get a specific Etsy listing.

        Args:
            listing_id: The Etsy listing identifier.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"x-api-key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/application/listings/{listing_id}", headers=headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Etsy get_listing error: %s", e)
            return {"status": "error", "message": str(e)}
