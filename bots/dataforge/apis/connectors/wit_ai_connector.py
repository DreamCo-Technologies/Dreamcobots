"""Wit.ai NLU connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class WitAIConnector:
    """WitAIConnector for DataForge AI."""

    BASE_URL = "https://api.wit.ai"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("WIT_AI_TOKEN", "")
        if not self.api_key:
            logger.warning("WIT_AI_TOKEN not set.")

    def understand(self, query: str) -> dict:
        """Understand a natural language query using Wit.ai.

        Args:
            query: The natural language query to understand.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.get(f"{self.BASE_URL}/message", params={"q": query}, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Wit.ai understood query.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Wit.ai understand error: %s", e)
            return {"status": "error", "message": str(e)}
