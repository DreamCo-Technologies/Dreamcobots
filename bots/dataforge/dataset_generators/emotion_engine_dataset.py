"""Emotion engine multi-modal dataset generator for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import random
import uuid

logger = logging.getLogger(__name__)

EMOTION_TYPES = [
    "joy", "sadness", "anger", "fear", "disgust", "surprise",
    "contempt", "neutral", "anxiety", "confidence", "trust", "anticipation",
]
MODALITY_TEXTS = [
    "I'm really happy about this outcome.",
    "This is so frustrating, I can't believe it.",
    "I'm not sure how I feel about this.",
    "Everything is going great!",
    "I'm quite worried about the deadline.",
]


class EmotionEngineDatasetGenerator:
    """Generates multi-modal emotion engine training datasets."""

    def _generate_audio_features(self, emotion: str) -> dict:
        """Generate simulated audio feature vector for an emotion.

        Args:
            emotion: The target emotion label.

        Returns:
            Dict of audio feature values.
        """
        return {
            "pitch_mean": round(random.uniform(80, 300), 2),
            "pitch_std": round(random.uniform(5, 50), 2),
            "energy": round(random.uniform(0.1, 1.0), 3),
            "speech_rate": round(random.uniform(100, 250), 1),
            "pause_ratio": round(random.uniform(0.05, 0.4), 3),
        }

    def _generate_visual_features(self, emotion: str) -> dict:
        """Generate simulated visual feature vector for an emotion.

        Args:
            emotion: The target emotion label.

        Returns:
            Dict of visual feature values including action units.
        """
        return {
            "au_1": round(random.uniform(0, 1), 3),
            "au_4": round(random.uniform(0, 1), 3),
            "au_6": round(random.uniform(0, 1), 3),
            "au_12": round(random.uniform(0, 1), 3),
            "au_17": round(random.uniform(0, 1), 3),
            "head_pose_yaw": round(random.uniform(-30, 30), 2),
            "gaze_direction": random.choice(["forward", "left", "right", "down"]),
        }

    def generate(self, num_samples: int = 200) -> list:
        """Generate multi-modal emotion engine records.

        Args:
            num_samples: Number of records to generate (default 200).

        Returns:
            List of multi-modal emotion record dicts.
        """
        records = []
        for i in range(num_samples):
            emotion = random.choice(EMOTION_TYPES)
            record = {
                "id": str(uuid.uuid4()),
                "index": i,
                "emotion_type": emotion,
                "intensity": round(random.uniform(0.1, 1.0), 3),
                "modalities": {
                    "text": random.choice(MODALITY_TEXTS),
                    "audio_features": self._generate_audio_features(emotion),
                    "visual_features": self._generate_visual_features(emotion),
                },
                "stress_level": round(random.uniform(0.0, 1.0), 3),
                "trust_score": round(random.uniform(0.0, 1.0), 3),
                "deception_score": round(random.uniform(0.0, 1.0), 3),
                "synthetic": True,
                "license": "CC-BY-4.0",
            }
            records.append(record)
        logger.info("Generated %d emotion engine records.", num_samples)
        return records
