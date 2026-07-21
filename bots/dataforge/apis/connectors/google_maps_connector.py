"""Google Maps API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class GoogleMapsConnector:
    """GoogleMapsConnector for DataForge AI."""

    BASE_URL = "https://maps.googleapis.com/maps/api"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
        if not self.api_key:
            logger.warning("GOOGLE_MAPS_API_KEY not set.")

    def geocode(self, address: str) -> dict:
        """Geocode an address using Google Maps.

        Args:
            address: Address string to geocode.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"address": address, "key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/geocode/json", params=params, timeout=30)
            response.raise_for_status()
            logger.info("Google Maps geocoded: %s", address)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Google Maps geocode error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_directions(self, origin: str, destination: str, mode: str = "driving") -> dict:
        """Get directions from Google Maps.

        Args:
            origin: Starting location.
            destination: Ending location.
            mode: Travel mode (default 'driving').

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"origin": origin, "destination": destination, "mode": mode, "key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/directions/json", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Google Maps get_directions error: %s", e)
            return {"status": "error", "message": str(e)}
