"""Twitter/X API v2 connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class TwitterConnector:
    """TwitterConnector for DataForge AI."""

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self):
        """Initialize connector, reading Bearer token from environment."""
        self.bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "")
        if not self.bearer_token:
            logger.warning("TWITTER_BEARER_TOKEN not set.")

    def search_recent_tweets(self, query: str, max_results: int = 10) -> dict:
        """Search recent tweets using Twitter API v2.

        Args:
            query: Search query string.
            max_results: Max results to return (default 10, min 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        params = {"query": query, "max_results": max(10, max_results)}
        try:
            response = requests.get(f"{self.BASE_URL}/tweets/search/recent", params=params, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Twitter recent tweet search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Twitter search_recent_tweets error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_user_tweets(self, user_id: str, max_results: int = 10) -> dict:
        """Get recent tweets from a user.

        Args:
            user_id: Twitter user ID.
            max_results: Max results (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        try:
            response = requests.get(f"{self.BASE_URL}/users/{user_id}/tweets",
                params={"max_results": max(5, max_results)}, headers=headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Twitter get_user_tweets error: %s", e)
            return {"status": "error", "message": str(e)}
