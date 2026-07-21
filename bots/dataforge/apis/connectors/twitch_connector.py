"""Twitch Helix API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class TwitchConnector:
    """TwitchConnector for DataForge AI."""

    BASE_URL = "https://api.twitch.tv/helix"

    def __init__(self):
        """Initialize connector, reading credentials from environment."""
        self.client_id = os.environ.get("TWITCH_CLIENT_ID", "")
        self.access_token = os.environ.get("TWITCH_ACCESS_TOKEN", "")
        if not self.client_id or not self.access_token:
            logger.warning("TWITCH_CLIENT_ID or TWITCH_ACCESS_TOKEN not set.")

    def get_streams(self, game_id: str = None, first: int = 20) -> dict:
        """Get live streams from Twitch.

        Args:
            game_id: Optional game ID to filter streams.
            first: Number of streams to return (default 20).

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Client-ID": self.client_id, "Authorization": f"Bearer {self.access_token}"}
        params = {"first": first}
        if game_id:
            params["game_id"] = game_id
        try:
            response = requests.get(f"{self.BASE_URL}/streams", params=params, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Twitch streams fetched.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Twitch get_streams error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_users(self, logins: list) -> dict:
        """Get Twitch user information.

        Args:
            logins: List of login usernames to look up.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Client-ID": self.client_id, "Authorization": f"Bearer {self.access_token}"}
        params = [("login", login) for login in logins]
        try:
            response = requests.get(f"{self.BASE_URL}/users", params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Twitch get_users error: %s", e)
            return {"status": "error", "message": str(e)}
