"""OpenWeatherMap API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class OpenWeatherMapConnector:
    """OpenWeatherMapConnector for DataForge AI."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("OPENWEATHERMAP_API_KEY", "")
        if not self.api_key:
            logger.warning("OPENWEATHERMAP_API_KEY not set.")

    def get_current_weather(self, city: str) -> dict:
        """Get current weather for a city.

        Args:
            city: City name.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"q": city, "appid": self.api_key, "units": "metric"}
        try:
            response = requests.get(f"{self.BASE_URL}/weather", params=params, timeout=30)
            response.raise_for_status()
            logger.info("OpenWeatherMap current weather fetched for %s.", city)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("OpenWeatherMap get_current_weather error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_forecast(self, city: str) -> dict:
        """Get 5-day weather forecast for a city.

        Args:
            city: City name.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"q": city, "appid": self.api_key, "units": "metric"}
        try:
            response = requests.get(f"{self.BASE_URL}/forecast", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("OpenWeatherMap get_forecast error: %s", e)
            return {"status": "error", "message": str(e)}
