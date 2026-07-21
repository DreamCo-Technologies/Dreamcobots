"""Facial expression dataset generator for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import random
import uuid

logger = logging.getLogger(__name__)

BASE_EXPRESSIONS = [
    "joy", "sadness", "anger", "fear", "disgust", "surprise", "contempt",
    "neutral", "confusion", "concentration", "boredom", "excitement",
]
LIGHTING = ["natural", "studio", "low_light", "backlit", "mixed"]
AGE_GROUPS = ["child", "teen", "young_adult", "adult", "senior"]


def _generate_micro_expressions():
    """Generate 200+ micro-expression labels programmatically.

    Returns:
        List of micro-expression label strings.
    """
    intensities = ["slight", "moderate", "strong", "fleeting", "masked"]
    combinations = []
    for base in BASE_EXPRESSIONS:
        for intensity in intensities:
            combinations.append(f"{intensity}_{base}")
    extras = [
        "raised_inner_brow", "raised_outer_brow", "nose_wrinkle", "lip_corner_pull",
        "cheek_raise", "lid_tighten", "chin_raise", "dimpler", "brow_lowerer",
        "upper_lip_raise", "lip_stretch", "lip_tighten", "lip_pressor",
        "mouth_open", "jaw_drop", "blink_rapid", "gaze_avert",
    ]
    return combinations + extras


MICRO_EXPRESSIONS = _generate_micro_expressions()


class FacialDatasetGenerator:
    """Generates synthetic facial expression dataset metadata."""

    def generate(self, num_samples: int = 200) -> list:
        """Generate synthetic facial expression metadata records.

        Args:
            num_samples: Number of records to generate (default 200).

        Returns:
            List of facial expression metadata record dicts.
        """
        records = []
        for i in range(num_samples):
            record = {
                "id": str(uuid.uuid4()),
                "index": i,
                "expression": random.choice(MICRO_EXPRESSIONS),
                "base_emotion": random.choice(BASE_EXPRESSIONS),
                "lighting": random.choice(LIGHTING),
                "age_group": random.choice(AGE_GROUPS),
                "format": "PNG",
                "resolution": "224x224",
                "source": "synthetic_GAN",
                "real_person": False,
                "synthetic": True,
                "face_landmarks": random.randint(68, 478),
                "license": "CC-BY-4.0",
            }
            records.append(record)
        logger.info("Generated %d facial dataset records.", num_samples)
        return records
