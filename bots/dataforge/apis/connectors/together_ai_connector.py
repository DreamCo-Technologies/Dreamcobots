"""Together AI API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class TogetherAIConnector:
    """TogetherAIConnector for DataForge AI."""

    BASE_URL = "https://api.together.xyz/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("TOGETHER_AI_API_KEY", "")
        if not self.api_key:
            logger.warning("TOGETHER_AI_API_KEY not set.")

    def complete(self, prompt: str, model: str = "togethercomputer/llama-2-7b") -> dict:
        """Complete text using Together AI API.

        Args:
            prompt: The input prompt string.
            model: Model identifier (default llama-2-7b).

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "prompt": prompt}
        try:
            response = requests.post(f"{self.BASE_URL}/completions", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Together AI completion done with model %s.", model)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Together AI error: %s", e)
            return {"status": "error", "message": str(e)}
