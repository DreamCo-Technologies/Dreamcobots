"""Voice dataset generator for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import random
import uuid

logger = logging.getLogger(__name__)

EMOTIONS = ["angry", "happy", "sad", "fearful", "disgusted", "surprised", "neutral"]
ACCENTS = ["american", "british", "australian", "indian", "canadian"]
SAMPLE_TEXTS = [
    "Please help me with my order.",
    "I am very satisfied with this product.",
    "This is completely unacceptable.",
    "Could you explain the pricing?",
    "I need to cancel my subscription.",
    "Thank you for your assistance.",
    "I have a complaint about my recent purchase.",
    "When will my package arrive?",
    "I want to speak with a manager.",
    "The product works exactly as described.",
]


class VoiceDatasetGenerator:
    """Generates synthetic voice dataset metadata for emotion-labeled audio."""

    def generate(self, num_samples: int = 100) -> list:
        """Generate emotion-labeled voice dataset metadata records.

        Args:
            num_samples: Number of records to generate (default 100).

        Returns:
            List of voice dataset metadata record dicts.
        """
        records = []
        for i in range(num_samples):
            record = {
                "id": str(uuid.uuid4()),
                "index": i,
                "emotion": random.choice(EMOTIONS),
                "accent": random.choice(ACCENTS),
                "text": random.choice(SAMPLE_TEXTS),
                "duration_ms": random.randint(1000, 8000),
                "sample_rate": 22050,
                "format": "WAV",
                "channels": 1,
                "bit_depth": 16,
                "speaker_id": f"SYNTH_{random.randint(1000, 9999)}",
                "synthetic": True,
                "license": "CC-BY-4.0",
            }
            records.append(record)
        logger.info("Generated %d voice dataset records.", num_samples)
        return records
