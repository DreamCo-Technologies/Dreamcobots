"""DeepAI API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class DeepAIConnector:
    """DeepAIConnector for DataForge AI."""

    BASE_URL = "https://api.deepai.org/api"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("DEEPAI_API_KEY", "")
        if not self.api_key:
            logger.warning("DEEPAI_API_KEY not set.")

    def text_generation(self, text: str) -> dict:
        """Generate text using DeepAI API.

        Args:
            text: Input text prompt.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.post(f"{self.BASE_URL}/text-generator", data={"text": text}, headers={"api-key": self.api_key}, timeout=30)
            response.raise_for_status()
            logger.info("DeepAI text generation completed.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("DeepAI text_generation error: %s", e)
            return {"status": "error", "message": str(e)}

    def summarize(self, text: str) -> dict:
        """Summarize text using DeepAI API.

        Args:
            text: Text to summarize.

        Returns:
            API response dict with summary or error dict.
        """
        import requests
        try:
            response = requests.post(f"{self.BASE_URL}/summarization", data={"text": text}, headers={"api-key": self.api_key}, timeout=30)
            response.raise_for_status()
            logger.info("DeepAI summarization completed.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("DeepAI summarize error: %s", e)
            return {"status": "error", "message": str(e)}
