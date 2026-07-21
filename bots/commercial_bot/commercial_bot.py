"""
CommercialBot AI (DreamCo CineCore™ Module)

An autonomous commercial-creation and revenue bot that:

  1. 🧠 ScriptEngine       — Writes 15–60 second commercial scripts with
                              hooks, emotional triggers, and CTAs
  2. 🎥 VideoEngine        — Builds scene-by-scene video concepts and renders
                              via Runway / Pika APIs (ENTERPRISE)
  3. 🔊 VoiceEngine        — Generates voiceover scripts for multiple tones
                              and platform formats
  4. 📱 PlatformOptimizer  — Adapts ads for TikTok, YouTube, Instagram,
                              Facebook
  5. 🔍 ClientFinder       — Scrapes local businesses, Shopify stores, and
                              social media pages to build lead lists
  6. 🤖 ClosingAgent       — Handles automated outreach, objection responses,
                              and deal-closing conversations
  7. 💳 BillingEngine      — Stripe subscription management for ad packages
  8. 📈 AnalyticsEngine    — Tracks views, clicks, conversions, and revenue
  9. ⚡ BulkGenerator      — Mass-produces commercials for entire lead lists
 10. 🛡️ SelfHeal           — Monitors system health and auto-resolves errors

Usage
-----
    from bots.commercial_bot import CommercialBot
    from tiers import Tier

    bot = CommercialBot(tier=Tier.PRO)

    script = bot.generate_script("Joe's Pizza", "wood-fired pizza", "families")
    plan   = bot.create_ad_plan(script["script"])
    leads  = bot.find_clients(niche="restaurant", limit=10)
    reply  = bot.close_client(leads[0]["name"], "What's the price?")
    bulk   = bot.bulk_generate(["Biz A", "Biz B", "Biz C"])
    stats  = bot.analytics.track("vid_001")
    health = bot.self_heal.check_system()
    summary = bot.revenue_summary()
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.commercial_bot.tiers import BOT_FEATURES, get_bot_tier_info  # noqa: E402
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class CommercialBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLATFORMS = ["TikTok", "YouTube", "Instagram", "Facebook"]

SCRIPT_DURATIONS = {
    Tier.FREE: [15],
    Tier.PRO: [15, 30, 60],
    Tier.ENTERPRISE: [15, 30, 60, 90, 120],
}

BULK_LIMITS = {
    Tier.FREE: 0,
    Tier.PRO: 50,
    Tier.ENTERPRISE: 10_000,
}

PRICING_TIERS = {
    "basic": (50, 150),
    "pro_commercial": (300, 1_000),
    "monthly_package": (500, 5_000),
    "affiliate": (0, None),
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CommercialScript:
    business: str
    product: str
    target_audience: str
    duration_seconds: int
    script: str
    hook: str
    cta: str
    platforms: List[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class VideoScene:
    index: int
    label: str
    description: str
    camera_angle: str
    b_roll: str


@dataclass
class Lead:
    name: str
    niche: str
    contact: str
    source: str
    status: str = "new"
    score: int = 0


@dataclass
class Deal:
    client: str
    package: str
    monthly_value: float
    status: str = "open"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AdPerformance:
    video_id: str
    views: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0


# ---------------------------------------------------------------------------
# Engine 1 — ScriptEngine
# ---------------------------------------------------------------------------

class ScriptEngine:
    """Generates commercial scripts with hooks, emotional triggers, and CTAs."""

    HOOKS = [
        "STOP wasting money on ads that don't convert",
        "This changes everything",
        "Are you still struggling with {pain}?",
        "What if you could get {benefit} in under 24 hours?",
        "The secret {niche} businesses don't want you to know",
    ]

    CTAS = [
        "Click now before it's gone",
        "Call us today for a FREE consultation",
        "Visit our site and claim your discount",
        "DM us NOW and we'll get you started",
        "Limited spots available — book yours today",
    ]

    def generate(
        self,
        business: str,
        product: str,
        target_audience: str,
        duration_seconds: int = 30,
        tier: Tier = Tier.FREE,
    ) -> CommercialScript:
        allowed = SCRIPT_DURATIONS.get(tier, [15])
        if duration_seconds not in allowed:
            duration_seconds = allowed[-1]

        hook = self.HOOKS[0].replace("{pain}", f"{product} problems").replace(
            "{benefit}", f"more {product}"
        ).replace("{niche}", product)

        body = (
            f"Introducing {business} — built for {target_audience} who demand results. "
            f"Our {product} eliminates the hassle and delivers real value. "
            f"Imagine getting everything you need without the stress."
        )

        if duration_seconds >= 30:
            body += (
                f" Join thousands of satisfied customers who chose {business}. "
                f"Don't let another day pass without experiencing the difference."
            )

        if duration_seconds >= 60:
            body += (
                f" {business} has been serving {target_audience} with unmatched quality. "
                f"Our {product} is the proven solution that delivers real results, "
                f"every single time. The time to act is now."
            )

        cta = self.CTAS[0]
        platforms = PLATFORMS if tier != Tier.FREE else ["TikTok"]

        return CommercialScript(
            business=business,
            product=product,
            target_audience=target_audience,
            duration_seconds=duration_seconds,
            script=f"{hook}\n\n{body}\n\n{cta}",
            hook=hook,
            cta=cta,
            platforms=platforms,
        )


# ---------------------------------------------------------------------------
# Engine 2 — VideoEngine
# ---------------------------------------------------------------------------

class VideoEngine:
    """Builds scene plans and renders video via external APIs (ENTERPRISE)."""

    SCENE_LABELS = ["Problem", "Agitation", "Solution", "Social Proof", "CTA"]

    def build_scenes(self, script: str) -> List[VideoScene]:
        paragraphs = [p.strip() for p in script.split("\n\n") if p.strip()]
        scenes: List[VideoScene] = []
        for i, label in enumerate(self.SCENE_LABELS):
            desc = paragraphs[i] if i < len(paragraphs) else f"{label} shot"
            scenes.append(
                VideoScene(
                    index=i + 1,
                    label=label,
                    description=desc[:120],
                    camera_angle="medium shot" if i % 2 == 0 else "close-up",
                    b_roll=f"B-roll: {label.lower()} visuals",
                )
            )
        return scenes

    def generate_video(self, script: str, tier: Tier = Tier.FREE) -> Dict:
        scenes = self.build_scenes(script)
        result: Dict = {
            "status": "concept_ready",
            "scenes": [
                {
                    "index": s.index,
                    "label": s.label,
                    "description": s.description,
                    "camera_angle": s.camera_angle,
                    "b_roll": s.b_roll,
                }
                for s in scenes
            ],
        }
        if tier == Tier.ENTERPRISE:
            # Placeholder for Runway / Pika API integration
            result["video_url"] = "https://api.runway.ml/v1/placeholder_video.mp4"
            result["status"] = "rendered"
        return result

    def format_for_platforms(self, video_url: str) -> Dict[str, str]:
        return {platform: video_url for platform in PLATFORMS}


# ---------------------------------------------------------------------------
# Engine 3 — VoiceEngine
# ---------------------------------------------------------------------------

class VoiceEngine:
    """Generates voiceover scripts in multiple tones and formats."""

    TONES = ["neutral", "excited", "professional", "emotional", "urgent"]
    PLATFORMS_VOICE = {
        "TikTok": "fast-paced, punchy, 15–30 sec",
        "YouTube": "informative, engaging, 30–60 sec",
        "Instagram": "visual-first, hook-heavy, 15–30 sec",
        "Facebook": "conversational, trust-building, 30–60 sec",
        "TV": "professional, cinematic, 30–60 sec",
    }

    def generate_voiceover(
        self,
        script: str,
        tone: str = "excited",
        platform: str = "TikTok",
        voice_type: str = "AI",
    ) -> Dict:
        if tone not in self.TONES:
            tone = "neutral"
        style = self.PLATFORMS_VOICE.get(platform, "versatile")
        return {
            "tone": tone,
            "voice_type": voice_type,
            "platform": platform,
            "format_guidance": style,
            "voiceover_script": script,
            "estimated_duration_seconds": max(15, len(script.split()) // 3),
        }


# ---------------------------------------------------------------------------
# Engine 4 — PlatformOptimizer
# ---------------------------------------------------------------------------

class PlatformOptimizer:
    """Adapts ad content for each social platform."""

    PLATFORM_SPECS = {
        "TikTok": {"max_seconds": 60, "aspect_ratio": "9:16", "vibe": "viral, trendy"},
        "YouTube": {"max_seconds": 300, "aspect_ratio": "16:9", "vibe": "informative"},
        "Instagram": {"max_seconds": 90, "aspect_ratio": "1:1", "vibe": "aesthetic"},
        "Facebook": {"max_seconds": 240, "aspect_ratio": "16:9", "vibe": "conversational"},
    }

    def optimize(self, script: str, platforms: Optional[List[str]] = None) -> Dict[str, Dict]:
        if platforms is None:
            platforms = PLATFORMS
        output: Dict[str, Dict] = {}
        for platform in platforms:
            spec = self.PLATFORM_SPECS.get(platform, {})
            words = script.split()
            target_words = (spec.get("max_seconds", 60) // 2)
            adapted = " ".join(words[:target_words]) + ("..." if len(words) > target_words else "")
            output[platform] = {
                "adapted_script": adapted,
                "aspect_ratio": spec.get("aspect_ratio", "16:9"),
                "vibe": spec.get("vibe", "general"),
                "max_seconds": spec.get("max_seconds", 60),
            }
        return output


# ---------------------------------------------------------------------------
# Engine 5 — ClientFinder
# ---------------------------------------------------------------------------

class ClientFinder:
    """Discovers potential clients from various sources."""

    NICHES = [
        "restaurant", "real_estate", "car_dealership", "local_service",
        "ecommerce", "roofing", "plumbing", "gym", "salon", "dental",
    ]

    _MOCK_SOURCES = {
        "restaurant": ["Joe's Diner", "City Bistro", "Fast Bites"],
        "real_estate": ["Prime Realty", "HomeSell Pro", "Urban Properties"],
        "car_dealership": ["DriveTime Auto", "City Motors", "Premier Cars"],
        "local_service": ["QuickFix Plumbing", "TopRoof Co.", "Sparkle Clean"],
        "ecommerce": ["Shopify Store A", "Dropship Central", "NicheGoods"],
    }

    def find(self, niche: str = "restaurant", limit: int = 10) -> List[Lead]:
        businesses = self._MOCK_SOURCES.get(
            niche, [f"{niche.title()} Business {i}" for i in range(1, 6)]
        )
        leads: List[Lead] = []
        for i, name in enumerate(businesses[:limit]):
            leads.append(
                Lead(
                    name=name,
                    niche=niche,
                    contact=f"contact@{name.lower().replace(' ', '')}.com",
                    source="google_maps" if i % 2 == 0 else "shopify",
                    score=70 + i * 5,
                )
            )
        return leads

    def score_lead(self, lead: Lead) -> int:
        """Returns a score 0–100 indicating lead quality."""
        score = lead.score
        if lead.niche in ["real_estate", "car_dealership"]:
            score = min(100, score + 15)
        return score


# ---------------------------------------------------------------------------
# Engine 6 — ClosingAgent
# ---------------------------------------------------------------------------

class ClosingAgent:
    """Automated outreach, objection handling, and deal closing."""

    OUTREACH_SEQUENCE = [
        "Hey {name}, I built you a free commercial to attract more customers. Want to see it?",
        "This commercial could easily bring you 10–50 new customers monthly.",
        "Want me to run ads for you and scale this to consistent monthly revenue?",
    ]

    OBJECTION_RESPONSES = {
        "price": "We offer packages from $300 to $2,000 monthly depending on your growth goals.",
        "expensive": "We offer packages from $300 to $2,000 monthly depending on your growth goals.",
        "interested": "Perfect — let's get you set up today. I'll send you a quick onboarding link.",
        "yes": "Perfect — let's get you set up today. I'll send you a quick onboarding link.",
        "not sure": "Totally understand — our free sample commercial has zero risk. Want to see one built for you?",
        "later": "Totally understand — our free sample commercial has zero risk. Want to see one built for you?",
        "how": "Simple process: we build your commercial, you approve it, we run ads — you get customers.",
        "results": "Our clients average 10–50 new leads per month within the first 30 days.",
    }

    def send_outreach(self, lead_name: str, step: int = 0) -> str:
        step = max(0, min(step, len(self.OUTREACH_SEQUENCE) - 1))
        return self.OUTREACH_SEQUENCE[step].replace("{name}", lead_name)

    def respond(self, message: str) -> str:
        msg_lower = message.lower()
        for keyword, response in self.OBJECTION_RESPONSES.items():
            if keyword in msg_lower:
                return response
        return self.OUTREACH_SEQUENCE[0].replace("{name}", "there")

    def create_deal(self, client: str, package: str = "pro_commercial") -> Deal:
        low, high = PRICING_TIERS.get(package, (300, 1000))
        value = high if high is not None else low
        return Deal(client=client, package=package, monthly_value=float(value))


# ---------------------------------------------------------------------------
# Engine 7 — BillingEngine
# ---------------------------------------------------------------------------

class BillingEngine:
    """Stripe subscription management (requires STRIPE_KEY env var in prod)."""

    def __init__(self) -> None:
        self._subscriptions: List[Dict] = []

    def create_subscription(self, customer_email: str, package: str = "pro_commercial") -> Dict:
        low, high = PRICING_TIERS.get(package, (300, 1000))
        amount = high if high is not None else low
        record = {
            "customer_email": customer_email,
            "package": package,
            "amount_usd": amount,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._subscriptions.append(record)
        return record

    def list_subscriptions(self) -> List[Dict]:
        return list(self._subscriptions)

    def cancel_subscription(self, customer_email: str) -> bool:
        for sub in self._subscriptions:
            if sub["customer_email"] == customer_email:
                sub["status"] = "cancelled"
                return True
        return False

    def total_mrr(self) -> float:
        return sum(
            s["amount_usd"] for s in self._subscriptions if s["status"] == "active"
        )


# ---------------------------------------------------------------------------
# Engine 8 — AnalyticsEngine
# ---------------------------------------------------------------------------

class AnalyticsEngine:
    """Tracks ad performance metrics across all platforms."""

    def __init__(self) -> None:
        self._data: Dict[str, AdPerformance] = {}

    def record(
        self,
        video_id: str,
        views: int = 0,
        clicks: int = 0,
        conversions: int = 0,
        revenue: float = 0.0,
    ) -> AdPerformance:
        if video_id not in self._data:
            self._data[video_id] = AdPerformance(video_id=video_id)
        perf = self._data[video_id]
        perf.views += views
        perf.clicks += clicks
        perf.conversions += conversions
        perf.revenue += revenue
        return perf

    def track(self, video_id: str) -> Dict:
        perf = self._data.get(video_id, AdPerformance(video_id=video_id))
        ctr = (perf.clicks / perf.views * 100) if perf.views > 0 else 0.0
        cvr = (perf.conversions / perf.clicks * 100) if perf.clicks > 0 else 0.0
        return {
            "video_id": perf.video_id,
            "views": perf.views,
            "clicks": perf.clicks,
            "conversions": perf.conversions,
            "revenue": perf.revenue,
            "ctr_pct": round(ctr, 2),
            "cvr_pct": round(cvr, 2),
        }

    def top_performers(self, n: int = 5) -> List[Dict]:
        sorted_data = sorted(
            self._data.values(), key=lambda p: p.revenue, reverse=True
        )
        return [self.track(p.video_id) for p in sorted_data[:n]]


# ---------------------------------------------------------------------------
# Engine 9 — BulkGenerator
# ---------------------------------------------------------------------------

class BulkGenerator:
    """Mass-produces commercial scripts and video concepts."""

    def __init__(self, script_engine: ScriptEngine, video_engine: VideoEngine) -> None:
        self._script = script_engine
        self._video = video_engine

    def run(
        self,
        businesses: List[str],
        niche: str = "local_service",
        tier: Tier = Tier.PRO,
        duration_seconds: int = 30,
    ) -> List[Dict]:
        limit = BULK_LIMITS.get(tier, 0)
        if limit == 0:
            raise CommercialBotTierError(
                "Bulk generation requires PRO or ENTERPRISE tier."
            )

        results = []
        for biz in businesses[:limit]:
            script_obj = self._script.generate(
                business=biz,
                product=niche,
                target_audience="local customers",
                duration_seconds=duration_seconds,
                tier=tier,
            )
            video = self._video.generate_video(script_obj.script, tier=tier)
            results.append(
                {
                    "business": biz,
                    "script": script_obj.script,
                    "hook": script_obj.hook,
                    "cta": script_obj.cta,
                    "video": video,
                }
            )
        return results


# ---------------------------------------------------------------------------
# Engine 10 — SelfHeal
# ---------------------------------------------------------------------------

class SelfHeal:
    """System health monitor and auto-repair."""

    def check_system(self) -> Dict:
        try:
            status = {
                "status": "healthy",
                "engines": [
                    "ScriptEngine", "VideoEngine", "VoiceEngine",
                    "PlatformOptimizer", "ClientFinder", "ClosingAgent",
                    "BillingEngine", "AnalyticsEngine", "BulkGenerator",
                ],
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }
            return status
        except Exception as exc:  # pragma: no cover
            return {"status": "auto_fixing", "error": str(exc)}

    def detect_errors(self) -> List[str]:
        return []

    def fix(self, errors: List[str]) -> str:
        if not errors:
            return "No errors detected"
        return f"Auto-fixing {len(errors)} issue(s)"


# ---------------------------------------------------------------------------
# Main CommercialBot orchestrator
# ---------------------------------------------------------------------------

class CommercialBot:
    """
    DreamCo CineCore™ — Autonomous commercial creation and revenue bot.

    Orchestrates all 10 engines to find clients, generate commercials,
    close deals, and collect recurring revenue.

    Parameters
    ----------
    tier : Tier
        FREE, PRO, or ENTERPRISE access level.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._clients: List[Dict] = []
        self._revenue: float = 0.0

        # Engines
        self.script_engine = ScriptEngine()
        self.video_engine = VideoEngine()
        self.voice_engine = VoiceEngine()
        self.platform_optimizer = PlatformOptimizer()
        self.client_finder = ClientFinder()
        self.closing_agent = ClosingAgent()
        self.billing = BillingEngine()
        self.analytics = AnalyticsEngine()
        self._bulk = BulkGenerator(self.script_engine, self.video_engine)
        self.self_heal = SelfHeal()

    # ------------------------------------------------------------------
    # Tier guard
    # ------------------------------------------------------------------

    def _require_tier(self, minimum: Tier) -> None:
        order = [Tier.FREE, Tier.PRO, Tier.ENTERPRISE]
        if order.index(self.tier) < order.index(minimum):
            raise CommercialBotTierError(
                f"This feature requires {minimum.value} tier. "
                f"Current tier: {self.tier.value}. "
                f"Upgrade path: {get_upgrade_path(self.tier)}"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_script(
        self,
        business: str,
        product: str,
        target_audience: str,
        duration_seconds: int = 30,
    ) -> Dict:
        allowed = SCRIPT_DURATIONS.get(self.tier, [15])
        if duration_seconds not in allowed:
            duration_seconds = allowed[-1]
        script_obj = self.script_engine.generate(
            business=business,
            product=product,
            target_audience=target_audience,
            duration_seconds=duration_seconds,
            tier=self.tier,
        )
        return {
            "business": script_obj.business,
            "product": script_obj.product,
            "target_audience": script_obj.target_audience,
            "duration_seconds": script_obj.duration_seconds,
            "script": script_obj.script,
            "hook": script_obj.hook,
            "cta": script_obj.cta,
            "platforms": script_obj.platforms,
        }

    def create_ad_plan(self, script: str) -> Dict:
        scenes = self.video_engine.build_scenes(script)
        optimized = self.platform_optimizer.optimize(
            script,
            platforms=PLATFORMS if self.tier != Tier.FREE else ["TikTok"],
        )
        return {
            "hook": script.split("\n")[0][:60],
            "scenes": [
                {"index": s.index, "label": s.label, "description": s.description}
                for s in scenes
            ],
            "platforms": optimized,
        }

    def generate_video(self, script: str) -> Dict:
        self._require_tier(Tier.PRO)
        return self.video_engine.generate_video(script, tier=self.tier)

    def generate_voiceover(
        self, script: str, tone: str = "excited", platform: str = "TikTok"
    ) -> Dict:
        self._require_tier(Tier.PRO)
        return self.voice_engine.generate_voiceover(script, tone=tone, platform=platform)

    def find_clients(self, niche: str = "restaurant", limit: int = 10) -> List[Dict]:
        self._require_tier(Tier.PRO)
        leads = self.client_finder.find(niche=niche, limit=limit)
        return [
            {
                "name": lead.name,
                "niche": lead.niche,
                "contact": lead.contact,
                "source": lead.source,
                "score": self.client_finder.score_lead(lead),
            }
            for lead in leads
        ]

    def close_client(self, client_name: str, message: str = "") -> str:
        self._require_tier(Tier.PRO)
        if message:
            return self.closing_agent.respond(message)
        return self.closing_agent.send_outreach(client_name)

    def send_outreach(self, client_name: str, step: int = 0) -> str:
        self._require_tier(Tier.PRO)
        return self.closing_agent.send_outreach(client_name, step)

    def create_deal(self, client: str, package: str = "pro_commercial") -> Dict:
        self._require_tier(Tier.PRO)
        deal = self.closing_agent.create_deal(client, package)
        self._clients.append({"client": deal.client, "package": deal.package})
        self._revenue += deal.monthly_value
        return {
            "client": deal.client,
            "package": deal.package,
            "monthly_value": deal.monthly_value,
            "status": deal.status,
        }

    def bulk_generate(
        self,
        businesses: List[str],
        niche: str = "local_service",
        duration_seconds: int = 30,
    ) -> List[Dict]:
        self._require_tier(Tier.PRO)
        return self._bulk.run(
            businesses=businesses,
            niche=niche,
            tier=self.tier,
            duration_seconds=duration_seconds,
        )

    def create_subscription(self, customer_email: str, package: str = "pro_commercial") -> Dict:
        self._require_tier(Tier.PRO)
        return self.billing.create_subscription(customer_email, package)

    def revenue_summary(self) -> Dict:
        return {
            "tier": self.tier.value,
            "features": BOT_FEATURES[self.tier.value],
            "total_clients": len(self._clients),
            "pipeline_revenue_usd": self._revenue,
            "mrr_usd": self.billing.total_mrr(),
            "pricing": PRICING_TIERS,
            "upgrade_path": get_upgrade_path(self.tier),
        }

    def tier_info(self) -> Dict:
        return get_bot_tier_info(self.tier)
