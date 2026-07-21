"""JSONL dataset packager for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import json
import logging
import os

logger = logging.getLogger(__name__)


class JSONLPackager:
    """Packages datasets into JSONL (JSON Lines) format."""

    def pack(self, data: list, output_path: str) -> str:
        """Write data list to a JSONL file (one JSON object per line).

        Args:
            data: List of records to serialize.
            output_path: File path for the output JSONL file.

        Returns:
            The output_path string.
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for record in data:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        logger.info("JSONL packed %d records to %s", len(data), output_path)
        return output_path

    def validate(self, data) -> bool:
        """Validate that data is a non-empty list.

        Args:
            data: Data to validate.

        Returns:
            True if valid, False otherwise.
        """
        if not isinstance(data, list) or not data:
            logger.warning("JSONL validation failed: empty or non-list data.")
            return False
        return True
