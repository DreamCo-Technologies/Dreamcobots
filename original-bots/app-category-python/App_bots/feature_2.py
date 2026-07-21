"""
Feature 2: App User Support Bot
Functionality: Provides customer support through a chat interface. Handles
  FAQ lookups, ticket creation, escalation, and AI-powered answer generation.
Use Cases: Users needing help with technical issues and feature questions.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example support knowledge-base entries
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "question": "How do I reset my password?",                      "category": "account",     "answer": "Go to Settings → Security → Reset Password. You'll receive an email with a reset link within 2 minutes.", "helpful_votes": 342, "difficulty": "easy",   "escalate": False},
    {"id": 2,  "question": "How do I upgrade my plan?",                        "category": "billing",     "answer": "Navigate to Settings → Billing → Upgrade Plan. Select your desired tier and complete checkout.", "helpful_votes": 287, "difficulty": "easy",   "escalate": False},
    {"id": 3,  "question": "Why is my bot not running?",                       "category": "technical",   "answer": "Check 1) Token balance in Billing, 2) Bot status in Dashboard, 3) API key validity in Settings → Developer.", "helpful_votes": 412, "difficulty": "medium", "escalate": False},
    {"id": 4,  "question": "How do I connect my CRM?",                         "category": "integrations","answer": "Go to Settings → Integrations and select your CRM (Salesforce, HubSpot, Pipedrive). Follow the OAuth flow.", "helpful_votes": 198, "difficulty": "medium", "escalate": False},
    {"id": 5,  "question": "How do I generate an API key?",                    "category": "developer",   "answer": "Go to Settings → Developer → API Keys → Generate New Key. Copy and store it securely — it's only shown once.", "helpful_votes": 356, "difficulty": "easy",   "escalate": False},
    {"id": 6,  "question": "Why am I being charged twice?",                    "category": "billing",     "answer": "This may be due to a failed charge retry. Please contact billing@dreamcobots.com with your invoice numbers.", "helpful_votes": 145, "difficulty": "hard",   "escalate": True},
    {"id": 7,  "question": "How do I cancel my subscription?",                 "category": "billing",     "answer": "Go to Settings → Billing → Cancel Plan. Your access continues until the end of the billing period.", "helpful_votes": 223, "difficulty": "easy",   "escalate": False},
    {"id": 8,  "question": "Can I export my data?",                            "category": "data",        "answer": "Yes! Go to Settings → Data → Export. Choose CSV or JSON format. Enterprise users get automated daily exports.", "helpful_votes": 189, "difficulty": "easy",   "escalate": False},
    {"id": 9,  "question": "How do I invite team members?",                    "category": "collaboration","answer": "Go to Settings → Team → Invite Members. Enter their email. They'll receive an invite valid for 48 hours.", "helpful_votes": 267, "difficulty": "easy",   "escalate": False},
    {"id": 10, "question": "What are tokens and how are they used?",           "category": "billing",     "answer": "Tokens are the currency used to run bots. Each bot action costs a fixed number of tokens. View usage in Dashboard.", "helpful_votes": 445, "difficulty": "easy",   "escalate": False},
    {"id": 11, "question": "How do I set up a Stripe integration?",            "category": "integrations","answer": "Go to Settings → Payments → Connect Stripe. You'll be redirected to Stripe's OAuth page to connect your account.", "helpful_votes": 312, "difficulty": "medium", "escalate": False},
    {"id": 12, "question": "My bot returned wrong data — what do I do?",       "category": "technical",   "answer": "Check your bot configuration filters and API connections. If the issue persists, submit a bug report from the Dashboard.", "helpful_votes": 178, "difficulty": "medium", "escalate": False},
    {"id": 13, "question": "How do I create a custom bot template?",           "category": "product",     "answer": "Go to Bot Factory → Create New → Start from Scratch. Define inputs, outputs, and automation logic using our visual builder.", "helpful_votes": 234, "difficulty": "hard",   "escalate": False},
    {"id": 14, "question": "Does DreamCo support GDPR compliance?",            "category": "compliance",  "answer": "Yes. DreamCo is GDPR compliant. Go to Settings → Privacy to configure data retention, consent banners, and DPA agreements.", "helpful_votes": 289, "difficulty": "medium", "escalate": False},
    {"id": 15, "question": "How do I view bot performance analytics?",         "category": "analytics",   "answer": "Go to Dashboard → Analytics → Bot Performance. Filter by date range, bot type, or revenue generated.", "helpful_votes": 321, "difficulty": "easy",   "escalate": False},
    {"id": 16, "question": "Why is my account suspended?",                     "category": "account",     "answer": "Suspensions occur for TOS violations or unpaid invoices. Contact support@dreamcobots.com immediately to resolve.", "helpful_votes": 89,  "difficulty": "hard",   "escalate": True},
    {"id": 17, "question": "How do I configure webhook notifications?",        "category": "developer",   "answer": "Go to Settings → Developer → Webhooks → Add Endpoint. Enter your URL and select the events to subscribe to.", "helpful_votes": 267, "difficulty": "medium", "escalate": False},
    {"id": 18, "question": "Can I use DreamCo on mobile?",                    "category": "product",     "answer": "Yes! The DreamCo mobile app is available on iOS and Android. Download from the App Store or Google Play.", "helpful_votes": 198, "difficulty": "easy",   "escalate": False},
    {"id": 19, "question": "How do I set up a referral link?",                 "category": "growth",      "answer": "Go to Dashboard → Referrals → Copy Your Link. Share it and earn $50 for every customer who upgrades.", "helpful_votes": 345, "difficulty": "easy",   "escalate": False},
    {"id": 20, "question": "How do I report a security vulnerability?",       "category": "security",    "answer": "Email security@dreamcobots.com with details. We follow responsible disclosure and reward valid reports.", "helpful_votes": 156, "difficulty": "medium", "escalate": True},
    {"id": 21, "question": "How do I bulk import leads?",                     "category": "product",     "answer": "Go to Lead Manager → Import → Upload CSV. Map the fields and confirm. Supports up to 50,000 records.", "helpful_votes": 278, "difficulty": "medium", "escalate": False},
    {"id": 22, "question": "Why is the dashboard loading slowly?",            "category": "technical",   "answer": "Try clearing cache, using a different browser, or checking status.dreamcobots.com for incidents.", "helpful_votes": 213, "difficulty": "easy",   "escalate": False},
    {"id": 23, "question": "How do I enable white-label mode?",               "category": "enterprise",  "answer": "White-label is available on ENTERPRISE plans. Go to Settings → White Label → Configure Brand to upload your logo and colors.", "helpful_votes": 189, "difficulty": "medium", "escalate": False},
    {"id": 24, "question": "Can I run multiple bots simultaneously?",         "category": "product",     "answer": "Yes! PRO and ENTERPRISE users can run multiple bots at the same time. Free tier runs one bot at a time.", "helpful_votes": 312, "difficulty": "easy",   "escalate": False},
    {"id": 25, "question": "How do I get a refund?",                          "category": "billing",     "answer": "We offer a 14-day money-back guarantee. Email billing@dreamcobots.com with your account email and reason.", "helpful_votes": 267, "difficulty": "medium", "escalate": True},
    {"id": 26, "question": "How do I connect Google Sheets?",                 "category": "integrations","answer": "Go to Settings → Integrations → Google Sheets. Click Connect and authorize access. Then map sheets to your bots.", "helpful_votes": 345, "difficulty": "easy",   "escalate": False},
    {"id": 27, "question": "How do I create a drip email sequence?",          "category": "marketing",   "answer": "Go to Marketing → Email → New Sequence. Add steps, set delays, and configure triggers. Preview before activating.", "helpful_votes": 231, "difficulty": "medium", "escalate": False},
    {"id": 28, "question": "What's the uptime SLA for ENTERPRISE?",          "category": "enterprise",  "answer": "Enterprise plans include a 99.9% uptime SLA with dedicated infrastructure and priority support.", "helpful_votes": 178, "difficulty": "easy",   "escalate": False},
    {"id": 29, "question": "How do I set rate limits on bots?",               "category": "developer",   "answer": "Go to Bot Settings → Advanced → Rate Limiting. Set max requests per minute/hour/day to prevent overuse.", "helpful_votes": 145, "difficulty": "hard",   "escalate": False},
    {"id": 30, "question": "How do I access the API documentation?",          "category": "developer",   "answer": "Visit docs.dreamcobots.com for full REST API documentation, SDK guides, and code examples.", "helpful_votes": 423, "difficulty": "easy",   "escalate": False},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_queries": 10,   "ai_answers": False, "ticket_creation": False},
    "PRO":        {"price_usd": 29,  "max_queries": 500,  "ai_answers": True,  "ticket_creation": True},
    "ENTERPRISE": {"price_usd": 99,  "max_queries": None, "ai_answers": True,  "ticket_creation": True},
}


class UserSupportBot:
    """Answers user questions, creates support tickets, and escalates issues.

    Competes with Intercom and Zendesk by combining FAQ search, AI answer
    generation, and intelligent ticket routing.
    Monetization: $29/month PRO or $99/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="UserSupportBot")
        self._query_count: int = 0
        self._tickets: list[dict] = []

    def _check_query_limit(self) -> None:
        max_q = self._config["max_queries"]
        if max_q is not None and self._query_count >= max_q:
            raise PermissionError(
                f"Query limit of {max_q} reached on {self.tier} tier. "
                "Upgrade at dreamcobots.com/pricing"
            )

    def search_faq(self, query: str) -> list[dict]:
        """Search the FAQ knowledge base for matching questions."""
        self._check_query_limit()
        self._query_count += 1
        query_lower = query.lower()
        results = [
            e for e in EXAMPLES
            if any(word in e["question"].lower() for word in query_lower.split())
        ]
        return results[:5] if results else EXAMPLES[:3]

    def get_answer(self, question_id: int) -> dict:
        """Get the answer to a specific FAQ entry."""
        self._check_query_limit()
        self._query_count += 1
        entry = next((e for e in EXAMPLES if e["id"] == question_id), None)
        if entry is None:
            raise ValueError(f"Question ID {question_id} not found.")
        result = {
            "question": entry["question"],
            "answer": entry["answer"],
            "category": entry["category"],
            "helpful_votes": entry["helpful_votes"],
        }
        if entry["escalate"]:
            result["note"] = "⚠️ This issue may require human support. A ticket can be created."
        return result

    def create_ticket(self, user_email: str, subject: str, description: str,
                      priority: str = "normal") -> dict:
        """Create a support ticket (PRO/ENTERPRISE)."""
        if not self._config["ticket_creation"]:
            raise PermissionError(
                "Ticket creation requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        ticket_id = f"TKT-{len(self._tickets) + 1:04d}"
        ticket = {
            "ticket_id": ticket_id,
            "user_email": user_email,
            "subject": subject,
            "description": description,
            "priority": priority,
            "status": "open",
        }
        self._tickets.append(ticket)
        return ticket

    def get_questions_by_category(self, category: str) -> list[dict]:
        """Return all FAQ entries for a specific category."""
        return [e for e in EXAMPLES if e["category"] == category]

    def get_escalation_required_questions(self) -> list[dict]:
        """Return FAQ entries that require human escalation."""
        return [e for e in EXAMPLES if e["escalate"]]

    def get_top_questions(self, count: int = 5) -> list[dict]:
        """Return the most helpful FAQ entries."""
        return sorted(EXAMPLES, key=lambda e: e["helpful_votes"], reverse=True)[:count]

    def get_ai_answer(self, query: str) -> dict:
        """Generate an AI-powered contextual answer (PRO/ENTERPRISE)."""
        if not self._config["ai_answers"]:
            raise PermissionError(
                "AI answers require PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        matches = self.search_faq(query)
        if matches:
            best = max(matches, key=lambda m: m["helpful_votes"])
            return {
                "query": query,
                "ai_answer": best["answer"],
                "confidence": "high",
                "source_question": best["question"],
                "needs_escalation": best["escalate"],
            }
        return {
            "query": query,
            "ai_answer": "I couldn't find a specific answer. Please create a support ticket for personalized help.",
            "confidence": "low",
            "source_question": None,
            "needs_escalation": True,
        }

    def get_support_stats(self) -> dict:
        """Return support knowledge base statistics."""
        categories: dict[str, int] = {}
        for e in EXAMPLES:
            categories[e["category"]] = categories.get(e["category"], 0) + 1
        return {
            "total_faq_entries": len(EXAMPLES),
            "by_category": categories,
            "escalation_required": len(self.get_escalation_required_questions()),
            "avg_helpful_votes": round(sum(e["helpful_votes"] for e in EXAMPLES) / len(EXAMPLES), 1),
            "open_tickets": len([t for t in self._tickets if t["status"] == "open"]),
            "tier": self.tier,
        }

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_queries"] if cfg["max_queries"] else "unlimited"
        lines = [
            f"=== UserSupportBot — {self.tier} Tier ===",
            f"  Monthly price   : ${cfg['price_usd']}/month",
            f"  Max queries     : {limit}",
            f"  AI answers      : {'enabled' if cfg['ai_answers'] else 'disabled'}",
            f"  Ticket creation : {'enabled' if cfg['ticket_creation'] else 'disabled'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "user_support", "faq_entries": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "stats": self.get_support_stats()}


if __name__ == "__main__":
    bot = UserSupportBot(tier="PRO")
    top = bot.get_top_questions(3)
    print("Top 3 FAQs:")
    for q in top:
        print(f"  ✅ [{q['helpful_votes']} votes] {q['question']}")
    answer = bot.get_ai_answer("how do I reset password")
    print(f"\nAI Answer: {answer['ai_answer'][:80]}...")
    print(bot.describe_tier())


SupportBot = UserSupportBot


# ---------------------------------------------------------------------------
# Tier system additions for test compatibility
# ---------------------------------------------------------------------------
import random as _random_tier
from enum import Enum as _TierEnum


class Tier(_TierEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other.upper()
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()


_TIER_MONTHLY_PRICE = {"free": 0, "pro": 29, "enterprise": 99}


class UserSupportBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_usersupport_bot_init = UserSupportBot.__init__


def _usersupport_bot_new_init(self, tier=Tier.FREE):
    if not isinstance(tier, Tier):
        tier_str = str(tier).lower()
        if tier_str not in ("free", "pro", "enterprise"):
            raise ValueError(f"Invalid tier '{tier}'. Choose from ['FREE', 'PRO', 'ENTERPRISE']")
        tier = Tier(tier_str)
    _orig_usersupport_bot_init(self, tier.value.upper())
    self.tier = tier


UserSupportBot.__init__ = _usersupport_bot_new_init
UserSupportBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _usersupport_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _usersupport_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _usersupport_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise UserSupportBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _usersupport_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _usersupport_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "UserSupportBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _usersupport_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "UserSupportBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


UserSupportBot.monthly_price = _usersupport_bot_monthly_price
UserSupportBot.get_tier_info = _usersupport_bot_get_tier_info
UserSupportBot._enforce_tier = _usersupport_bot_enforce_tier
UserSupportBot.list_items = _usersupport_bot_list_items
UserSupportBot.analyze = _usersupport_bot_analyze
UserSupportBot.export_report = _usersupport_bot_export_report
