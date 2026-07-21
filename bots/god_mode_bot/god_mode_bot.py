"""
God Mode Bot — DreamCo's Autonomous Business Operator

The full autonomous business operator suite.  GodModeBot orchestrates five
specialised engines to hunt leads, close deals, collect payments, generate
viral content, and continuously improve its own performance.

Sub-systems
-----------
  • AutoClientHunter     — lead scraping simulation, scoring, niche targeting
  • AutoCloser           — 7-stage negotiation state machine with objection handling
  • PaymentAutoCollector — subscription billing, invoice generation, MRR/ARR stats
  • ViralEngine          — trend detection, platform-specific posts, engagement scoring
  • SelfImprovingAI      — performance analysis, service prioritisation, recommendations

Tier access
-----------
  FREE:       Lead hunting (5/cycle), basic viral content (3 posts), view-only stats.
  PRO:        20 leads/cycle, all platforms viral engine, auto-closer, payment
              collection (≤50 subscribers), self-improving AI.
  ENTERPRISE: Unlimited leads, all engines, white-label, API access, dedicated support.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.god_mode_bot import GodModeBot, Tier

    bot = GodModeBot(tier=Tier.PRO)
    report = bot.run_all_engines()
    print(bot.get_summary())
"""

from __future__ import annotations

import sys
import os
import random
import time
from datetime import datetime
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401
from bots.god_mode_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_LEAD_HUNTING,
    FEATURE_AUTO_CLOSER,
    FEATURE_PAYMENT_COLLECTION,
    FEATURE_VIRAL_ENGINE,
    FEATURE_SELF_IMPROVING_AI,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
)


# ---------------------------------------------------------------------------
# AutoClientHunter engine
# ---------------------------------------------------------------------------

_NICHES = ["ecommerce", "real_estate", "health_wellness", "tech_startups", "local_business"]

_NICHE_PAIN_POINTS = {
    "ecommerce": ["low conversion rate", "high cart abandonment", "poor ROAS"],
    "real_estate": ["too few leads", "low listing visibility", "slow follow-up"],
    "health_wellness": ["hard to stand out", "booking friction", "low retention"],
    "tech_startups": ["not enough users", "high churn", "unclear positioning"],
    "local_business": ["no online presence", "poor Google ranking", "no referral system"],
}

_LEAD_SCORES = ["hot", "warm", "cold"]


class AutoClientHunter:
    """Simulates lead scraping across business niches with quality scoring."""

    def hunt_leads(self, niche: str = "ecommerce", count: int = 10) -> list[dict]:
        """Return a list of scored leads for *niche*.

        Parameters
        ----------
        niche : str
            One of the supported niche keys.
        count : int
            Number of leads to generate.
        """
        pain_points = _NICHE_PAIN_POINTS.get(niche, _NICHE_PAIN_POINTS["ecommerce"])
        leads = []
        for i in range(count):
            score_label = random.choice(_LEAD_SCORES)
            niche_match = random.random() > 0.3
            leads.append({
                "id": f"LEAD-{int(time.time() * 1000)}-{i}",
                "niche": niche,
                "company": f"{niche.replace('_', ' ').title()} Venture {i + 1} LLC",
                "contact_name": f"Contact {i + 1}",
                "email": f"contact{i + 1}@{niche.replace('_', '')}.example.com",
                "pain_point": random.choice(pain_points),
                "score": score_label,
                "niche_match": niche_match,
                "qualified": score_label in ("hot", "warm") and niche_match,
            })
        return leads


# ---------------------------------------------------------------------------
# AutoCloser engine
# ---------------------------------------------------------------------------

_STAGES = [
    "initial_contact",
    "discovery",
    "proposal",
    "objection_handling",
    "closing",
    "follow_up",
    "booked",
]

_OBJECTION_RESPONSES = {
    "too expensive": "Our pricing typically returns 3–5x within 90 days. Want an ROI breakdown?",
    "not the right time": "What would need to change for the timing to work? Let's map that out.",
    "need to think about it": "What specific questions can I answer right now to make it easier?",
    "already have a solution": "Many clients already had a solution — we often complement it significantly.",
    "need to talk to my team": "I can prepare a one-pager and join your team call. Would that help?",
}


