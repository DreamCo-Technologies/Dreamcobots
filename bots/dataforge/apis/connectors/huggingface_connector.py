"""HuggingFace Inference API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class HuggingFaceConnector:
    """HuggingFaceConnector: HuggingFace Inference API connector for DataForge AI."""

    BASE_URL = "https://api-inference.huggingface.co"

    def __init__(self):
        """Initialize connector, reading API key from environment."""
        self.api_key = os.environ.get("HUGGINGFACE_TOKEN", "")
        if not self.api_key:
            logger.warning("HUGGINGFACE_TOKEN not set.")

    def run_inference(self, model_id: str, inputs) -> dict:
        """Run inference on a HuggingFace model.

        Args:
            model_id: The model identifier on HuggingFace Hub.
            inputs: Input data for the model.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.post(f"{self.BASE_URL}/models/{model_id}", json={"inputs": inputs}, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("HuggingFace inference run for model %s.", model_id)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("HuggingFace inference error: %s", e)
            return {"status": "error", "message": str(e)}

    def list_models(self, task: str) -> dict:
        """List HuggingFace models for a given task.

        Args:
            task: The task type (e.g., 'text-classification').

        Returns:
            API response dict with list of models.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/models?filter={task}", timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("HuggingFace list_models error: %s", e)
            return {"status": "error", "message": str(e)}
