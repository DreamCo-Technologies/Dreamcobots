"""HuggingFace Datasets API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class HuggingFaceDatasetsConnector:
    """HuggingFaceDatasetsConnector for DataForge AI."""

    BASE_URL = "https://datasets-server.huggingface.co"

    def __init__(self):
        """Initialize connector with optional token from environment."""
        self.token = os.environ.get("HUGGINGFACE_TOKEN", "")

    def load_dataset_info(self, dataset_id: str) -> dict:
        """Load info about a HuggingFace dataset.

        Args:
            dataset_id: The dataset identifier on HuggingFace Hub.

        Returns:
            API response dict with dataset info or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/info?dataset={dataset_id}", timeout=30)
            response.raise_for_status()
            logger.info("HuggingFace dataset info loaded for %s.", dataset_id)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("HuggingFace load_dataset_info error: %s", e)
            return {"status": "error", "message": str(e)}

    def search_datasets(self, query: str) -> dict:
        """Search HuggingFace datasets.

        Args:
            query: Search query string.

        Returns:
            API response dict with search results or error dict.
        """
        import requests
        try:
            response = requests.get(f"https://huggingface.co/api/datasets?search={query}", timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("HuggingFace search_datasets error: %s", e)
            return {"status": "error", "message": str(e)}