class AutoCloser:
    """7-stage negotiation state machine with objection handling."""

    def close_leads(self, leads: list[dict]) -> list[dict]:
        """Run each qualified lead through the 7-stage state machine.

        Parameters
        ----------
        leads : list[dict]
            Lead objects, typically from AutoClientHunter.hunt_leads().
        """
        closed_deals = []
        for lead in leads:
            if not lead.get("qualified"):
                continue
            stage_index = random.randint(3, len(_STAGES) - 1)
            final_stage = _STAGES[stage_index]
            won = final_stage == "booked" and random.random() > 0.35
            closed_deals.append({
                "lead_id": lead["id"],
                "company": lead["company"],
                "final_stage": final_stage,
                "won": won,
                "deal_value": random.randint(1000, 8000) if won else 0,
                "stages_traversed": _STAGES[: stage_index + 1],
            })
        return closed_deals


# ---------------------------------------------------------------------------
# PaymentAutoCollector engine
# ---------------------------------------------------------------------------

_PLANS = {
    "starter": {"price": 29, "label": "Starter"},
    "pro": {"price": 97, "label": "Pro"},
    "enterprise": {"price": 297, "label": "Enterprise"},
}

_TAX_RATE = 0.085


class PaymentAutoCollector:
    """In-memory subscription billing with invoice generation and MRR stats."""

    def __init__(self) -> None:
        self._subscriptions: list[dict] = []
        self._invoices: list[dict] = []

    def collect_payments(self, clients: list[dict]) -> dict:
        """Onboard clients as subscribers, generate invoices, and collect payments.

        Parameters
        ----------
        clients : list[dict]
            Closed deals or client objects with at least an 'id' key.
        """
        plan_keys = list(_PLANS.keys())
        collected = 0
        total_amount = 0.0

        for client in clients:
            plan_key = random.choice(plan_keys)
            plan = _PLANS[plan_key]
            sub = {
                "subscription_id": f"SUB-{int(time.time() * 1000)}-{len(self._subscriptions)}",
                "customer_id": client.get("lead_id", client.get("id", "unknown")),
                "plan": plan_key,
                "price_usd": plan["price"],
                "status": "active",
            }
            self._subscriptions.append(sub)

            subtotal = plan["price"]
            tax = round(subtotal * _TAX_RATE, 2)
            total = round(subtotal + tax, 2)
            invoice = {
                "invoice_id": f"INV-{int(time.time() * 1000)}-{len(self._invoices)}",
                "subscription_id": sub["subscription_id"],
                "subtotal": subtotal,
                "tax": tax,
                "total": total,
                "status": "pending",
            }
            self._invoices.append(invoice)

            success = random.random() > 0.08
            invoice["status"] = "paid" if success else "failed"
            if success:
                collected += 1
                total_amount += total

        active = [s for s in self._subscriptions if s["status"] == "active"]
        mrr = sum(s["price_usd"] for s in active)
        return {
            "subscribers_added": len(clients),
            "payments_collected": collected,
            "total_collected": round(total_amount, 2),
            "mrr": mrr,
            "arr": mrr * 12,
            "total_subscribers": len(active),
            "total_invoices": len(self._invoices),
        }


# ---------------------------------------------------------------------------
# ViralEngine
# ---------------------------------------------------------------------------

_PLATFORMS = ["tiktok", "instagram", "twitter", "facebook", "linkedin", "youtube"]

_TRENDS_BY_NICHE = {
    "business": ["AI automation", "solopreneur tools", "no-code launch", "building in public"],
    "fitness": ["zone 2 cardio", "protein-first meals", "12-week challenge", "home gym setup"],
    "finance": ["dividend stacking", "HYSA rates", "passive income", "index fund compounding"],
    "tech": ["vibe coding", "local LLMs", "API monetisation", "edge AI"],
    "lifestyle": ["digital nomad", "slow living", "micro-habits", "travel hacking"],
}

