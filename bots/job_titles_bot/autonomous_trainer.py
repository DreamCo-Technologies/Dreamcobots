"""
Autonomous Trainer — Train humans and AI for job-specific tasks.

Capabilities
------------
* Face recognition training (register known faces, identify unknowns).
* Object recognition training (antiques, coins, currency, everyday items).
* Item valuation (estimate market value of physical items from descriptions).
* Buddy Bot propagation: when a training module improves, all bots update.
* Job-role-specific skill training tracks.

All recognition and valuation logic is implemented as deterministic rule-based
inference so there are no external ML dependencies at runtime.  Production
deployments can swap the estimator methods with real model calls.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class FaceRecord:
    """A registered face in the recognition system."""
    face_id: str
    label: str              # e.g. person's name or role
    encoding_hash: str      # SHA-256 of the raw encoding bytes (simulated)
    registered_at: float = field(default_factory=time.time)
    extra_metadata: dict = field(default_factory=dict)


@dataclass
class ObjectRecord:
    """A registered object category in the recognition system."""
    object_id: str
    category: str           # e.g. 'coin', 'antique', 'currency'
    description: str
    visual_keywords: list[str]
    estimated_value_usd: float = 0.0
    confidence: float = 1.0


@dataclass
class ValuationResult:
    """Result of an item valuation query."""
    item_description: str
    category: str
    estimated_min_usd: float
    estimated_max_usd: float
    estimated_value_usd: float
    confidence: float
    explanation: str
    factors: list[str]


@dataclass
class TrainingSession:
    """Records a completed training session."""
    session_id: str
    trainee: str            # 'human' | 'ai' | 'bot_name'
    skill: str
    duration_seconds: int
    score: float            # 0.0 – 1.0
    passed: bool
    feedback: str


# ---------------------------------------------------------------------------
# Valuation rules (deterministic heuristics)
# ---------------------------------------------------------------------------

_COIN_VALUES: dict[str, tuple[float, float]] = {
    "penny": (0.01, 50.0),
    "nickel": (0.05, 75.0),
    "dime": (0.10, 100.0),
    "quarter": (0.25, 200.0),
    "half dollar": (0.50, 500.0),
    "silver dollar": (10.0, 2000.0),
    "gold coin": (500.0, 10000.0),
    "bitcoin": (20000.0, 100000.0),
    "rare coin": (50.0, 50000.0),
    "commemorative coin": (5.0, 500.0),
}

_ANTIQUE_VALUES: dict[str, tuple[float, float]] = {
    "vase": (20.0, 5000.0),
    "furniture": (100.0, 20000.0),
    "painting": (50.0, 500000.0),
    "jewelry": (100.0, 50000.0),
    "watch": (50.0, 100000.0),
    "book": (5.0, 10000.0),
    "porcelain": (25.0, 15000.0),
    "clock": (30.0, 8000.0),
    "lamp": (20.0, 3000.0),
    "toy": (5.0, 2000.0),
    "stamp": (1.0, 5000.0),
    "baseball card": (1.0, 100000.0),
    "vinyl record": (5.0, 1000.0),
    "postcard": (1.0, 500.0),
}

_CURRENCY_MULTIPLIERS: dict[str, float] = {
    "usd": 1.0,
    "eur": 1.08,
    "gbp": 1.27,
    "cad": 0.74,
    "aud": 0.65,
    "jpy": 0.0067,
    "cny": 0.14,
    "bitcoin": 65000.0,
    "ethereum": 3500.0,
}


# ---------------------------------------------------------------------------
# Core class
# ---------------------------------------------------------------------------

class AutonomousTrainer:
    """
    Trains humans and AI agents for job-specific tasks, face recognition,
    object recognition, and item valuation.

    Designed to be embedded inside the ``JobTitlesBot`` and registered as
    a capability with BuddyBot.

    Parameters
    ----------
    trainer_id : str
        Unique identifier for this trainer instance.
    """

    CURRENT_MODULE_VERSION: str = "1.0.0"

    def __init__(self, trainer_id: str = "dreamco_trainer_v1") -> None:
        self.trainer_id = trainer_id
        self.version = self.CURRENT_MODULE_VERSION

        # Registries
        self._faces: dict[str, FaceRecord] = {}
        self._objects: dict[str, ObjectRecord] = {}
        self._sessions: list[TrainingSession] = []

        # Buddy Bot upgrade propagation callbacks
        self._upgrade_callbacks: list = []

    # ── Face Recognition ─────────────────────────────────────────────────────

    def register_face(
        self,
        label: str,
        raw_encoding: bytes,
        extra_metadata: Optional[dict] = None,
    ) -> FaceRecord:
        """
        Register a face with a label.

        Parameters
        ----------
        label : str
            Human-readable name or role (e.g. 'John Smith', 'Security Guard').
        raw_encoding : bytes
            Raw face-encoding bytes (from a camera or uploaded image).

        Returns
        -------
        FaceRecord
        """
        encoding_hash = hashlib.sha256(raw_encoding).hexdigest()
        face_id = f"face_{encoding_hash[:16]}"
        record = FaceRecord(
            face_id=face_id,
            label=label,
            encoding_hash=encoding_hash,
            extra_metadata=extra_metadata or {},
        )
        self._faces[face_id] = record
        return record

    def identify_face(self, raw_encoding: bytes) -> Optional[FaceRecord]:
        """
        Identify a face from raw encoding bytes.

        Returns the matching ``FaceRecord`` if found, otherwise ``None``.
        """
        encoding_hash = hashlib.sha256(raw_encoding).hexdigest()
        face_id = f"face_{encoding_hash[:16]}"
        return self._faces.get(face_id)

    def list_faces(self) -> list[FaceRecord]:
        """Return all registered face records."""
        return list(self._faces.values())

    # ── Object Recognition ───────────────────────────────────────────────────

    def register_object(
        self,
        category: str,
        description: str,
        visual_keywords: list[str],
        estimated_value_usd: float = 0.0,
    ) -> ObjectRecord:
        """
        Register a new object category for recognition.

        Parameters
        ----------
        category : str
            High-level category (e.g. 'coin', 'antique', 'currency').
        description : str
            Text description used for matching.
        visual_keywords : list[str]
            Keywords that visually identify this object.
        estimated_value_usd : float
            Known or estimated USD value.
        """
        object_id = f"obj_{hashlib.md5(description.encode()).hexdigest()[:12]}"
        record = ObjectRecord(
            object_id=object_id,
            category=category,
            description=description,
            visual_keywords=visual_keywords,
            estimated_value_usd=estimated_value_usd,
        )
        self._objects[object_id] = record
        return record

    def recognize_object(self, description: str) -> list[ObjectRecord]:
        """
        Attempt to recognize an object from its text description.

        Matches registered objects whose visual keywords appear in *description*.
        """
        desc_lower = description.lower()
        matches = [
            obj for obj in self._objects.values()
            if any(kw.lower() in desc_lower for kw in obj.visual_keywords)
        ]
        return sorted(matches, key=lambda o: o.confidence, reverse=True)

    # ── Item Valuation ───────────────────────────────────────────────────────

    def valuate_item(
        self, item_description: str, condition: str = "good"
    ) -> ValuationResult:
        """
        Estimate the market value of a physical item from its description.

        Handles coins, antiques, currency, and general collectibles using
        built-in heuristic tables.  Condition applies a multiplier:
          'poor': 0.3 × | 'fair': 0.6 × | 'good': 1.0 × |
          'very good': 1.3 × | 'excellent': 1.6 × | 'mint': 2.0 ×

        Parameters
        ----------
        item_description : str
            Natural-language description (e.g. "1955 double-die penny").
        condition : str
            Physical condition of the item.

        Returns
        -------
        ValuationResult
        """
        desc = item_description.lower()
        condition_mult = {
            "poor": 0.3, "fair": 0.6, "good": 1.0,
            "very good": 1.3, "excellent": 1.6, "mint": 2.0,
        }.get(condition.lower(), 1.0)

        # Try coins first
        for keyword, (lo, hi) in _COIN_VALUES.items():
            if keyword in desc:
                base = (lo + hi) / 2
                adjusted = round(base * condition_mult, 2)
                return ValuationResult(
                    item_description=item_description,
                    category="coin",
                    estimated_min_usd=round(lo * condition_mult, 2),
                    estimated_max_usd=round(hi * condition_mult, 2),
                    estimated_value_usd=adjusted,
                    confidence=0.75,
                    explanation=(
                        f"This appears to be a {keyword}. "
                        f"Condition '{condition}' applies a {condition_mult}× multiplier. "
                        f"Typical range: ${lo:,.2f}–${hi:,.2f}."
                    ),
                    factors=[f"item type: {keyword}", f"condition: {condition}"],
                )

        # Try antiques
        for keyword, (lo, hi) in _ANTIQUE_VALUES.items():
            if keyword in desc:
                base = (lo + hi) / 2
                adjusted = round(base * condition_mult, 2)
                return ValuationResult(
                    item_description=item_description,
                    category="antique",
                    estimated_min_usd=round(lo * condition_mult, 2),
                    estimated_max_usd=round(hi * condition_mult, 2),
                    estimated_value_usd=adjusted,
                    confidence=0.65,
                    explanation=(
                        f"Detected antique category: {keyword}. "
                        f"Condition '{condition}' applies a {condition_mult}× multiplier. "
                        f"Typical range: ${lo:,.2f}–${hi:,.2f}."
                    ),
                    factors=[f"antique type: {keyword}", f"condition: {condition}"],
                )

        # Try currency
        for currency, mult in _CURRENCY_MULTIPLIERS.items():
            if currency in desc:
                base = 1.0 * mult
                return ValuationResult(
                    item_description=item_description,
                    category="currency",
                    estimated_min_usd=round(base * 0.9, 4),
                    estimated_max_usd=round(base * 1.1, 4),
                    estimated_value_usd=round(base, 4),
                    confidence=0.90,
                    explanation=(
                        f"Currency type '{currency}' detected. "
                        f"Current exchange rate: 1 {currency} ≈ ${mult:,.4f} USD."
                    ),
                    factors=[f"currency: {currency}"],
                )

        # Generic fallback
        return ValuationResult(
            item_description=item_description,
            category="unknown",
            estimated_min_usd=0.0,
            estimated_max_usd=500.0,
            estimated_value_usd=50.0,
            confidence=0.20,
            explanation=(
                "Unable to identify specific item type from description. "
                "For a precise valuation, please provide more details or upload an image."
            ),
            factors=["unknown item type"],
        )

    # ── Skill Training ───────────────────────────────────────────────────────

    def run_training_session(
        self,
        trainee: str,
        skill: str,
        duration_seconds: int = 60,
    ) -> TrainingSession:
        """
        Simulate a training session for a human or AI agent.

        Parameters
        ----------
        trainee : str
            Identifier for the trainee ('human', 'ai', or a bot name).
        skill : str
            The skill being trained (e.g. 'data entry', 'coin identification').
        duration_seconds : int
            Length of the simulated session.

        Returns
        -------
        TrainingSession
        """
        # Deterministic score based on skill string hash so tests are stable
        hash_val = int(hashlib.md5(skill.encode()).hexdigest(), 16)
        score = round(0.5 + (hash_val % 500) / 1000.0, 2)   # 0.50–0.99
        passed = score >= 0.6
        session_id = f"session_{hashlib.md5(f'{trainee}{skill}{time.time()}'.encode()).hexdigest()[:12]}"
        feedback = (
            f"Training complete for '{skill}'. Score: {score:.0%}. "
            + ("Passed ✓" if passed else "Needs improvement — please retry.")
        )
        session = TrainingSession(
            session_id=session_id,
            trainee=trainee,
            skill=skill,
            duration_seconds=duration_seconds,
            score=score,
            passed=passed,
            feedback=feedback,
        )
        self._sessions.append(session)
        return session

    def training_history(self, trainee: Optional[str] = None) -> list[TrainingSession]:
        """Return past training sessions, optionally filtered by trainee."""
        if trainee:
            return [s for s in self._sessions if s.trainee == trainee]
        return list(self._sessions)

    # ── Buddy Bot upgrade propagation ────────────────────────────────────────

    def register_upgrade_callback(self, callback) -> None:
        """Register a callable invoked when this module upgrades."""
        self._upgrade_callbacks.append(callback)

    def upgrade_module(self, new_version: str) -> dict:
        """
        Upgrade this trainer module and notify all registered callbacks.
        Called automatically when Buddy Bot propagates a global upgrade.
        """
        old_version = self.version
        self.version = new_version
        notified = len(self._upgrade_callbacks)
        for cb in self._upgrade_callbacks:
            try:
                cb(new_version)
            except Exception:  # noqa: BLE001
                pass
        return {
            "trainer_id": self.trainer_id,
            "old_version": old_version,
            "new_version": new_version,
            "callbacks_notified": notified,
        }

    # ── Stats ────────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        """Return a summary of trainer activity."""
        return {
            "version": self.version,
            "registered_faces": len(self._faces),
            "registered_objects": len(self._objects),
            "training_sessions": len(self._sessions),
            "sessions_passed": sum(1 for s in self._sessions if s.passed),
        }


__all__ = [
    "AutonomousTrainer",
    "FaceRecord",
    "ObjectRecord",
    "ValuationResult",
    "TrainingSession",
]
