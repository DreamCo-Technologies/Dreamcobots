"""CSV dataset packager for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import csv
import logging
import os

logger = logging.getLogger(__name__)


class CSVPackager:
    """Packages datasets into CSV format."""

    def pack(self, data: list, output_path: str, fieldnames: list = None) -> str:
        """Write data list to a CSV file.

        Args:
            data: List of record dicts to write.
            output_path: File path for the output CSV file.
            fieldnames: Optional list of field names; defaults to keys of first record.

        Returns:
            The output_path string.
        """
        if not data:
            logger.warning("CSV pack called with empty data.")
            return output_path
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fieldnames = fieldnames or list(data[0].keys())
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(data)
        logger.info("CSV packed %d records to %s", len(data), output_path)
        return output_path

    def validate(self, data) -> bool:
        """Validate that data is a non-empty list of dicts.

        Args:
            data: Data to validate.

        Returns:
            True if valid, False otherwise.
        """
        if not isinstance(data, list) or not data:
            logger.warning("CSV validation failed: empty or non-list data.")
            return False
        return True
