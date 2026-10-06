"""Lookup for the production checklist. It returns names and links, never values."""

from __future__ import annotations

import json

ITEMS = [
    {"name": "DATABASE_URL", "where": "https://github.com/DreamCo-Technologies/Dreamcobots/settings/secrets/actions"},
    {"name": "STRIPE_LIVE_SECRET_KEY", "where": "https://dashboard.stripe.com/apikeys"},
    {"name": "STRIPE_LIVE_PK", "where": "https://dashboard.stripe.com/apikeys"},
    {"name": "STRIPE_WEBHOOK_SECRET", "where": "https://dashboard.stripe.com/webhooks"},
    {"name": "OWNER_BILLING_TOKEN", "where": "https://github.com/DreamCo-Technologies/Dreamcobots/settings/secrets/actions"},
    {"name": "OWNER_SECRET_KEY", "where": "https://github.com/DreamCo-Technologies/Dreamcobots/settings/secrets/actions"},
]


def lookup() -> dict:
    return {"paste_values": "https://github.com/DreamCo-Technologies/Dreamcobots/settings/secrets/actions", "items": ITEMS, "values_included": False}


if __name__ == "__main__":
    print(json.dumps(lookup()))
