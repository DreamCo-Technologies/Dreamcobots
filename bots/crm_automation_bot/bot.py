"""
Dreamcobots CRMAutomationBot — tier-aware CRM contact management and pipeline automation.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.crm_automation_bot.tiers import CRM_AUTOMATION_FEATURES, get_crm_automation_tier_info
import uuid
from datetime import datetime


class CRMAutomationBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class CRMAutomationBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class CRMAutomationBot:
    """Tier-aware CRM contact management and pipeline automation bot."""

    FREE_STAGES = ["lead", "prospect", "customer"]
    FULL_STAGES = ["lead", "prospect", "qualified", "proposal", "negotiation", "customer", "churned"]

    CONTACT_LIMITS = {
        "free": 100,
        "pro": 10000,
        "enterprise": None,
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._contacts: dict = {}
        self._contact_count: int = 0

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise CRMAutomationBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_contact_limit(self) -> None:
        limit = self.CONTACT_LIMITS[self.tier.value]
        if limit is not None and self._contact_count >= limit:
            raise CRMAutomationBotTierError(
                f"Contact limit of {limit:,} reached on the {self.config.name} tier. "
                "Please upgrade to add more contacts."
            )

    def _check_feature(self, feature: str) -> None:
        features = CRM_AUTOMATION_FEATURES[self.tier.value]
        if not any(feature.lower() in f.lower() for f in features):
            raise CRMAutomationBotTierError(
                f"'{feature}' is not available on the {self.config.name} tier. "
                f"Please upgrade to access this feature."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    def add_contact(self, contact: dict) -> dict:
        """
        Add a new contact to the CRM.

        Args:
            contact: {"name": str, "email": str, "company": str optional}

        Returns:
            {"contact_id": str, "name": str, "email": str, "pipeline_stage": str, "tier": str}
        """
        self._check_request_limit()
        self._check_contact_limit()
        self._request_count += 1

        contact_id = str(uuid.uuid4())
        name = contact.get("name", "")
        email = contact.get("email", "")
        company = contact.get("company", "")

        record = {
            "contact_id": contact_id,
            "name": name,
            "email": email,
            "company": company,
            "pipeline_stage": "lead",
            "tier": self.tier.value,
        }
        self._contacts[contact_id] = record
        self._contact_count += 1

        return {
            "contact_id": contact_id,
            "name": name,
            "email": email,
            "pipeline_stage": "lead",
            "tier": self.tier.value,
        }

    def update_pipeline(self, contact_id: str, stage: str) -> dict:
        """
        Move a contact to a new pipeline stage.

        Args:
            contact_id: The contact identifier.
            stage: Target pipeline stage.

        Returns:
            {"contact_id": str, "previous_stage": str, "new_stage": str, "tier": str}
        """
        allowed_stages = self.FREE_STAGES if self.tier == Tier.FREE else self.FULL_STAGES

        if stage not in allowed_stages:
            raise CRMAutomationBotTierError(
                f"Pipeline stage '{stage}' is not available on the {self.config.name} tier. "
                f"Available stages: {allowed_stages}. Please upgrade for full pipeline access."
            )

        contact = self._contacts.get(contact_id, {})
        previous_stage = contact.get("pipeline_stage", "lead")

        if contact_id in self._contacts:
            self._contacts[contact_id]["pipeline_stage"] = stage

        return {
            "contact_id": contact_id,
            "previous_stage": previous_stage,
            "new_stage": stage,
            "tier": self.tier.value,
        }

    def get_pipeline_stats(self) -> dict:
        """
        Get statistics about the current pipeline.

        Returns:
            {"total_contacts": int, "stages": dict, "tier": str, "buddy_integration": True}
        """
        stages: dict = {}
        for contact in self._contacts.values():
            stage = contact.get("pipeline_stage", "lead")
            stages[stage] = stages.get(stage, 0) + 1

        return {
            "total_contacts": self._contact_count,
            "stages": stages,
            "tier": self.tier.value,
            "buddy_integration": True,
        }

    def get_stats(self) -> dict:
        return {
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
            "contact_count": self._contact_count,
            "buddy_integration": True,
        }
