"""
Learning method classifier for the DreamCo Global AI Learning System.

Performs keyword-based classification of ingested records into one of the
canonical AI/ML learning method types.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
import datetime
import uuid

from .tiers import Tier, TierConfig, get_tier_config, FEATURE_CLASSIFIER
from .ingestion import IngestedRecord
from framework import GlobalAISourcesFlow  # noqa: F401


class LearningMethodType(Enum):
    SUPERVISED = "supervised_learning"
    UNSUPERVISED = "unsupervised_learning"
    REINFORCEMENT = "reinforcement_learning"
    SEMI_SUPERVISED = "semi_supervised_learning"
    SELF_SUPERVISED = "self_supervised_learning"
    TRANSFER_LEARNING = "transfer_learning"
    FEDERATED_LEARNING = "federated_learning"
    META_LEARNING = "meta_learning"


@dataclass
class ClassifiedMethod:
    """A record that has been classified into a learning method category.

    Attributes
    ----------
    id : str
        Unique identifier (UUID4).
    title : str
        Title inherited from the source record.
    method_type : LearningMethodType
        Predicted learning method category.
    country_of_origin : str
        Country associated with the originating lab.
    lab_name : str
        Name of the originating research lab.
    novelty_score : float
        Inherited from the source record (0.0–1.0).
    confidence : float
        Classifier confidence for the predicted category (0.0–1.0).
    tags : List[str]
        Tags inherited and extended from the source record.
    classified_at : datetime.datetime
        UTC timestamp of classification.
    source_record_id : str | None
        ID of the originating IngestedRecord, if available.
    """

    id: str
    title: str
    method_type: LearningMethodType
    country_of_origin: str
    lab_name: str
    novelty_score: float
    confidence: float
    tags: List[str]
    classified_at: datetime.datetime
    source_record_id: Optional[str] = None


class ClassifierTierError(Exception):
    """Raised when the current tier does not support classification."""


# ---------------------------------------------------------------------------
# Keyword rules: order matters — more specific rules are listed first
# ---------------------------------------------------------------------------

_KEYWORD_RULES: List[tuple] = [
    # (method_type, keywords, base_confidence)
    (LearningMethodType.FEDERATED_LEARNING,   ["federated", "federated_learning"],                   0.91),
    (LearningMethodType.META_LEARNING,         ["meta_learning", "meta-learning", "maml", "few_shot"], 0.89),
    (LearningMethodType.SELF_SUPERVISED,       ["self_supervised", "self-supervised", "contrastive",
                                                "contrastive_learning", "pretext"],                   0.88),
    (LearningMethodType.SEMI_SUPERVISED,       ["semi_supervised", "semi-supervised"],                0.87),
    (LearningMethodType.TRANSFER_LEARNING,     ["transfer_learning", "transfer-learning",
                                                "pre_trained", "pretrained", "fine_tuning",
                                                "fine-tuning", "finetune"],                           0.86),
    (LearningMethodType.REINFORCEMENT,         ["reinforcement_learning", "reinforcement",
                                                "rlhf", "policy_gradient", "ppo", "q_learning",
                                                "dqn", "actor_critic", "reward"],                    0.90),
    (LearningMethodType.UNSUPERVISED,          ["unsupervised_learning", "unsupervised",
                                                "cluster", "clustering", "gan", "generative",
                                                "autoencoder", "vae", "diffusion"],                   0.85),
    (LearningMethodType.SUPERVISED,            ["supervised_learning", "supervised",
                                                "classification", "regression", "detection",
                                                "segmentation", "labelled", "labeled"],               0.84),
]

_DEFAULT_METHOD = LearningMethodType.SUPERVISED
_DEFAULT_CONFIDENCE = 0.70


def _classify_tags(tags: List[str], title: str) -> tuple:
    """Return (LearningMethodType, confidence) for a set of tags and title."""
    text_tokens = set(tags)
    # also tokenize the title
    for word in title.lower().replace("-", "_").split():
        text_tokens.add(word)

    for method_type, keywords, confidence in _KEYWORD_RULES:
        for kw in keywords:
            if kw in text_tokens or any(kw in tok for tok in text_tokens):
                return method_type, confidence

    return _DEFAULT_METHOD, _DEFAULT_CONFIDENCE


class LearningMethodClassifier:
    """Classifies ingested records into AI/ML learning method categories.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE and above support classification).
    """

    def __init__(self, tier: Tier) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._classified: List[ClassifiedMethod] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, record: IngestedRecord) -> ClassifiedMethod:
        """Classify a single ingested record.

        Parameters
        ----------
        record : IngestedRecord
            The record to classify.

        Returns
        -------
        ClassifiedMethod
            The classification result.

        Raises
        ------
        ClassifierTierError
            If the current tier does not have FEATURE_CLASSIFIER.
        """
        self._check_tier()

        method_type, confidence = _classify_tags(record.tags, record.title)
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

        classified = ClassifiedMethod(
            id=str(uuid.uuid4()),
            title=record.title,
            method_type=method_type,
            country_of_origin=record.metadata.get("country", "Unknown"),
            lab_name=record.metadata.get("lab_name", "Unknown"),
            novelty_score=record.novelty_score,
            confidence=confidence,
            tags=list(record.tags),
            classified_at=now,
            source_record_id=record.id,
        )
        self._classified.append(classified)
        return classified

    def classify_batch(self, records: List[IngestedRecord]) -> List[ClassifiedMethod]:
        """Classify a list of ingested records.

        Parameters
        ----------
        records : List[IngestedRecord]
            Records to classify.

        Returns
        -------
        List[ClassifiedMethod]
            Classification results in the same order.
        """
        return [self.classify(r) for r in records]

    def get_classified_methods(self) -> List[ClassifiedMethod]:
        """Return all classified methods produced so far."""
        return list(self._classified)

    def get_stats(self) -> dict:
        """Return a summary of classification activity."""
        type_counts: dict = {}
        for m in self._classified:
            key = m.method_type.value
            type_counts[key] = type_counts.get(key, 0) + 1
        avg_confidence = (
            sum(m.confidence for m in self._classified) / len(self._classified)
            if self._classified else 0.0
        )
        return {
            "total_classified": len(self._classified),
            "by_method_type": type_counts,
            "average_confidence": round(avg_confidence, 4),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_tier(self) -> None:
        if not self.config.has_feature(FEATURE_CLASSIFIER):
            raise ClassifierTierError(
                f"Learning method classification is not available on the "
                f"{self.config.name} tier. Please upgrade."
            )
