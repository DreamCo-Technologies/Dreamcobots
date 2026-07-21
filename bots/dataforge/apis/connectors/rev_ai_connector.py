"""Rev.ai speech transcription connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class RevAIConnector:
    """RevAIConnector for DataForge AI."""

    BASE_URL = "https://api.rev.ai/speechtotext/v1"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("REVAI_ACCESS_TOKEN", "")
        if not self.api_key:
            logger.warning("REVAI_ACCESS_TOKEN not set.")

    def submit_job(self, media_url: str) -> dict:
        """Submit a transcription job to Rev.ai.

        Args:
            media_url: URL of the media file to transcribe.

        Returns:
            API response dict with job ID or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            response = requests.post(f"{self.BASE_URL}/jobs", json={"media_url": media_url}, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Rev.ai transcription job submitted.")
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Rev.ai submit_job error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_transcript(self, job_id: str) -> dict:
        """Get transcript result from Rev.ai.

        Args:
            job_id: The Rev.ai job identifier.

        Returns:
            API response dict with transcript or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.get(f"{self.BASE_URL}/jobs/{job_id}/transcript", headers=headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Rev.ai get_transcript error: %s", e)
            return {"status": "error", "message": str(e)}
