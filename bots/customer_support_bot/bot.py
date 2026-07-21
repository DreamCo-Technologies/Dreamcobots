"""
Dreamcobots CustomerSupportBot — tier-aware customer support automation.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.customer_support_bot.tiers import CUSTOMER_SUPPORT_FEATURES, get_customer_support_tier_info
import uuid
from datetime import datetime


class CustomerSupportBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class CustomerSupportBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class CustomerSupportBot:
    """Tier-aware customer support automation bot."""

    FREE_CATEGORIES = ["billing", "technical", "general"]

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise CustomerSupportBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_feature(self, feature: str) -> None:
        features = CUSTOMER_SUPPORT_FEATURES[self.tier.value]
        if not any(feature.lower() in f.lower() for f in features):
            raise CustomerSupportBotTierError(
                f"'{feature}' is not available on the {self.config.name} tier. "
                f"Please upgrade to access this feature."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    def _analyze_sentiment(self, message: str) -> str:
        """Basic sentiment analysis using keyword matching."""
        message_lower = message.lower()
        negative_keywords = ["angry", "frustrated", "terrible", "awful", "broken", "failed", "error", "wrong", "bad", "horrible"]
        positive_keywords = ["great", "excellent", "happy", "satisfied", "wonderful", "amazing", "love", "perfect", "thank"]
        neg_count = sum(1 for kw in negative_keywords if kw in message_lower)
        pos_count = sum(1 for kw in positive_keywords if kw in message_lower)
        if neg_count > pos_count:
            return "negative"
        if pos_count > neg_count:
            return "positive"
        return "neutral"

    def handle_ticket(self, ticket: dict) -> dict:
        """
        Handle a support ticket.

        Args:
            ticket: {"id": str optional, "message": str, "category": str optional}

        Returns:
            {"ticket_id": str, "response": str, "category": str, "sentiment": str,
             "escalated": bool, "tier": str}
        """
        self._check_request_limit()
        self._request_count += 1

        message = ticket.get("message", "")
        category = ticket.get("category", "general").lower()
        ticket_id = ticket.get("id", str(uuid.uuid4()))

        if self.tier == Tier.FREE:
            if category not in self.FREE_CATEGORIES:
                category = "general"
            sentiment = "neutral"
            escalated = False
            response = f"Thank you for contacting support. Your {category} inquiry has been received. Our team will respond via email within 2-3 business days."

        elif self.tier == Tier.PRO:
            sentiment = self._analyze_sentiment(message)
            escalated = sentiment == "negative"
            response = (
                f"Thank you for reaching out. We've received your {category} inquiry "
                f"and have assigned it priority routing. "
                + ("A specialist will contact you shortly due to the urgency detected." if escalated
                   else "We will respond within 4 hours.")
            )

        else:  # ENTERPRISE
            sentiment = self._analyze_sentiment(message)
            escalated = sentiment == "negative"
            response = (
                f"Your {category} request has been received and processed by our AI system. "
                f"Sentiment: {sentiment}. "
                + ("Escalating to your dedicated SLA team immediately." if escalated
                   else "Your dedicated agent will respond within 1 hour per your SLA.")
            )

        return {
            "ticket_id": ticket_id,
            "response": response,
            "category": category,
            "sentiment": sentiment,
            "escalated": escalated,
            "tier": self.tier.value,
        }

    def escalate(self, ticket_id: str) -> dict:
        """
        Escalate a ticket to a higher-level agent.

        Args:
            ticket_id: The ticket identifier to escalate.

        Returns:
            {"ticket_id": str, "escalated": bool, "assigned_to": str, "tier": str}
        """
        if self.tier == Tier.FREE:
            raise CustomerSupportBotTierError(
                "Ticket escalation is not available on the Free tier. "
                "Please upgrade to PRO or ENTERPRISE to access this feature."
            )

        assigned_to = "support_team" if self.tier == Tier.PRO else "dedicated_agent"

        return {
            "ticket_id": ticket_id,
            "escalated": True,
            "assigned_to": assigned_to,
            "tier": self.tier.value,
        }

    def get_stats(self) -> dict:
        return {
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
            "buddy_integration": True,
        }
