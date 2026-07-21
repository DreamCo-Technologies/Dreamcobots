"""
Integration Hub — Fortune 500 partner integrations for the DreamCo Bot
Marketplace.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import hashlib
import random
import uuid
from datetime import datetime, timezone
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401

INTEGRATION_PARTNERS = [
    "SALESFORCE",
    "SAP",
    "ORACLE",
    "MICROSOFT_365",
    "GOOGLE_WORKSPACE",
    "SLACK",
    "JIRA",
    "ZENDESK",
    "HUBSPOT",
    "WORKDAY",
    "SERVICENOW",
    "TABLEAU",
]

_WEBHOOK_BASE = "https://hooks.botmarketplace.dreamco.ai/webhook"


class IntegrationHub:
    """Manages Fortune 500 partner integrations for bot listings."""

    def __init__(self) -> None:
        self._integrations: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_integration(
        self,
        listing_id: str,
        partner: str,
        config: Optional[dict] = None,
    ) -> dict:
        """Register a new integration between a listing and a partner."""
        if partner not in INTEGRATION_PARTNERS:
            raise ValueError(
                f"Unknown partner '{partner}'. Must be one of {INTEGRATION_PARTNERS}."
            )
        integration_id = str(uuid.uuid4())
        integration = {
            "integration_id": integration_id,
            "listing_id": listing_id,
            "partner": partner,
            "config": config or {},
            "status": "REGISTERED",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._integrations[integration_id] = integration
        return integration

    def get_integration(self, integration_id: str) -> dict:
        """Return a single integration by ID."""
        return self._get_or_raise(integration_id)

    def list_integrations(self, listing_id: Optional[str] = None) -> list:
        """Return all integrations, optionally filtered by listing_id."""
        integrations = list(self._integrations.values())
        if listing_id is not None:
            integrations = [i for i in integrations if i["listing_id"] == listing_id]
        return integrations

    # ------------------------------------------------------------------
    # Testing & webhooks
    # ------------------------------------------------------------------

    def test_integration(self, integration_id: str) -> dict:
        """Simulate a connectivity test for the integration."""
        self._get_or_raise(integration_id)
        # Deterministic simulation: always CONNECTED in test context
        latency_ms = random.randint(12, 80)
        result = {
            "integration_id": integration_id,
            "status": "CONNECTED",
            "latency_ms": latency_ms,
            "message": "Integration endpoint reachable.",
            "tested_at": datetime.now(timezone.utc).isoformat(),
        }
        self._integrations[integration_id]["last_test"] = result
        return result

    def generate_integration_webhook(self, integration_id: str) -> dict:
        """Generate a webhook URL and secret token for the integration."""
        integration = self._get_or_raise(integration_id)
        secret_token = hashlib.sha256(
            (integration_id + integration["partner"]).encode()
        ).hexdigest()
        webhook_url = f"{_WEBHOOK_BASE}/{integration_id}"
        events = [
            "bot.purchased",
            "bot.rated",
            "bot.updated",
            "upsell.purchased",
        ]
        webhook = {
            "integration_id": integration_id,
            "webhook_url": webhook_url,
            "secret_token": secret_token,
            "events": events,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._integrations[integration_id]["webhook"] = webhook
        return webhook

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_or_raise(self, integration_id: str) -> dict:
        if integration_id not in self._integrations:
            raise KeyError(f"Integration '{integration_id}' not found.")
        return self._integrations[integration_id]
