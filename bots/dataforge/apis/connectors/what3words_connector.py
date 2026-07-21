"""What3Words location API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class What3WordsConnector:
    """What3WordsConnector for DataForge AI."""

    BASE_URL = "https://api.what3words.com/v3"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("WHAT3WORDS_API_KEY", "")
        if not self.api_key:
            logger.warning("WHAT3WORDS_API_KEY not set.")

    def convert_to_coordinates(self, words: str) -> dict:
        """Convert a what3words address to coordinates.

        Args:
            words: Three-word address (e.g., 'filled.count.soap').

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"words": words, "key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/convert-to-coordinates", params=params, timeout=30)
            response.raise_for_status()
            logger.info("What3Words converted words to coordinates: %s", words)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("What3Words convert_to_coordinates error: %s", e)
            return {"status": "error", "message": str(e)}

    def convert_to_3wa(self, lat: float, lng: float) -> dict:
        """Convert coordinates to a what3words address.

        Args:
            lat: Latitude coordinate.
            lng: Longitude coordinate.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"coordinates": f"{lat},{lng}", "key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/convert-to-3wa", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("What3Words convert_to_3wa error: %s", e)
            return {"status": "error", "message": str(e)}
