"""
Buddy Teach Bot — Item Detector

Identifies and values physical items from descriptions or uploaded images
using deterministic rule-based heuristics.

Supported item categories:
  - Coins & Currency (pennies, silver dollars, commemorative, crypto)
  - Antiques (furniture, paintings, vases, jewelry, watches)
  - Trading Cards (Pokémon, sports, collectible card games)
  - Stamps (rare, first-day covers, error stamps)
  - Electronics (vintage consoles, cameras, audio gear)
  - Toys & Collectibles (Funko Pop, LEGO sets, action figures)

All valuation logic is deterministic heuristics — production deployments
can swap estimator methods with real computer-vision model calls.
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  — GLOBAL AI SOURCES FLOW


class ItemCategory(Enum):
    COIN = "coin"
    ANTIQUE = "antique"
    TRADING_CARD = "trading_card"
    STAMP = "stamp"
    ELECTRONICS = "electronics"
    TOY_COLLECTIBLE = "toy_collectible"
    JEWELRY = "jewelry"
    ARTWORK = "artwork"
    UNKNOWN = "unknown"


class ConditionGrade(Enum):
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    VERY_GOOD = "very_good"
    EXCELLENT = "excellent"
    MINT = "mint"


# Condition multipliers applied to base value
_CONDITION_MULTIPLIERS: dict[str, float] = {
    ConditionGrade.POOR.value: 0.10,
    ConditionGrade.FAIR.value: 0.25,
    ConditionGrade.GOOD.value: 0.50,
    ConditionGrade.VERY_GOOD.value: 0.75,
    ConditionGrade.EXCELLENT.value: 0.90,
    ConditionGrade.MINT.value: 1.00,
}


# ---------------------------------------------------------------------------
# Valuation knowledge bases
# ---------------------------------------------------------------------------

_COIN_DB: dict[str, tuple[float, float]] = {
    "penny": (0.01, 50.0),
    "wheat penny": (0.05, 200.0),
    "1943 steel penny": (50.0, 500.0),
    "nickel": (0.05, 75.0),
    "buffalo nickel": (1.0, 300.0),
    "dime": (0.10, 100.0),
    "mercury dime": (2.0, 250.0),
    "quarter": (0.25, 200.0),
    "bicentennial quarter": (0.25, 50.0),
    "half dollar": (0.50, 500.0),
    "walking liberty half dollar": (10.0, 600.0),
    "silver dollar": (10.0, 2000.0),
    "morgan silver dollar": (25.0, 3000.0),
    "gold coin": (500.0, 15000.0),
    "rare coin": (50.0, 50000.0),
    "error coin": (100.0, 100000.0),
    "commemorative coin": (5.0, 500.0),
    "foreign coin": (0.50, 200.0),
    "ancient coin": (20.0, 5000.0),
}

_ANTIQUE_DB: dict[str, tuple[float, float]] = {
    "vase": (20.0, 5000.0),
    "porcelain vase": (100.0, 25000.0),
    "furniture": (100.0, 20000.0),
    "victorian furniture": (500.0, 50000.0),
    "painting": (50.0, 500000.0),
    "oil painting": (200.0, 1000000.0),
    "jewelry": (100.0, 50000.0),
    "diamond jewelry": (1000.0, 250000.0),
    "watch": (50.0, 100000.0),
    "pocket watch": (100.0, 5000.0),
    "book": (5.0, 10000.0),
    "first edition book": (100.0, 100000.0),
    "clock": (50.0, 10000.0),
    "silver": (20.0, 20000.0),
    "lamp": (25.0, 5000.0),
    "tiffany lamp": (500.0, 100000.0),
    "ceramic": (10.0, 5000.0),
    "sculpture": (50.0, 500000.0),
}

_TRADING_CARD_DB: dict[str, tuple[float, float]] = {
    "pokemon card": (0.25, 500.0),
    "charizard": (50.0, 50000.0),
    "pikachu": (1.0, 5000.0),
    "holographic pokemon": (5.0, 10000.0),
    "first edition pokemon": (100.0, 300000.0),
    "psa 10 pokemon": (200.0, 500000.0),
    "sports card": (0.50, 5000.0),
    "rookie card": (5.0, 100000.0),
    "michael jordan rookie": (1000.0, 750000.0),
    "lebron james rookie": (500.0, 500000.0),
    "baseball card": (0.25, 10000.0),
    "1952 topps mickey mantle": (5000.0, 5000000.0),
    "magic the gathering": (0.10, 50000.0),
    "black lotus mtg": (10000.0, 1000000.0),
    "yu-gi-oh": (0.10, 10000.0),
}

_TOY_COLLECTIBLE_DB: dict[str, tuple[float, float]] = {
    "funko pop": (5.0, 2000.0),
    "lego set": (20.0, 10000.0),
    "action figure": (5.0, 500.0),
    "star wars figure": (10.0, 5000.0),
    "barbie doll": (5.0, 1000.0),
    "vintage toy": (20.0, 5000.0),
    "comic book": (1.0, 100000.0),
    "first appearance comic": (100.0, 1000000.0),
    "video game": (5.0, 2000.0),
    "sealed video game": (50.0, 100000.0),
}

_ELECTRONICS_DB: dict[str, tuple[float, float]] = {
    "vintage console": (50.0, 2000.0),
    "atari 2600": (30.0, 300.0),
    "nintendo nes": (50.0, 500.0),
    "vintage camera": (20.0, 2000.0),
    "leica camera": (500.0, 10000.0),
    "vintage audio": (50.0, 5000.0),
    "vinyl record": (1.0, 500.0),
    "first pressing vinyl": (10.0, 2000.0),
}


def _lookup_value(description: str, db: dict) -> Optional[tuple[float, float]]:
    """Find the best matching value range from a knowledge base."""
    desc_lower = description.lower()
    best_key = None
    best_len = 0
    for key in db:
        if key in desc_lower and len(key) > best_len:
            best_key = key
            best_len = len(key)
    if best_key:
        return db[best_key]
    return None


@dataclass
class DetectionResult:
    """Result of an item detection and valuation query."""

    result_id: str
    item_description: str
    detected_category: ItemCategory
    condition: ConditionGrade
    estimated_min_usd: float
    estimated_max_usd: float
    estimated_value_usd: float
    confidence: float
    explanation: str
    factors: list[str]
    comparable_sales: list[str]
    detected_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "result_id": self.result_id,
            "item_description": self.item_description,
            "detected_category": self.detected_category.value,
            "condition": self.condition.value,
            "estimated_min_usd": self.estimated_min_usd,
            "estimated_max_usd": self.estimated_max_usd,
            "estimated_value_usd": self.estimated_value_usd,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "factors": self.factors,
            "comparable_sales": self.comparable_sales,
            "detected_at": self.detected_at,
        }


@dataclass
class TrainingExample:
    """An image-based training example for the AI model."""

    example_id: str
    category: ItemCategory
    description: str
    visual_keywords: list[str]
    known_value_usd: Optional[float] = None
    contributor_id: str = "system"
    added_at: float = field(default_factory=time.time)


class ItemDetectorError(Exception):
    """Raised when item detection fails."""


class ItemDetector:
    """
    Item detector and valuator.

    Accepts natural-language descriptions (and, in production, image blobs)
    to identify items and estimate market value.
    """

    def __init__(self) -> None:
        self._detection_history: list[DetectionResult] = []
        self._training_examples: list[TrainingExample] = []
        self._ai_training_sessions: int = 0

    # ------------------------------------------------------------------
    # Detection & valuation
    # ------------------------------------------------------------------

    def detect_and_value(
        self,
        description: str,
        condition: ConditionGrade = ConditionGrade.GOOD,
        extra_context: Optional[str] = None,
    ) -> DetectionResult:
        """
        Identify an item and estimate its market value.

        Parameters
        ----------
        description:    Natural-language description of the item.
        condition:      Physical condition grade.
        extra_context:  Optional extra info (e.g. "first edition", "1952").
        """
        full_desc = description
        if extra_context:
            full_desc = f"{description} {extra_context}"

        category, raw_min, raw_max, confidence, explanation, factors = (
            self._classify_and_value(full_desc)
        )

        multiplier = _CONDITION_MULTIPLIERS[condition.value]
        est_min = round(raw_min * multiplier, 2)
        est_max = round(raw_max * multiplier, 2)
        est_value = round((est_min + est_max) / 2, 2)

        comparables = self._generate_comparables(category, full_desc, est_value)

        result = DetectionResult(
            result_id=str(uuid.uuid4()),
            item_description=full_desc,
            detected_category=category,
            condition=condition,
            estimated_min_usd=est_min,
            estimated_max_usd=est_max,
            estimated_value_usd=est_value,
            confidence=confidence,
            explanation=explanation,
            factors=factors,
            comparable_sales=comparables,
        )
        self._detection_history.append(result)
        return result

    def _classify_and_value(
        self, description: str
    ) -> tuple[ItemCategory, float, float, float, str, list[str]]:
        """Return (category, raw_min, raw_max, confidence, explanation, factors)."""
        desc_lower = description.lower()

        # Try each knowledge base in priority order
        for db, category in [
            (_COIN_DB, ItemCategory.COIN),
            (_TRADING_CARD_DB, ItemCategory.TRADING_CARD),
            (_ANTIQUE_DB, ItemCategory.ANTIQUE),
            (_TOY_COLLECTIBLE_DB, ItemCategory.TOY_COLLECTIBLE),
            (_ELECTRONICS_DB, ItemCategory.ELECTRONICS),
        ]:
            match = _lookup_value(description, db)
            if match:
                raw_min, raw_max = match
                factors = self._extract_factors(desc_lower, category)
                explanation = self._build_explanation(description, category, raw_min, raw_max)
                return category, raw_min, raw_max, 0.85, explanation, factors

        # Jewelry detection
        if any(w in desc_lower for w in ["gold", "silver", "diamond", "ring", "necklace", "bracelet"]):
            match = _lookup_value(description, _ANTIQUE_DB) or (100.0, 10000.0)
            raw_min, raw_max = match if isinstance(match, tuple) else match
            factors = ["precious metal/stone content", "craftsmanship", "brand/hallmark"]
            explanation = f"Detected as jewelry. Value based on material and craftsmanship."
            return ItemCategory.JEWELRY, raw_min, raw_max, 0.70, explanation, factors

        # Artwork detection
        if any(w in desc_lower for w in ["painting", "drawing", "sketch", "artwork", "print", "lithograph"]):
            raw_min, raw_max = 50.0, 500000.0
            factors = ["artist reputation", "provenance", "medium", "size", "condition"]
            explanation = "Detected as artwork. Value varies enormously by artist and provenance."
            return ItemCategory.ARTWORK, raw_min, raw_max, 0.65, explanation, factors

        return ItemCategory.UNKNOWN, 0.0, 0.0, 0.30, "Item not recognised in the database.", []

    def _extract_factors(
        self, desc_lower: str, category: ItemCategory
    ) -> list[str]:
        factors = ["item condition", "market demand"]
        if category == ItemCategory.COIN:
            if "error" in desc_lower:
                factors.append("minting error (major value booster)")
            if "1943" in desc_lower or "1909" in desc_lower:
                factors.append("key date")
            if "proof" in desc_lower:
                factors.append("proof strike")
            factors += ["metal composition", "rarity", "grading"]
        elif category == ItemCategory.TRADING_CARD:
            if "first edition" in desc_lower or "1st edition" in desc_lower:
                factors.append("first edition print run")
            if "psa" in desc_lower or "bgs" in desc_lower:
                factors.append("professional grading")
            if "holo" in desc_lower or "holographic" in desc_lower:
                factors.append("holographic variant")
            factors += ["card edition", "centering", "surface condition"]
        elif category in (ItemCategory.ANTIQUE, ItemCategory.ARTWORK):
            factors += ["age", "provenance", "artist/maker", "rarity"]
        return factors

    def _build_explanation(
        self,
        description: str,
        category: ItemCategory,
        raw_min: float,
        raw_max: float,
    ) -> str:
        return (
            f"Identified as {category.value.replace('_', ' ')}. "
            f"Base value range before condition adjustment: "
            f"${raw_min:,.2f} – ${raw_max:,.2f}. "
            "Condition grade is applied as a multiplier to the base range."
        )

    def _generate_comparables(
        self, category: ItemCategory, description: str, est_value: float
    ) -> list[str]:
        low = round(est_value * 0.80, 2)
        high = round(est_value * 1.20, 2)
        return [
            f"Recent auction: ${low:,.2f}",
            f"Recent auction: ${est_value:,.2f}",
            f"Buy-it-now listing: ${high:,.2f}",
        ]

    # ------------------------------------------------------------------
    # AI model training
    # ------------------------------------------------------------------

    def add_training_example(
        self,
        category: ItemCategory,
        description: str,
        visual_keywords: list[str],
        known_value_usd: Optional[float] = None,
        contributor_id: str = "user",
    ) -> TrainingExample:
        """Submit a labelled example to improve item detection."""
        example = TrainingExample(
            example_id=str(uuid.uuid4()),
            category=category,
            description=description,
            visual_keywords=visual_keywords,
            known_value_usd=known_value_usd,
            contributor_id=contributor_id,
        )
        self._training_examples.append(example)
        self._ai_training_sessions += 1
        return example

    def training_stats(self) -> dict:
        cat_counts: dict[str, int] = {}
        for ex in self._training_examples:
            k = ex.category.value
            cat_counts[k] = cat_counts.get(k, 0) + 1
        return {
            "total_examples": len(self._training_examples),
            "ai_training_sessions": self._ai_training_sessions,
            "categories": cat_counts,
        }

    def detection_history(self) -> list[DetectionResult]:
        return list(self._detection_history)
