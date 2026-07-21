"""
Dreamcobots LeadGenerationBot — tier-aware lead capture and scoring.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.lead_generation_bot.tiers import LEAD_GENERATION_FEATURES, get_lead_generation_tier_info
import uuid
from datetime import datetime


class LeadGenerationBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class LeadGenerationBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class LeadGenerationBot:
    """Tier-aware lead capture and scoring bot."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._leads: dict = {}

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise LeadGenerationBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_feature(self, feature: str) -> None:
        features = LEAD_GENERATION_FEATURES[self.tier.value]
        if not any(feature.lower() in f.lower() for f in features):
            raise LeadGenerationBotTierError(
                f"'{feature}' is not available on the {self.config.name} tier. "
                f"Please upgrade to access this feature."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    def _score_by_domain(self, email: str, source: str = "") -> float:
        """Score a lead based on email domain and source."""
        domain = email.split("@")[-1].split(".")[-1].lower() if "@" in email else ""
        domain_scores = {
            "edu": 0.3,
            "gov": 0.4,
            "com": 0.7,
            "io": 0.8,
        }
        score = domain_scores.get(domain, 0.5)
        if source and source.lower() in ["referral", "partner"]:
            score = min(score + 0.1, 1.0)
        return round(score, 2)

    def capture_lead(self, lead: dict) -> dict:
        """
        Capture and score a new lead.

        Args:
            lead: {"name": str, "email": str, "source": str optional}

        Returns:
            {"lead_id": str, "name": str, "email": str, "score": float, "tier": str}
        """
        self._check_request_limit()
        self._request_count += 1

        lead_id = str(uuid.uuid4())
        name = lead.get("name", "")
        email = lead.get("email", "")
        source = lead.get("source", "")

        if self.tier == Tier.FREE:
            score = 0.5
        elif self.tier == Tier.PRO:
            score = self._score_by_domain(email, source)
        else:  # ENTERPRISE
            score = min(self._score_by_domain(email, source) + 0.1, 1.0)

        result = {
            "lead_id": lead_id,
            "name": name,
            "email": email,
            "score": score,
            "tier": self.tier.value,
        }
        self._leads[lead_id] = result
        return result

    def score_lead(self, lead_id: str) -> dict:
        """
        Re-score an existing lead.

        Args:
            lead_id: The lead identifier.

        Returns:
            {"lead_id": str, "score": float, "tier": str}
        """
        if self.tier == Tier.FREE:
            raise LeadGenerationBotTierError(
                "Lead re-scoring is not available on the Free tier. "
                "Please upgrade to PRO or ENTERPRISE."
            )

        lead = self._leads.get(lead_id)
        score = lead["score"] if lead else 0.5

        return {
            "lead_id": lead_id,
            "score": score,
            "tier": self.tier.value,
        }

    def export_leads(self, format: str = "csv") -> dict:
        """
        Export captured leads in the specified format.

        Args:
            format: "csv", "json", or "xml" (availability depends on tier)

        Returns:
            {"format": str, "count": int, "data": list, "tier": str}
        """
        allowed_formats = {"free": ["csv"], "pro": ["csv", "json"], "enterprise": ["csv", "json", "xml"]}
        available = allowed_formats[self.tier.value]

        if format.lower() not in available:
            raise LeadGenerationBotTierError(
                f"Export format '{format}' is not available on the {self.config.name} tier. "
                f"Available formats: {available}. Please upgrade to access more formats."
            )

        data = list(self._leads.values())
        return {
            "format": format.lower(),
            "count": len(data),
            "data": data,
            "tier": self.tier.value,
        }

    def get_stats(self) -> dict:
        return {
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
            "leads_captured": len(self._leads),
            "buddy_integration": True,
        }
