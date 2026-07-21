"""DreamCo Bot Wars Bot — Competition system, challenge manager, and drag-drop builder."""

from bots.bot_wars_bot.bot_wars_bot import BotWarsBot, BotWarsBotError, BotWarsTierError
from bots.bot_wars_bot.tiers import Tier
from bots.bot_wars_bot.competition_engine import CompetitionEngine, CompetitionEngineError
from bots.bot_wars_bot.challenge_manager import ChallengeManager, ChallengeManagerError, CHALLENGE_TYPES
from bots.bot_wars_bot.drag_drop_builder import DragDropBuilder, DragDropBuilderError, BOT_COMPONENT_TYPES

__all__ = [
    "BotWarsBot",
    "BotWarsBotError",
    "BotWarsTierError",
    "Tier",
    "CompetitionEngine",
    "CompetitionEngineError",
    "ChallengeManager",
    "ChallengeManagerError",
    "CHALLENGE_TYPES",
    "DragDropBuilder",
    "DragDropBuilderError",
    "BOT_COMPONENT_TYPES",
]
