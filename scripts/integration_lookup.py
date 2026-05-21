"""
integration_lookup.py – Local integration-opportunity search for DreamCobots.

Searches the built-in integration registry (no external API required) and
appends matching opportunities to ``data/integration_lookup.json``.

Usage
-----
    python scripts/integration_lookup.py "automation reliability tooling"

The script exits 0 whether or not matches are found so that the GitHub
Actions workflow always succeeds.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Built-in integration registry
# ---------------------------------------------------------------------------
# Keeps the lookup fully offline and dependency-free.  New entries can be
# added at any time — simply append to this list.

_REGISTRY: List[Dict[str, Any]] = [
    {
        "id": "stripe",
        "name": "Stripe",
        "category": "payments",
        "tags": ["payments", "billing", "subscriptions", "saas"],
        "description": "Payment processing platform for online businesses.",
        "docs_url": "https://stripe.com/docs",
        "status": "stable",
    },
    {
        "id": "openai",
        "name": "OpenAI",
        "category": "ai",
        "tags": ["ai", "llm", "gpt", "automation", "intelligence"],
        "description": "AI models for text, image, and code generation.",
        "docs_url": "https://platform.openai.com/docs",
        "status": "stable",
    },
    {
        "id": "zapier",
        "name": "Zapier",
        "category": "automation",
        "tags": ["automation", "workflow", "integration", "no-code", "reliability", "tooling"],
        "description": "No-code automation connecting 6000+ apps.",
        "docs_url": "https://zapier.com/apps",
        "status": "stable",
    },
    {
        "id": "make",
        "name": "Make (Integromat)",
        "category": "automation",
        "tags": ["automation", "workflow", "integration", "tooling"],
        "description": "Visual automation platform for complex workflows.",
        "docs_url": "https://www.make.com/en/help",
        "status": "stable",
    },
    {
        "id": "github_actions",
        "name": "GitHub Actions",
        "category": "ci_cd",
        "tags": ["ci", "cd", "automation", "reliability", "tooling", "monitoring"],
        "description": "Automation platform built into GitHub for CI/CD.",
        "docs_url": "https://docs.github.com/en/actions",
        "status": "stable",
    },
    {
        "id": "prometheus",
        "name": "Prometheus",
        "category": "monitoring",
        "tags": ["monitoring", "metrics", "observability", "reliability", "alerting"],
        "description": "Open-source monitoring and alerting toolkit.",
        "docs_url": "https://prometheus.io/docs",
        "status": "stable",
    },
    {
        "id": "grafana",
        "name": "Grafana",
        "category": "observability",
        "tags": ["dashboards", "monitoring", "observability", "metrics", "reliability"],
        "description": "Open-source analytics and monitoring platform.",
        "docs_url": "https://grafana.com/docs",
        "status": "stable",
    },
    {
        "id": "slack",
        "name": "Slack",
        "category": "communication",
        "tags": ["notifications", "alerts", "communication", "webhooks"],
        "description": "Business messaging and workflow automation platform.",
        "docs_url": "https://api.slack.com",
        "status": "stable",
    },
    {
        "id": "sendgrid",
        "name": "SendGrid",
        "category": "email",
        "tags": ["email", "marketing", "notifications", "saas"],
        "description": "Cloud-based email delivery and marketing platform.",
        "docs_url": "https://docs.sendgrid.com",
        "status": "stable",
    },
    {
        "id": "twilio",
        "name": "Twilio",
        "category": "communication",
        "tags": ["sms", "voice", "communication", "notifications", "saas"],
        "description": "Cloud communications APIs for SMS, voice and messaging.",
        "docs_url": "https://www.twilio.com/docs",
        "status": "stable",
    },
    {
        "id": "hubspot",
        "name": "HubSpot",
        "category": "crm",
        "tags": ["crm", "sales", "marketing", "automation"],
        "description": "CRM platform with marketing, sales and service tools.",
        "docs_url": "https://developers.hubspot.com/docs",
        "status": "stable",
    },
    {
        "id": "airtable",
        "name": "Airtable",
        "category": "database",
        "tags": ["database", "spreadsheet", "automation", "no-code"],
        "description": "Relational database with a spreadsheet interface.",
        "docs_url": "https://airtable.com/developers/web/api",
        "status": "stable",
    },
]


# ---------------------------------------------------------------------------
# Search helpers
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> List[str]:
    """Return lowercase tokens from *text*."""
    return [w.strip().lower() for w in text.replace(",", " ").split() if w.strip()]


def search_registry(query: str, registry: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Return registry entries whose tags or name/description match *query*.

    Scoring:
    - +2 for each query token found in the entry's tags
    - +1 for each query token found in name or description (case-insensitive)

    Entries with score == 0 are excluded.  Results are sorted by score desc.
    """
    if registry is None:
        registry = _REGISTRY

    tokens = _tokenize(query)
    if not tokens:
        return list(registry)

    scored: List[tuple[int, Dict[str, Any]]] = []
    for entry in registry:
        score = 0
        entry_tags = [t.lower() for t in entry.get("tags", [])]
        name_desc = (entry.get("name", "") + " " + entry.get("description", "")).lower()
        for token in tokens:
            if token in entry_tags:
                score += 2
            elif token in name_desc:
                score += 1
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored]


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

_DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "integration_lookup.json"
)


def _load_store(path: str) -> Dict[str, Any]:
    """Load existing lookup store, returning an empty store on any error."""
    if not os.path.exists(path):
        return {"last_updated": None, "total_queries": 0, "queries": {}}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read %s (%s) — starting fresh.", path, exc)
        return {"last_updated": None, "total_queries": 0, "queries": {}}


def save_integration_results(
    query: str,
    results: List[Dict[str, Any]],
    data_path: str = _DEFAULT_DATA_PATH,
) -> None:
    """Append *results* for *query* to the persistent lookup store."""
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    store = _load_store(data_path)
    store["queries"][query] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "result_count": len(results),
        "results": results,
    }
    store["total_queries"] = len(store["queries"])
    store["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(data_path, "w", encoding="utf-8") as fh:
        json.dump(store, fh, indent=2)
    logger.info("Saved %d result(s) for query %r → %s", len(results), query, data_path)


# ---------------------------------------------------------------------------
# Retry helper (kept for any future live-API extension)
# ---------------------------------------------------------------------------

def with_retry(fn, retries: int = 3, backoff: float = 2.0):
    """
    Execute *fn()* up to *retries* times with exponential backoff.

    Returns the result of the first successful call, or raises the last
    exception if all attempts fail.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < retries:
                wait = backoff ** (attempt - 1)
                logger.warning(
                    "Attempt %d/%d failed (%s). Retrying in %.1fs…",
                    attempt, retries, exc, wait,
                )
                time.sleep(wait)
            else:
                logger.error(
                    "All %d attempts failed. Last error: %s",
                    retries, exc,
                )
    raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def fetch_integration_opportunities(query: str) -> List[Dict[str, Any]]:
    """
    Search the local registry for *query* and return matching opportunities.

    This function is fully offline — no external API calls are made.
    """
    results = search_registry(query)
    if results:
        logger.info("Found %d integration opportunity/ies for %r.", len(results), query)
    else:
        logger.info("No matches found for %r — returning full registry.", query)
        results = list(_REGISTRY)
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "automation"
    logger.info("Fetching integration opportunities for: %s", query)

    opportunities = fetch_integration_opportunities(query)
    save_integration_results(query, opportunities)

    if opportunities:
        logger.info("Integration opportunities saved for %r", query)
        for opp in opportunities:
            print(f"  • {opp['name']} ({opp['category']}): {opp['description']}")
    else:
        logger.info("No results found.")