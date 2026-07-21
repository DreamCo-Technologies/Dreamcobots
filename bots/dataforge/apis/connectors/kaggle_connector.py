"""Kaggle datasets API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class KaggleConnector:
    """KaggleConnector for DataForge AI."""

    BASE_URL = "https://www.kaggle.com/api/v1"

    def __init__(self):
        """Initialize connector, reading credentials from environment."""
        self.username = os.environ.get("KAGGLE_USERNAME", "")
        self.key = os.environ.get("KAGGLE_KEY", "")
        if not self.username or not self.key:
            logger.warning("KAGGLE_USERNAME or KAGGLE_KEY not set.")

    def search_datasets(self, query: str) -> dict:
        """Search Kaggle datasets.

        Args:
            query: Search query string.

        Returns:
            API response dict with datasets or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/datasets/list?search={query}", auth=(self.username, self.key), timeout=30)
            response.raise_for_status()
            logger.info("Kaggle dataset search completed for query: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Kaggle search_datasets error: %s", e)
            return {"status": "error", "message": str(e)}

    def download_dataset(self, dataset_ref: str, path: str = ".") -> dict:
        """Download a Kaggle dataset.

        Args:
            dataset_ref: Dataset reference (owner/name).
            path: Local download path (default '.').

        Returns:
            Dict with status and download path.
        """
        try:
            import kaggle
            kaggle.api.dataset_download_files(dataset_ref, path=path, unzip=True)
            logger.info("Kaggle dataset downloaded: %s to %s", dataset_ref, path)
            return {"status": "success", "dataset": dataset_ref, "path": path}
        except Exception as e:
            logger.error("Kaggle download_dataset error: %s", e)
            return {"status": "error", "message": str(e)}
