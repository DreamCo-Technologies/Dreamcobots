"""OpenAI GPT API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class OpenAIConnector:
    """OpenAIConnector: OpenAI GPT API connector for DataForge AI."""

    BASE_URL = "https://api.openai.com/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set.")

    def generate_text(self, prompt: str, model: str = "gpt-4o") -> dict:
        """Generate text using OpenAI API.

        Args:
            prompt: The input prompt string.
            model: Model identifier (default 'gpt-4o').

        Returns:
            API response dict or error dict.
        """
        import requests
        if not self.api_key:
            return {"status": "error", "message": "No OpenAI API key provided."}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        try:
            response = requests.post(f"{self.BASE_URL}/chat/completions", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("OpenAI text generated for model %s.", model)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("OpenAI error: %s", e)
            return {"status": "error", "message": str(e)}
