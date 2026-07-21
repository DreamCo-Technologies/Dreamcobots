"""AirVisual air quality data connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class AirVisualConnector:
    """AirVisualConnector for DataForge AI."""

    BASE_URL = "https://api.airvisual.com/v2"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("AIRVISUAL_API_KEY", "")
        if not self.api_key:
            logger.warning("AIRVISUAL_API_KEY not set.")

    def get_city_data(self, city: str, state: str, country: str) -> dict:
        """Get air quality data for a city.

        Args:
            city: City name.
            state: State/province name.
            country: Country name.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"city": city, "state": state, "country": country, "key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/city", params=params, timeout=30)
            response.raise_for_status()
            logger.info("AirVisual city data fetched for %s.", city)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("AirVisual get_city_data error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_nearest_city(self) -> dict:
        """Get air quality data for the nearest city based on IP.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/nearest_city", params={"key": self.api_key}, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("AirVisual get_nearest_city error: %s", e)
            return {"status": "error", "message": str(e)}
