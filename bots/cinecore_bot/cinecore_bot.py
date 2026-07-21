"""
DreamCo CineCore Bot — AI-Powered Commercial & Video Creation System.

Automates the full lifecycle of AI-powered commercials and video content:

  1. 🧠 ScriptEngine       — Hook, emotional triggers, and CTA generation
  2. 🎥 VideoEngine        — AI video generation (Runway AI, Pika Labs)
  3. 🔊 VoiceEngine        — Voiceovers with emotional tone control
  4. 📱 PlatformOptimizer  — Multi-platform ad formatting and distribution
  5. 🔍 LeadEngine         — Legal lead generation with public business APIs
  6. 🤖 ClosingAgent       — AI-powered client communication and deal closing
  7. 💳 BillingEngine      — Stripe integration for auto billing + subscriptions
  8. 📊 AnalyticsEngine    — Ad performance tracking and revenue analytics
  9. ⚡ BulkGenerator      — Mass commercial production engine
 10. 🛡️  SelfHeal           — Auto-detection and fixing of system issues

Usage
-----
    from bots.cinecore_bot import CineCoreBot
    from tiers import Tier

    bot = CineCoreBot(tier=Tier.PRO)

    # Generate a commercial script
    script = bot.generate_script("Local Cafe", "specialty coffee", "young professionals")

    # Generate a video from the script
    video = bot.generate_video(script["script"])

    # Find and score leads
    leads = bot.find_leads("restaurant near me")
    scored = bot.score_leads(leads)

    # Generate outreach for a lead (human-in-loop approval)
    outreach = bot.generate_outreach(leads[0])

    # Create a Stripe subscription
    subscription = bot.create_subscription("client@example.com")

    # Get analytics
    analytics = bot.get_analytics("video_001")

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import random
import sys
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.cinecore_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class CineCoreBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class CineCoreBotError(Exception):
    """General CineCore bot error."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_PLATFORMS = ["tiktok", "youtube", "instagram", "facebook"]
SUPPORTED_VOICE_TONES = ["neutral", "excited", "serious", "warm", "urgent"]
SUPPORTED_GENRES = ["ad", "documentary", "biography", "viral", "product_promo"]
HIGH_OPPORTUNITY_SCORE = 70
SCRIPT_DAILY_LIMIT_FREE = 5
SCRIPT_DAILY_LIMIT_PRO = 50
LEAD_DAILY_LIMIT_FREE = 3
LEAD_DAILY_LIMIT_PRO = 50
BULK_LIMIT_PRO = 20


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CommercialScript:
    """A generated commercial script with all components."""
    business_name: str
    product: str
    target_audience: str
    hook: str
    body: str
    cta: str
    script: str
    platforms: List[str]
    genre: str = "ad"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    script_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> dict:
        return {
            "script_id": self.script_id,
            "business_name": self.business_name,
            "product": self.product,
            "target_audience": self.target_audience,
            "hook": self.hook,
            "body": self.body,
            "cta": self.cta,
            "script": self.script,
            "platforms": self.platforms,
            "genre": self.genre,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class VideoAsset:
    """A generated video asset."""
    script_id: str
    video_url: str
    provider: str
    duration_seconds: int
    platforms: Dict[str, str] = field(default_factory=dict)
    status: str = "processing"
    video_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "script_id": self.script_id,
            "video_url": self.video_url,
            "provider": self.provider,
            "duration_seconds": self.duration_seconds,
            "platforms": self.platforms,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class LeadRecord:
    """A business lead found via the lead engine."""
    name: str
    business_type: str
    location: str
    rating: float = 0.0
    opportunity_score: int = 0
    contact_info: str = ""
    lead_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> dict:
        return {
            "lead_id": self.lead_id,
            "name": self.name,
            "business_type": self.business_type,
            "location": self.location,
            "rating": self.rating,
            "opportunity_score": self.opportunity_score,
            "contact_info": self.contact_info,
        }


@dataclass
class AnalyticsRecord:
    """Performance metrics for a video asset."""
    video_id: str
    views: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue_usd: float = 0.0
    platform: str = "all"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "views": self.views,
            "clicks": self.clicks,
            "conversions": self.conversions,
            "revenue_usd": self.revenue_usd,
            "platform": self.platform,
            "ctr": round(self.clicks / self.views, 4) if self.views > 0 else 0.0,
            "cvr": round(self.conversions / self.clicks, 4) if self.clicks > 0 else 0.0,
            "timestamp": self.timestamp.isoformat(),
        }


# ---------------------------------------------------------------------------
# Sub-engines
# ---------------------------------------------------------------------------

