"""DreamCo AI Brain package — decision engine, state manager, and metrics tracker."""

from bots.ai_brain.ai_brain import AIBrain, AIBrainError, AIBrainTierError
from bots.ai_brain.tiers import Tier, TierConfig, get_tier_config
from bots.ai_brain.decision_engine import (
    DecisionEngine,
    DECISION_SCALE_LEADS,
    DECISION_INCREASE_OUTREACH,
    DECISION_SCALE_SYSTEM,
    DECISION_OPTIMIZE,
    DECISION_CREATE_SCALING_BOT,
    DECISION_CREATE_RECOVERY_BOT,
)
from bots.ai_brain.state_manager import StateManager, save_state, load_state
from bots.ai_brain.metrics_tracker import MetricsTracker

__all__ = [
    "AIBrain",
    "AIBrainError",
    "AIBrainTierError",
    "Tier",
    "TierConfig",
    "get_tier_config",
    "DecisionEngine",
    "DECISION_SCALE_LEADS",
    "DECISION_INCREASE_OUTREACH",
    "DECISION_SCALE_SYSTEM",
    "DECISION_OPTIMIZE",
    "DECISION_CREATE_SCALING_BOT",
    "DECISION_CREATE_RECOVERY_BOT",
    "StateManager",
    "save_state",
    "load_state",
    "MetricsTracker",
]
