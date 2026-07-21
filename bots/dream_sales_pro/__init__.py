"""
DreamSalesPro Division Module — package initialiser.
"""
# GLOBAL AI SOURCES FLOW

from bots.dream_sales_pro.dream_sales_pro_bot import DreamSalesProBot, DSPAccessError
from bots.dream_sales_pro.tiers import DSPtier, get_tier_config, get_upgrade_path

# Provide a top-level ``Bot`` alias so the Dreamcobots framework
# (tools/check_bot_framework.py) can auto-discover this module.
Bot = DreamSalesProBot

__all__ = [
    "DreamSalesProBot",
    "Bot",
    "DSPtier",
    "DSPAccessError",
    "get_tier_config",
    "get_upgrade_path",
]