class ScriptEngine:
    """
    Generates commercial scripts with hooks, emotional triggers, and CTAs.

    FREE:       up to SCRIPT_DAILY_LIMIT_FREE scripts/day, basic templates.
    PRO:        up to SCRIPT_DAILY_LIMIT_PRO scripts/day, emotional storytelling.
    ENTERPRISE: unlimited, full cinematic + biography modes.
    """

    HOOKS = {
        "ad": [
            "STOP wasting money on ads that don't convert.",
            "What if you could 10x your customers this month?",
            "This one change brought {business} 50 new clients.",
        ],
        "viral": [
            "You won't believe what happened next...",
            "Everyone in {location} is talking about this.",
            "This video changed everything for {business}.",
        ],
        "biography": [
            "The story of {business} started with a single dream.",
            "From zero to industry leader — the {business} journey.",
            "Meet the team behind {business}.",
        ],
        "documentary": [
            "Behind the scenes of {business}.",
            "The untold story of {product}.",
            "What really goes into making {product}?",
        ],
        "product_promo": [
            "Introducing {product} — built for {target_audience}.",
            "{product}: the solution {target_audience} has been waiting for.",
            "Finally, a {product} that actually works.",
        ],
    }

    CTAs = [
        "Click now before it's gone.",
        "Visit us today and get started.",
        "Call us now for a free consultation.",
        "Sign up today and get your first month free.",
        "Limited spots available — book yours now.",
    ]

    def __init__(self, tier: Tier) -> None:
        self.tier = tier
        self._scripts_today: int = 0

    @property
    def daily_limit(self) -> int:
        if self.tier == Tier.FREE:
            return SCRIPT_DAILY_LIMIT_FREE
        if self.tier == Tier.PRO:
            return SCRIPT_DAILY_LIMIT_PRO
        return 999_999  # ENTERPRISE: unlimited

    def generate(
        self,
        business_name: str,
        product: str,
        target_audience: str,
        genre: str = "ad",
    ) -> CommercialScript:
        """Generate a complete commercial script."""
        if self._scripts_today >= self.daily_limit:
            raise CineCoreBotTierError(
                f"Daily script limit ({self.daily_limit}) reached. Upgrade your tier."
            )
        if genre not in SUPPORTED_GENRES:
            raise CineCoreBotError(
                f"Genre '{genre}' not supported. Choose from: {SUPPORTED_GENRES}"
            )

        hook_templates = self.HOOKS.get(genre, self.HOOKS["ad"])
        hook = hook_templates[0].format(
            business=business_name,
            product=product,
            target_audience=target_audience,
            location="your area",
        )

        if self.tier == Tier.FREE:
            body = (
                f"Stop struggling with your needs. {business_name} helps you win. "
                f"Our {product} is designed for {target_audience}."
            )
        else:
            body = (
                f"Imagine getting the results you've always wanted without the usual pain. "
                f"{business_name} delivers {product} built specifically for "
                f"{target_audience}. Real results, real fast."
            )

        cta = self.CTAs[self._scripts_today % len(self.CTAs)]

        script_text = f"{hook}\n\n{body}\n\n{cta}"

        platforms = ["tiktok"]
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            platforms = SUPPORTED_PLATFORMS[:]

        result = CommercialScript(
            business_name=business_name,
            product=product,
            target_audience=target_audience,
            hook=hook,
            body=body,
            cta=cta,
            script=script_text,
            platforms=platforms,
            genre=genre,
        )

        self._scripts_today += 1
        return result

    def reset_daily_counter(self) -> None:
        """Reset the daily script generation counter (called by scheduler)."""
        self._scripts_today = 0


class VideoEngine:
    """
    AI video generation using Runway AI and Pika Labs (simulated).

    FREE:       not available.
    PRO:        Runway or Pika generation, up to 15-second clips.
    ENTERPRISE: full Runway + Pika, up to 60-second clips, movie mode.
    """

    PROVIDERS = {
        Tier.FREE: [],
        Tier.PRO: ["runway", "pika"],
        Tier.ENTERPRISE: ["runway", "pika", "custom"],
    }

    def __init__(self, tier: Tier) -> None:
        self.tier = tier

    @property
    def available_providers(self) -> List[str]:
        return self.PROVIDERS.get(self.tier, [])

    @property
    def max_duration(self) -> int:
        if self.tier == Tier.ENTERPRISE:
            return 60
        if self.tier == Tier.PRO:
            return 15
        return 0

    def generate(
        self,
        script: str,
        provider: str = "runway",
        duration: int = 15,
    ) -> VideoAsset:
        """Generate a video from a script using the specified AI provider."""
        if not self.available_providers:
            raise CineCoreBotTierError(
                "Video generation requires PRO or ENTERPRISE tier."
            )
        if provider not in self.available_providers:
            raise CineCoreBotError(
                f"Provider '{provider}' not available on {self.tier.value} tier. "
                f"Available: {self.available_providers}"
            )
        if duration > self.max_duration:
            raise CineCoreBotTierError(
                f"Duration {duration}s exceeds {self.tier.value} tier limit "
                f"of {self.max_duration}s."
            )

        # Simulated API call to Runway / Pika
        # In production: POST to https://api.runwayml.com/v1/generate
        # or https://api.pika.art/generate with the script prompt
        script_preview = script[:80].replace("\n", " ")
        video_url = f"https://dreamco-cdn.example.com/videos/{provider}/{uuid.uuid4().hex[:12]}.mp4"

        platforms = {
            "tiktok": video_url,
            "instagram": video_url,
            "youtube": video_url,
            "facebook": video_url,
        }

        return VideoAsset(
            script_id=str(uuid.uuid4())[:8],
            video_url=video_url,
            provider=provider,
            duration_seconds=duration,
            platforms=platforms,
            status="ready",
        )

    def format_for_platforms(self, video_asset: VideoAsset) -> dict:
        """Return platform-specific video URLs."""
        return dict(video_asset.platforms)


