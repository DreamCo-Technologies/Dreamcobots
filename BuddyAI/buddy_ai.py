"""
buddy_ai.py – BuddyAI: Central AI manager for the DreamCObots ecosystem.

BuddyAI orchestrates all registered bots, routes incoming messages to the
most appropriate bot, aggregates analytics, and provides a unified interface
for the entire DreamCObots platform.

Architecture
------------
* Bot registry  – maintains a catalogue of all active bot instances.
* Intent router – uses NLP to pick the best bot for each message.
* Session manager – tracks per-user active sessions.
* Aggregated analytics – surfaces revenue and interaction metrics across bots.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from typing import Any, Dict, List, Optional, Type

from framework import BaseBot
from framework.nlp_engine import NLPEngine


class BuddyAI:
    """
    Central AI hub that manages and routes conversations across all DreamCObots.

    Usage
    -----
    >>> buddy = BuddyAI()
    >>> buddy.register(JobSearchBot())
    >>> buddy.register(InvoicingBot())
    >>> response = buddy.chat("I need help with my resume", user_id="alice")
    >>> print(response)
    """

    # Mapping of domain keywords to bot categories for smart routing
    _DOMAIN_KEYWORDS: Dict[str, List[str]] = {
        "occupational": ["job", "career", "resume", "interview", "hire", "employment", "work"],
        "business":     ["invoice", "billing", "project", "meeting", "schedule", "business"],
        "marketing":    ["marketing", "email", "social", "campaign", "feedback", "brand"],
        "real_estate":  ["property", "house", "listing", "real estate", "mortgage", "viewing"],
        "side_hustle":  ["hustle", "freelance", "fiverr", "gig", "content", "dropship", "ecommerce"],
        "app":          ["app", "onboard", "feature", "support", "update", "software"],
    }

    def __init__(self):
        self._bots: Dict[str, BaseBot] = {}          # bot_id → bot
        self._category_index: Dict[str, List[str]] = {}  # category → [bot_ids]
        self._nlp = NLPEngine()
        self._user_sessions: Dict[str, str] = {}     # user_id → active bot_id

    # ------------------------------------------------------------------
    # Bot registration
    # ------------------------------------------------------------------

    def register(self, bot: BaseBot) -> None:
        """Register a bot with BuddyAI."""
        self._bots[bot.bot_id] = bot
        category = bot.category
        if category not in self._category_index:
            self._category_index[category] = []
        self._category_index[category].append(bot.bot_id)
        print(f"[BuddyAI] Registered: {bot.name} (category={category}, id={bot.bot_id[:8]}…)")

    def unregister(self, bot_id: str) -> bool:
        """Remove a bot from the registry."""
        bot = self._bots.pop(bot_id, None)
        if bot:
            self._category_index.get(bot.category, []).remove(bot_id)
            return True
        return False

    def get_bot(self, bot_id: str) -> Optional[BaseBot]:
        return self._bots.get(bot_id)

    def list_bots(self) -> List[Dict[str, str]]:
        return [
            {"bot_id": b.bot_id, "name": b.name, "category": b.category, "domain": b.domain}
            for b in self._bots.values()
        ]

    # ------------------------------------------------------------------
    # Conversation routing
    # ------------------------------------------------------------------

    def chat(self, user_input: str, user_id: str = "anonymous") -> str:
        """
        Route a user message to the most appropriate bot and return its response.

        Routing strategy
        ----------------
        1. If the user has an active session, continue with that bot.
        2. Otherwise, use NLP to detect the best-fit category, then pick the
           first registered bot in that category.
        3. Fall back to the first registered bot if no match is found.
        """
        if not self._bots:
            return "BuddyAI: No bots are currently registered. Please check back soon!"

        # Honour existing session
        active_bot_id = self._user_sessions.get(user_id)
        if active_bot_id and active_bot_id in self._bots:
            bot = self._bots[active_bot_id]
        else:
            bot = self._route(user_input)
            self._user_sessions[user_id] = bot.bot_id

        response = bot.chat(user_input, user_id=user_id)
        return f"[{bot.name}] {response}"

    def switch_bot(self, user_id: str, bot_name: str) -> str:
        """Explicitly switch a user to a named bot."""
        for bot in self._bots.values():
            if bot_name.lower() in bot.name.lower():
                self._user_sessions[user_id] = bot.bot_id
                return f"[BuddyAI] Switched to **{bot.name}**. How can I help?"
        available = ", ".join(b.name for b in self._bots.values())
        return f"[BuddyAI] Bot '{bot_name}' not found. Available: {available}"

    def end_session(self, user_id: str) -> str:
        """End a user session and trigger adaptive learning updates."""
        bot_id = self._user_sessions.pop(user_id, None)
        if bot_id and bot_id in self._bots:
            self._bots[bot_id].end_session(user_id)
            return f"[BuddyAI] Session ended. See you next time, {user_id}!"
        return "[BuddyAI] No active session found."

    def _route(self, text: str) -> BaseBot:
        """Pick the best bot for the given text using keyword-category matching."""
        nlp_result = self._nlp.process(text)
        tokens = set(nlp_result["tokens"])
        raw = text.lower()

        scores: Dict[str, int] = {}
        for category, keywords in self._DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in tokens or kw in raw)
            if score:
                scores[category] = score

        if scores:
            best_category = max(scores, key=lambda k: scores[k])
            bot_ids = self._category_index.get(best_category, [])
            if bot_ids:
                return self._bots[bot_ids[0]]

        # Fall back to first registered bot
        return next(iter(self._bots.values()))

    # ------------------------------------------------------------------
    # Platform-wide analytics
    # ------------------------------------------------------------------

    def platform_summary(self) -> Dict[str, Any]:
        """Aggregate metrics across all registered bots."""
        total_revenue = 0.0
        total_datasets = 0
        total_sales = 0
        bot_summaries = []

        for bot in self._bots.values():
            status = bot.status()
            total_revenue += status["revenue"]["total_revenue_usd"]
            total_datasets += status["datasets"]["datasets_available"]
            total_sales += status["datasets"]["total_sales"]
            bot_summaries.append({
                "name": bot.name,
                "category": bot.category,
                "revenue_usd": status["revenue"]["total_revenue_usd"],
                "datasets": status["datasets"]["datasets_available"],
                "top_intents": status["top_intents"],
            })

        return {
            "registered_bots": len(self._bots),
            "active_sessions": len(self._user_sessions),
            "total_platform_revenue_usd": round(total_revenue, 2),
            "total_datasets_available": total_datasets,
            "total_dataset_sales": total_sales,
            "bots": bot_summaries,
        }


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from Occupational_bots.feature_1 import JobSearchBot
    from Occupational_bots.feature_2 import ResumeBuildingBot
    from Occupational_bots.feature_3 import InterviewPrepBot
    from Business_bots.feature_1 import MeetingSchedulerBot
    from Business_bots.feature_3 import InvoicingBot
    from Marketing_bots.feature_1 import SocialMediaBot
    from Marketing_bots.feature_3 import CustomerFeedbackBot
    from Side_Hustle_bots.feature_1 import ContentCreatorBot
    from Side_Hustle_bots.feature_3 import GigEconomyBot

    buddy = BuddyAI()
    for bot in [
        JobSearchBot(), ResumeBuildingBot(), InterviewPrepBot(),
        MeetingSchedulerBot(), InvoicingBot(),
        SocialMediaBot(), CustomerFeedbackBot(),
        ContentCreatorBot(), GigEconomyBot(),
    ]:
        buddy.register(bot)

    print("\n--- BuddyAI Demo ---\n")
    print(buddy.chat("Hello! I'm looking for a software engineering job.", user_id="alice"))
    print(buddy.chat("Can you help me with my resume?", user_id="bob"))
    print(buddy.chat("I need to schedule a meeting with my team.", user_id="carol"))
    print(buddy.chat("I want to start a YouTube channel about cooking.", user_id="dave"))
    print("\n--- Platform Summary ---")
    import json
    print(json.dumps(buddy.platform_summary(), indent=2))
