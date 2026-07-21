"""OpenCage geocoding API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class OpenCageConnector:
    """OpenCageConnector for DataForge AI."""

    BASE_URL = "https://api.opencagedata.com/geocode/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("OPENCAGE_API_KEY", "")
        if not self.api_key:
            logger.warning("OPENCAGE_API_KEY not set.")

    def geocode(self, query: str) -> dict:
        """Geocode a place name or address.

        Args:
            query: Place name or address to geocode.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"q": query, "key": self.api_key, "no_annotations": 1}
        try:
            response = requests.get(f"{self.BASE_URL}/json", params=params, timeout=30)
            response.raise_for_status()
            logger.info("OpenCage geocoded: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("OpenCage geocode error: %s", e)
            return {"status": "error", "message": str(e)}

    def reverse_geocode(self, lat: float, lng: float) -> dict:
        """Reverse geocode coordinates.

        Args:
            lat: Latitude coordinate.
            lng: Longitude coordinate.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"q": f"{lat}+{lng}", "key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/json", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("OpenCage reverse_geocode error: %s", e)
            return {"status": "error", "message": str(e)}
