"""OpenStreetMap Nominatim geocoding connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class OpenStreetMapConnector:
    """OpenStreetMapConnector for DataForge AI."""

    BASE_URL = "https://nominatim.openstreetmap.org"

    def __init__(self):
        """Initialize connector with custom user agent."""
        self.headers = {"User-Agent": "DataForge-AI-Bot/1.0 (dataforge@example.com)"}

    def search_place(self, query: str) -> dict:
        """Search for a place using OpenStreetMap Nominatim.

        Args:
            query: Place name or address to search.

        Returns:
            API response dict with place results or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/search", params={"q": query, "format": "json"}, headers=self.headers, timeout=30)
            response.raise_for_status()
            logger.info("OpenStreetMap place search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("OpenStreetMap search_place error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_nominatim(self, lat: float, lon: float) -> dict:
        """Reverse geocode coordinates using Nominatim.

        Args:
            lat: Latitude coordinate.
            lon: Longitude coordinate.

        Returns:
            API response dict with location data or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/reverse", params={"lat": lat, "lon": lon, "format": "json"}, headers=self.headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("OpenStreetMap get_nominatim error: %s", e)
            return {"status": "error", "message": str(e)}
