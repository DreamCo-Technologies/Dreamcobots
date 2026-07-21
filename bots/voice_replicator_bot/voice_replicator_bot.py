"""
Voice Replicator Bot — Main Entry Point

An AI-powered voice synthesis and cloning assistant for the DreamCobots ecosystem.

Core capabilities:
  • Text-to-Speech      — Basic and HD voice synthesis across 25 languages
  • Voice Cloning       — Clone any voice from an audio sample (ENTERPRISE)
  • Real-Time Translation & Speak — Translate text and synthesize in multiple languages (ENTERPRISE)
  • Language Support    — Broad multilingual coverage

Tier limits:
  - FREE:       10 requests/day, basic TTS, 5 languages.
  - PRO:        200 requests/day, advanced HD TTS, all 25 languages.
  - ENTERPRISE: Unlimited, voice cloning, real-time translation, natural tone adaptation.

Usage
-----
    from bots.voice_replicator_bot import VoiceReplicatorBot, Tier
    bot = VoiceReplicatorBot(tier=Tier.PRO)
    result = bot.synthesize_speech("Hello, world!", language="en-US")
    print(bot.get_voice_dashboard())
"""

from __future__ import annotations

import sys
import os
import uuid
import random
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from bots.voice_replicator_bot.tiers import (
    BOT_FEATURES,
    get_bot_tier_info,
    DAILY_LIMITS,
    FEATURE_BASIC_TTS,
    FEATURE_ADVANCED_TTS,
    FEATURE_LANGUAGE_BASIC,
    FEATURE_LANGUAGE_FULL,
    FEATURE_VOICE_SYNTHESIS_HD,
    FEATURE_VOICE_CLONING,
    FEATURE_REAL_TIME_TRANSLATION,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401

ALL_LANGUAGES = [
    "en-US", "en-GB", "es-ES", "es-MX", "fr-FR", "de-DE", "it-IT", "pt-BR",
    "pt-PT", "ja-JP", "ko-KR", "zh-CN", "zh-TW", "ar-SA", "hi-IN", "ru-RU",
    "nl-NL", "pl-PL", "sv-SE", "tr-TR", "id-ID", "th-TH", "vi-VN", "uk-UA",
    "cs-CZ",
]
BASIC_LANGUAGES = ALL_LANGUAGES[:5]


class VoiceReplicatorBotError(Exception):
    """Raised when a tier limit or feature restriction is violated."""


class VoiceReplicatorBot:
    """AI-powered voice replication and synthesis bot with tier-based feature gating.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling daily limits and feature access.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self.tier_info = get_bot_tier_info(tier)
        self.flow = GlobalAISourcesFlow(bot_name="VoiceReplicatorBot")
        self._daily_count: int = 0

    def _check_daily_limit(self) -> None:
        """Raise VoiceReplicatorBotError if the daily limit is exceeded."""
        limit = DAILY_LIMITS[self.tier.value]
        if limit is not None and self._daily_count >= limit:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo) for more."
                if upgrade else ""
            )
            raise VoiceReplicatorBotError(
                f"Daily limit of {limit} reached for the {self.tier.value.upper()} tier.{upgrade_msg}"
            )

    def _check_feature(self, feature: str) -> None:
        """Raise VoiceReplicatorBotError if the feature is not available on the current tier."""
        if feature not in BOT_FEATURES[self.tier.value]:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} for access." if upgrade else ""
            )
            raise VoiceReplicatorBotError(
                f"Feature '{feature}' is not available on the {self.tier.value.upper()} tier.{upgrade_msg}"
            )

    def _record(self) -> None:
        self._daily_count += 1

    def synthesize_speech(
        self, text: str, language: str = "en-US", voice_id: str | None = None
    ) -> dict:
        """Synthesize speech from text.

        FREE tier: basic TTS. PRO/ENTERPRISE: advanced HD synthesis.

        Parameters
        ----------
        text : str
            Text to convert to speech.
        language : str
            BCP-47 language tag (e.g. ``en-US``).
        voice_id : str | None
            Optional pre-trained voice model ID.
        """
        self._check_feature(FEATURE_BASIC_TTS)
        self._check_daily_limit()
        is_hd = FEATURE_VOICE_SYNTHESIS_HD in BOT_FEATURES[self.tier.value]
        result = self.flow.run_pipeline(
            raw_data={
                "task": "synthesize_speech",
                "text": text,
                "language": language,
                "voice_id": voice_id,
                "hd": is_hd,
            },
            learning_method="supervised",
        )
        uid = uuid.uuid4().hex[:12]
        self._record()
        return {
            "text": text,
            "language": language,
            "voice_id": voice_id or "default_v1",
            "audio_url": f"https://cdn.dreamcobots.ai/tts/{uid}.wav",
            "duration_secs": round(len(text) / 15, 2),
            "sample_rate": 44100,
            "format": "WAV",
            "quality": "HD" if is_hd else "Standard",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def clone_voice(self, audio_source: str) -> dict:
        """Clone a voice from an audio sample (ENTERPRISE only).

        Parameters
        ----------
        audio_source : str
            URL or file path to the reference audio sample.
        """
        self._check_feature(FEATURE_VOICE_CLONING)
        self._check_daily_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "clone_voice", "audio_source": audio_source},
            learning_method="self_supervised",
        )
        uid = uuid.uuid4().hex[:12]
        self._record()
        return {
            "voice_id": f"cloned_{uid}",
            "audio_source": audio_source,
            "model": "VoiceClone-v3",
            "language_detected": "en-US",
            "quality_score": round(random.uniform(0.88, 0.98), 2),
            "speaker_characteristics": {
                "pitch_hz": random.randint(100, 300),
                "timbre": random.choice(["warm", "bright", "neutral", "deep"]),
                "speech_rate_wpm": random.randint(120, 180),
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def translate_and_speak(
        self, text: str, source_lang: str, target_langs: list[str]
    ) -> dict:
        """Translate text into multiple languages and synthesize speech for each (ENTERPRISE only).

        Parameters
        ----------
        text : str
            Source text to translate and speak.
        source_lang : str
            BCP-47 language code of the source text.
        target_langs : list[str]
            List of BCP-47 language codes for the translations.
        """
        self._check_feature(FEATURE_REAL_TIME_TRANSLATION)
        self._check_daily_limit()
        result = self.flow.run_pipeline(
            raw_data={
                "task": "translate_and_speak",
                "text": text,
                "source_lang": source_lang,
                "target_langs": target_langs,
            },
            learning_method="supervised",
        )
        uid = uuid.uuid4().hex[:12]
        translations = [
            {
                "lang": lang,
                "translated_text": f"[{lang}] {text}",
                "audio_url": f"https://cdn.dreamcobots.ai/tts/{uid}_{lang}.wav",
                "duration_secs": round(len(text) / 15, 2),
            }
            for lang in target_langs
        ]
        self._record()
        return {
            "source_text": text,
            "source_lang": source_lang,
            "translations": translations,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def list_supported_languages(self) -> list[str]:
        """Return supported languages. FREE: 5 languages, PRO/ENTERPRISE: all 25."""
        if FEATURE_LANGUAGE_FULL in BOT_FEATURES[self.tier.value]:
            return ALL_LANGUAGES
        self._check_feature(FEATURE_LANGUAGE_BASIC)
        return BASIC_LANGUAGES

    def get_voice_dashboard(self) -> dict:
        """Return dashboard with usage stats and tier information."""
        limit = DAILY_LIMITS[self.tier.value]
        upgrade = get_upgrade_path(self.tier)
        return {
            "bot_name": "VoiceReplicatorBot",
            "tier": self.tier.value,
            "tier_display": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "daily_limit": limit,
            "count_today": self._daily_count,
            "remaining": (limit - self._daily_count) if limit is not None else "unlimited",
            "languages_available": len(self.list_supported_languages()),
            "features": BOT_FEATURES[self.tier.value],
            "commercial_rights": self.tier_info["commercial_rights"],
            "upgrade_available": upgrade is not None,
            "upgrade_to": upgrade.name if upgrade else None,
            "upgrade_price_usd": upgrade.price_usd_monthly if upgrade else None,
        }
