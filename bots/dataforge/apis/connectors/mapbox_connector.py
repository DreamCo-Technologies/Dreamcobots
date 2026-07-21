"""Mapbox geolocation API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class MapboxConnector:
    """MapboxConnector for DataForge AI."""

    BASE_URL = "https://api.mapbox.com"

    def __init__(self):
        """Initialize connector, reading access token from environment."""
        self.access_token = os.environ.get("MAPBOX_ACCESS_TOKEN", "")
        if not self.access_token:
            logger.warning("MAPBOX_ACCESS_TOKEN not set.")

    def geocoding_forward(self, search_text: str) -> dict:
        """Forward geocode a search text using Mapbox.

        Args:
            search_text: Address or place name to geocode.

        Returns:
            API response dict or error dict.
        """
        import requests
        import urllib.parse
        encoded = urllib.parse.quote(search_text)
        try:
            response = requests.get(
                f"{self.BASE_URL}/geocoding/v5/mapbox.places/{encoded}.json",
                params={"access_token": self.access_token}, timeout=30)
            response.raise_for_status()
            logger.info("Mapbox forward geocoding completed for: %s", search_text)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Mapbox geocoding_forward error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_static_map(self, lon: float, lat: float, zoom: int = 10) -> dict:
        """Get a static map image URL from Mapbox.

        Args:
            lon: Longitude coordinate.
            lat: Latitude coordinate.
            zoom: Map zoom level (default 10).

        Returns:
            Dict with static map URL or error.
        """
        url = f"{self.BASE_URL}/styles/v1/mapbox/streets-v11/static/{lon},{lat},{zoom}/600x400?access_token={self.access_token}"
        logger.info("Mapbox static map URL generated for lon=%s lat=%s.", lon, lat)
        return {"status": "success", "url": url, "lon": lon, "lat": lat, "zoom": zoom}
