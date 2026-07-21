"""
DreamRealEstate Division Module — package initialiser.
"""
# GLOBAL AI SOURCES FLOW

from bots.dream_real_estate.dream_real_estate_bot import DreamRealEstateBot, DREAccessError
from bots.dream_real_estate.tiers import DREtier, get_tier_config, get_upgrade_path

# Provide a top-level ``Bot`` alias so the Dreamcobots framework
# (tools/check_bot_framework.py) can auto-discover this module.
Bot = DreamRealEstateBot

__all__ = [
    "DreamRealEstateBot",
    "Bot",
    "DREtier",
    "DREAccessError",
    "get_tier_config",
    "get_upgrade_path",
]
