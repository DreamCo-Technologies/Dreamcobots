"""JSON dataset packager for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import json
import logging
import os

logger = logging.getLogger(__name__)


class JSONPackager:
    """Packages datasets into JSON format."""

    def pack(self, data: list, output_path: str) -> str:
        """Write data list to a JSON file.

        Args:
            data: List of records to serialize.
            output_path: File path for the output JSON file.

        Returns:
            The output_path string.
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("JSON packed %d records to %s", len(data), output_path)
        return output_path

    def validate(self, data) -> bool:
        """Validate that data is a non-empty list of dicts.

        Args:
            data: Data to validate.

        Returns:
            True if valid, False otherwise.
        """
        if not isinstance(data, list) or not data:
            logger.warning("JSON validation failed: data must be a non-empty list.")
            return False
        if not all(isinstance(r, dict) for r in data):
            logger.warning("JSON validation failed: all records must be dicts.")
            return False
        return True
