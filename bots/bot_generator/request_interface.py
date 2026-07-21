"""
Auto-Bot Factory — Request Interface Module

Accepts and validates bot creation requests from admins or clients.
Input includes category, purpose, features, and target audience.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class BotRequest:
    """Structured representation of a bot creation request."""

    category: str
    purpose: str
    features: List[str]
    target_audience: str = "general"
    bot_name: Optional[str] = None
    pricing_model: str = "subscription"
    priority: str = "standard"

    def __post_init__(self) -> None:
        if not self.category:
            raise ValueError("category must not be empty")
        if not self.purpose:
            raise ValueError("purpose must not be empty")
        if not isinstance(self.features, list):
            raise TypeError("features must be a list")
        if self.bot_name is None:
            slug = self.category.lower().replace(" ", "_")
            self.bot_name = f"{slug}_bot"

    def to_dict(self) -> dict:
        """Return a JSON-serialisable representation."""
        return {
            "category": self.category,
            "purpose": self.purpose,
            "features": self.features,
            "target_audience": self.target_audience,
            "bot_name": self.bot_name,
            "pricing_model": self.pricing_model,
            "priority": self.priority,
        }


# ---------------------------------------------------------------------------
# Request Interface
# ---------------------------------------------------------------------------

class RequestInterfaceError(Exception):
    """Raised when a bot request is invalid."""


class RequestInterface:
    """
    DreamCo Auto-Bot Factory — Request Interface.

    Accepts input (bot category, purpose, features, target audience) and
    converts it into a validated :class:`BotRequest` ready for the
    Auto-Bot Factory pipeline.

    Usage::

        interface = RequestInterface()
        req = interface.submit(
            category="Lead Generation",
            purpose="Capture and qualify real-estate leads",
            features=["SMS outreach", "CRM sync", "follow-up automation"],
            target_audience="Real estate agents",
        )
        print(req.bot_name)
    """

    VALID_PRICING_MODELS = ("free", "subscription", "usage_based", "one_time")
    VALID_PRIORITIES = ("low", "standard", "high", "urgent")

    # 200-strategy categories supported by the factory
    SUPPORTED_CATEGORIES = [
        "Lead Generation",
        "Sales Automation",
        "Customer Support",
        "Data Scraping",
        "Revenue Optimization",
        "Marketing",
        "Analytics",
        "Content Creation",
        "E-Commerce",
        "Real Estate",
        "Healthcare",
        "Finance",
        "Legal",
        "Education",
        "Logistics",
        "HR & Recruiting",
        "Social Media",
        "SEO",
        "Email Outreach",
        "Competitor Monitoring",
    ]

    def __init__(self) -> None:
        self._requests: List[BotRequest] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit(
        self,
        category: str,
        purpose: str,
        features: List[str],
        target_audience: str = "general",
        bot_name: Optional[str] = None,
        pricing_model: str = "subscription",
        priority: str = "standard",
    ) -> BotRequest:
        """
        Validate and queue a new bot creation request.

        Parameters
        ----------
        category : str
            High-level category (e.g. "Lead Generation", "Sales Automation").
        purpose : str
            Human-readable description of what the bot should do.
        features : list[str]
            Desired feature list (will be optimized by FeatureOptimizer).
        target_audience : str
            Who the bot is built for (e.g. "Real estate agents").
        bot_name : str, optional
            Override the auto-generated bot name.
        pricing_model : str
            Monetisation model: "free", "subscription", "usage_based", "one_time".
        priority : str
            Build priority: "low", "standard", "high", "urgent".

        Returns
        -------
        BotRequest
            Validated and queued request.
        """
        self._validate(category, features, pricing_model, priority)

        req = BotRequest(
            category=category,
            purpose=purpose,
            features=list(features),
            target_audience=target_audience,
            bot_name=bot_name,
            pricing_model=pricing_model,
            priority=priority,
        )
        self._requests.append(req)
        return req

    def list_requests(self) -> List[BotRequest]:
        """Return all submitted requests."""
        return list(self._requests)

    def list_categories(self) -> List[str]:
        """Return the supported bot categories."""
        return list(self.SUPPORTED_CATEGORIES)

    def get_summary(self) -> dict:
        """Return a summary of queued requests."""
        return {
            "total_requests": len(self._requests),
            "categories": list({r.category for r in self._requests}),
            "priorities": {
                p: sum(1 for r in self._requests if r.priority == p)
                for p in self.VALID_PRIORITIES
            },
        }

    def run(self) -> str:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        summary = self.get_summary()
        return (
            f"RequestInterface active — {summary['total_requests']} request(s) queued."
        )

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _validate(
        self,
        category: str,
        features: List[str],
        pricing_model: str,
        priority: str,
    ) -> None:
        if not category.strip():
            raise RequestInterfaceError("category must not be empty")
        if not isinstance(features, list) or len(features) == 0:
            raise RequestInterfaceError("features must be a non-empty list")
        if pricing_model not in self.VALID_PRICING_MODELS:
            raise RequestInterfaceError(
                f"Invalid pricing_model '{pricing_model}'. "
                f"Choose from: {self.VALID_PRICING_MODELS}"
            )
        if priority not in self.VALID_PRIORITIES:
            raise RequestInterfaceError(
                f"Invalid priority '{priority}'. "
                f"Choose from: {self.VALID_PRIORITIES}"
            )
