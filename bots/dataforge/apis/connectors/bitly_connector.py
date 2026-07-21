"""Bitly URL shortener connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class BitlyConnector:
    """BitlyConnector for DataForge AI."""

    BASE_URL = "https://api-ssl.bitly.com/v4"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("BITLY_ACCESS_TOKEN", "")
        if not self.api_key:
            logger.warning("BITLY_ACCESS_TOKEN not set.")

    def shorten_url(self, long_url: str) -> dict:
        """Shorten a URL using Bitly.

        Args:
            long_url: The URL to shorten.

        Returns:
            API response dict with short URL or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            response = requests.post(f"{self.BASE_URL}/shorten", json={"long_url": long_url}, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Bitly URL shortened.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Bitly shorten_url error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_clicks(self, bitlink_id: str) -> dict:
        """Get click metrics for a Bitly link.

        Args:
            bitlink_id: The Bitly link identifier.

        Returns:
            API response dict with click data or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.get(f"{self.BASE_URL}/bitlinks/{bitlink_id}/clicks/summary", headers=headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Bitly get_clicks error: %s", e)
            return {"status": "error", "message": str(e)}
