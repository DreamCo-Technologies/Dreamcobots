"""
DreamCo Lead Generation Bot
============================

Generates and stores industry-specific business leads, feeding the
downstream Sales Bot and other monetisation bots in the DreamCo network.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import random
import re
import sys
import io
import csv
from datetime import datetime, timezone
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

# ---------------------------------------------------------------------------
# Default data file (relative to repo root)
# ---------------------------------------------------------------------------
_DEFAULT_LEADS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "leads.txt"
)

INDUSTRIES = [
    "real estate",
    "roofing",
    "plumbing",
    "barbershops",
    "landscaping",
    "HVAC",
    "electricians",
    "restaurants",
    "retail",
    "dental offices",
]


class Bot:
    """
    Lead Generation Bot.

    Generates simulated business leads and persists them to disk so that
    the Sales Bot and other downstream bots can act on them.
    Replace ``generate_leads()`` internals with real scraping / API calls
    for production use.
    """

    def __init__(self, leads_file: str = _DEFAULT_LEADS_FILE) -> None:
        self.name = "Lead Generator Bot"
        self.leads_file = leads_file
        self._total_generated: int = 0
        os.makedirs(os.path.dirname(os.path.abspath(self.leads_file)), exist_ok=True)

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Generate a batch of leads and persist them."""
        leads = self.generate_leads()
        self.save_leads(leads)
        self._total_generated += len(leads)
        return f"Generated {len(leads)} leads (total: {self._total_generated})"

    def generate_leads(self, count: int | None = None) -> List[Dict]:
        """
        Produce a batch of placeholder leads.

        Parameters
        ----------
        count : int, optional
            Number of leads to generate.  Defaults to a random value
            between 2 and 5.
        """
        if count is None:
            count = random.randint(2, 5)

        leads: List[Dict] = []
        for i in range(count):
            industry = random.choice(INDUSTRIES)
            leads.append({
                "business": f"{industry.title()} Business #{i + 1}",
                "industry": industry,
                "phone": f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "email": f"contact{random.randint(1, 9999)}@{industry.replace(' ', '')}.example.com",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            })
        return leads

    def save_leads(self, leads: List[Dict]) -> None:
        """Append *leads* to the persistent leads file."""
        with open(self.leads_file, "a", encoding="utf-8") as fh:
            for lead in leads:
                fh.write(str(lead) + "\n")

    # ------------------------------------------------------------------
    # Status / reporting
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Return current bot status."""
        return {
            "name": self.name,
            "total_generated": self._total_generated,
            "leads_file": self.leads_file,
            "status": "active",
        }


class LeadGenBot:
    """Compatibility adapter used by backend FastAPI endpoints."""

    def __init__(
        self,
        db_dsn: str | None = None,
        revenue_engine=None,
        monetization_hooks=None,
        dream_core=None,
    ) -> None:
        self.db_dsn = db_dsn
        self.revenue_engine = revenue_engine
        self.monetization_hooks = monetization_hooks
        self.dream_core = dream_core
        self._html_sources: list[str] = []
        self._leads: list[dict] = []
        self._outreach_emails: list[str] = []

    def add_html_source(self, html: str) -> None:
        if html:
            self._html_sources.append(html)

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None

    def scrape_html(self, html: str) -> list[dict]:
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", html or "")
        url_match = re.search(r"https?://[^\s\"']+", html or "")
        name_match = re.search(r'name:\s*"([^"]+)"', html or "", re.IGNORECASE)
        company_match = re.search(r"company:\s*([^\n<]+)", html or "", re.IGNORECASE)

        lead = {
            "name": (name_match.group(1).strip() if name_match else "Unknown Lead"),
            "email": (email_match.group(0).strip() if email_match else ""),
            "phone": "",
            "company": (company_match.group(1).strip() if company_match else ""),
            "url": (url_match.group(0).strip() if url_match else ""),
        }
        return [lead]

    def add_lead(self, lead: dict) -> None:
        if lead:
            self._leads.append(lead)

    def run(self) -> None:
        for html in self._html_sources:
            leads = self.scrape_html(html)
            for lead in leads:
                self.add_lead(lead)
                email = lead.get("email")
                if email:
                    self._outreach_emails.append(f"Hello {lead.get('name', '')} <{email}>")
        if self.revenue_engine and hasattr(self.revenue_engine, "record"):
            self.revenue_engine.record("lead_gen_bot", max(len(self._leads), 1) * 5.0)

    def get_leads(self) -> list[dict]:
        return list(self._leads)

    def get_outreach_emails(self) -> list[str]:
        return list(self._outreach_emails)

    def export_csv(self) -> str:
        rows = self._leads or []
        fields = ["name", "email", "phone", "company", "url"]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})
        return output.getvalue()
