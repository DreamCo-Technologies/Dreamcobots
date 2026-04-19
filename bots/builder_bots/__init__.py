"""
Builder Bots — Fleet of specialised construction agents.

Each builder bot focuses on a specific domain:

  • OrchestrationBuilderBot  — async/parallel pipeline infrastructure
  • VoiceEngineBuilderBot    — voice synthesis pipeline enhancements
  • ImageVideoBuilderBot     — image and video generation pipeline
  • MarketplaceBuilderBot    — AI Marketplace expansion and monetisation
  • CreativeStudioBuilderBot — ads, music, and cinematic content hub
  • BotTesterIntegrator      — automated testing and end-to-end integration

After completing their foundational tasks every bot automatically pivots to
generating placeholder scaffolding and logging innovative bot ideas to
``bot_ideas_log.txt``.
"""

from bots.builder_bots.orchestration_builder_bot import OrchestrationBuilderBot
from bots.builder_bots.voice_engine_builder_bot import VoiceEngineBuilderBot
from bots.builder_bots.image_video_builder_bot import ImageVideoBuilderBot
from bots.builder_bots.marketplace_builder_bot import MarketplaceBuilderBot
from bots.builder_bots.creative_studio_builder_bot import CreativeStudioBuilderBot
from bots.builder_bots.bot_tester_integrator import BotTesterIntegrator

__all__ = [
    "OrchestrationBuilderBot",
    "VoiceEngineBuilderBot",
    "ImageVideoBuilderBot",
    "MarketplaceBuilderBot",
    "CreativeStudioBuilderBot",
    "BotTesterIntegrator",
]
