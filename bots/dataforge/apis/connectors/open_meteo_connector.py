"""Open-Meteo free weather API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class OpenMeteoConnector:
    """OpenMeteoConnector for DataForge AI."""

    BASE_URL = "https://api.open-meteo.com/v1"

    def __init__(self):
        """Initialize connector (no API key required)."""
        logger.info("OpenMeteoConnector initialized.")

    def get_forecast(self, latitude: float, longitude: float, hourly: str = "temperature_2m") -> dict:
        """Get weather forecast from Open-Meteo.

        Args:
            latitude: Latitude coordinate.
            longitude: Longitude coordinate.
            hourly: Hourly variable to fetch (default 'temperature_2m').

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"latitude": latitude, "longitude": longitude, "hourly": hourly}
        try:
            response = requests.get(f"{self.BASE_URL}/forecast", params=params, timeout=30)
            response.raise_for_status()
            logger.info("Open-Meteo forecast fetched for lat=%s lon=%s.", latitude, longitude)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Open-Meteo get_forecast error: %s", e)
            return {"status": "error", "message": str(e)}
