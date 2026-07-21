"""
Feature 3: Business Invoicing Bot
Functionality: Generates, sends, and tracks invoices for clients. Includes
  tax calculation, payment status tracking, and overdue reminders.
Use Cases: Freelancers and businesses needing to bill their clients.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example invoice records
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": "INV-001", "client": "Acme Corp",          "service": "Website Redesign",         "amount": 5000,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-15", "paid_date": "2025-04-12", "currency": "USD"},
    {"id": "INV-002", "client": "Beta Tech",           "service": "Mobile App Development",   "amount": 12000, "tax_rate": 0.08, "status": "pending", "due_date": "2025-05-15", "paid_date": None,         "currency": "USD"},
    {"id": "INV-003", "client": "Gamma LLC",           "service": "SEO Consulting",            "amount": 2500,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-20", "paid_date": "2025-04-18", "currency": "USD"},
    {"id": "INV-004", "client": "Delta Startup",       "service": "UI/UX Design Package",     "amount": 3500,  "tax_rate": 0.08, "status": "overdue", "due_date": "2025-04-01", "paid_date": None,         "currency": "USD"},
    {"id": "INV-005", "client": "Epsilon Media",       "service": "Content Marketing Package","amount": 1800,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-10", "paid_date": "2025-04-08", "currency": "USD"},
    {"id": "INV-006", "client": "Zeta Foods",          "service": "Social Media Management",  "amount": 900,   "tax_rate": 0.08, "status": "pending", "due_date": "2025-05-20", "paid_date": None,         "currency": "USD"},
    {"id": "INV-007", "client": "Eta Consulting",      "service": "Strategy Workshop",        "amount": 4000,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-05", "paid_date": "2025-04-03", "currency": "USD"},
    {"id": "INV-008", "client": "Theta Analytics",     "service": "Data Dashboard Build",     "amount": 7500,  "tax_rate": 0.08, "status": "partial", "due_date": "2025-05-10", "paid_date": None,         "currency": "USD"},
    {"id": "INV-009", "client": "Iota E-commerce",     "service": "Shopify Store Setup",      "amount": 2200,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-25", "paid_date": "2025-04-24", "currency": "USD"},
    {"id": "INV-010", "client": "Kappa Financial",     "service": "Financial Reporting",      "amount": 3000,  "tax_rate": 0.08, "status": "overdue", "due_date": "2025-03-31", "paid_date": None,         "currency": "USD"},
    {"id": "INV-011", "client": "Lambda SaaS",         "service": "API Integration",          "amount": 6500,  "tax_rate": 0.08, "status": "pending", "due_date": "2025-05-25", "paid_date": None,         "currency": "USD"},
    {"id": "INV-012", "client": "Mu Logistics",        "service": "Automation Setup",         "amount": 4500,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-18", "paid_date": "2025-04-17", "currency": "USD"},
    {"id": "INV-013", "client": "Nu Healthcare",       "service": "HIPAA Compliance Audit",   "amount": 8000,  "tax_rate": 0.08, "status": "pending", "due_date": "2025-06-01", "paid_date": None,         "currency": "USD"},
    {"id": "INV-014", "client": "Xi Real Estate",      "service": "Property Listing Bot",     "amount": 3200,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-22", "paid_date": "2025-04-21", "currency": "USD"},
    {"id": "INV-015", "client": "Omicron AI",          "service": "AI Model Fine-tuning",     "amount": 15000, "tax_rate": 0.08, "status": "partial", "due_date": "2025-05-15", "paid_date": None,         "currency": "USD"},
    {"id": "INV-016", "client": "Pi Retail",           "service": "Email Marketing Setup",    "amount": 1500,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-12", "paid_date": "2025-04-10", "currency": "USD"},
    {"id": "INV-017", "client": "Rho Education",       "service": "LMS Development",          "amount": 9500,  "tax_rate": 0.08, "status": "overdue", "due_date": "2025-04-05", "paid_date": None,         "currency": "USD"},
    {"id": "INV-018", "client": "Sigma Fitness",       "service": "App Development",          "amount": 5500,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-28", "paid_date": "2025-04-26", "currency": "USD"},
    {"id": "INV-019", "client": "Tau Manufacturing",   "service": "ERP Integration",          "amount": 18000, "tax_rate": 0.08, "status": "pending", "due_date": "2025-06-15", "paid_date": None,         "currency": "USD"},
    {"id": "INV-020", "client": "Upsilon Travel",      "service": "Booking Engine Build",     "amount": 6000,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-30", "paid_date": "2025-04-29", "currency": "USD"},
    {"id": "INV-021", "client": "Phi Legal",           "service": "Document Automation",      "amount": 4800,  "tax_rate": 0.08, "status": "pending", "due_date": "2025-05-30", "paid_date": None,         "currency": "USD"},
    {"id": "INV-022", "client": "Chi Media",           "service": "Video Production",         "amount": 7200,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-20", "paid_date": "2025-04-19", "currency": "USD"},
    {"id": "INV-023", "client": "Psi Security",        "service": "Penetration Testing",      "amount": 11000, "tax_rate": 0.08, "status": "overdue", "due_date": "2025-04-10", "paid_date": None,         "currency": "USD"},
    {"id": "INV-024", "client": "Omega Events",        "service": "Event Website Development","amount": 2800,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-16", "paid_date": "2025-04-14", "currency": "USD"},
    {"id": "INV-025", "client": "Alpha Prime",         "service": "CRM Implementation",       "amount": 9000,  "tax_rate": 0.08, "status": "partial", "due_date": "2025-05-20", "paid_date": None,         "currency": "USD"},
    {"id": "INV-026", "client": "Beta Prime",          "service": "Cloud Migration",          "amount": 22000, "tax_rate": 0.08, "status": "pending", "due_date": "2025-07-01", "paid_date": None,         "currency": "USD"},
    {"id": "INV-027", "client": "Gamma Prime",         "service": "Brand Strategy",           "amount": 3800,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-24", "paid_date": "2025-04-23", "currency": "USD"},
    {"id": "INV-028", "client": "Delta Prime",         "service": "DevOps Setup",             "amount": 5200,  "tax_rate": 0.08, "status": "pending", "due_date": "2025-05-28", "paid_date": None,         "currency": "USD"},
    {"id": "INV-029", "client": "Epsilon Prime",       "service": "AI Consulting",            "amount": 13500, "tax_rate": 0.08, "status": "overdue", "due_date": "2025-04-08", "paid_date": None,         "currency": "USD"},
    {"id": "INV-030", "client": "Zeta Prime",          "service": "Full Stack Development",   "amount": 8500,  "tax_rate": 0.08, "status": "paid",    "due_date": "2025-04-26", "paid_date": "2025-04-25", "currency": "USD"},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_invoices": 5,    "tax_calc": False, "overdue_alerts": False, "pdf_export": False},
    "PRO":        {"price_usd": 29,  "max_invoices": 100,  "tax_calc": True,  "overdue_alerts": True,  "pdf_export": False},
    "ENTERPRISE": {"price_usd": 99,  "max_invoices": None, "tax_calc": True,  "overdue_alerts": True,  "pdf_export": True},
}


class InvoicingBot:
    """Generates, tracks, and manages invoices with tax calculation and alerts.

    Competes with FreshBooks and Wave by providing automated overdue reminders,
    tax calculation, and multi-currency invoice generation.
    Monetization: $29/month PRO or $99/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="InvoicingBot")

    def _available_invoices(self) -> list[dict]:
        limit = self._config["max_invoices"]
        return EXAMPLES[:limit] if limit else EXAMPLES

    def get_invoice(self, invoice_id: str) -> dict:
        """Retrieve a specific invoice by ID."""
        invoice = next((i for i in EXAMPLES if i["id"] == invoice_id), None)
        if invoice is None:
            raise ValueError(f"Invoice '{invoice_id}' not found.")
        result = dict(invoice)
        if self._config["tax_calc"]:
            result["tax_amount"] = round(invoice["amount"] * invoice["tax_rate"], 2)
            result["total_with_tax"] = round(invoice["amount"] * (1 + invoice["tax_rate"]), 2)
        return result

    def get_invoices_by_status(self, status: str) -> list[dict]:
        """Return invoices filtered by status."""
        valid = {"paid", "pending", "overdue", "partial"}
        if status not in valid:
            raise ValueError(f"Invalid status. Choose from {valid}")
        return [i for i in self._available_invoices() if i["status"] == status]

    def get_overdue_invoices(self) -> list[dict]:
        """Return all overdue invoices."""
        return self.get_invoices_by_status("overdue")

    def send_overdue_reminder(self, invoice_id: str) -> dict:
        """Send an overdue payment reminder (PRO/ENTERPRISE)."""
        if not self._config["overdue_alerts"]:
            raise PermissionError(
                "Overdue alerts require PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        invoice = next((i for i in EXAMPLES if i["id"] == invoice_id), None)
        if invoice is None:
            raise ValueError(f"Invoice '{invoice_id}' not found.")
        if invoice["status"] != "overdue":
            return {"sent": False, "reason": f"Invoice is not overdue (status: {invoice['status']})"}
        message = (
            f"Dear {invoice['client']}, this is a reminder that invoice {invoice_id} "
            f"for {invoice['service']} (${invoice['amount']:,.2f}) was due on "
            f"{invoice['due_date']}. Please process payment at your earliest convenience."
        )
        return {"sent": True, "invoice_id": invoice_id, "client": invoice["client"], "message": message}

    def calculate_tax(self, invoice_id: str) -> dict:
        """Calculate tax for an invoice (PRO/ENTERPRISE)."""
        if not self._config["tax_calc"]:
            raise PermissionError(
                "Tax calculation requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        invoice = next((i for i in EXAMPLES if i["id"] == invoice_id), None)
        if invoice is None:
            raise ValueError(f"Invoice '{invoice_id}' not found.")
        tax_amount = round(invoice["amount"] * invoice["tax_rate"], 2)
        total = round(invoice["amount"] + tax_amount, 2)
        return {
            "invoice_id": invoice_id,
            "subtotal": invoice["amount"],
            "tax_rate_pct": invoice["tax_rate"] * 100,
            "tax_amount": tax_amount,
            "total": total,
        }

    def get_revenue_summary(self) -> dict:
        """Return total revenue, outstanding, and overdue amounts."""
        invoices = self._available_invoices()
        paid = sum(i["amount"] for i in invoices if i["status"] == "paid")
        pending = sum(i["amount"] for i in invoices if i["status"] == "pending")
        overdue = sum(i["amount"] for i in invoices if i["status"] == "overdue")
        partial = sum(i["amount"] for i in invoices if i["status"] == "partial")
        return {
            "total_invoiced": sum(i["amount"] for i in invoices),
            "total_paid": paid,
            "total_pending": pending,
            "total_overdue": overdue,
            "total_partial": partial,
            "collection_rate_pct": round(paid / sum(i["amount"] for i in invoices) * 100, 1) if invoices else 0,
            "invoice_count": len(invoices),
            "tier": self.tier,
        }

    def export_pdf(self, invoice_id: str) -> dict:
        """Export invoice as PDF (ENTERPRISE only)."""
        if not self._config["pdf_export"]:
            raise PermissionError(
                "PDF export requires ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        invoice = self.get_invoice(invoice_id)
        return {
            "exported": True,
            "filename": f"{invoice_id}.pdf",
            "invoice": invoice,
            "message": f"Invoice {invoice_id} exported to PDF successfully.",
        }

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_invoices"] if cfg["max_invoices"] else "unlimited"
        lines = [
            f"=== InvoicingBot — {self.tier} Tier ===",
            f"  Monthly price   : ${cfg['price_usd']}/month",
            f"  Max invoices    : {limit}",
            f"  Tax calculation : {'enabled' if cfg['tax_calc'] else 'disabled'}",
            f"  Overdue alerts  : {'enabled' if cfg['overdue_alerts'] else 'disabled'}",
            f"  PDF export      : {'enabled' if cfg['pdf_export'] else 'disabled (ENTERPRISE)'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "invoicing", "invoices_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "revenue": self.get_revenue_summary()}


if __name__ == "__main__":
    bot = InvoicingBot(tier="PRO")
    revenue = bot.get_revenue_summary()
    print(f"Total invoiced: ${revenue['total_invoiced']:,}")
    print(f"Total paid: ${revenue['total_paid']:,} (Collection rate: {revenue['collection_rate_pct']}%)")
    overdue = bot.get_overdue_invoices()
    print(f"Overdue invoices: {len(overdue)}")
    reminder = bot.send_overdue_reminder("INV-004")
    print(f"Reminder sent: {reminder['sent']}")
    print(bot.describe_tier())

# ---------------------------------------------------------------------------
# Tier system additions for test compatibility
# ---------------------------------------------------------------------------
import random as _random_tier
from enum import Enum as _TierEnum


class Tier(_TierEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


_TIER_MONTHLY_PRICE = {"free": 0, "pro": 29, "enterprise": 99}


class InvoicingBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_invoicing_bot_init = InvoicingBot.__init__


def _invoicing_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_invoicing_bot_init(self, tier_val.upper())
    self.tier = tier if isinstance(tier, Tier) else Tier(tier_val)


InvoicingBot.__init__ = _invoicing_bot_new_init
InvoicingBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _invoicing_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _invoicing_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _invoicing_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise InvoicingBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _invoicing_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _invoicing_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "InvoicingBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _invoicing_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "InvoicingBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


InvoicingBot.monthly_price = _invoicing_bot_monthly_price
InvoicingBot.get_tier_info = _invoicing_bot_get_tier_info
InvoicingBot._enforce_tier = _invoicing_bot_enforce_tier
InvoicingBot.list_items = _invoicing_bot_list_items
InvoicingBot.analyze = _invoicing_bot_analyze
InvoicingBot.export_report = _invoicing_bot_export_report

# ---------------------------------------------------------------------------
# InvoicingBot extended interface: chat with invoice counter
# ---------------------------------------------------------------------------
import uuid as _uuid_inv


def _invoicingbot_full_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_invoicing_bot_init(self, tier_val.upper())
    self.tier = tier if isinstance(tier, Tier) else Tier(tier_val)
    if not hasattr(self, "bot_id"):
        self.bot_id = str(_uuid_inv.uuid4())
    self.name = "Invoicing Bot"
    self.category = "business"
    self.domain = "invoicing"
    self._invoice_counter = 1000


def _invoicingbot_chat(self, user_input: str, user_id: str = "anonymous") -> str:
    q = user_input.lower()
    if any(w in q for w in ("invoice", "bill", "charge", "payment")):
        inv_num = f"INV-{self._invoice_counter}"
        self._invoice_counter += 1
        return f"Invoice {inv_num} created successfully."
    return "I'm your Invoicing Bot. I can create and manage invoices."


InvoicingBot.__init__ = _invoicingbot_full_init
InvoicingBot.chat = _invoicingbot_chat
InvoicingBot.end_session = lambda self, user_id: None