_POST_TIMES = {
    "tiktok": "18:00–21:00",
    "instagram": "11:00–13:00",
    "twitter": "08:00–10:00",
    "facebook": "13:00–16:00",
    "linkedin": "07:00–09:00",
    "youtube": "14:00–17:00",
}


class ViralEngine:
    """Trend detection and platform-specific content scheduling."""

    def create_viral_content(self, niche: str = "business") -> list[dict]:
        """Generate optimised posts for all supported platforms.

        Parameters
        ----------
        niche : str
            Content niche used to select trending topics.
        """
        trends = _TRENDS_BY_NICHE.get(niche, _TRENDS_BY_NICHE["business"])
        top_trend = random.choice(trends)
        posts = []
        for platform in _PLATFORMS:
            posts.append({
                "platform": platform,
                "content": f"🔥 {top_trend} — the {niche} playbook you need | Follow for daily tips",
                "trend": top_trend,
                "optimal_post_time": _POST_TIMES[platform],
                "engagement_score": round(random.uniform(6.0, 9.8), 1),
                "estimated_reach": random.randint(5000, 75000),
                "scheduled": True,
            })
        return posts


# ---------------------------------------------------------------------------
# SelfImprovingAI engine
# ---------------------------------------------------------------------------

class SelfImprovingAI:
    """Analyses cycle results and generates optimisation recommendations."""

    def analyze_performance(self, results: dict) -> dict:
        """Evaluate revenue and lead metrics and return improvement plan.

        Parameters
        ----------
        results : dict
            Output from run_all_engines() or a similar results dict.
        """
        total_revenue = results.get("total_revenue", 0)
        total_leads = results.get("total_leads", 0)
        recommendations = []

        if total_revenue < 5000:
            recommendations.append("Increase auto-closer conversion rate by refining objection scripts.")
        if total_leads < 20:
            recommendations.append("Expand lead hunting to 3+ niches per cycle.")
        recommendations.append("A/B test viral content hooks on TikTok and Instagram.")
        recommendations.append("Upsell warm leads from Starter to Pro plan automatically.")

        # Auto-prioritise services by revenue contribution
        service_scores = {
            "autoClientHunter": random.randint(70, 95),
            "autoCloser": random.randint(60, 90),
            "paymentAutoCollector": random.randint(65, 88),
            "viralEngine": random.randint(55, 85),
        }
        prioritised = sorted(service_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "performance_score": min(100, int(total_revenue / 100)),
            "revenue_analysis": f"Cycle revenue ${total_revenue:,.0f} — {'above' if total_revenue >= 5000 else 'below'} target",
            "recommendations": recommendations,
            "service_priority": [s for s, _ in prioritised],
            "next_cycle_target": max(total_revenue * 1.15, 5000),
        }


# ---------------------------------------------------------------------------
# GodModeBot — main orchestrator
# ---------------------------------------------------------------------------

