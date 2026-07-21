# bots/bot_base.py
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
# Shim: re-exports BotBase and helpers from the canonical backend/core/bot_base.py
# so that bots using `from bots.bot_base import BotBase` continue to work.
from backend.core.bot_base import (  # noqa: F401
    BotBase,
    RevenueEngine,
    AutomationEngine,
    MonetizationHooks,
    DreamCore,
    CrashGuard,
)
