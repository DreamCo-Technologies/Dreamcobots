"""Entry point for the Military Contract Bot."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from military_contract_bot import MilitaryContractBot, Tier

if __name__ == "__main__":
    bot = MilitaryContractBot(tier=Tier.ENTERPRISE)
    bot.run()
