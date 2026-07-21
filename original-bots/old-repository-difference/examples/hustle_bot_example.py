"""
Hustle Bot Examples
===================
Demonstrates the two key use cases described in the Dreamcobots examples README:

1. Goal Setting and Milestone Achievement
2. Scaling Ecosystem Collaboration

Run:
    python examples/hustle_bot_example.py
"""

import sys
import os
import json

# Allow imports from the bots directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bots", "hustle-bot"))

from hustle_bot import HustleBot


# ---------------------------------------------------------------------------
# Example 1: Goal Setting and Milestone Achievement
# ---------------------------------------------------------------------------

def example_goal_milestones():
    print("=" * 55)
    print("  Example 1: Goal Setting and Milestone Achievement")
    print("=" * 55)

    bot = HustleBot()

    # Jordan sets up a revenue goal
    bot.configure_goal("Jordan", revenue_goal=1000.0)

    # Bot suggests initial tasks aligned with Jordan's stage
    print("\nSuggested tasks for Jordan:")
    suggestions = bot.suggest_tasks("Jordan")
    for i, s in enumerate(suggestions):
        print(f"  [{i}] {s}")

    # Jordan works toward the goal – record incremental revenue
    for amount in [150, 250, 200, 300]:
        bot.record_revenue("Jordan", amount)

    # Complete first two tasks
    bot.complete_task("Jordan", 0)
    bot.complete_task("Jordan", 1)

    # Daily progress summary
    summary = bot.get_daily_summary("Jordan")
    print("\n--- Jordan's Daily Summary ---")
    print(json.dumps(summary, indent=2))
    return bot


# ---------------------------------------------------------------------------
# Example 2: Scaling Ecosystem Collaboration
# ---------------------------------------------------------------------------

def example_scaling_collaboration():
    print("\n" + "=" * 55)
    print("  Example 2: Scaling Ecosystem Collaboration")
    print("=" * 55)

    bot = HustleBot()

    # Hustle Bot identifies untapped markets for outreach
    markets = bot.identify_untapped_markets()
    top_market = markets[0]
    print(f"\nTop growth opportunity: {top_market['name']} (score {top_market['potential_score']}/10)")
    print("Hustle Bot is promoting community-specific benefits …")

    # Simulate targeted motivational campaigns for new community members
    for user_id in ["community_member_1", "community_member_2", "community_member_3"]:
        bot.configure_goal(user_id, revenue_goal=300.0)
        bot.run_motivational_campaign(user_id)

    print("\n✅  Community outreach campaign completed.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    example_goal_milestones()
    example_scaling_collaboration()
    print("\n✅  Hustle Bot examples completed successfully.")