class GodModeBot:
    """Autonomous business operator — orchestrates all five God Mode engines.

    Parameters
    ----------
    tier : Tier
        Subscription tier governing feature access and limits.
    niche : str
        Primary business niche for lead hunting and content (default: ``"business"``).
    """

    def __init__(self, tier: Tier = Tier.FREE, niche: str = "business") -> None:
        self.tier = tier
        self.niche = niche
        self._config: TierConfig = get_tier_config(tier)
        self._hunter = AutoClientHunter()
        self._closer = AutoCloser()
        self._payment_collector = PaymentAutoCollector()
        self._viral = ViralEngine()
        self._ai = SelfImprovingAI()
        self._last_report: dict = {}

    # ------------------------------------------------------------------
    # Engine methods (public, tier-gated)
    # ------------------------------------------------------------------

    def hunt_leads(self, niche: str | None = None, count: int = 10) -> list[dict]:
        """Hunt leads — count is capped by tier limit."""
        if not self._config.has_feature(FEATURE_LEAD_HUNTING):
            return []
        max_leads = self._config.max_leads_per_cycle
        if max_leads is not None:
            count = min(count, max_leads)
        return self._hunter.hunt_leads(niche or self.niche, count)

    def close_leads(self, leads: list[dict]) -> list[dict]:
        """Close leads through the negotiation state machine (PRO+ only)."""
        if not self._config.has_feature(FEATURE_AUTO_CLOSER):
            return []
        return self._closer.close_leads(leads)

    def collect_payments(self, clients: list[dict]) -> dict:
        """Collect subscription payments from closed clients (PRO+ only)."""
        if not self._config.has_feature(FEATURE_PAYMENT_COLLECTION):
            return {"error": "Payment collection requires PRO or higher tier."}
        max_subs = self._config.max_subscribers
        if max_subs is not None:
            clients = clients[:max_subs]
        return self._payment_collector.collect_payments(clients)

    def create_viral_content(self, niche: str | None = None) -> list[dict]:
        """Generate viral content posts (FREE: 3 posts, PRO+: all platforms)."""
        if not self._config.has_feature(FEATURE_VIRAL_ENGINE):
            return []
        posts = self._viral.create_viral_content(niche or self.niche)
        max_posts = self._config.max_viral_posts
        if max_posts is not None:
            posts = posts[:max_posts]
        return posts

    def analyze_performance(self, results: dict) -> dict:
        """Analyse performance and generate AI recommendations (PRO+ only)."""
        if not self._config.has_feature(FEATURE_SELF_IMPROVING_AI):
            return {"error": "Self-improving AI requires PRO or higher tier."}
        return self._ai.analyze_performance(results)

    # ------------------------------------------------------------------
    # Top-level orchestration
    # ------------------------------------------------------------------

    def run_all_engines(self) -> dict:
        """Run all available engines for one full cycle.

        Returns
        -------
        dict
            Comprehensive report with results from every engine.
        """
        report: dict[str, Any] = {
            "bot": "GodModeBot",
            "tier": self.tier.value,
            "niche": self.niche,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Lead hunting
        leads = self.hunt_leads(count=50)
        report["leads"] = leads
        report["leads_hunted"] = len(leads)

        # Auto-closer
        closed_deals = self.close_leads(leads)
        report["closed_deals"] = closed_deals
        report["deals_won"] = sum(1 for d in closed_deals if d.get("won"))

        # Payment collection
        winning_clients = [d for d in closed_deals if d.get("won")]
        if winning_clients:
            payment_stats = self.collect_payments(winning_clients)
        else:
            payment_stats = {"mrr": 0, "arr": 0, "total_collected": 0, "payments_collected": 0}
        report["payment_stats"] = payment_stats

        # Viral content
        posts = self.create_viral_content()
        report["viral_posts"] = posts
        report["posts_scheduled"] = len(posts)

        # Aggregate revenue estimate
        total_revenue = (
            payment_stats.get("total_collected", 0)
            + sum(d.get("deal_value", 0) for d in closed_deals)
            + len(posts) * random.randint(50, 200)
        )
        report["total_revenue"] = round(total_revenue, 2)
        report["total_leads"] = len(leads)

        # Self-improving AI
        ai_analysis = self.analyze_performance(report)
        report["ai_analysis"] = ai_analysis

        self._last_report = report
        return report

    def get_summary(self) -> dict:
        """Return a concise revenue/leads/status summary.

        Runs a fresh cycle if no report exists yet.
        """
        if not self._last_report:
            self.run_all_engines()

        report = self._last_report
        upgrade = get_upgrade_path(self.tier)
        return {
            "bot": "GodModeBot",
            "tier": self.tier.value,
            "status": "active",
            "total_revenue": report.get("total_revenue", 0),
            "total_leads": report.get("total_leads", 0),
            "deals_won": report.get("deals_won", 0),
            "posts_scheduled": report.get("posts_scheduled", 0),
            "mrr": report.get("payment_stats", {}).get("mrr", 0),
            "upgrade_available": upgrade.name if upgrade else None,
            "timestamp": report.get("timestamp"),
        }
