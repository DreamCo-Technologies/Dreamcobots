"""Google Gemini API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class GoogleGeminiConnector:
    """GoogleGeminiConnector: Google Gemini API connector for DataForge AI."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("GOOGLE_GEMINI_API_KEY", "")
        if not self.api_key:
            logger.warning("GOOGLE_GEMINI_API_KEY not set.")

    def generate_content(self, prompt: str, model: str = "gemini-pro") -> dict:
        """Generate content using Google Gemini API.

        Args:
            prompt: The input prompt string.
            model: Model identifier (default 'gemini-pro').

        Returns:
            API response dict or error dict.
        """
        import requests
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            url = f"{self.BASE_URL}/models/{model}:generateContent?key={self.api_key}"
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            logger.info("Google Gemini content generated with model %s.", model)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Google Gemini error: %s", e)
            return {"status": "error", "message": str(e)}
