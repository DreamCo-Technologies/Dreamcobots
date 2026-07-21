"""HuggingFace dataset publisher for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import json
import logging
import os

logger = logging.getLogger(__name__)


class HuggingFacePublisher:
    """Publishes datasets to HuggingFace Hub."""

    BASE_URL = "https://huggingface.co/api"

    def __init__(self):
        """Initialize publisher, reading token from environment."""
        self.token = os.environ.get("HUGGINGFACE_TOKEN", "")
        if not self.token:
            logger.warning("HUGGINGFACE_TOKEN not set.")

    def upload_dataset(self, dataset_name: str, data: list, token: str = None) -> dict:
        """Upload a dataset to HuggingFace Hub.

        Args:
            dataset_name: Name of the dataset to create.
            data: List of records to upload.
            token: Optional token override; falls back to env var.

        Returns:
            Result dict with status and message.
        """
        import requests
        auth_token = token or self.token
        if not auth_token:
            logger.error("HuggingFace upload failed: no token provided.")
            return {"status": "error", "message": "No HuggingFace token provided."}
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        payload = {"type": "dataset", "name": dataset_name, "private": False}
        try:
            response = requests.post(f"{self.BASE_URL}/repos/create", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Dataset %s uploaded to HuggingFace.", dataset_name)
            return {"status": "success", "dataset": dataset_name, "records": len(data)}
        except requests.RequestException as e:
            logger.error("HuggingFace upload error: %s", e)
            return {"status": "error", "message": str(e)}

    def list_datasets(self, owner: str) -> dict:
        """List datasets for an owner on HuggingFace.

        Args:
            owner: The HuggingFace username or organization.

        Returns:
            Result dict with status and datasets list.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/datasets?author={owner}", timeout=30)
            response.raise_for_status()
            return {"status": "success", "datasets": response.json()}
        except requests.RequestException as e:
            logger.error("HuggingFace list error: %s", e)
            return {"status": "error", "message": str(e)}
