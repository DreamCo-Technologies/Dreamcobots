"""Eden AI multi-provider connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class EdenAIConnector:
    """EdenAIConnector for DataForge AI."""

    BASE_URL = "https://api.edenai.run/v2"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("EDEN_AI_API_KEY", "")
        if not self.api_key:
            logger.warning("EDEN_AI_API_KEY not set.")

    def text_generation(self, providers: list, text: str) -> dict:
        """Generate text using Eden AI across multiple providers.

        Args:
            providers: List of provider names (e.g., ['openai', 'cohere']).
            text: Input text prompt.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"providers": ",".join(providers), "text": text}
        try:
            response = requests.post(f"{self.BASE_URL}/text/generation", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Eden AI text generation completed.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Eden AI error: %s", e)
            return {"status": "error", "message": str(e)}
