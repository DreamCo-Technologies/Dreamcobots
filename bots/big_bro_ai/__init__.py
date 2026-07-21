"""Big Bro AI package — Digital big brother, mentor, and autonomous platform builder."""

from bots.big_bro_ai.big_bro_ai import BigBroAI, BigBroAIError, BigBroTierError
from bots.big_bro_ai.tiers import Tier
from bots.big_bro_ai.interactive_dashboard import InteractiveDashboard, BotSpeed

__all__ = ["BigBroAI", "BigBroAIError", "BigBroTierError", "Tier", "InteractiveDashboard", "BotSpeed"]
