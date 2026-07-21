"""
Buddy Teach Bot — Main Entry Point

A multi-platform teaching and broadcasting bot for the DreamCobots ecosystem.

Core capabilities:
  • Broadcast Engine     — deliver lessons to TV, game consoles, phones,
                           tablets, computers, smart displays, and AR/VR headsets
  • Skill Trainer        — step-by-step human skill training (car repair,
                           healthcare, finance, and more) with quiz scoring
                           and completion certificates
  • Item Detector        — identify and value items (coins, Pokémon cards,
                           antiques, collectibles) from natural-language
                           descriptions; crowdsourced AI training pipeline
  • Personality Engine   — each bot builds a unique, evolving personality
                           tailored to its user through interaction history,
                           tone adaptation, and milestone celebration

Tiers
-----
  FREE ($0/mo):           1 broadcast target, 3 skill tracks, basic valuation,
                          personality engine.
  PRO ($49/mo):           10 broadcast targets, 25 skill tracks, AI training,
                          AR/VR overlays, live broadcast feedback.
  ENTERPRISE ($199/mo):   Unlimited targets, custom curriculum builder,
                          white-label, API access, dedicated support.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  — GLOBAL AI SOURCES FLOW

from bots.buddy_teach_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_SKILL_TRAINING,
    FEATURE_ITEM_DETECTION,
    FEATURE_BROADCAST,
    FEATURE_MULTI_BROADCAST,
    FEATURE_PERSONALITY,
    FEATURE_AI_TRAINING,
    FEATURE_CURRICULUM_BUILDER,
    FEATURE_AR_VR_OVERLAY,
    FEATURE_LIVE_FEEDBACK,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
)
from bots.buddy_teach_bot.broadcast_engine import (
    BroadcastEngine,
    BroadcastTarget,
    BroadcastSession,
    BroadcastState,
    DeviceCategory,
    ContentFormat,
    BroadcastEngineError,
)
from bots.buddy_teach_bot.skill_trainer import (
    SkillTrainer,
    Lesson,
    LessonProgress,
    LessonStatus,
    SkillDomain,
    DifficultyLevel,
    SkillTrainerError,
)
from bots.buddy_teach_bot.item_detector import (
    ItemDetector,
    DetectionResult,
    ItemCategory,
    ConditionGrade,
    TrainingExample,
    ItemDetectorError,
)
from bots.buddy_teach_bot.personality_engine import (
    PersonalityEngine,
    ToneStyle,
    PersonalityTrait,
    Milestone,
    PersonalityEngineError,
)


class BuddyTeachBotError(Exception):
    """Raised when a Buddy Teach Bot operation fails."""


class BuddyTeachBotTierError(BuddyTeachBotError):
    """Raised when a feature is not available on the current tier."""


class BuddyTeachBot:
    """
    Buddy Teach Bot — multi-platform teaching and broadcasting assistant.

    Instantiate with a subscription tier and, optionally, a user ID so
    the personality engine can personalise the experience.

    Parameters
    ----------
    tier:       Subscription tier (FREE, PRO, or ENTERPRISE).
    user_id:    Unique identifier for the user (drives personality engine).
    bot_name:   Display name for this Buddy instance.
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        user_id: str = "default_user",
        bot_name: str = "Buddy",
    ) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self.user_id = user_id
        self.bot_name = bot_name

        # Subsystems
        self.broadcast = BroadcastEngine(
            max_targets=self.config.max_broadcast_targets
        )
        self.trainer = SkillTrainer(
            max_skill_tracks=self.config.max_skill_tracks
        )
        self.detector = ItemDetector()
        self.personality = PersonalityEngine(
            bot_name=bot_name,
            user_id=user_id,
        )

        self._boot_log: list[str] = []
        self._boot()

    # ------------------------------------------------------------------
    # Boot
    # ------------------------------------------------------------------

    def _boot(self) -> None:
        self._boot_log.append(f"{self.bot_name} Teach Bot initialised.")
        self._boot_log.append(f"Tier: {self.config.name} (${self.config.price_usd_monthly}/mo)")
        self._boot_log.append(
            f"Max broadcast targets: "
            f"{self.config.max_broadcast_targets or 'unlimited'}"
        )
        self._boot_log.append(
            f"Max skill tracks: "
            f"{self.config.max_skill_tracks or 'unlimited'}"
        )
        self._boot_log.append(
            f"Max AI training sessions: "
            f"{self.config.max_ai_training_sessions or 'unlimited'}"
        )
        self._boot_log.append(f"{self.bot_name} is ready to teach. 🚀")

    def get_boot_log(self) -> list[str]:
        return list(self._boot_log)

    # ------------------------------------------------------------------
    # Feature gating
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise BuddyTeachBotTierError(
                f"Feature '{feature}' is not available on the "
                f"{self.config.name} tier. Upgrade to access it."
            )

    # ------------------------------------------------------------------
    # Broadcast management
    # ------------------------------------------------------------------

    def add_broadcast_target(
        self,
        name: str,
        category: DeviceCategory,
        platform: str = "",
        ip_address: str = "",
        ar_capable: bool = False,
    ) -> BroadcastTarget:
        """Register a new device to receive broadcast content."""
        self._require_feature(FEATURE_BROADCAST)
        return self.broadcast.register_target(
            name=name,
            category=category,
            platform=platform,
            ip_address=ip_address,
            ar_capable=ar_capable,
        )

    def start_lesson_broadcast(
        self,
        lesson_id: str,
        target_ids: list[str],
        content_format: Optional[ContentFormat] = None,
        content_url: str = "",
    ) -> BroadcastSession:
        """
        Broadcast a lesson to one or more registered devices.

        Multi-device broadcast requires PRO or ENTERPRISE tier.
        """
        self._require_feature(FEATURE_BROADCAST)
        if len(target_ids) > 1:
            self._require_feature(FEATURE_MULTI_BROADCAST)

        lesson = self.trainer.get_lesson(lesson_id)
        fmt = content_format or ContentFormat.STEP_BY_STEP
        session = self.broadcast.start_broadcast(
            lesson_title=lesson.title,
            content_format=fmt,
            target_ids=target_ids,
            content_url=content_url,
        )

        # Record a personality interaction
        self.personality.process_message(
            f"Started broadcasting '{lesson.title}'",
            topics=[lesson.domain.value],
        )
        return session

    def broadcast_to_all_devices(
        self,
        lesson_id: str,
        content_format: Optional[ContentFormat] = None,
        content_url: str = "",
    ) -> BroadcastSession:
        """Broadcast a lesson to every registered device (PRO/ENTERPRISE)."""
        self._require_feature(FEATURE_MULTI_BROADCAST)
        lesson = self.trainer.get_lesson(lesson_id)
        fmt = content_format or ContentFormat.STEP_BY_STEP
        session = self.broadcast.broadcast_to_all(
            lesson_title=lesson.title,
            content_format=fmt,
            content_url=content_url,
        )
        return session

    # ------------------------------------------------------------------
    # Skill training
    # ------------------------------------------------------------------

    def list_lessons(
        self,
        domain: Optional[SkillDomain] = None,
        difficulty: Optional[DifficultyLevel] = None,
    ) -> list[Lesson]:
        """List available lessons, optionally filtered by domain or difficulty."""
        self._require_feature(FEATURE_SKILL_TRAINING)
        return self.trainer.list_lessons(domain=domain, difficulty=difficulty)

    def start_lesson(self, lesson_id: str) -> LessonProgress:
        """Begin a lesson for this bot's user."""
        self._require_feature(FEATURE_SKILL_TRAINING)
        progress = self.trainer.start_lesson(self.user_id, lesson_id)
        lesson = self.trainer.get_lesson(lesson_id)
        self.personality.process_message(
            f"I want to learn: {lesson.title}",
            topics=[lesson.domain.value],
        )
        return progress

    def advance_step(self, progress_id: str) -> LessonProgress:
        """Advance to the next step in a lesson."""
        self._require_feature(FEATURE_SKILL_TRAINING)
        return self.trainer.advance_step(progress_id)

    def complete_lesson(
        self, progress_id: str, quiz_score: float
    ) -> LessonProgress:
        """
        Submit a quiz score and complete the lesson.

        If the score meets the passing threshold, a certificate is issued
        and a milestone is recorded in the personality engine.
        """
        self._require_feature(FEATURE_SKILL_TRAINING)
        progress = self.trainer.complete_lesson(progress_id, quiz_score)
        lesson = self.trainer.get_lesson(progress.lesson_id)

        if progress.status == LessonStatus.COMPLETED:
            milestone = self.personality.record_milestone(
                title=f"Completed: {lesson.title}",
                description=(
                    f"Finished '{lesson.title}' with a score of "
                    f"{progress.score * 100:.0f}%."
                ),
                category="lesson_completed",
            )
            celebration = self.personality.celebrate_milestone(milestone)
            progress.feedback.append(celebration)

        return progress

    def add_lesson(self, lesson: Lesson) -> None:
        """Add a custom lesson (ENTERPRISE tier — curriculum builder)."""
        self._require_feature(FEATURE_CURRICULUM_BUILDER)
        self.trainer.add_lesson(lesson)

    # ------------------------------------------------------------------
    # Item detection
    # ------------------------------------------------------------------

    def detect_item(
        self,
        description: str,
        condition: ConditionGrade = ConditionGrade.GOOD,
        extra_context: Optional[str] = None,
    ) -> DetectionResult:
        """Identify an item and estimate its market value."""
        self._require_feature(FEATURE_ITEM_DETECTION)
        result = self.detector.detect_and_value(
            description=description,
            condition=condition,
            extra_context=extra_context,
        )
        self.personality.process_message(
            f"Identify this item: {description}",
            topics=["collectibles"],
        )
        return result

    def add_training_example(
        self,
        category: ItemCategory,
        description: str,
        visual_keywords: list[str],
        known_value_usd: Optional[float] = None,
    ) -> TrainingExample:
        """Submit a labelled training example to improve AI item detection."""
        self._require_feature(FEATURE_AI_TRAINING)
        return self.detector.add_training_example(
            category=category,
            description=description,
            visual_keywords=visual_keywords,
            known_value_usd=known_value_usd,
            contributor_id=self.user_id,
        )

    # ------------------------------------------------------------------
    # Personality & chat
    # ------------------------------------------------------------------

    def chat(self, message: str) -> str:
        """
        Send a message to Buddy and receive a personalised response.

        Buddy's tone and suggestions evolve with every interaction.
        """
        self._require_feature(FEATURE_PERSONALITY)
        return self.personality.process_message(message)

    def set_tone(self, tone: ToneStyle) -> None:
        """Manually set Buddy's conversational tone preference."""
        self._require_feature(FEATURE_PERSONALITY)
        self.personality.set_tone_preference(tone)

    def proactive_suggestions(self) -> list[str]:
        """Return proactive suggestions based on interaction history."""
        self._require_feature(FEATURE_PERSONALITY)
        return self.personality.proactive_suggestions()

    # ------------------------------------------------------------------
    # Summary / diagnostics
    # ------------------------------------------------------------------

    def status(self) -> dict:
        """Return a full status snapshot of the bot."""
        return {
            "bot_name": self.bot_name,
            "tier": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "user_id": self.user_id,
            "broadcast_targets": len(self.broadcast.list_targets()),
            "active_broadcasts": len(self.broadcast.active_sessions()),
            "total_lessons": len(self.trainer.list_lessons()),
            "ai_training_examples": self.detector.training_stats()[
                "total_examples"
            ],
            "personality_profile": self.personality.get_personality_profile(),
        }

    def upgrade_info(self) -> Optional[dict]:
        """Return information about the next available tier upgrade."""
        next_tier = get_upgrade_path(self.tier)
        if next_tier is None:
            return None
        return {
            "current_tier": self.config.name,
            "next_tier": next_tier.name,
            "next_price": next_tier.price_usd_monthly,
            "new_features": [
                f for f in next_tier.features if f not in self.config.features
            ],
        }
