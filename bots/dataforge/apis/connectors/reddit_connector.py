"""Reddit public JSON API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class RedditConnector:
    """RedditConnector for DataForge AI."""

    BASE_URL = "https://www.reddit.com"

    def __init__(self):
        """Initialize connector with user agent."""
        self.headers = {"User-Agent": "DataForge-AI-Bot/1.0 (dataforge@example.com)"}
        self.client_id = os.environ.get("REDDIT_CLIENT_ID", "")
        self.client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")

    def search_posts(self, query: str, subreddit: str = "all", limit: int = 25) -> dict:
        """Search posts on Reddit.

        Args:
            query: Search query string.
            subreddit: Subreddit to search (default 'all').
            limit: Max results (default 25).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"q": query, "limit": limit, "sort": "relevance"}
        try:
            response = requests.get(f"{self.BASE_URL}/r/{subreddit}/search.json", params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            logger.info("Reddit search completed for: %s in r/%s", query, subreddit)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Reddit search_posts error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_comments(self, post_id: str) -> dict:
        """Get comments for a Reddit post.

        Args:
            post_id: The Reddit post identifier.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/comments/{post_id}.json", headers=self.headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Reddit get_comments error: %s", e)
            return {"status": "error", "message": str(e)}
