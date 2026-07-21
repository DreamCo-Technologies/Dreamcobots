"""Visual Crossing weather data connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class VisualCrossingConnector:
    """VisualCrossingConnector for DataForge AI."""

    BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("VISUAL_CROSSING_API_KEY", "")
        if not self.api_key:
            logger.warning("VISUAL_CROSSING_API_KEY not set.")

    def get_weather(self, location: str, date_from: str, date_to: str) -> dict:
        """Get historical or forecast weather data from Visual Crossing.

        Args:
            location: Location query (city, coordinates, etc).
            date_from: Start date (YYYY-MM-DD).
            date_to: End date (YYYY-MM-DD).

        Returns:
            API response dict or error dict.
        """
        import requests
        url = f"{self.BASE_URL}/timeline/{location}/{date_from}/{date_to}"
        params = {"unitGroup": "metric", "key": self.api_key, "contentType": "json"}
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            logger.info("Visual Crossing weather fetched for %s.", location)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Visual Crossing get_weather error: %s", e)
            return {"status": "error", "message": str(e)}
