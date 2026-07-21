"""
Buddy Trainer Bot — The ultimate AI, robotics, and human training companion.

Buddy Trainer Bot is the go-to system for:
  • Training AI models in real-time with adaptive feedback and data fine-tuning.
  • Automating AI model versioning, testing, and deployment via conversation.
  • Training robotics systems (industrial to consumer) with ML + code instructions.
  • Creating adaptive learning loops for physical robots via sensor feedback.
  • Teaching humans to train AI efficiently through guided workflows.
  • Managing datasets: labelling, curation, and export.
  • Provisioning GitHub-hosted personal Buddy bots upon payment (OWNER tier).
  • Multi-tier ownership: FREE → PRO ($49/mo) → ENTERPRISE ($199/mo) → OWNER ($499).

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.buddy_trainer_bot import BuddyTrainerBot, Tier

    buddy = BuddyTrainerBot(tier=Tier.PRO)
    response = buddy.chat("Train an image classifier on my cat vs dog dataset")
    print(response["message"])
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401

from bots.buddy_trainer_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_AI_TRAINING,
    FEATURE_AI_VERSIONING,
    FEATURE_AI_DEPLOYMENT,
    FEATURE_ROBOT_TRAINING,
    FEATURE_ADAPTIVE_LOOPS,
    FEATURE_SENSOR_FEEDBACK,
    FEATURE_HUMAN_COACHING,
    FEATURE_DATA_LABELING,
    FEATURE_DATASET_MANAGEMENT,
    FEATURE_GUIDED_WORKFLOWS,
    FEATURE_GITHUB_BUDDY,
    FEATURE_MULTI_MODEL,
    FEATURE_API_ACCESS,
    FEATURE_OWNERSHIP,
)
from bots.buddy_trainer_bot.ai_trainer import (
    AITrainer,
    ModelType,
    TrainingStatus,
    Dataset,
    ModelVersion,
    TrainingSession,
)
from bots.buddy_trainer_bot.robot_trainer import (
    RobotTrainer,
    RobotCategory,
    SensorType,
    TrainingPhase,
    Robot,
    RobotTrainingCycle,
)
from bots.buddy_trainer_bot.human_trainer import (
    HumanTrainer,
    SkillLevel,
    WorkflowType,
    LearningGoal,
    LearnerProfile,
    ManagedDataset,
)
from bots.buddy_trainer_bot.github_buddy_system import (
    GitHubBuddySystem,
    BuddySystem,
    BuddyFocusArea,
    BuddySystemStatus,
)
from bots.buddy_trainer_bot.ownership_system import (
    OwnershipSystem,
    License,
    PaymentMethod,
    LicenseStatus,
    Tier as OwnershipTier,
)


class BuddyTrainerError(Exception):
    """Raised when a Buddy Trainer operation fails."""


class BuddyTrainerTierError(BuddyTrainerError):
    """Raised when a feature is not available on the current tier."""


class BuddyTrainerBot:
    """
    Buddy Trainer Bot — AI, robotics, and human training companion.

    Acts as the conversational interface and orchestrator for all training
    subsystems within the DreamCobots ecosystem.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature access and session limits.
    owner_id : str
        Optional owner identifier (used for GitHub Buddy provisioning).
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        owner_id: str = "default_owner",
    ) -> None:
        self.tier = tier
        self.owner_id = owner_id
        self.config: TierConfig = get_tier_config(tier)

        # Subsystems
        self.ai_trainer = AITrainer(trainer_id=f"{owner_id}_ai_trainer")
        self.robot_trainer = RobotTrainer(trainer_id=f"{owner_id}_robot_trainer")
        self.human_trainer = HumanTrainer(trainer_id=f"{owner_id}_human_trainer")
        self.github_system = GitHubBuddySystem()
        self.ownership = OwnershipSystem()

        # Auto-activate a FREE license for the owner
        self.ownership.purchase_license(owner_id, Tier.FREE, PaymentMethod.CREDIT_CARD)

        self._session_count: int = 0

    # ------------------------------------------------------------------
    # Feature gate
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly:.0f}/mo)."
                if upgrade
                else ""
            )
            raise BuddyTrainerTierError(
                f"Feature '{feature}' is not available on the {self.config.name} tier.{upgrade_msg}"
            )

    def _check_session_limit(self) -> None:
        limit = self.config.max_ai_sessions_per_day
        if limit is not None and self._session_count >= limit:
            raise BuddyTrainerTierError(
                f"Daily session limit of {limit} reached on the {self.config.name} tier. "
                "Upgrade to Pro for unlimited sessions."
            )

    # ------------------------------------------------------------------
    # AI Training
    # ------------------------------------------------------------------

    def train_ai_model(
        self,
        model_name: str,
        model_type: ModelType,
        dataset_id: str,
        epochs: int = 20,
        learning_rate: float = 0.001,
    ) -> TrainingSession:
        """Train an AI model and return the completed session with feedback."""
        self._require_feature(FEATURE_AI_TRAINING)
        self._check_session_limit()
        session = self.ai_trainer.start_training(
            model_name, model_type, dataset_id, epochs, learning_rate
        )
        self._session_count += 1
        return session

    def register_training_dataset(
        self,
        name: str,
        num_samples: int,
        labels: list[str],
        source: str = "user_upload",
    ) -> Dataset:
        """Register a dataset for AI model training."""
        self._require_feature(FEATURE_AI_TRAINING)
        return self.ai_trainer.register_dataset(name, num_samples, labels, source)

    def deploy_model(self, model_name: str, version_id: str) -> dict:
        """Deploy a trained model version to production."""
        self._require_feature(FEATURE_AI_DEPLOYMENT)
        return self.ai_trainer.deploy_version(model_name, version_id)

    def rollback_model(self, model_name: str, version_id: str) -> dict:
        """Roll back a deployed model to a previous version."""
        self._require_feature(FEATURE_AI_VERSIONING)
        return self.ai_trainer.rollback(model_name, version_id)

    # ------------------------------------------------------------------
    # Robot Training
    # ------------------------------------------------------------------

    def register_robot(
        self,
        name: str,
        category: RobotCategory,
        manufacturer: str,
        model: str,
        sensors: list[SensorType] | None = None,
    ) -> Robot:
        """Register a robot for training."""
        self._require_feature(FEATURE_ROBOT_TRAINING)
        return self.robot_trainer.register_robot(name, category, manufacturer, model, sensors)

    def train_robot(
        self,
        robot_id: str,
        instructions: list[str] | None = None,
        phase: TrainingPhase = TrainingPhase.EXPLORATION,
    ) -> RobotTrainingCycle:
        """Run one adaptive training cycle for a robot."""
        self._require_feature(FEATURE_ROBOT_TRAINING)
        return self.robot_trainer.run_training_cycle(robot_id, instructions, phase)

    def run_adaptive_loop(
        self,
        robot_id: str,
        num_cycles: int = 5,
    ) -> list[RobotTrainingCycle]:
        """Run a full adaptive learning loop for a robot."""
        self._require_feature(FEATURE_ADAPTIVE_LOOPS)
        return self.robot_trainer.run_adaptive_loop(robot_id, num_cycles)

    # ------------------------------------------------------------------
    # Human Training
    # ------------------------------------------------------------------

    def enroll_human_learner(
        self,
        name: str,
        learning_goal: LearningGoal,
        skill_level: SkillLevel = SkillLevel.BEGINNER,
    ) -> LearnerProfile:
        """Enroll a human learner on the training platform."""
        self._require_feature(FEATURE_HUMAN_COACHING)
        return self.human_trainer.enroll_learner(name, learning_goal, skill_level)

    def get_learning_path(self, learner_id: str) -> list[dict]:
        """Return a personalised learning path for a human learner."""
        self._require_feature(FEATURE_GUIDED_WORKFLOWS)
        return self.human_trainer.get_learning_path(learner_id)

    def complete_learning_step(self, learner_id: str, step_id: str) -> dict:
        """Mark a guided workflow step as completed and award XP."""
        self._require_feature(FEATURE_HUMAN_COACHING)
        return self.human_trainer.complete_step(learner_id, step_id)

    def create_dataset(
        self,
        name: str,
        description: str,
        labels: list[str],
    ) -> ManagedDataset:
        """Create a new managed dataset for labelling."""
        self._require_feature(FEATURE_DATA_LABELING)
        return self.human_trainer.create_dataset(name, description, labels)

    def label_sample(
        self,
        dataset_id: str,
        raw_data: str,
        label: str,
        confidence: float = 1.0,
    ):
        """Add a labelled sample to a dataset."""
        self._require_feature(FEATURE_DATA_LABELING)
        return self.human_trainer.label_sample(dataset_id, raw_data, label, confidence)

    def export_dataset(self, dataset_id: str) -> dict:
        """Export a completed dataset."""
        self._require_feature(FEATURE_DATASET_MANAGEMENT)
        return self.human_trainer.export_dataset(dataset_id)

    # ------------------------------------------------------------------
    # GitHub Buddy System (OWNER tier)
    # ------------------------------------------------------------------

    def provision_personal_buddy(
        self,
        buddy_name: str,
        focus_area: BuddyFocusArea = BuddyFocusArea.FULL_SUITE,
        custom_greeting: str = "",
    ) -> BuddySystem:
        """Provision a personal GitHub-hosted Buddy bot (OWNER tier only)."""
        self._require_feature(FEATURE_GITHUB_BUDDY)
        return self.github_system.provision_buddy(
            owner_id=self.owner_id,
            buddy_name=buddy_name,
            focus_area=focus_area,
            tier=self.tier.value,
            custom_greeting=custom_greeting,
        )

    def start_personal_buddy(self) -> dict:
        """Start the user's personal GitHub-hosted Buddy bot."""
        self._require_feature(FEATURE_GITHUB_BUDDY)
        return self.github_system.start_buddy(self.owner_id)

    def stop_personal_buddy(self) -> dict:
        """Stop the user's personal GitHub-hosted Buddy bot."""
        self._require_feature(FEATURE_GITHUB_BUDDY)
        return self.github_system.stop_buddy(self.owner_id)

    # ------------------------------------------------------------------
    # Ownership & Licensing
    # ------------------------------------------------------------------

    def purchase_upgrade(
        self,
        target_tier: Tier,
        payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD,
    ) -> dict:
        """Purchase or upgrade to a higher Buddy tier."""
        result = self.ownership.upgrade_subscription(
            self.owner_id, target_tier, payment_method
        )
        if result.get("success"):
            self.tier = target_tier
            self.config = get_tier_config(target_tier)
        return result

    def apply_sponsorship(
        self,
        reason: str = "financial_hardship",
        tier_requested: Tier = Tier.PRO,
    ) -> dict:
        """
        Apply for a sponsored (free) Buddy license.

        Buddy is built to help everyone — including those who can't afford it.
        """
        return self.ownership.grant_sponsorship(
            beneficiary_user_id=self.owner_id,
            tier_granted=tier_requested,
            reason=reason,
        )

    # ------------------------------------------------------------------
    # System status
    # ------------------------------------------------------------------

    def system_status(self) -> dict:
        """Return a full Buddy Trainer Bot status snapshot."""
        return {
            "tier": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "owner_id": self.owner_id,
            "ai_trainer": self.ai_trainer.summary(),
            "robot_trainer": self.robot_trainer.summary(),
            "human_trainer": self.human_trainer.summary(),
            "github_systems": self.github_system.summary(),
            "ownership": self.ownership.revenue_summary(),
            "sessions_today": self._session_count,
            "features": self.config.features,
        }

    def describe_tier(self) -> str:
        """Return a human-readable tier description."""
        cfg = self.config
        upgrade = get_upgrade_path(self.tier)
        lines = [
            f"Buddy Trainer Bot — {cfg.name} Tier",
            f"Price: ${cfg.price_usd_monthly:.2f}/month"
            + (f" (or ${cfg.price_usd_one_time:.2f} one-time for Owner)" if cfg.price_usd_one_time else ""),
            f"AI sessions/day: {cfg.max_ai_sessions_per_day or 'Unlimited'}",
            f"Robot targets: {cfg.max_robot_targets or 'Unlimited'}",
            f"Human learners: {cfg.max_human_learners or 'Unlimited'}",
            f"GitHub Buddy: {'Included' if cfg.github_buddy_included else 'Not included'}",
            f"Support: {cfg.support_level}",
            f"Features: {', '.join(cfg.features)}",
        ]
        if upgrade:
            lines.append(
                f"Upgrade: {upgrade.name} — ${upgrade.price_usd_monthly:.2f}/month"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # BuddyAI-compatible chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Handle a natural-language message and return a conversational response.

        This method makes BuddyTrainerBot compatible with the BuddyAI orchestrator.
        """
        msg = message.lower().strip()

        # --- Status / overview ---
        if any(k in msg for k in ("status", "overview", "summary")):
            return {
                "response": "buddy_trainer_bot",
                "message": "Here is your Buddy Trainer Bot status.",
                "data": self.system_status(),
            }

        # --- Tier / pricing ---
        if any(k in msg for k in ("tier", "plan", "pricing", "upgrade", "cost", "price")):
            return {
                "response": "buddy_trainer_bot",
                "message": self.describe_tier(),
                "data": {},
            }

        # --- AI training ---
        if any(k in msg for k in ("train ai", "ai model", "classifier", "nlp model", "train model")):
            return {
                "response": "buddy_trainer_bot",
                "message": (
                    "I can train AI models in real-time! Tell me: "
                    "(1) your model name, (2) model type (e.g. classification, NLP), "
                    "(3) dataset ID. I'll handle training, versioning, and deployment for you."
                ),
                "data": {"feature": FEATURE_AI_TRAINING, "available": self.config.has_feature(FEATURE_AI_TRAINING)},
            }

        # --- Robot training ---
        if any(k in msg for k in ("robot", "robotics", "drone", "industrial", "servo")):
            return {
                "response": "buddy_trainer_bot",
                "message": (
                    "I can train robots! Register your robot with its category, manufacturer, "
                    "and sensors. I'll run adaptive training cycles and generate a control policy."
                ),
                "data": {"feature": FEATURE_ROBOT_TRAINING, "available": self.config.has_feature(FEATURE_ROBOT_TRAINING)},
            }

        # --- Human training ---
        if any(k in msg for k in ("teach me", "how to train", "learn ai", "data label", "dataset")):
            return {
                "response": "buddy_trainer_bot",
                "message": (
                    "I'll guide you step by step! Tell me your learning goal "
                    "(e.g. 'train an image classifier', 'build a chatbot') and I'll create "
                    "a personalised learning path with XP rewards."
                ),
                "data": {"feature": FEATURE_HUMAN_COACHING, "available": self.config.has_feature(FEATURE_HUMAN_COACHING)},
            }

        # --- GitHub / ownership ---
        if any(k in msg for k in ("own", "github", "my buddy", "personal buddy", "purchase", "buy")):
            return {
                "response": "buddy_trainer_bot",
                "message": (
                    "With the Owner tier ($499 one-time) you get your own personal Buddy bot "
                    "hosted on GitHub — full source code, your datasets, and config. "
                    "You have full runtime control. Ask about 'pricing' to see all tiers."
                ),
                "data": {"feature": FEATURE_GITHUB_BUDDY, "available": self.config.has_feature(FEATURE_GITHUB_BUDDY)},
            }

        # --- Apply sponsorship --- (must be checked BEFORE general "sponsor" keyword)
        if "apply for sponsorship" in msg or "apply sponsorship" in msg:
            result = self.apply_sponsorship()
            return {
                "response": "buddy_trainer_bot",
                "message": result.get("message", "Sponsorship processed."),
                "data": result,
            }

        # --- Sponsorship / affordability ---
        if any(k in msg for k in ("free", "afford", "sponsor", "help", "poor", "assistance")):
            return {
                "response": "buddy_trainer_bot",
                "message": (
                    "Buddy is for everyone! If you can't afford a paid plan, apply for a "
                    "DreamCo sponsorship — we'll give you free Pro access. Just ask me to "
                    "'apply for sponsorship'."
                ),
                "data": {"sponsorship_available": True},
            }

        # --- Deployment ---
        if any(k in msg for k in ("deploy", "release", "publish model", "go live")):
            return {
                "response": "buddy_trainer_bot",
                "message": (
                    "Ready to deploy! Use deploy_model(model_name, version_id) to push "
                    "your best model version live. I can also rollback if needed."
                ),
                "data": {"feature": FEATURE_AI_DEPLOYMENT, "available": self.config.has_feature(FEATURE_AI_DEPLOYMENT)},
            }

        # --- Default friendly response ---
        return {
            "response": "buddy_trainer_bot",
            "message": (
                "Hey! I'm Buddy — your AI, robotics, and human training companion. "
                "I can help you train AI models, program robots, label datasets, or teach "
                "you how to build your own intelligent systems. What would you like to do?"
            ),
            "data": {},
        }

    # ------------------------------------------------------------------
    # BuddyAI registration helper
    # ------------------------------------------------------------------

    def register_with_buddy(self, buddy_bot_instance) -> None:
        """Register this BuddyTrainerBot instance with a BuddyAI orchestrator."""
        buddy_bot_instance.register_bot("buddy_trainer", self)
