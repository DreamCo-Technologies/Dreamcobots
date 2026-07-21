"""
method_classifier.py — Main AI method classification microservice.

Auto-classifies ingested AI methods into canonical categories such as
supervised learning, reinforcement learning, and self-supervised learning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Method categories
# ---------------------------------------------------------------------------

CATEGORY_SUPERVISED = "supervised_learning"
CATEGORY_UNSUPERVISED = "unsupervised_learning"
CATEGORY_REINFORCEMENT = "reinforcement_learning"
CATEGORY_SELF_SUPERVISED = "self_supervised_learning"
CATEGORY_SEMI_SUPERVISED = "semi_supervised_learning"
CATEGORY_TRANSFER = "transfer_learning"
CATEGORY_GENERATIVE = "generative_models"
CATEGORY_OTHER = "other"

ALL_CATEGORIES = [
    CATEGORY_SUPERVISED,
    CATEGORY_UNSUPERVISED,
    CATEGORY_REINFORCEMENT,
    CATEGORY_SELF_SUPERVISED,
    CATEGORY_SEMI_SUPERVISED,
    CATEGORY_TRANSFER,
    CATEGORY_GENERATIVE,
    CATEGORY_OTHER,
]

# Keyword → category mapping used by the rule-based fallback classifier
_KEYWORD_MAP: Dict[str, str] = {
    "supervised": CATEGORY_SUPERVISED,
    "classification": CATEGORY_SUPERVISED,
    "regression": CATEGORY_SUPERVISED,
    "random forest": CATEGORY_SUPERVISED,
    "svm": CATEGORY_SUPERVISED,
    "xgboost": CATEGORY_SUPERVISED,
    "clustering": CATEGORY_UNSUPERVISED,
    "k-means": CATEGORY_UNSUPERVISED,
    "pca": CATEGORY_UNSUPERVISED,
    "autoencoder": CATEGORY_UNSUPERVISED,
    "reinforcement": CATEGORY_REINFORCEMENT,
    "reward": CATEGORY_REINFORCEMENT,
    "policy gradient": CATEGORY_REINFORCEMENT,
    "q-learning": CATEGORY_REINFORCEMENT,
    "self-supervised": CATEGORY_SELF_SUPERVISED,
    "contrastive": CATEGORY_SELF_SUPERVISED,
    "self supervised": CATEGORY_SELF_SUPERVISED,
    "semi-supervised": CATEGORY_SEMI_SUPERVISED,
    "semi supervised": CATEGORY_SEMI_SUPERVISED,
    "pseudo label": CATEGORY_SEMI_SUPERVISED,
    "transfer": CATEGORY_TRANSFER,
    "fine-tune": CATEGORY_TRANSFER,
    "pretrain": CATEGORY_TRANSFER,
    "generative": CATEGORY_GENERATIVE,
    "gan": CATEGORY_GENERATIVE,
    "diffusion": CATEGORY_GENERATIVE,
    "vae": CATEGORY_GENERATIVE,
}


@dataclass
class ClassificationResult:
    """Holds the result of classifying a single method or document."""

    input_text: str
    category: str
    confidence: float
    matched_keywords: List[str] = field(default_factory=list)
    secondary_categories: List[str] = field(default_factory=list)


class MethodClassifier:
    """
    Classifies AI methods by keyword analysis.

    Parameters
    ----------
    confidence_threshold : float
        Minimum confidence (0–1) required to accept a classification.
        Inputs below this threshold are assigned ``CATEGORY_OTHER``.
    """

    def __init__(self, confidence_threshold: float = 0.3):
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0 and 1.")
        self.confidence_threshold = confidence_threshold

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def classify(self, text: str) -> ClassificationResult:
        """
        Classify a single text snippet.

        Parameters
        ----------
        text : str
            Title, abstract, or description of an AI method.

        Returns
        -------
        ClassificationResult
        """
        lower = text.lower()
        scores: Dict[str, float] = {}
        matched: List[str] = []

        for keyword, category in _KEYWORD_MAP.items():
            if keyword in lower:
                scores[category] = scores.get(category, 0.0) + 1.0
                matched.append(keyword)

        if not scores:
            return ClassificationResult(
                input_text=text,
                category=CATEGORY_OTHER,
                confidence=0.0,
                matched_keywords=[],
            )

        total = sum(scores.values())
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_cat, top_score = sorted_cats[0]
        confidence = top_score / total

        secondary = [c for c, _ in sorted_cats[1:] if c != top_cat]

        if confidence < self.confidence_threshold:
            top_cat = CATEGORY_OTHER

        return ClassificationResult(
            input_text=text,
            category=top_cat,
            confidence=round(confidence, 4),
            matched_keywords=matched,
            secondary_categories=secondary,
        )

    def classify_batch(self, texts: List[str]) -> List[ClassificationResult]:
        """Classify a list of text snippets."""
        return [self.classify(t) for t in texts]

    def list_categories(self) -> List[str]:
        """Return all recognised category identifiers."""
        return list(ALL_CATEGORIES)
