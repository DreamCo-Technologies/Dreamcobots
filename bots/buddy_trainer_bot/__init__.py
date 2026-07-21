"""BuddyTrainerBot package — AI, robotics, and human training companion."""

from bots.buddy_trainer_bot.buddy_trainer_bot import (
    BuddyTrainerBot,
    BuddyTrainerError,
    BuddyTrainerTierError,
)
from bots.buddy_trainer_bot.tiers import Tier, TierConfig, get_tier_config, list_tiers
from bots.buddy_trainer_bot.ai_trainer import AITrainer, ModelType, TrainingStatus
from bots.buddy_trainer_bot.robot_trainer import RobotTrainer, RobotCategory, TrainingPhase
from bots.buddy_trainer_bot.human_trainer import HumanTrainer, SkillLevel, LearningGoal
from bots.buddy_trainer_bot.github_buddy_system import GitHubBuddySystem, BuddyFocusArea
from bots.buddy_trainer_bot.ownership_system import OwnershipSystem, PaymentMethod

__all__ = [
    "BuddyTrainerBot",
    "BuddyTrainerError",
    "BuddyTrainerTierError",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "list_tiers",
    "AITrainer",
    "ModelType",
    "TrainingStatus",
    "RobotTrainer",
    "RobotCategory",
    "TrainingPhase",
    "HumanTrainer",
    "SkillLevel",
    "LearningGoal",
    "GitHubBuddySystem",
    "BuddyFocusArea",
    "OwnershipSystem",
    "PaymentMethod",
]
