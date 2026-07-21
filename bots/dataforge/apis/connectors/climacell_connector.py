"""Climacell/Tomorrow.io weather connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class ClimacellConnector:
    """ClimacellConnector for DataForge AI."""

    BASE_URL = "https://data.tomorrow.io/v4"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("TOMORROW_IO_API_KEY", "")
        if not self.api_key:
            logger.warning("TOMORROW_IO_API_KEY not set.")

    def get_timeline(self, location: str, fields: list) -> dict:
        """Get weather timeline from Climacell/Tomorrow.io.

        Args:
            location: Location string (lat,lon or place name).
            fields: List of weather fields to retrieve.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"location": location, "fields": ",".join(fields), "apikey": self.api_key, "timesteps": "1h"}
        try:
            response = requests.get(f"{self.BASE_URL}/timelines", params=params, timeout=30)
            response.raise_for_status()
            logger.info("Climacell timeline fetched for %s.", location)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Climacell get_timeline error: %s", e)
            return {"status": "error", "message": str(e)}
