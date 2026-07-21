"""Barcode Lookup API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class BarcodeLookupConnector:
    """BarcodeLookupConnector for DataForge AI."""

    BASE_URL = "https://api.barcodelookup.com/v3"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("BARCODE_LOOKUP_API_KEY", "")
        if not self.api_key:
            logger.warning("BARCODE_LOOKUP_API_KEY not set.")

    def lookup(self, barcode: str) -> dict:
        """Look up a product by barcode.

        Args:
            barcode: Product barcode string.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"barcode": barcode, "formatted": "y", "key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/products", params=params, timeout=30)
            response.raise_for_status()
            logger.info("Barcode lookup completed for: %s", barcode)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Barcode Lookup error: %s", e)
            return {"status": "error", "message": str(e)}
