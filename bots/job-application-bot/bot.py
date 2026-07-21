"""
bot.py

Main entry point for the Job Application Bot.

Usage (from this directory):
    python bot.py --help
    python bot.py parse-resume
    python bot.py login
    python bot.py apply --headless
    python bot.py run --headless
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from cli import main

if __name__ == "__main__":
    main()
