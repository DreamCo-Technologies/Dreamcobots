"""
DreamCo Python Bots — Real Estate Bot

Discovers real-estate deals and publishes a ``deal_found`` event on the
shared event bus so downstream bots (analyser, outreach, payment) can act.
"""

from __future__ import annotations

from python_bots.base_bot import BaseBot
from event_bus.base_bus import BaseEventBus


class RealEstateBot(BaseBot):
    """
    Finds real-estate deals and emits them on the event bus.

    Publishes
    ---------
    deal_found
        ``{"address": str, "profit": int, "source": str}``
    """

    def run(self, event_bus: BaseEventBus) -> None:
        print(f"🏠 {self.name}: Running Real Estate Bot")

        deal = {
            "address": "123 Main St",
            "profit": 25000,
            "source": self.name,
        }

        event_bus.publish("deal_found", deal)
        print(f"🏠 {self.name}: Published deal_found → {deal}")
