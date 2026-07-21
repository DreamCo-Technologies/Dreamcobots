"""YouTube Data API v3 connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class YouTubeConnector:
    """YouTubeConnector for DataForge AI."""

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("YOUTUBE_API_KEY", "")
        if not self.api_key:
            logger.warning("YOUTUBE_API_KEY not set.")

    def search_videos(self, query: str, max_results: int = 10) -> dict:
        """Search YouTube videos.

        Args:
            query: Search query string.
            max_results: Max results to return (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"part": "snippet", "q": query, "maxResults": max_results, "type": "video", "key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/search", params=params, timeout=30)
            response.raise_for_status()
            logger.info("YouTube video search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("YouTube search_videos error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_video_details(self, video_id: str) -> dict:
        """Get details for a YouTube video.

        Args:
            video_id: YouTube video identifier.

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"part": "snippet,statistics,contentDetails", "id": video_id, "key": self.api_key}
        try:
            response = requests.get(f"{self.BASE_URL}/videos", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("YouTube get_video_details error: %s", e)
            return {"status": "error", "message": str(e)}
