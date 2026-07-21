"""
Referral Bot Examples
=====================
Demonstrates the two key use cases described in the Dreamcobots examples README:

1. User Referral and Earnings Tracking
2. Bot-to-Bot Interaction: Referral Bot + Hustle Bot

Run:
    python examples/referral_bot_example.py
"""

import sys
import os
import json

# Allow imports from the bots directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bots", "referral-bot"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bots", "hustle-bot"))

from referral_bot import ReferralBot
from hustle_bot import HustleBot


# ---------------------------------------------------------------------------
# Example 1: User Referral and Earnings Tracking
# ---------------------------------------------------------------------------

def example_referral_earnings():
    print("=" * 55)
    print("  Example 1: User Referral and Earnings Tracking")
    print("=" * 55)

    bot = ReferralBot(config={"commission_rate": 0.10})

    # Alex registers and generates an invite link
    bot.register_user("Alex")
    bot.generate_invite_link("Alex")

    # Three friends join via Alex's link
    for friend in ["Casey", "Jordan", "Taylor"]:
        bot.register_user(friend, referrer_id="Alex")

    # Friends generate revenue
    bot.record_revenue("Casey", 300)
    bot.record_revenue("Jordan", 500)
    bot.record_revenue("Taylor", 50)

    # Display Alex's real-time dashboard
    dashboard = bot.get_referrer_dashboard("Alex")
    print("\n--- Alex's Referral Dashboard ---")
    print(json.dumps(dashboard, indent=2))
    return bot


# ---------------------------------------------------------------------------
# Example 2: Bot-to-Bot Interaction
# ---------------------------------------------------------------------------

def example_bot_to_bot():
    print("\n" + "=" * 55)
    print("  Example 2: Bot-to-Bot Interaction")
    print("=" * 55)

    referral_bot = ReferralBot(config={"commission_rate": 0.10})
    hustle_bot = HustleBot()

    # Set up users
    referral_bot.register_user("Alex")
    referral_bot.register_user("Taylor", referrer_id="Alex")
    referral_bot.record_revenue("Taylor", 30)  # Taylor is underperforming

    # Give Taylor a goal in Hustle Bot so the campaign context is meaningful
    hustle_bot.configure_goal("Taylor", revenue_goal=500.0)

    # Referral Bot identifies underperformers and triggers Hustle Bot
    print("\nReferral Bot checking for underperformers (threshold=$100) …")
    referral_bot.notify_hustle_bot(hustle_bot, "Alex", revenue_threshold=100.0)

    # Show Taylor's updated summary
    summary = hustle_bot.get_daily_summary("Taylor")
    print("\n--- Taylor's Hustle Bot Summary after campaign ---")
    print(json.dumps(summary, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    example_referral_earnings()
    example_bot_to_bot()
    print("\n✅  Referral Bot examples completed successfully.")
