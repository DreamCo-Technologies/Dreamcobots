"""Google Dialogflow connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class DialogflowConnector:
    """DialogflowConnector for DataForge AI."""

    BASE_URL = "https://dialogflow.googleapis.com/v2"

    def __init__(self):
        """Initialize connector, reading project ID and credentials from environment."""
        self.project_id = os.environ.get("DIALOGFLOW_PROJECT_ID", "")
        self.api_key = os.environ.get("DIALOGFLOW_API_KEY", "")
        if not self.project_id:
            logger.warning("DIALOGFLOW_PROJECT_ID not set.")

    def detect_intent(self, session_id: str, text: str, language_code: str = "en") -> dict:
        """Detect intent from user text using Dialogflow.

        Args:
            session_id: Unique session identifier.
            text: User text input.
            language_code: Language code (default 'en').

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "queryInput": {"text": {"text": text, "languageCode": language_code}}
        }
        url = f"{self.BASE_URL}/projects/{self.project_id}/agent/sessions/{session_id}:detectIntent"
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Dialogflow intent detected for session %s.", session_id)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Dialogflow error: %s", e)
            return {"status": "error", "message": str(e)}
