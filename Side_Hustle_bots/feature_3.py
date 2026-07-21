# Side Hustle Bot – Feature 3: Gig Economy & Freelancing Advisor
# Functionality: Helps gig workers maximise earnings and manage multiple income streams.
# Use Cases: Uber drivers, TaskRabbit workers, multi-platform freelancers.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class GigEconomyBot(BaseBot):
    """
    Side-hustle bot that optimises earnings for gig economy workers.

    Provides platform comparisons, peak-hour insights, tax tips, and
    multi-stream income strategies.  Sells gig-worker earnings datasets
    to labour economists and gig-platform analytics teams.
    """

    _PLATFORMS = {
        "rideshare":   ["Uber", "Lyft", "Via"],
        "delivery":    ["DoorDash", "Instacart", "Amazon Flex", "Postmates"],
        "freelance":   ["Upwork", "Fiverr", "Toptal", "99designs"],
        "tasks":       ["TaskRabbit", "Handy", "Thumbtack"],
        "tutoring":    ["Wyzant", "Chegg Tutors", "VIPKid"],
    }

    def __init__(self):
        super().__init__(
            name="Gig Economy Bot",
            domain="gig_economy",
            category="side_hustle",
        )

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Gig Worker Earnings & Hours Dataset",
            description="Anonymised earnings, hours, and platform data from 50K gig workers.",
            domain="gig_economy",
            size_mb=65.0,
            price_usd=149.00,
            license="CC-BY-4.0",
            tags=["gig economy", "earnings", "labour", "freelance"],
            ethical_review_passed=True,
        )

    def _setup_plans(self):
        super()._setup_plans()
        self.monetization.add_plan(PricingPlan(
            plan_id="gig_optimizer",
            name="Gig Optimizer",
            model=PricingModel.SUBSCRIPTION,
            price_usd=9.99,
            description="Monthly earnings optimisation with peak-hour alerts and tax estimates.",
            features=["Peak-hour alerts", "Platform earnings comparison", "Tax estimates", "Tips"],
        ))

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        tokens = set(nlp_result.get("tokens", []))
        prefix = self._emotion_prefix()

        matched_category = None
        matched_platforms = []
        for category, platforms in self._PLATFORMS.items():
            if any(p.lower() in tokens for p in platforms) or category in tokens:
                matched_category = category
                matched_platforms = platforms
                break

        if intent == "pricing_inquiry":
            response = (
                f"{prefix}Top earner tips: 💡 Work peak hours (Fri/Sat evenings for rideshare). "
                "Track all expenses for tax deductions. Diversify across 2-3 platforms."
            )
        elif intent == "greeting":
            all_platforms = sum(self._PLATFORMS.values(), [])
            response = (
                f"{prefix}Hey! 💼 I'm {self.name}. I'll help you maximise your gig income. "
                f"I support {len(all_platforms)} platforms. Which do you use?"
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer gig worker earnings and hours datasets."
                + self._dataset_offer()
            )
        elif intent == "help":
            response = (
                "I can: 💰 Compare platform earnings  |  ⏰ Find peak hours  |  "
                "🧾 Estimate taxes  |  📈 Build multiple income streams."
            )
        elif matched_category:
            platform_list = ", ".join(matched_platforms)
            response = (
                f"{prefix}For **{matched_category}** gigs, consider: {platform_list}. "
                "To maximise earnings, work peak demand windows and maintain a top rating."
            )
        else:
            response = (
                f"{prefix}Tell me which gig platforms you're on and your weekly hours, "
                "and I'll show you how to increase your earnings."
            )
        return response


if __name__ == "__main__":
    bot = GigEconomyBot()
    print(bot.chat("Hi! I drive for Uber and want to earn more."))
    print(bot.chat("How do I maximise my earnings?"))
    print(bot.status())
