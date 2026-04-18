"""
DreamCo Talent Bot — AI-Powered Music Producer & Worldwide Talent Agency.

Automates the full lifecycle of music creation, talent management, rights
registration, and financial resources access:

  1. 🎵 MusicProductionEngine  — Beat & song generation, mastering, commercials,
                                  podcasts, and Reels/TikTok content
  2. 🎤 VoiceCloneEngine       — Voice cloning, voiceovers, multi-language dubbing
  3. ⚖️  RightsEngine           — Copyright, trademark, patent search & registration,
                                  invention & IP portfolio management
  4. 🌟 TalentAgencyEngine     — Worldwide talent management, show booking, artist
                                  profiles, and fame-building show outlets
  5. 💰 FinancialEngine        — Grant & loan sourcing, royalty tracking, licensing,
                                  revenue dashboard
  6. 📱 ContentCreatorEngine   — YouTube, TikTok, Instagram Reels, podcast, and
                                  OnlyFans content tools
  7. 🛒 MarketplaceEngine      — Sell AI-created beats, songs, and videos;
                                  copyright-safe track store; white-label storefront
  8. 🛡️  SelfHealEngine         — System health monitoring and auto-recovery

Usage
-----
    from bots.dreamco_talent_bot import DreamCoTalentBot
    from tiers import Tier

    bot = DreamCoTalentBot(tier=Tier.PRO)

    # Generate a beat
    beat = bot.generate_beat("hip-hop", bpm=95)

    # Clone a voice
    voice = bot.clone_voice("artist_sample.wav", voice_name="MyVoice")

    # Register a copyright
    reg = bot.register_copyright("My Song Title", "musical_work", "Jane Doe")

    # Book a show
    booking = bot.book_show("Jane Doe", "Club Nova", "2025-09-15")

    # Find grants
    grants = bot.find_grants("music production")

    # List a beat for sale
    listing = bot.list_beat_for_sale(beat, price_usd=49.99)

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
from bots.dreamco_talent_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class DreamCoTalentBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class DreamCoTalentBotError(Exception):
    """General DreamCo Talent Bot error."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_GENRES = [
    "hip-hop", "r&b", "pop", "trap", "lo-fi", "jazz", "gospel",
    "country", "electronic", "reggaeton", "afrobeats", "rock",
]
SUPPORTED_PLATFORMS = ["spotify", "apple_music", "tiktok", "youtube", "instagram", "soundcloud"]
SUPPORTED_CONTENT_TYPES = ["reel", "podcast", "commercial", "youtube_short", "onlyfans_clip"]
SUPPORTED_RIGHT_TYPES = ["copyright", "trademark", "patent", "trade_secret"]
SUPPORTED_GRANT_CATEGORIES = [
    "music_production", "podcast", "film", "invention", "small_business",
    "nonprofit", "technology", "arts", "education",
]

BEAT_DAILY_LIMIT_FREE = 5
BEAT_DAILY_LIMIT_PRO = 50
VOICE_CLONE_LIMIT_FREE = 0
VOICE_CLONE_LIMIT_PRO = 3
BOOKING_LIMIT_FREE = 1
BOOKING_LIMIT_PRO = 20


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class BeatTrack:
    """A generated beat or music track."""
    genre: str
    bpm: int
    key: str
    duration_seconds: int
    title: str
    audio_url: str
    copyright_safe: bool = True
    track_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "track_id": self.track_id,
            "title": self.title,
            "genre": self.genre,
            "bpm": self.bpm,
            "key": self.key,
            "duration_seconds": self.duration_seconds,
            "audio_url": self.audio_url,
            "copyright_safe": self.copyright_safe,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class VoiceProfile:
    """A cloned voice profile."""
    voice_name: str
    language: str
    tone: str
    source_sample: str
    voice_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: str = "ready"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "voice_id": self.voice_id,
            "voice_name": self.voice_name,
            "language": self.language,
            "tone": self.tone,
            "source_sample": self.source_sample,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class RightsRecord:
    """A rights registration record."""
    title: str
    rights_type: str
    owner: str
    description: str
    status: str = "pending"
    registration_number: str = field(default_factory=lambda: f"DC-{str(uuid.uuid4())[:6].upper()}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "registration_number": self.registration_number,
            "title": self.title,
            "rights_type": self.rights_type,
            "owner": self.owner,
            "description": self.description,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ArtistProfile:
    """An artist / talent profile."""
    name: str
    genre: str
    bio: str
    social_handles: Dict[str, str] = field(default_factory=dict)
    booking_rate_usd: float = 0.0
    artist_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    verified: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "artist_id": self.artist_id,
            "name": self.name,
            "genre": self.genre,
            "bio": self.bio,
            "social_handles": self.social_handles,
            "booking_rate_usd": self.booking_rate_usd,
            "verified": self.verified,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ShowBooking:
    """A show booking record."""
    artist_name: str
    venue: str
    event_date: str
    status: str = "confirmed"
    booking_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    payout_usd: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "booking_id": self.booking_id,
            "artist_name": self.artist_name,
            "venue": self.venue,
            "event_date": self.event_date,
            "status": self.status,
            "payout_usd": self.payout_usd,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class GrantOpportunity:
    """A grant or loan opportunity."""
    name: str
    category: str
    amount_usd: float
    deadline: str
    eligibility: str
    apply_url: str
    opportunity_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> dict:
        return {
            "opportunity_id": self.opportunity_id,
            "name": self.name,
            "category": self.category,
            "amount_usd": self.amount_usd,
            "deadline": self.deadline,
            "eligibility": self.eligibility,
            "apply_url": self.apply_url,
        }


@dataclass
class MarketplaceListing:
    """A marketplace listing for a beat, song, or video."""
    title: str
    asset_type: str
    price_usd: float
    track_id: str
    description: str = ""
    listing_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: str = "active"
    sales: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "listing_id": self.listing_id,
            "title": self.title,
            "asset_type": self.asset_type,
            "price_usd": self.price_usd,
            "track_id": self.track_id,
            "description": self.description,
            "status": self.status,
            "sales": self.sales,
            "timestamp": self.timestamp.isoformat(),
        }


