"""
Bot Generator Bot package.

Usage::

    from bots.bot_generator_bot.bot_generator_bot import BotGeneratorBot
    from bots.bot_generator_bot.tiers import Tier

    bot = BotGeneratorBot(tier=Tier.PRO)
    result = bot.generate("Make a Dentist Lead Bot")
"""

from bots.bot_generator_bot.bot_generator_bot import BotGeneratorBot
from bots.bot_generator_bot.tiers import Tier

__all__ = ["BotGeneratorBot", "Tier"]
