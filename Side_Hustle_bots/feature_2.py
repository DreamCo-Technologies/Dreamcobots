# Side Hustle Bot – Feature 2: Dropshipping & E-commerce Assistant
# Functionality: Guides entrepreneurs through product sourcing, store setup, and scaling.
# Use Cases: Side hustlers launching or growing an e-commerce store.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class DropshippingBot(BaseBot):
    """
    Side-hustle bot for dropshipping and e-commerce entrepreneurs.

    Assists with niche selection, supplier sourcing, store optimisation,
    and scaling strategies.  Sells product trend and sales data to
    e-commerce analytics platforms.
    """

    _TRENDING_NICHES = [
        "Eco-friendly home products",
        "Pet accessories",
        "Home office ergonomics",
        "Fitness & wellness gear",
        "Smart kitchen gadgets",
    ]

    def __init__(self):
        super().__init__(
            name="Dropshipping Bot",
            domain="ecommerce",
            category="side_hustle",
        )

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="E-commerce Product Trends Dataset",
            description="Monthly sales velocity and margin data for 500K SKUs across 10 niches.",
            domain="ecommerce",
            size_mb=380.0,
            price_usd=329.00,
            license="Proprietary",
            tags=["ecommerce", "dropshipping", "products", "trends", "sales"],
            ethical_review_passed=True,
        )

    def _setup_plans(self):
        super()._setup_plans()
        self.monetization.add_plan(PricingPlan(
            plan_id="ecom_starter",
            name="E-Commerce Starter",
            model=PricingModel.ONE_TIME,
            price_usd=49.99,
            description="One-time setup guide + niche analysis report.",
            features=["Niche report", "Supplier list", "Store checklist", "Ad copy templates"],
        ))

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()

        if intent == "greeting":
            niches = ", ".join(self._TRENDING_NICHES[:3])
            response = (
                f"{prefix}Hey entrepreneur! 🛒 I'm {self.name}. "
                f"Trending niches right now: {niches}. "
                "What product category interests you?"
            )
        elif intent == "pricing_inquiry":
            response = (
                f"{prefix}Profit margins in dropshipping typically range from 15–45%. "
                "I'll help you find products with strong margins. "
                "What budget are you working with?"
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer e-commerce product trend datasets."
                + self._dataset_offer()
            )
        elif intent == "help":
            response = (
                "I can: 🔍 Find winning products  |  🏭 Source suppliers  |  "
                "🛍️ Optimise your store  |  📊 Analyse competition  |  💾 Sell trend datasets."
            )
        else:
            response = (
                f"{prefix}Let's find your winning product! "
                "Tell me your target market and budget and I'll identify high-potential items."
            )
        return response


if __name__ == "__main__":
    bot = DropshippingBot()
    print(bot.chat("Hi! I want to start a dropshipping store selling fitness products."))
    print(bot.chat("What are the profit margins like?"))
    print(bot.status())
