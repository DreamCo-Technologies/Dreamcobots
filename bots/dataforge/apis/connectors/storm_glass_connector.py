"""Storm Glass marine weather connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class StormGlassConnector:
    """StormGlassConnector for DataForge AI."""

    BASE_URL = "https://api.stormglass.io/v2"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("STORM_GLASS_API_KEY", "")
        if not self.api_key:
            logger.warning("STORM_GLASS_API_KEY not set.")

    def get_weather(self, lat: float, lng: float, params: str = "airTemperature,waveHeight") -> dict:
        """Get weather and marine data from Storm Glass.

        Args:
            lat: Latitude coordinate.
            lng: Longitude coordinate.
            params: Comma-separated weather parameters.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": self.api_key}
        request_params = {"lat": lat, "lng": lng, "params": params}
        try:
            response = requests.get(f"{self.BASE_URL}/weather/point", params=request_params, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Storm Glass weather fetched for lat=%s lng=%s.", lat, lng)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Storm Glass get_weather error: %s", e)
            return {"status": "error", "message": str(e)}