# ---------------------------------------------------------------------------
# Engine 1: Music Production Engine
# ---------------------------------------------------------------------------

class MusicProductionEngine:
    """Generates beats, full songs, and content for commercials and social media."""

    KEYS = ["C", "D", "E", "F", "G", "A", "B", "C#", "Eb", "F#", "Ab", "Bb"]
    TITLE_PREFIXES = ["Night", "Gold", "Dream", "Fire", "Wave", "Rise", "Neon", "Deep"]
    TITLE_SUFFIXES = ["Vibes", "Rush", "Flow", "Mode", "Sound", "Beat", "Track", "Wave"]

    def __init__(self, daily_limit: int) -> None:
        self._daily_limit = daily_limit
        self._generated_today: int = 0

    def _check_limit(self) -> None:
        if self._daily_limit is not None and self._generated_today >= self._daily_limit:
            raise DreamCoTalentBotTierError(
                f"Daily beat generation limit ({self._daily_limit}) reached. Upgrade to generate more."
            )

    def generate_beat(self, genre: str, bpm: int = 0, duration_seconds: int = 30) -> BeatTrack:
        self._check_limit()
        if genre not in SUPPORTED_GENRES:
            genre = "hip-hop"
        bpm = bpm if bpm > 0 else random.randint(70, 160)
        key = random.choice(self.KEYS)
        title = f"{random.choice(self.TITLE_PREFIXES)} {random.choice(self.TITLE_SUFFIXES)}"
        track = BeatTrack(
            genre=genre,
            bpm=bpm,
            key=key,
            duration_seconds=duration_seconds,
            title=title,
            audio_url=f"https://cdn.dreamco.ai/beats/{str(uuid.uuid4())[:8]}.mp3",
            copyright_safe=True,
        )
        self._generated_today += 1
        return track

    def generate_song(self, title: str, genre: str, lyrics: str, beat: Optional[BeatTrack] = None) -> dict:
        self._check_limit()
        song_id = str(uuid.uuid4())[:8]
        return {
            "song_id": song_id,
            "title": title,
            "genre": genre,
            "lyrics": lyrics,
            "beat_id": beat.track_id if beat else None,
            "audio_url": f"https://cdn.dreamco.ai/songs/{song_id}.mp3",
            "copyright_safe": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def generate_content(self, content_type: str, topic: str, duration_seconds: int = 60) -> dict:
        if content_type not in SUPPORTED_CONTENT_TYPES:
            content_type = "reel"
        content_id = str(uuid.uuid4())[:8]
        return {
            "content_id": content_id,
            "content_type": content_type,
            "topic": topic,
            "duration_seconds": duration_seconds,
            "video_url": f"https://cdn.dreamco.ai/content/{content_id}.mp4",
            "audio_url": f"https://cdn.dreamco.ai/content/{content_id}.mp3",
            "copyright_safe": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def master_track(self, track_id: str) -> dict:
        return {
            "track_id": track_id,
            "mastered": True,
            "loudness_lufs": round(random.uniform(-14.0, -9.0), 1),
            "mastered_url": f"https://cdn.dreamco.ai/mastered/{track_id}.mp3",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# Engine 2: Voice Clone Engine
# ---------------------------------------------------------------------------

class VoiceCloneEngine:
    """Clones voices, generates voiceovers, and supports multi-language dubbing."""

    SUPPORTED_LANGUAGES = ["en", "es", "fr", "de", "pt", "ja", "ko", "zh", "ar"]

    def __init__(self, clone_limit: Optional[int]) -> None:
        self._clone_limit = clone_limit
        self._cloned_voices: List[VoiceProfile] = []

    def _check_clone_limit(self) -> None:
        if self._clone_limit is not None and len(self._cloned_voices) >= self._clone_limit:
            raise DreamCoTalentBotTierError(
                f"Voice clone limit ({self._clone_limit}) reached. Upgrade to clone more voices."
            )

    def clone_voice(self, source_sample: str, voice_name: str, language: str = "en") -> VoiceProfile:
        self._check_clone_limit()
        if language not in self.SUPPORTED_LANGUAGES:
            language = "en"
        profile = VoiceProfile(
            voice_name=voice_name,
            language=language,
            tone=random.choice(["warm", "powerful", "smooth", "energetic"]),
            source_sample=source_sample,
        )
        self._cloned_voices.append(profile)
        return profile

    def generate_voiceover(self, text: str, voice_id: Optional[str] = None, language: str = "en") -> dict:
        vo_id = str(uuid.uuid4())[:8]
        return {
            "voiceover_id": vo_id,
            "text": text,
            "voice_id": voice_id or "default",
            "language": language,
            "audio_url": f"https://cdn.dreamco.ai/voiceovers/{vo_id}.mp3",
            "duration_seconds": max(3, len(text) // 15),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def dub_audio(self, audio_url: str, target_language: str) -> dict:
        dub_id = str(uuid.uuid4())[:8]
        return {
            "dub_id": dub_id,
            "original_url": audio_url,
            "target_language": target_language,
            "dubbed_url": f"https://cdn.dreamco.ai/dubbed/{dub_id}.mp3",
            "status": "processing",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def list_voices(self) -> List[dict]:
        return [v.to_dict() for v in self._cloned_voices]


# ---------------------------------------------------------------------------
# Engine 3: Rights Engine
# ---------------------------------------------------------------------------

class RightsEngine:
    """Handles copyright, trademark, patent search and registration."""

    def __init__(self, tier: Tier) -> None:
        self._tier = tier
        self._registrations: List[RightsRecord] = []

    def search_copyright(self, query: str) -> List[dict]:
        return [
            {
                "result_id": str(uuid.uuid4())[:8],
                "query": query,
                "match_title": f"{query} - Original Work",
                "owner": "Unknown Owner",
                "registration_number": f"TX-{random.randint(100000, 999999)}",
                "status": "registered",
            }
            for _ in range(random.randint(1, 3))
        ]

    def register_copyright(self, title: str, work_type: str, owner: str) -> RightsRecord:
        if self._tier == Tier.FREE:
            raise DreamCoTalentBotTierError("Copyright registration requires PRO tier or higher.")
        record = RightsRecord(
            title=title,
            rights_type="copyright",
            owner=owner,
            description=f"{work_type} work by {owner}",
            status="filed",
        )
        self._registrations.append(record)
        return record

    def search_trademark(self, name: str, class_code: int = 41) -> List[dict]:
        if self._tier == Tier.FREE:
            raise DreamCoTalentBotTierError("Trademark search requires PRO tier or higher.")
        return [
            {
                "result_id": str(uuid.uuid4())[:8],
                "name": name,
                "class_code": class_code,
                "status": random.choice(["registered", "abandoned", "pending"]),
                "owner": f"Sample Owner {i + 1}",
            }
            for i in range(random.randint(0, 2))
        ]

    def register_trademark(self, name: str, owner: str, description: str) -> RightsRecord:
        if self._tier == Tier.FREE:
            raise DreamCoTalentBotTierError("Trademark registration requires PRO tier or higher.")
        record = RightsRecord(
            title=name,
            rights_type="trademark",
            owner=owner,
            description=description,
            status="filed",
        )
        self._registrations.append(record)
        return record

    def search_patent(self, invention_description: str) -> List[dict]:
        if self._tier not in (Tier.PRO, Tier.ENTERPRISE):
            raise DreamCoTalentBotTierError("Patent search requires PRO tier or higher.")
        return [
            {
                "patent_id": f"US{random.randint(10000000, 19999999)}",
                "title": f"Patent related to: {invention_description[:40]}",
                "inventor": "Sample Inventor",
                "filing_date": "2023-01-01",
                "status": random.choice(["granted", "pending", "abandoned"]),
            }
            for _ in range(random.randint(1, 4))
        ]

    def file_patent(self, invention_title: str, owner: str, description: str) -> RightsRecord:
        if self._tier != Tier.ENTERPRISE:
            raise DreamCoTalentBotTierError("Patent filing requires ENTERPRISE tier.")
        record = RightsRecord(
            title=invention_title,
            rights_type="patent",
            owner=owner,
            description=description,
            status="filed",
        )
        self._registrations.append(record)
        return record

    def list_registrations(self) -> List[dict]:
        return [r.to_dict() for r in self._registrations]


# ---------------------------------------------------------------------------
# Engine 4: Talent Agency Engine
# ---------------------------------------------------------------------------

class TalentAgencyEngine:
    """Manages artist profiles, show bookings, and fame-building outlets."""

    VENUE_TYPES = ["club", "arena", "festival", "online_stream", "corporate_event", "podcast_stage"]

    def __init__(self, booking_limit: Optional[int]) -> None:
        self._booking_limit = booking_limit
        self._artists: Dict[str, ArtistProfile] = {}
        self._bookings: List[ShowBooking] = []

    def create_artist_profile(
        self,
        name: str,
        genre: str,
        bio: str,
        social_handles: Optional[Dict[str, str]] = None,
        booking_rate_usd: float = 0.0,
    ) -> ArtistProfile:
        profile = ArtistProfile(
            name=name,
            genre=genre,
            bio=bio,
            social_handles=social_handles or {},
            booking_rate_usd=booking_rate_usd,
        )
        self._artists[profile.artist_id] = profile
        return profile

    def book_show(
        self,
        artist_name: str,
        venue: str,
        event_date: str,
        payout_usd: float = 0.0,
    ) -> ShowBooking:
        active = [b for b in self._bookings if b.status == "confirmed"]
        if self._booking_limit is not None and len(active) >= self._booking_limit:
            raise DreamCoTalentBotTierError(
                f"Booking limit ({self._booking_limit}) reached. Upgrade for more bookings."
            )
        booking = ShowBooking(
            artist_name=artist_name,
            venue=venue,
            event_date=event_date,
            payout_usd=payout_usd,
            status="confirmed",
        )
        self._bookings.append(booking)
        return booking

    def create_show_outlet(self, name: str, platform: str, description: str) -> dict:
        outlet_id = str(uuid.uuid4())[:8]
        return {
            "outlet_id": outlet_id,
            "name": name,
            "platform": platform,
            "description": description,
            "url": f"https://dreamco.live/{outlet_id}",
            "status": "live",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def list_artists(self) -> List[dict]:
        return [a.to_dict() for a in self._artists.values()]

    def list_bookings(self) -> List[dict]:
        return [b.to_dict() for b in self._bookings]

    def get_booking_stats(self) -> dict:
        total = len(self._bookings)
        confirmed = sum(1 for b in self._bookings if b.status == "confirmed")
        total_payout = sum(b.payout_usd for b in self._bookings)
        return {
            "total_bookings": total,
            "confirmed_bookings": confirmed,
            "total_payout_usd": round(total_payout, 2),
            "artists_managed": len(self._artists),
        }


# ---------------------------------------------------------------------------
# Engine 5: Financial Engine
# ---------------------------------------------------------------------------

class FinancialEngine:
    """Handles grant/loan sourcing, royalty tracking, and revenue reporting."""

    _SAMPLE_GRANTS = [
        {
            "name": "NEA Music Creators Grant",
            "category": "music_production",
            "amount_usd": 10000.0,
            "deadline": "2025-12-01",
            "eligibility": "Independent musicians and producers",
            "apply_url": "https://www.arts.gov/grants",
        },
        {
            "name": "Small Business Innovation Fund",
            "category": "small_business",
            "amount_usd": 25000.0,
            "deadline": "2025-09-30",
            "eligibility": "US-based small businesses",
            "apply_url": "https://www.sba.gov/funding",
        },
        {
            "name": "Podcast Creator Grant",
            "category": "podcast",
            "amount_usd": 5000.0,
            "deadline": "2025-11-15",
            "eligibility": "Podcast creators with 1000+ subscribers",
            "apply_url": "https://dreamco.ai/grants/podcast",
        },
        {
            "name": "Inventor's Seed Loan",
            "category": "invention",
            "amount_usd": 50000.0,
            "deadline": "2026-03-01",
            "eligibility": "Patent holders and inventors",
            "apply_url": "https://dreamco.ai/loans/inventors",
        },
        {
            "name": "Arts & Culture Development Grant",
            "category": "arts",
            "amount_usd": 15000.0,
            "deadline": "2025-10-01",
            "eligibility": "Artists and cultural organizations",
            "apply_url": "https://dreamco.ai/grants/arts",
        },
    ]

    def __init__(self, tier: Tier) -> None:
        self._tier = tier
        self._royalties: List[dict] = []

    def find_grants(self, category: str) -> List[GrantOpportunity]:
        results = []
        for g in self._SAMPLE_GRANTS:
            if category.lower() in g["category"] or g["category"] in category.lower():
                results.append(GrantOpportunity(**g))
        if not results:
            results = [GrantOpportunity(**g) for g in self._SAMPLE_GRANTS[:2]]
        return results

    def apply_for_grant(self, grant_id: str, applicant_name: str, project_description: str) -> dict:
        if self._tier == Tier.FREE:
            raise DreamCoTalentBotTierError("Grant application assistance requires PRO tier or higher.")
        return {
            "application_id": str(uuid.uuid4())[:8],
            "grant_id": grant_id,
            "applicant": applicant_name,
            "status": "submitted",
            "project_description": project_description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def record_royalty(self, track_id: str, platform: str, streams: int, rate_per_stream: float = 0.004) -> dict:
        if self._tier == Tier.FREE:
            raise DreamCoTalentBotTierError("Royalty tracking requires PRO tier or higher.")
        earned = round(streams * rate_per_stream, 2)
        record = {
            "royalty_id": str(uuid.uuid4())[:8],
            "track_id": track_id,
            "platform": platform,
            "streams": streams,
            "rate_per_stream": rate_per_stream,
            "earned_usd": earned,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._royalties.append(record)
        return record

    def royalty_summary(self) -> dict:
        total_streams = sum(r["streams"] for r in self._royalties)
        total_earned = sum(r["earned_usd"] for r in self._royalties)
        return {
            "total_royalty_records": len(self._royalties),
            "total_streams": total_streams,
            "total_earned_usd": round(total_earned, 2),
        }


# ---------------------------------------------------------------------------
# Engine 6: Content Creator Engine
# ---------------------------------------------------------------------------

class ContentCreatorEngine:
    """Creates platform-specific content: YouTube, TikTok, Reels, Podcasts, OnlyFans."""

    HOOK_TEMPLATES = [
        "You won't believe what happened when {subject} tried {action}.",
        "The secret {industry} pros don't want you to know about {topic}.",
        "How {subject} went from broke to famous in 90 days.",
        "This one trick changed everything for {subject}.",
    ]

    def __init__(self, tier: Tier) -> None:
        self._tier = tier

    def generate_hook(self, subject: str, topic: str, industry: str = "music") -> str:
        template = random.choice(self.HOOK_TEMPLATES)
        return template.format(subject=subject, topic=topic, industry=industry, action=topic)

    def create_content_plan(self, creator_name: str, niche: str, platforms: List[str]) -> dict:
        plan_id = str(uuid.uuid4())[:8]
        return {
            "plan_id": plan_id,
            "creator_name": creator_name,
            "niche": niche,
            "platforms": platforms,
            "weekly_posts": {p: random.randint(3, 7) for p in platforms},
            "hooks": [self.generate_hook(creator_name, niche) for _ in range(3)],
            "hashtags": [f"#{niche.replace(' ', '')}", "#DreamCo", "#AI", "#Music", "#Talent"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def create_podcast_episode(
        self,
        show_name: str,
        episode_title: str,
        topic: str,
        duration_minutes: int = 30,
    ) -> dict:
        ep_id = str(uuid.uuid4())[:8]
        return {
            "episode_id": ep_id,
            "show_name": show_name,
            "episode_title": episode_title,
            "topic": topic,
            "duration_minutes": duration_minutes,
            "intro_script": f"Welcome to {show_name}. Today we're talking about {topic}.",
            "outro_script": f"Thanks for listening to {show_name}. Subscribe for more!",
            "audio_url": f"https://cdn.dreamco.ai/podcasts/{ep_id}.mp3",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def create_onlyfans_content(self, creator_name: str, content_type: str, description: str) -> dict:
        if self._tier != Tier.ENTERPRISE:
            raise DreamCoTalentBotTierError("OnlyFans content tools require ENTERPRISE tier.")
        content_id = str(uuid.uuid4())[:8]
        return {
            "content_id": content_id,
            "creator_name": creator_name,
            "content_type": content_type,
            "description": description,
            "url": f"https://cdn.dreamco.ai/creator/{content_id}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def distribute_to_platforms(self, asset_url: str, platforms: List[str], caption: str = "") -> dict:
        if self._tier == Tier.FREE:
            raise DreamCoTalentBotTierError("Cross-platform distribution requires PRO tier or higher.")
        results = {}
        for platform in platforms:
            results[platform] = {
                "status": "published",
                "post_id": str(uuid.uuid4())[:8],
                "url": f"https://{platform}.com/dreamco/{str(uuid.uuid4())[:6]}",
            }
        return {
            "asset_url": asset_url,
            "caption": caption,
            "platforms": results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# Engine 7: Marketplace Engine
# ---------------------------------------------------------------------------

class MarketplaceEngine:
    """Manages beat/song/video listings, sales, and white-label storefronts."""

    def __init__(self, tier: Tier) -> None:
        self._tier = tier
        self._listings: List[MarketplaceListing] = []

    def list_beat_for_sale(self, beat: BeatTrack, price_usd: float, description: str = "") -> MarketplaceListing:
        listing = MarketplaceListing(
            title=beat.title,
            asset_type="beat",
            price_usd=price_usd,
            track_id=beat.track_id,
            description=description or f"Copyright-safe {beat.genre} beat at {beat.bpm} BPM",
        )
        self._listings.append(listing)
        return listing

    def list_song_for_sale(self, song: dict, price_usd: float, description: str = "") -> MarketplaceListing:
        listing = MarketplaceListing(
            title=song.get("title", "Untitled Song"),
            asset_type="song",
            price_usd=price_usd,
            track_id=song.get("song_id", str(uuid.uuid4())[:8]),
            description=description,
        )
        self._listings.append(listing)
        return listing

    def purchase_listing(self, listing_id: str, buyer_email: str) -> dict:
        listing = next((l for l in self._listings if l.listing_id == listing_id), None)
        if not listing:
            raise DreamCoTalentBotError(f"Listing '{listing_id}' not found.")
        listing.sales += 1
        return {
            "purchase_id": str(uuid.uuid4())[:8],
            "listing_id": listing_id,
            "buyer_email": buyer_email,
            "price_paid_usd": listing.price_usd,
            "download_url": f"https://cdn.dreamco.ai/purchases/{listing.track_id}.zip",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def create_white_label_store(self, store_name: str, owner: str) -> dict:
        if self._tier != Tier.ENTERPRISE:
            raise DreamCoTalentBotTierError("White-label store requires ENTERPRISE tier.")
        store_id = str(uuid.uuid4())[:8]
        return {
            "store_id": store_id,
            "store_name": store_name,
            "owner": owner,
            "url": f"https://{store_name.lower().replace(' ', '-')}.dreamco.store",
            "status": "active",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def marketplace_summary(self) -> dict:
        total_revenue = sum(l.price_usd * l.sales for l in self._listings)
        return {
            "total_listings": len(self._listings),
            "active_listings": sum(1 for l in self._listings if l.status == "active"),
            "total_sales": sum(l.sales for l in self._listings),
            "total_revenue_usd": round(total_revenue, 2),
        }

    def list_marketplace(self, asset_type: Optional[str] = None) -> List[dict]:
        results = self._listings
        if asset_type:
            results = [l for l in self._listings if l.asset_type == asset_type]
        return [l.to_dict() for l in results]


# ---------------------------------------------------------------------------
# Engine 8: Self-Heal Engine
# ---------------------------------------------------------------------------

class SelfHealEngine:
    """Monitors system health and auto-recovers from issues."""

    COMPONENTS = [
        "music_production", "voice_clone", "rights_engine",
        "talent_agency", "financial", "content_creator", "marketplace",
    ]

    def __init__(self) -> None:
        self._component_status: Dict[str, str] = {c: "ok" for c in self.COMPONENTS}
        self._incident_log: List[dict] = []

    def monitor(self, component: str, status: str = "ok") -> dict:
        self._component_status[component] = status
        if status != "ok":
            incident = {
                "incident_id": str(uuid.uuid4())[:8],
                "component": component,
                "status": status,
                "action": "auto_restart",
                "resolved": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._incident_log.append(incident)
            self._component_status[component] = "ok"
            return incident
        return {"component": component, "status": "ok"}

    def system_health(self) -> dict:
        all_ok = all(v == "ok" for v in self._component_status.values())
        return {
            "overall_status": "healthy" if all_ok else "degraded",
            "components": dict(self._component_status),
            "total_incidents": len(self._incident_log),
            "uptime_pct": 99.9 if all_ok else round(random.uniform(95.0, 99.5), 1),
        }

    def incident_log(self) -> List[dict]:
        return list(self._incident_log)


# ---------------------------------------------------------------------------
# Main Bot
# ---------------------------------------------------------------------------

class DreamCoTalentBot:
    """
    DreamCo Talent Bot — AI Music Producer & Worldwide Talent Agency.

    Combines MusicProductionEngine, VoiceCloneEngine, RightsEngine,
    TalentAgencyEngine, FinancialEngine, ContentCreatorEngine,
    MarketplaceEngine, and SelfHealEngine into a unified platform.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE / PRO / ENTERPRISE).
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)

        # ------------------------------------------------------------------
        # GLOBAL AI SOURCES FLOW — mandatory pipeline
        # ------------------------------------------------------------------
        self.flow = GlobalAISourcesFlow(bot_name="DreamCoTalentBot")

        # Determine per-tier limits
        beat_limit = (
            None if tier == Tier.ENTERPRISE
            else BEAT_DAILY_LIMIT_PRO if tier == Tier.PRO
            else BEAT_DAILY_LIMIT_FREE
        )
        voice_limit = (
            None if tier == Tier.ENTERPRISE
            else VOICE_CLONE_LIMIT_PRO if tier == Tier.PRO
            else VOICE_CLONE_LIMIT_FREE
        )
        booking_limit = (
            None if tier == Tier.ENTERPRISE
            else BOOKING_LIMIT_PRO if tier == Tier.PRO
            else BOOKING_LIMIT_FREE
        )

        # ------------------------------------------------------------------
        # 8 Engines
        # ------------------------------------------------------------------
        self._music = MusicProductionEngine(daily_limit=beat_limit)
        self._voice = VoiceCloneEngine(clone_limit=voice_limit)
        self._rights = RightsEngine(tier=tier)
        self._agency = TalentAgencyEngine(booking_limit=booking_limit)
        self._financial = FinancialEngine(tier=tier)
        self._content = ContentCreatorEngine(tier=tier)
        self._marketplace = MarketplaceEngine(tier=tier)
        self._self_heal = SelfHealEngine()

    # ------------------------------------------------------------------
    # 1. Music Production
    # ------------------------------------------------------------------

    def generate_beat(self, genre: str = "hip-hop", bpm: int = 0, duration_seconds: int = 30) -> dict:
        """Generate a copyright-safe beat."""
        return self._music.generate_beat(genre, bpm, duration_seconds).to_dict()

    def generate_song(self, title: str, genre: str, lyrics: str) -> dict:
        """Generate a full AI song."""
        beat = self._music.generate_beat(genre)
        return self._music.generate_song(title, genre, lyrics, beat)

    def generate_content(self, content_type: str, topic: str, duration_seconds: int = 60) -> dict:
        """Generate a short-form content asset (reel, podcast, commercial, etc.)."""
        return self._music.generate_content(content_type, topic, duration_seconds)

    def master_track(self, track_id: str) -> dict:
        """Master a produced track to streaming standards."""
        return self._music.master_track(track_id)

    # ------------------------------------------------------------------
    # 2. Voice Cloning
    # ------------------------------------------------------------------

    def clone_voice(self, source_sample: str, voice_name: str, language: str = "en") -> dict:
        """Clone a voice from a sample file."""
        if self.tier == Tier.FREE:
            raise DreamCoTalentBotTierError("Voice cloning requires PRO tier or higher.")
        return self._voice.clone_voice(source_sample, voice_name, language).to_dict()

    def generate_voiceover(self, text: str, voice_id: Optional[str] = None, language: str = "en") -> dict:
        """Generate a voiceover for any content."""
        return self._voice.generate_voiceover(text, voice_id, language)

    def dub_audio(self, audio_url: str, target_language: str) -> dict:
        """Dub an audio file into a target language."""
        if self.tier != Tier.ENTERPRISE:
            raise DreamCoTalentBotTierError("Multi-language dubbing requires ENTERPRISE tier.")
        return self._voice.dub_audio(audio_url, target_language)

    def list_voices(self) -> List[dict]:
        """List all cloned voice profiles."""
        return self._voice.list_voices()

    # ------------------------------------------------------------------
    # 3. Rights Management
    # ------------------------------------------------------------------

    def search_copyright(self, query: str) -> List[dict]:
        """Search for existing copyright registrations."""
        return self._rights.search_copyright(query)

    def register_copyright(self, title: str, work_type: str, owner: str) -> dict:
        """File a copyright registration."""
        return self._rights.register_copyright(title, work_type, owner).to_dict()

    def search_trademark(self, name: str, class_code: int = 41) -> List[dict]:
        """Search for existing trademarks."""
        return self._rights.search_trademark(name, class_code)

    def register_trademark(self, name: str, owner: str, description: str) -> dict:
        """File a trademark registration."""
        return self._rights.register_trademark(name, owner, description).to_dict()

    def search_patent(self, invention_description: str) -> List[dict]:
        """Search for existing patents."""
        return self._rights.search_patent(invention_description)

    def file_patent(self, invention_title: str, owner: str, description: str) -> dict:
        """File a patent application (ENTERPRISE only)."""
        return self._rights.file_patent(invention_title, owner, description).to_dict()

    def list_rights_registrations(self) -> List[dict]:
        """List all filed rights registrations."""
        return self._rights.list_registrations()

    # ------------------------------------------------------------------
    # 4. Talent Agency
    # ------------------------------------------------------------------

    def create_artist_profile(
        self,
        name: str,
        genre: str,
        bio: str,
        social_handles: Optional[Dict[str, str]] = None,
        booking_rate_usd: float = 0.0,
    ) -> dict:
        """Create an artist or talent profile."""
        return self._agency.create_artist_profile(name, genre, bio, social_handles, booking_rate_usd).to_dict()

    def book_show(
        self,
        artist_name: str,
        venue: str,
        event_date: str,
        payout_usd: float = 0.0,
    ) -> dict:
        """Book a show for an artist."""
        return self._agency.book_show(artist_name, venue, event_date, payout_usd).to_dict()

    def create_show_outlet(self, name: str, platform: str, description: str) -> dict:
        """Create a show outlet to help talent go viral."""
        return self._agency.create_show_outlet(name, platform, description)

    def list_artists(self) -> List[dict]:
        """List all managed artists."""
        return self._agency.list_artists()

    def list_bookings(self) -> List[dict]:
        """List all show bookings."""
        return self._agency.list_bookings()

    def get_booking_stats(self) -> dict:
        """Return booking statistics."""
        return self._agency.get_booking_stats()

    # ------------------------------------------------------------------
    # 5. Financial
    # ------------------------------------------------------------------

    def find_grants(self, category: str) -> List[dict]:
        """Find grant and loan opportunities by category."""
        return [g.to_dict() for g in self._financial.find_grants(category)]

    def apply_for_grant(self, grant_id: str, applicant_name: str, project_description: str) -> dict:
        """Submit a grant application."""
        return self._financial.apply_for_grant(grant_id, applicant_name, project_description)

    def record_royalty(self, track_id: str, platform: str, streams: int) -> dict:
        """Record streaming royalties for a track."""
        return self._financial.record_royalty(track_id, platform, streams)

    def royalty_summary(self) -> dict:
        """Return a royalty earnings summary."""
        return self._financial.royalty_summary()

    # ------------------------------------------------------------------
    # 6. Content Creator
    # ------------------------------------------------------------------

    def generate_hook(self, subject: str, topic: str) -> str:
        """Generate a viral content hook."""
        return self._content.generate_hook(subject, topic)

    def create_content_plan(self, creator_name: str, niche: str, platforms: List[str]) -> dict:
        """Create a content plan for a creator across platforms."""
        return self._content.create_content_plan(creator_name, niche, platforms)

    def create_podcast_episode(
        self,
        show_name: str,
        episode_title: str,
        topic: str,
        duration_minutes: int = 30,
    ) -> dict:
        """Create a podcast episode with intro/outro scripts."""
        return self._content.create_podcast_episode(show_name, episode_title, topic, duration_minutes)

    def create_onlyfans_content(self, creator_name: str, content_type: str, description: str) -> dict:
        """Create OnlyFans content assets (ENTERPRISE only)."""
        return self._content.create_onlyfans_content(creator_name, content_type, description)

    def distribute_to_platforms(self, asset_url: str, platforms: List[str], caption: str = "") -> dict:
        """Distribute a content asset to multiple platforms."""
        return self._content.distribute_to_platforms(asset_url, platforms, caption)

    # ------------------------------------------------------------------
    # 7. Marketplace
    # ------------------------------------------------------------------

    def list_beat_for_sale(self, beat: dict, price_usd: float, description: str = "") -> dict:
        """List a beat for sale on the marketplace."""
        beat_obj = BeatTrack(
            genre=beat.get("genre", "hip-hop"),
            bpm=beat.get("bpm", 90),
            key=beat.get("key", "C"),
            duration_seconds=beat.get("duration_seconds", 30),
            title=beat.get("title", "Untitled"),
            audio_url=beat.get("audio_url", ""),
            track_id=beat.get("track_id", str(uuid.uuid4())[:8]),
        )
        return self._marketplace.list_beat_for_sale(beat_obj, price_usd, description).to_dict()

    def list_song_for_sale(self, song: dict, price_usd: float, description: str = "") -> dict:
        """List a song for sale on the marketplace."""
        return self._marketplace.list_song_for_sale(song, price_usd, description).to_dict()

    def purchase_listing(self, listing_id: str, buyer_email: str) -> dict:
        """Purchase a marketplace listing."""
        return self._marketplace.purchase_listing(listing_id, buyer_email)

    def create_white_label_store(self, store_name: str, owner: str) -> dict:
        """Create a white-label beat/song store (ENTERPRISE only)."""
        return self._marketplace.create_white_label_store(store_name, owner)

    def marketplace_summary(self) -> dict:
        """Return marketplace revenue summary."""
        return self._marketplace.marketplace_summary()

    def list_marketplace(self, asset_type: Optional[str] = None) -> List[dict]:
        """Browse all marketplace listings."""
        return self._marketplace.list_marketplace(asset_type)

    # ------------------------------------------------------------------
    # 8. Self-Heal
    # ------------------------------------------------------------------

    def system_health(self) -> dict:
        """Return system health status."""
        return self._self_heal.system_health()

    def monitor_component(self, component: str, status: str = "ok") -> dict:
        """Monitor a specific component."""
        return self._self_heal.monitor(component, status)

    def incident_log(self) -> List[dict]:
        """Return the incident log."""
        return self._self_heal.incident_log()

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def run_full_music_campaign(
        self,
        artist_name: str,
        genre: str,
        song_title: str,
        lyrics: str,
        platforms: Optional[List[str]] = None,
    ) -> dict:
        """
        Full pipeline: Beat → Song → Voiceover → Mastering → Marketplace → Distribution.
        """
        platforms = platforms or ["spotify", "tiktok", "youtube"]
        report: dict = {
            "tier": self.tier.value,
            "artist": artist_name,
            "steps_completed": [],
        }

        # Step 1: Generate beat
        beat = self._music.generate_beat(genre)
        report["beat"] = beat.to_dict()
        report["steps_completed"].append("beat_generation")

        # Step 2: Generate song
        song = self._music.generate_song(song_title, genre, lyrics, beat)
        report["song"] = song
        report["steps_completed"].append("song_generation")

        # Step 3: Voiceover / vocal guide
        vo = self._voice.generate_voiceover(lyrics[:200])
        report["voiceover"] = vo
        report["steps_completed"].append("voiceover")

        # Step 4: Master
        mastered = self._music.master_track(beat.track_id)
        report["mastered"] = mastered
        report["steps_completed"].append("mastering")

        # Step 5: Marketplace listing (PRO+)
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            listing = self._marketplace.list_beat_for_sale(beat, price_usd=29.99)
            report["marketplace_listing"] = listing.to_dict()
            report["steps_completed"].append("marketplace_listing")

            # Step 6: Distribution
            try:
                dist = self._content.distribute_to_platforms(song["audio_url"], platforms)
                report["distribution"] = dist
                report["steps_completed"].append("platform_distribution")
            except DreamCoTalentBotTierError as exc:
                report["distribution_error"] = str(exc)

        return report

    def describe_tier(self) -> str:
        """Return a formatted string describing the current tier."""
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} DreamCo Talent Bot Tier ===",
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
