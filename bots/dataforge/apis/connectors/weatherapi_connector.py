"""WeatherAPI.com connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class WeatherAPIConnector:
    """WeatherAPIConnector for DataForge AI."""

    BASE_URL = "https://api.weatherapi.com/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("WEATHERAPI_KEY", "")
        if not self.api_key:
            logger.warning("WEATHERAPI_KEY not set.")

    def get_current(self, location: str) -> dict:
        """Get current weather for a location.

        Args:
            location: Location query (city name, zip code, or coordinates).

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/current.json", params={"key": self.api_key, "q": location}, timeout=30)
            response.raise_for_status()
            logger.info("WeatherAPI current weather fetched for %s.", location)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("WeatherAPI get_current error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_forecast(self, location: str, days: int = 3) -> dict:
        """Get weather forecast for a location.

        Args:
            location: Location query.
            days: Number of forecast days (default 3).

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/forecast.json",
                params={"key": self.api_key, "q": location, "days": days}, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("WeatherAPI get_forecast error: %s", e)
            return {"status": "error", "message": str(e)}