class VoiceEngine:
    """
    Voiceover generation with emotional tone control.

    FREE:       neutral tone only.
    PRO:        all tones, male/female/AI voices, platform-ready formats.
    ENTERPRISE: voice cloning + multi-language dubbing.
    """

    VOICES = ["male", "female", "ai_neutral", "ai_warm", "ai_energetic"]

    def __init__(self, tier: Tier) -> None:
        self.tier = tier

    @property
    def available_tones(self) -> List[str]:
        if self.tier == Tier.FREE:
            return ["neutral"]
        return SUPPORTED_VOICE_TONES[:]

    @property
    def available_voices(self) -> List[str]:
        if self.tier == Tier.FREE:
            return ["ai_neutral"]
        if self.tier == Tier.PRO:
            return self.VOICES[:3]
        return self.VOICES[:]

    def generate(
        self,
        script: str,
        voice: str = "ai_neutral",
        tone: str = "neutral",
        platform: str = "tiktok",
    ) -> dict:
        """Generate a voiceover for the given script."""
        if tone not in self.available_tones:
            raise CineCoreBotTierError(
                f"Tone '{tone}' requires PRO or ENTERPRISE tier."
            )
        if voice not in self.available_voices:
            raise CineCoreBotTierError(
                f"Voice '{voice}' not available on {self.tier.value} tier."
            )

        audio_url = (
            f"https://dreamco-cdn.example.com/audio/{voice}/{tone}/"
            f"{uuid.uuid4().hex[:12]}.mp3"
        )

        return {
            "audio_url": audio_url,
            "voice": voice,
            "tone": tone,
            "platform": platform,
            "duration_estimate_seconds": max(10, len(script.split()) // 3),
            "status": "ready",
        }

    def clone_voice(self, sample_audio_url: str, script: str) -> dict:
        """Clone a voice from a sample and generate voiceover (ENTERPRISE only)."""
        if self.tier != Tier.ENTERPRISE:
            raise CineCoreBotTierError("Voice cloning requires ENTERPRISE tier.")
        return {
            "audio_url": f"https://dreamco-cdn.example.com/audio/cloned/{uuid.uuid4().hex[:12]}.mp3",
            "source_sample": sample_audio_url,
            "status": "ready",
        }


class PlatformOptimizer:
    """
    Formats and distributes ads across TikTok, YouTube, Instagram, Facebook.

    FREE:       TikTok only.
    PRO:        all 4 platforms.
    ENTERPRISE: all platforms + custom scheduling + auto-posting.
    """

    PLATFORM_SPECS = {
        "tiktok":    {"max_duration": 60,  "aspect_ratio": "9:16", "format": "mp4"},
        "youtube":   {"max_duration": 60,  "aspect_ratio": "16:9", "format": "mp4"},
        "instagram": {"max_duration": 60,  "aspect_ratio": "1:1",  "format": "mp4"},
        "facebook":  {"max_duration": 240, "aspect_ratio": "16:9", "format": "mp4"},
    }

    def __init__(self, tier: Tier) -> None:
        self.tier = tier

    @property
    def available_platforms(self) -> List[str]:
        if self.tier == Tier.FREE:
            return ["tiktok"]
        return SUPPORTED_PLATFORMS[:]

    def optimize(self, video_asset: VideoAsset) -> dict:
        """Return platform-optimized versions of the video."""
        optimized: dict = {}
        for platform in self.available_platforms:
            spec = self.PLATFORM_SPECS[platform]
            optimized[platform] = {
                "video_url": video_asset.video_url,
                "aspect_ratio": spec["aspect_ratio"],
                "format": spec["format"],
                "max_duration": spec["max_duration"],
                "status": "optimized",
            }
        return optimized

    def auto_post(self, video_asset: VideoAsset, caption: str = "") -> dict:
        """Simulate auto-posting to all available platforms (ENTERPRISE: scheduled)."""
        if self.tier == Tier.FREE:
            raise CineCoreBotTierError("Auto-posting requires PRO or ENTERPRISE tier.")
        results: dict = {}
        for platform in self.available_platforms:
            results[platform] = {
                "status": "posted",
                "video_url": video_asset.video_url,
                "caption": caption,
                "posted_at": datetime.now(timezone.utc).isoformat(),
            }
        return results


class LeadEngine:
    """
    Legal lead generation using public business directories / APIs.

    Searches public sources (Google Places API style) and filters businesses
    with weak marketing potential.  Always operates in human-in-the-loop mode
    for outreach (no unsolicited spam automation).

    FREE:       up to LEAD_DAILY_LIMIT_FREE searches/day.
    PRO:        up to LEAD_DAILY_LIMIT_PRO searches/day with scoring.
    ENTERPRISE: unlimited searches + advanced filtering.
    """

    # Simulated public business data (replaces live API in tests)
    _SAMPLE_BUSINESSES = [
        {"name": "Joe's Diner",      "type": "restaurant",   "rating": 3.1, "location": "downtown"},
        {"name": "AutoFix Pro",      "type": "auto_service", "rating": 2.8, "location": "westside"},
        {"name": "Sunset Realty",    "type": "real_estate",  "rating": 3.5, "location": "suburbs"},
        {"name": "CurlsNMore Salon", "type": "beauty",       "rating": 3.8, "location": "midtown"},
        {"name": "QuickPlumb Co",    "type": "plumbing",     "rating": 2.5, "location": "eastside"},
        {"name": "TechStart LLC",    "type": "tech",         "rating": 4.5, "location": "downtown"},
        {"name": "Green Lawn Care",  "type": "landscaping",  "rating": 3.2, "location": "suburbs"},
        {"name": "FitLife Gym",      "type": "fitness",      "rating": 3.7, "location": "northside"},
    ]

    HIGH_VALUE_TYPES = {"restaurant", "real_estate", "auto_service", "plumbing", "roofing"}

    def __init__(self, tier: Tier) -> None:
        self.tier = tier
        self._searches_today: int = 0

    @property
    def daily_limit(self) -> int:
        if self.tier == Tier.FREE:
            return LEAD_DAILY_LIMIT_FREE
        if self.tier == Tier.PRO:
            return LEAD_DAILY_LIMIT_PRO
        return 999_999

    def search(self, query: str = "business near me") -> List[LeadRecord]:
        """Search for public business leads matching the query."""
        if self._searches_today >= self.daily_limit:
            raise CineCoreBotTierError(
                f"Daily lead search limit ({self.daily_limit}) reached. Upgrade your tier."
            )
        self._searches_today += 1

        # Simulated: filter sample businesses by query keywords
        query_lower = query.lower()
        results = []
        for biz in self._SAMPLE_BUSINESSES:
            if (
                query_lower in biz["name"].lower()
                or query_lower in biz["type"].lower()
                or query_lower in biz["location"].lower()
                or "near me" in query_lower
                or "business" in query_lower
            ):
                results.append(
                    LeadRecord(
                        name=biz["name"],
                        business_type=biz["type"],
                        location=biz["location"],
                        rating=biz["rating"],
                    )
                )
        return results

    def filter_weak_marketing(self, leads: List[LeadRecord]) -> List[LeadRecord]:
        """Return only leads with rating < 4.0 (likely weak marketing)."""
        return [lead for lead in leads if lead.rating < 4.0]

    def reset_daily_counter(self) -> None:
        self._searches_today = 0


class BusinessScorer:
    """
    Scores and ranks business leads by marketing opportunity.

    Higher score = higher opportunity for a commercial campaign.
    """

    BASE_SCORE = 100

    def score(self, lead: LeadRecord) -> int:
        """Calculate opportunity score for a lead."""
        score = self.BASE_SCORE

        # Low rating = poor marketing = opportunity
        if lead.rating < 3.0:
            score += 40
        elif lead.rating < 3.5:
            score += 25
        elif lead.rating < 4.0:
            score += 10

        # High-value business types
        if lead.business_type in LeadEngine.HIGH_VALUE_TYPES:
            score += 30

        return min(score, 200)  # Cap at 200

    def rank(self, leads: List[LeadRecord]) -> List[LeadRecord]:
        """Return leads sorted by opportunity score (highest first)."""
        scored = []
        for lead in leads:
            lead.opportunity_score = self.score(lead)
            scored.append(lead)
        return sorted(scored, key=lambda l: l.opportunity_score, reverse=True)


class ClosingAgent:
    """
    AI-powered client communication and deal closing.

    Always operates in human-in-the-loop mode — generates outreach drafts
    for human approval rather than sending automatically.

    FREE:       basic response templates.
    PRO:        objection handling + upsell scripts.
    ENTERPRISE: full deal-closing pipeline + AI negotiation.
    """

    OUTREACH_TEMPLATES = {
        "initial": (
            "Hi {name},\n\n"
            "I noticed your business and created a free AI commercial to help you "
            "attract more customers. This could easily bring you 10–50 new clients monthly.\n\n"
            "Would you like to see it? No strings attached.\n\n"
            "Best,\nDreamCo CineCore"
        ),
        "follow_up": (
            "Hi {name},\n\n"
            "Just following up — I finished your free commercial demo. "
            "Businesses like yours typically see a 30% increase in foot traffic with "
            "targeted video ads.\n\n"
            "Want me to send it over?\n\nBest,\nDreamCo CineCore"
        ),
        "close": (
            "Hi {name},\n\n"
            "Ready to launch your ad campaign? We offer packages starting at $300/month "
            "that include full ad creation, distribution, and analytics.\n\n"
            "Shall we get started today?\n\nBest,\nDreamCo CineCore"
        ),
    }

    OBJECTION_RESPONSES = {
        "price": (
            "We completely understand budget concerns. Our packages scale with your results — "
            "you only pay for ads that bring you customers. We offer a 30-day money-back "
            "guarantee too."
        ),
        "time": (
            "That's exactly why we handle everything. You'll spend zero time on this — "
            "we create, post, and track all your ads automatically."
        ),
        "interested": (
            "Fantastic! Let's get you set up today. I'll send over a quick onboarding form "
            "and we can launch your first campaign within 48 hours."
        ),
        "not_interested": (
            "No problem at all. If anything changes, we're always here. "
            "Your free commercial demo will be ready whenever you want it."
        ),
        "default": (
            "Great question! Let me provide more details about how our system can "
            "specifically help your business grow."
        ),
    }

    def __init__(self, tier: Tier) -> None:
        self.tier = tier

    def generate_outreach(self, lead: LeadRecord, template: str = "initial") -> dict:
        """
        Generate an outreach message draft for human review and approval.

        This is NOT an automated sender — always requires human approval.
        """
        if template not in self.OUTREACH_TEMPLATES:
            template = "initial"

        message = self.OUTREACH_TEMPLATES[template].format(
            name=lead.name,
            type=lead.business_type,
            location=lead.location,
        )

        return {
            "lead_id": lead.lead_id,
            "lead_name": lead.name,
            "template": template,
            "message": message,
            "requires_approval": True,
            "status": "draft",
        }

    def handle_reply(self, reply: str) -> str:
        """Generate a contextual response to a client reply."""
        reply_lower = reply.lower()

        for keyword, response in self.OBJECTION_RESPONSES.items():
            if keyword in reply_lower and keyword != "default":
                return response

        if self.tier == Tier.FREE:
            return self.OBJECTION_RESPONSES["default"]

        # PRO / ENTERPRISE: richer responses
        if "demo" in reply_lower or "sample" in reply_lower:
            return "I'll send your custom demo right away. Expect it within the hour."
        if "contract" in reply_lower or "sign" in reply_lower:
            return (
                "I'll prepare a straightforward agreement for you. "
                "Our contracts are month-to-month with no long-term lock-in."
            )

        return self.OBJECTION_RESPONSES["default"]

    def generate_upsell(self, current_spend: float) -> str:
        """Generate an upsell offer for an existing client (PRO+ only)."""
        if self.tier == Tier.FREE:
            raise CineCoreBotTierError("Upsell generation requires PRO or ENTERPRISE tier.")

        if current_spend < 300:
            return "Upgrade to our Pro package ($500/month) for 5x more ad reach and analytics."
        if current_spend < 1000:
            return "Our Enterprise plan ($2,000/month) includes unlimited ads and a dedicated manager."
        return "You're on our best plan! Refer a friend and get one month free."


class BillingEngine:
    """
    Stripe integration for auto billing and subscription management.

    FREE:       view pricing only.
    PRO:        create customers and subscriptions.
    ENTERPRISE: full billing management, invoicing, refunds.
    """

    PLANS = {
        "basic":      {"name": "Basic Ad",         "price_usd": 150.0,   "interval": "one-time"},
        "pro":        {"name": "Pro Commercial",   "price_usd": 500.0,   "interval": "monthly"},
        "enterprise": {"name": "Monthly Ads Pack", "price_usd": 2000.0,  "interval": "monthly"},
    }

    def __init__(self, tier: Tier) -> None:
        self.tier = tier

    def list_plans(self) -> List[dict]:
        """Return available billing plans."""
        return [{"plan_id": k, **v} for k, v in self.PLANS.items()]

    def create_customer(self, email: str) -> dict:
        """Create a Stripe customer record (simulated)."""
        if self.tier == Tier.FREE:
            raise CineCoreBotTierError("Billing management requires PRO or ENTERPRISE tier.")
        return {
            "customer_id": f"cus_{uuid.uuid4().hex[:14]}",
            "email": email,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def create_subscription(self, email: str, plan: str = "pro") -> dict:
        """Create a Stripe subscription for a customer (simulated)."""
        if self.tier == Tier.FREE:
            raise CineCoreBotTierError("Subscriptions require PRO or ENTERPRISE tier.")
        if plan not in self.PLANS:
            raise CineCoreBotError(f"Plan '{plan}' not found. Available: {list(self.PLANS.keys())}")

        customer = self.create_customer(email)
        plan_info = self.PLANS[plan]

        return {
            "subscription_id": f"sub_{uuid.uuid4().hex[:14]}",
            "customer_id": customer["customer_id"],
            "email": email,
            "plan": plan,
            "plan_name": plan_info["name"],
            "amount_usd": plan_info["price_usd"],
            "interval": plan_info["interval"],
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def cancel_subscription(self, subscription_id: str) -> dict:
        """Cancel an active subscription (ENTERPRISE only)."""
        if self.tier != Tier.ENTERPRISE:
            raise CineCoreBotTierError("Subscription cancellation requires ENTERPRISE tier.")
        return {
            "subscription_id": subscription_id,
            "status": "cancelled",
            "cancelled_at": datetime.now(timezone.utc).isoformat(),
        }


class AnalyticsEngine:
    """
    Ad performance tracking and revenue analytics.

    FREE:       views only.
    PRO:        views, clicks, conversions, revenue per ad.
    ENTERPRISE: full dashboard with trends, ROI, and audience insights.
    """

    def __init__(self, tier: Tier) -> None:
        self.tier = tier
        self._records: List[AnalyticsRecord] = []

    def track(self, video_id: str, platform: str = "all") -> AnalyticsRecord:
        """Simulate fetching analytics for a video asset."""
        random.seed(hash(video_id + platform))

        views = random.randint(100, 50_000)
        clicks = random.randint(5, views // 10) if self.tier != Tier.FREE else 0
        conversions = random.randint(0, clicks // 5) if self.tier != Tier.FREE else 0
        revenue = round(conversions * random.uniform(50, 500), 2) if self.tier != Tier.FREE else 0.0

        record = AnalyticsRecord(
            video_id=video_id,
            views=views,
            clicks=clicks,
            conversions=conversions,
            revenue_usd=revenue,
            platform=platform,
        )
        self._records.append(record)
        return record

    def revenue_summary(self) -> dict:
        """Return aggregated revenue across all tracked videos."""
        total_views = sum(r.views for r in self._records)
        total_revenue = sum(r.revenue_usd for r in self._records)
        total_conversions = sum(r.conversions for r in self._records)

        return {
            "total_videos_tracked": len(self._records),
            "total_views": total_views,
            "total_conversions": total_conversions,
            "total_revenue_usd": round(total_revenue, 2),
            "avg_revenue_per_video": (
                round(total_revenue / len(self._records), 2) if self._records else 0.0
            ),
        }

    def records(self) -> List[dict]:
        return [r.to_dict() for r in self._records]


class BulkGenerator:
    """
    Mass commercial production engine.

    FREE:       single generation only (no bulk).
    PRO:        up to BULK_LIMIT_PRO commercials per run.
    ENTERPRISE: unlimited bulk generation.
    """

    def __init__(self, tier: Tier, script_engine: ScriptEngine, video_engine: VideoEngine) -> None:
        self.tier = tier
        self._script_engine = script_engine
        self._video_engine = video_engine

    @property
    def bulk_limit(self) -> int:
        if self.tier == Tier.FREE:
            return 1
        if self.tier == Tier.PRO:
            return BULK_LIMIT_PRO
        return 999_999

    def run(
        self,
        businesses: List[dict],
        genre: str = "ad",
        include_video: bool = False,
    ) -> List[dict]:
        """
        Generate commercials for a list of businesses.

        Each entry in ``businesses`` should have:
            name, product, target_audience (all strings).
        """
        if len(businesses) > self.bulk_limit:
            raise CineCoreBotTierError(
                f"Bulk limit ({self.bulk_limit}) exceeded for {self.tier.value} tier. "
                "Upgrade to generate more."
            )

        results = []
        for biz in businesses:
            script = self._script_engine.generate(
                business_name=biz.get("name", "Business"),
                product=biz.get("product", "product"),
                target_audience=biz.get("target_audience", "general audience"),
                genre=genre,
            )
            entry: dict = {"script": script.to_dict()}

            if include_video and self._video_engine.available_providers:
                try:
                    video = self._video_engine.generate(script.script)
                    entry["video"] = video.to_dict()
                except CineCoreBotTierError:
                    entry["video"] = {"error": "video generation not available on this tier"}

            results.append(entry)

        return results


class SelfHeal:
    """
    Auto-detection and fixing of system issues.

    Monitors engines for errors, resets counters on daily cycles,
    and reports health status.
    """

    def __init__(self) -> None:
        self._issues: List[dict] = []
        self._fixes_applied: int = 0

    def monitor(self, component: str, status: str = "ok") -> dict:
        """Record a component health check."""
        if status != "ok":
            issue = {
                "component": component,
                "status": status,
                "detected_at": datetime.now(timezone.utc).isoformat(),
            }
            self._issues.append(issue)
            fix_result = self._auto_fix(issue)
            return {"health": "degraded", "issue": issue, "fix": fix_result}
        return {"health": "ok", "component": component}

    def _auto_fix(self, issue: dict) -> dict:
        """Attempt to automatically resolve a detected issue."""
        self._fixes_applied += 1
        return {
            "action": f"auto_fix_applied_to_{issue['component']}",
            "fix_id": self._fixes_applied,
            "status": "resolved",
        }

    def system_health(self) -> dict:
        """Return overall system health report."""
        open_issues = [i for i in self._issues if i.get("status") != "resolved"]
        return {
            "status": "healthy" if not open_issues else "degraded",
            "total_issues_detected": len(self._issues),
            "fixes_applied": self._fixes_applied,
            "open_issues": len(open_issues),
        }

    def reset(self) -> None:
        """Reset issues and fixes (used in testing / daily cycles)."""
        self._issues = []
        self._fixes_applied = 0


# ---------------------------------------------------------------------------
# CRM
# ---------------------------------------------------------------------------

class CRM:
    """
    Client Relationship Management system.

    Tracks leads, active clients, pipeline stages, and revenue per client.
    """

    PIPELINE_STAGES = ["new_lead", "demo_sent", "negotiating", "closed_won", "closed_lost"]

    def __init__(self) -> None:
        self._leads: List[dict] = []
        self._clients: List[dict] = []

    def add_lead(self, lead: LeadRecord) -> dict:
        """Add a new lead to the pipeline."""
        entry = {**lead.to_dict(), "stage": "new_lead", "added_at": datetime.now(timezone.utc).isoformat()}
        self._leads.append(entry)
        return entry

    def update_stage(self, lead_id: str, stage: str) -> dict:
        """Move a lead to a new pipeline stage."""
        if stage not in self.PIPELINE_STAGES:
            raise CineCoreBotError(
                f"Stage '{stage}' not valid. Choose from: {self.PIPELINE_STAGES}"
            )
        for lead in self._leads:
            if lead["lead_id"] == lead_id:
                lead["stage"] = stage
                if stage == "closed_won":
                    self._clients.append({**lead, "client_since": datetime.now(timezone.utc).isoformat()})
                return lead
        raise CineCoreBotError(f"Lead '{lead_id}' not found.")

    def convert_to_client(self, lead: LeadRecord) -> dict:
        """Convert a lead directly to an active client."""
        entry = {
            **lead.to_dict(),
            "stage": "closed_won",
            "client_since": datetime.now(timezone.utc).isoformat(),
        }
        self._clients.append(entry)
        return entry

    @property
    def leads(self) -> List[dict]:
        return list(self._leads)

    @property
    def clients(self) -> List[dict]:
        return list(self._clients)

    def pipeline_summary(self) -> dict:
        """Return counts by pipeline stage."""
        summary: dict = {stage: 0 for stage in self.PIPELINE_STAGES}
        for lead in self._leads:
            stage = lead.get("stage", "new_lead")
            if stage in summary:
                summary[stage] += 1
        summary["total_leads"] = len(self._leads)
        summary["total_clients"] = len(self._clients)
        return summary


# ---------------------------------------------------------------------------
# Main CineCoreBot
# ---------------------------------------------------------------------------

class CineCoreBot:
    """
    DreamCo CineCore™ — AI-Powered Commercial & Video Creation System.

    Orchestrates all 10 engines into a single unified interface.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)

        # Instantiate all engines
        self._script_engine = ScriptEngine(tier)
        self._video_engine = VideoEngine(tier)
        self._voice_engine = VoiceEngine(tier)
        self._platform_optimizer = PlatformOptimizer(tier)
        self._lead_engine = LeadEngine(tier)
        self._business_scorer = BusinessScorer()
        self._closing_agent = ClosingAgent(tier)
        self._billing_engine = BillingEngine(tier)
        self._analytics_engine = AnalyticsEngine(tier)
        self._bulk_generator = BulkGenerator(tier, self._script_engine, self._video_engine)
        self._self_heal = SelfHeal()
        self._crm = CRM()

    # ------------------------------------------------------------------
    # 1. Script Engine
    # ------------------------------------------------------------------

    def generate_script(
        self,
        business_name: str,
        product: str,
        target_audience: str,
        genre: str = "ad",
    ) -> dict:
        """Generate a commercial script and return as a dict."""
        result = self._script_engine.generate(business_name, product, target_audience, genre)
        return result.to_dict()

    # ------------------------------------------------------------------
    # 2. Video Engine
    # ------------------------------------------------------------------

    def generate_video(
        self,
        script: str,
        provider: str = "runway",
        duration: int = 15,
    ) -> dict:
        """Generate an AI video from a script."""
        asset = self._video_engine.generate(script, provider, duration)
        return asset.to_dict()

    # ------------------------------------------------------------------
    # 3. Voice Engine
    # ------------------------------------------------------------------

    def generate_voiceover(
        self,
        script: str,
        voice: str = "ai_neutral",
        tone: str = "neutral",
        platform: str = "tiktok",
    ) -> dict:
        """Generate a voiceover for the given script."""
        return self._voice_engine.generate(script, voice, tone, platform)

    def clone_voice(self, sample_audio_url: str, script: str) -> dict:
        """Clone a voice from a sample audio URL (ENTERPRISE only)."""
        return self._voice_engine.clone_voice(sample_audio_url, script)

    # ------------------------------------------------------------------
    # 4. Platform Optimizer
    # ------------------------------------------------------------------

    def optimize_for_platforms(self, video_dict: dict) -> dict:
        """Optimize a video asset for all available platforms."""
        asset = VideoAsset(
            script_id=video_dict.get("script_id", ""),
            video_url=video_dict.get("video_url", ""),
            provider=video_dict.get("provider", "runway"),
            duration_seconds=video_dict.get("duration_seconds", 15),
        )
        return self._platform_optimizer.optimize(asset)

    def auto_post(self, video_dict: dict, caption: str = "") -> dict:
        """Auto-post a video to all available platforms."""
        asset = VideoAsset(
            script_id=video_dict.get("script_id", ""),
            video_url=video_dict.get("video_url", ""),
            provider=video_dict.get("provider", "runway"),
            duration_seconds=video_dict.get("duration_seconds", 15),
        )
        return self._platform_optimizer.auto_post(asset, caption)

    # ------------------------------------------------------------------
    # 5. Lead Engine
    # ------------------------------------------------------------------

    def find_leads(self, query: str = "business near me") -> List[dict]:
        """Find business leads using the lead engine."""
        leads = self._lead_engine.search(query)
        return [lead.to_dict() for lead in leads]

    def score_leads(self, leads: List[dict]) -> List[dict]:
        """Score and rank leads by marketing opportunity."""
        lead_objs = [
            LeadRecord(
                name=l["name"],
                business_type=l["business_type"],
                location=l["location"],
                rating=l["rating"],
                lead_id=l["lead_id"],
            )
            for l in leads
        ]
        ranked = self._business_scorer.rank(lead_objs)
        return [l.to_dict() for l in ranked]

    # ------------------------------------------------------------------
    # 6. Closing Agent
    # ------------------------------------------------------------------

    def generate_outreach(self, lead: dict, template: str = "initial") -> dict:
        """Generate an outreach draft for a lead (requires human approval)."""
        lead_obj = LeadRecord(
            name=lead["name"],
            business_type=lead["business_type"],
            location=lead["location"],
            rating=lead.get("rating", 0.0),
            lead_id=lead.get("lead_id", str(uuid.uuid4())[:8]),
        )
        return self._closing_agent.generate_outreach(lead_obj, template)

    def handle_client_reply(self, reply: str) -> str:
        """Generate a contextual response to a client message."""
        return self._closing_agent.handle_reply(reply)

    def generate_upsell(self, current_spend: float) -> str:
        """Generate an upsell offer for an existing client."""
        return self._closing_agent.generate_upsell(current_spend)

    # ------------------------------------------------------------------
    # 7. Billing Engine
    # ------------------------------------------------------------------

    def list_plans(self) -> List[dict]:
        """Return available billing plans."""
        return self._billing_engine.list_plans()

    def create_subscription(self, email: str, plan: str = "pro") -> dict:
        """Create a Stripe subscription for a customer."""
        return self._billing_engine.create_subscription(email, plan)

    def create_customer(self, email: str) -> dict:
        """Create a Stripe customer record."""
        return self._billing_engine.create_customer(email)

    # ------------------------------------------------------------------
    # 8. Analytics Engine
    # ------------------------------------------------------------------

    def get_analytics(self, video_id: str, platform: str = "all") -> dict:
        """Get performance analytics for a video."""
        record = self._analytics_engine.track(video_id, platform)
        return record.to_dict()

    def revenue_summary(self) -> dict:
        """Return aggregated revenue across all tracked videos."""
        return self._analytics_engine.revenue_summary()

    # ------------------------------------------------------------------
    # 9. Bulk Generator
    # ------------------------------------------------------------------

    def bulk_generate(
        self,
        businesses: List[dict],
        genre: str = "ad",
        include_video: bool = False,
    ) -> List[dict]:
        """Generate commercials in bulk for a list of businesses."""
        return self._bulk_generator.run(businesses, genre, include_video)

    # ------------------------------------------------------------------
    # 10. Self-Heal
    # ------------------------------------------------------------------

    def system_health(self) -> dict:
        """Return system health report."""
        return self._self_heal.system_health()

    def monitor_component(self, component: str, status: str = "ok") -> dict:
        """Monitor a specific component's health."""
        return self._self_heal.monitor(component, status)

    # ------------------------------------------------------------------
    # CRM
    # ------------------------------------------------------------------

    def add_lead_to_crm(self, lead: dict) -> dict:
        """Add a lead to the CRM pipeline."""
        lead_obj = LeadRecord(
            name=lead["name"],
            business_type=lead["business_type"],
            location=lead["location"],
            rating=lead.get("rating", 0.0),
            lead_id=lead.get("lead_id", str(uuid.uuid4())[:8]),
        )
        return self._crm.add_lead(lead_obj)

    def update_lead_stage(self, lead_id: str, stage: str) -> dict:
        """Update a lead's pipeline stage."""
        return self._crm.update_stage(lead_id, stage)

    def crm_summary(self) -> dict:
        """Return CRM pipeline summary."""
        return self._crm.pipeline_summary()

    # ------------------------------------------------------------------
    # Tier & orchestration
    # ------------------------------------------------------------------

    def run_full_campaign(self, business_name: str, product: str, target_audience: str) -> dict:
        """
        Run the complete CineCore commercial campaign pipeline:
        Script → Video (PRO+) → Voiceover → Platform optimization → Analytics.
        """
        report: dict = {
            "tier": self.tier.value,
            "business": business_name,
            "steps_completed": [],
        }

        # Step 1: Script
        script = self.generate_script(business_name, product, target_audience)
        report["script"] = script
        report["steps_completed"].append("script_generation")

        # Step 2: Video (PRO / ENTERPRISE only)
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            try:
                video = self.generate_video(script["script"])
                report["video"] = video
                report["steps_completed"].append("video_generation")

                # Step 3: Platform optimization
                optimized = self.optimize_for_platforms(video)
                report["platforms"] = optimized
                report["steps_completed"].append("platform_optimization")

                # Step 4: Analytics (simulated)
                analytics = self.get_analytics(video["video_id"])
                report["analytics"] = analytics
                report["steps_completed"].append("analytics_tracking")
            except CineCoreBotTierError as exc:
                report["video_error"] = str(exc)

        # Step 5: Voiceover
        voice = self.generate_voiceover(script["script"])
        report["voiceover"] = voice
        report["steps_completed"].append("voiceover_generation")

        return report

    def describe_tier(self) -> str:
        """Return a formatted string describing the current tier."""
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} CineCore Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        upgrade = get_upgrade_path(self.tier)
        if upgrade:
            lines.append(f"\nUpgrade to {upgrade.name} for ${upgrade.price_usd_monthly:.2f}/month")
        output = "\n".join(lines)
        print(output)
        return output
