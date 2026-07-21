"""MonkeyLearn text analysis connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class MonkeyLearnConnector:
    """MonkeyLearnConnector for DataForge AI."""

    BASE_URL = "https://api.monkeylearn.com/v3"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("MONKEYLEARN_API_KEY", "")
        if not self.api_key:
            logger.warning("MONKEYLEARN_API_KEY not set.")

    def classify(self, module_id: str, texts: list) -> dict:
        """Classify texts using a MonkeyLearn classifier.

        Args:
            module_id: The classifier module identifier.
            texts: List of text strings to classify.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Token {self.api_key}", "Content-Type": "application/json"}
        payload = {"data": texts}
        try:
            response = requests.post(f"{self.BASE_URL}/classifiers/{module_id}/classify/", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("MonkeyLearn classification completed for module %s.", module_id)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("MonkeyLearn classify error: %s", e)
            return {"status": "error", "message": str(e)}
