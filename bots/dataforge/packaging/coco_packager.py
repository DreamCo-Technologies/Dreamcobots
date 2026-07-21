"""COCO format dataset packager for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class COCOPackager:
    """Packages datasets into COCO (Common Objects in Context) annotation format."""

    def pack(self, annotations: list, output_path: str) -> str:
        """Write annotations in COCO JSON format.

        Args:
            annotations: List of annotation dicts.
            output_path: File path for the output COCO JSON file.

        Returns:
            The output_path string.
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        coco_data = {
            "info": {
                "description": "DataForge AI Synthetic Dataset",
                "version": "1.0",
                "year": datetime.utcnow().year,
                "date_created": datetime.utcnow().isoformat(),
            },
            "licenses": [{"id": 1, "name": "CC-BY-4.0"}],
            "images": [],
            "annotations": annotations,
            "categories": [],
        }
        for i, ann in enumerate(annotations):
            coco_data["images"].append({
                "id": i,
                "file_name": f"image_{i:05d}.png",
                "width": 224,
                "height": 224,
            })
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(coco_data, f, indent=2)
        logger.info("COCO packed %d annotations to %s", len(annotations), output_path)
        return output_path

    def validate(self, annotations) -> bool:
        """Validate COCO annotation structure.

        Args:
            annotations: List of annotation dicts to validate.

        Returns:
            True if annotations is a list, False otherwise.
        """
        if not isinstance(annotations, list):
            logger.warning("COCO validation failed: annotations must be a list.")
            return False
        return True
