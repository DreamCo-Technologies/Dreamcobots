"""Entry point for the government-contract-grant-bot."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from government_contract_grant_bot import GovernmentContractGrantBot

if __name__ == "__main__":
    bot = GovernmentContractGrantBot()
    bot.run()
