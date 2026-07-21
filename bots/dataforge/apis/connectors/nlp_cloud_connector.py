"""NLP Cloud API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class NLPCloudConnector:
    """NLPCloudConnector for DataForge AI."""

    BASE_URL = "https://api.nlpcloud.io/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("NLP_CLOUD_API_KEY", "")
        if not self.api_key:
            logger.warning("NLP_CLOUD_API_KEY not set.")

    def sentiment_analysis(self, text: str, model: str = "distilbert-base-uncased-finetuned-sst-2-english") -> dict:
        """Analyze sentiment of text using NLP Cloud.

        Args:
            text: Input text to analyze.
            model: Model identifier (default distilbert-base-uncased-finetuned-sst-2-english).

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Token {self.api_key}", "Content-Type": "application/json"}
        try:
            response = requests.post(f"{self.BASE_URL}/{model}/sentiment", json={"text": text}, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("NLP Cloud sentiment analysis completed.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("NLP Cloud error: %s", e)
            return {"status": "error", "message": str(e)}
