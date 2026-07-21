"""WAV dataset metadata packager for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import json
import logging
import os

logger = logging.getLogger(__name__)


class WAVPackager:
    """Packages WAV dataset metadata manifests."""

    def pack(self, metadata: list, output_dir: str) -> str:
        """Create a WAV dataset metadata manifest file.

        Args:
            metadata: List of WAV record metadata dicts.
            output_dir: Directory to write the manifest file to.

        Returns:
            Path to the written manifest JSON file.
        """
        os.makedirs(output_dir, exist_ok=True)
        manifest_path = os.path.join(output_dir, "wav_manifest.json")
        manifest = {
            "format": "WAV",
            "record_count": len(metadata),
            "records": metadata,
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        logger.info("WAV manifest written to %s (%d records)", manifest_path, len(metadata))
        return manifest_path

    def validate(self, metadata) -> bool:
        """Validate WAV metadata list.

        Args:
            metadata: List of metadata dicts to validate.

        Returns:
            True if all records are WAV format, False otherwise.
        """
        if not isinstance(metadata, list) or not metadata:
            logger.warning("WAV validation failed: empty or non-list metadata.")
            return False
        for record in metadata:
            if "format" not in record or record.get("format") != "WAV":
                logger.warning("WAV validation: record missing WAV format field.")
                return False
        return True
