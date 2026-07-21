"""Cohere NLP API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class CohereConnector:
    """CohereConnector: Cohere NLP API connector for DataForge AI."""

    BASE_URL = "https://api.cohere.ai/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("COHERE_API_KEY", "")
        if not self.api_key:
            logger.warning("COHERE_API_KEY not set.")

    def generate(self, prompt: str, model: str = "command") -> dict:
        """Generate text using Cohere API.

        Args:
            prompt: The input prompt string.
            model: Model identifier (default 'command').

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "prompt": prompt}
        try:
            response = requests.post(f"{self.BASE_URL}/generate", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Cohere text generated.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Cohere generate error: %s", e)
            return {"status": "error", "message": str(e)}

    def embed(self, texts: list) -> dict:
        """Embed texts using Cohere API.

        Args:
            texts: List of strings to embed.

        Returns:
            API response dict with embeddings or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            response = requests.post(f"{self.BASE_URL}/embed", json={"texts": texts}, headers=headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Cohere embed error: %s", e)
            return {"status": "error", "message": str(e)}
