"""Spotify Web API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class SpotifyConnector:
    """SpotifyConnector for DataForge AI."""

    BASE_URL = "https://api.spotify.com/v1"
    AUTH_URL = "https://accounts.spotify.com/api/token"

    def __init__(self):
        """Initialize connector, reading credentials from environment."""
        self.client_id = os.environ.get("SPOTIFY_CLIENT_ID", "")
        self.client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
        if not self.client_id or not self.client_secret:
            logger.warning("SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET not set.")

    def get_access_token(self) -> dict:
        """Get a Spotify OAuth access token using client credentials flow.

        Returns:
            Dict with access_token or error.
        """
        import requests
        import base64
        credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = requests.post(self.AUTH_URL, data={"grant_type": "client_credentials"}, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Spotify access token obtained.")
            return {"status": "success", "access_token": response.json().get("access_token")}
        except requests.RequestException as e:
            logger.error("Spotify get_access_token error: %s", e)
            return {"status": "error", "message": str(e)}

    def search(self, query: str, type: str = "track", limit: int = 10) -> dict:
        """Search Spotify catalog.

        Args:
            query: Search query string.
            type: Item type to search (default 'track').
            limit: Max results (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        token_result = self.get_access_token()
        if token_result.get("status") != "success":
            return token_result
        headers = {"Authorization": f"Bearer {token_result['access_token']}"}
        params = {"q": query, "type": type, "limit": limit}
        try:
            response = requests.get(f"{self.BASE_URL}/search", params=params, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Spotify search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Spotify search error: %s", e)
            return {"status": "error", "message": str(e)}
