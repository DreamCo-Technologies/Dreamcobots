"""Kaggle dataset publisher for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import json
import logging
import os
import tempfile

logger = logging.getLogger(__name__)


class KagglePublisher:
    """Publishes datasets to Kaggle."""

    def __init__(self):
        """Initialize publisher, reading Kaggle credentials from environment."""
        self.username = os.environ.get("KAGGLE_USERNAME", "")
        self.key = os.environ.get("KAGGLE_KEY", "")
        if not self.username or not self.key:
            logger.warning("KAGGLE_USERNAME or KAGGLE_KEY not set.")

    def publish_dataset(self, title: str, data: list, description: str = "") -> dict:
        """Publish a dataset to Kaggle.

        Args:
            title: Title of the dataset.
            data: List of records to publish.
            description: Optional dataset description.

        Returns:
            Result dict with status and message.
        """
        if not self.username or not self.key:
            return {"status": "error", "message": "Kaggle credentials not configured."}
        try:
            import kaggle
            with tempfile.TemporaryDirectory() as tmpdir:
                data_path = os.path.join(tmpdir, "data.json")
                with open(data_path, "w") as f:
                    json.dump(data, f)
                meta = {
                    "title": title,
                    "id": f"{self.username}/{title.lower().replace(' ', '-')}",
                    "licenses": [{"name": "CC0-1.0"}],
                    "description": description,
                }
                meta_path = os.path.join(tmpdir, "dataset-metadata.json")
                with open(meta_path, "w") as f:
                    json.dump(meta, f)
                kaggle.api.dataset_create_new(tmpdir, public=True)
            logger.info("Dataset '%s' published to Kaggle.", title)
            return {"status": "success", "title": title, "records": len(data)}
        except Exception as e:
            logger.error("Kaggle publish error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_dataset_info(self, dataset_id: str) -> dict:
        """Get info about a Kaggle dataset.

        Args:
            dataset_id: The dataset identifier to look up.

        Returns:
            Result dict with status and dataset info.
        """
        try:
            import kaggle
            info = kaggle.api.dataset_list(search=dataset_id)
            return {"status": "success", "info": str(info)}
        except Exception as e:
            logger.error("Kaggle get_dataset_info error: %s", e)
            return {"status": "error", "message": str(e)}
