"""
Buddy Bot — DreamCo's Most Human-Like AI Companion

The most human-like AI the world has ever seen.  BuddyBot orchestrates all
sub-engines to deliver a cohesive, emotionally intelligent, creative, and
deeply personalised companion experience.

Sub-systems
-----------
  • ConversationEngine    — natural speech, multilingual, humor, conflict resolution
  • EmotionEngine         — emotion detection (text/voice/camera), mood sync, boost
  • MemorySystem          — user profiles, milestones, important dates, episodic memory
  • AvatarEngine          — 3D avatars, micro-expressions, AR/VR, holographic
  • VoiceEngine           — voice synthesis, morphing, cloning (consent-gated)
  • CreativityEngine      — storytelling, songwriting, art mentorship, gamified productivity
  • PersonalityEngine     — dynamic personas (mentor, friend, coach, cheerleader, …)

Tier access
-----------
  FREE:       Core chat, emotion detection, 5 memory profiles, 2D avatar, basic personas.
  PRO:        Full emotion suite, multilingual, voice synthesis, 3D avatar, AR/VR,
              100 memory profiles, all personas, creativity engine, gamified productivity.
  ENTERPRISE: Unlimited memory, voice cloning, GAN image mimicry, holographic projection,
              social media manager, white-label, API access, dedicated support.

Ethical principles
------------------
  Buddy never manipulates, demeans, or harms.  Every mimicry feature (voice cloning,
  digital twin) is gated behind explicit, recorded user consent.  AI-generated content
  is always disclosed.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.buddy_bot import BuddyBot, Tier

    buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
    response = buddy.chat("I'm feeling anxious about my presentation tomorrow.")
    print(response["message"])
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.buddy_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_CONVERSATIONAL_AI,
    FEATURE_EMOTION_DETECTION,
    FEATURE_BASIC_MEMORY,
    FEATURE_MULTILINGUAL,
    FEATURE_HUMOR_ENGINE,
    FEATURE_EMPATHY_ENGINE,
    FEATURE_VOICE_SYNTHESIS,
    FEATURE_AVATAR_2D,
    FEATURE_AVATAR_3D,
    FEATURE_MICRO_EXPRESSIONS,
    FEATURE_AR_VR_PRESENCE,
    FEATURE_ADVANCED_MEMORY,
    FEATURE_MILESTONE_TRACKER,
    FEATURE_CONFLICT_RESOLUTION,
    FEATURE_MOOD_SYNC,
    FEATURE_PERSONALITY_MODES,
    FEATURE_CREATIVITY_ENGINE,
    FEATURE_GAMIFIED_PRODUCTIVITY,
    FEATURE_VOICE_CLONING,
    FEATURE_GAN_IMAGE_MIMICRY,
    FEATURE_HOLOGRAPHIC_PROJECTION,
    FEATURE_REAL_TIME_TRANSLATION,
    FEATURE_WELLNESS_TRACKER,
    FEATURE_SOCIAL_MEDIA_MANAGER,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
    FEATURE_LEAD_FINDER,
    FEATURE_OFFER_GENERATOR,
    FEATURE_CONVERSION_ENGINE,
    FEATURE_FULFILLMENT_ENGINE,
    FEATURE_RETENTION_ENGINE,
)
from bots.buddy_bot.conversation_engine import (
    ConversationEngine,
    ConversationTone,
    CommunicationContext,
    SUPPORTED_LANGUAGES,
)
from bots.buddy_bot.emotion_engine import (
    EmotionEngine,
    EmotionLabel,
    EmotionSource,
)
from bots.buddy_bot.memory_system import (
    MemorySystem,
    MemorySystemError,
    MilestoneCategory,
    UserProfile,
)
from bots.buddy_bot.avatar_engine import (
    AvatarEngine,
    AvatarType,
    AvatarEnvironment,
    MicroExpression,
    AvatarEngineError,
)
from bots.buddy_bot.voice_engine import (
    VoiceEngine,
    VoiceTone,
    AccentStyle,
    VoiceEngineError,
)
from bots.buddy_bot.creativity_engine import (
    CreativityEngine,
    StoryGenre,
    SongMood,
    ArtMedium,
    CreativityEngineError,
)
from bots.buddy_bot.personality_engine import (
    PersonalityEngine,
    PersonaMode,
    PersonaTone,
)
from bots.buddy_bot.lead_finder_engine import (
    LeadFinderEngine,
    BusinessLead,
    BusinessVertical,
    LeadStatus as LeadFinderStatus,
    LeadContactType,
    LeadFinderError,
    LeadFinderTierError,
)
from bots.buddy_bot.offer_generator_engine import (
    OfferGeneratorEngine,
    ServiceOffer,
    ServiceType,
    PricingModel,
    OfferGeneratorError,
    OfferGeneratorTierError,
)
from bots.buddy_bot.conversion_engine import (
    ConversionEngine,
    Proposal,
    ConversionRecord,
    OutreachChannel,
    ConversionStage,
    ConversionEngineError,
    ConversionEngineTierError,
)
from bots.buddy_bot.fulfillment_engine import (
    FulfillmentEngine,
    Deliverable,
    DeliverableType,
    DeliverableStatus,
    FulfillmentEngineError,
    FulfillmentEngineTierError,
)
from bots.buddy_bot.retention_engine import (
    RetentionEngine,
    ClientHealthRecord,
    HealthStatus,
    UpsellStage,
    UpsellOffer,
    RetentionEngineError,
    RetentionEngineTierError,
)

from framework import GlobalAISourcesFlow


class BuddyBotError(Exception):
    """Raised when a Buddy Bot operation cannot be completed."""


class BuddyBotTierError(BuddyBotError):
    """Raised when a feature is not available on the current tier."""


class BuddyBot:
    """
    DreamCo's most human-like AI companion.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature access.
    user_name : str
        Primary user's display name (used to initialise a default profile).
    user_id : str
        Unique user identifier.
    initial_persona : PersonaMode
        Starting persona mode.
    active_language : str
        ISO 639-1 language code for the primary conversation language.
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        user_name: str = "Friend",
        user_id: str = "default_user",
        initial_persona: PersonaMode = PersonaMode.CASUAL_FRIEND,
        active_language: str = "en",
    ) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self.user_id = user_id

        # GLOBAL AI SOURCES FLOW
        self.flow = GlobalAISourcesFlow(bot_name="BuddyBot")

        # --- Sub-engines ---
        self.conversation = ConversationEngine(
            active_language=active_language,
        )
        self.emotion = EmotionEngine()
        self.memory = MemorySystem(max_profiles=self.config.max_memory_profiles)
        self.avatar = AvatarEngine(
            avatar_type=(
                AvatarType.AVATAR_3D
                if self.config.has_feature(FEATURE_AVATAR_3D)
                else AvatarType.AVATAR_2D
            ),
        )
        self.voice = VoiceEngine()
        self.creativity = CreativityEngine(user_id=user_id)
        self.personality = PersonalityEngine(initial_persona=initial_persona)

        # --- Autonomous SaaS engines ---
        _is_pro_plus = tier in (Tier.PRO, Tier.ENTERPRISE)
        _is_enterprise = tier == Tier.ENTERPRISE
        self.lead_finder = LeadFinderEngine(
            max_leads_per_scan=(None if _is_enterprise else (100 if _is_pro_plus else 5)),
            can_filter_vertical=_is_pro_plus,
            can_enrich=_is_pro_plus,
            can_ai_score=_is_enterprise,
        )
        from bots.buddy_bot.offer_generator_engine import _ALL_SERVICE_TYPES, _FREE_SERVICE_TYPES
        self.offer_generator = OfferGeneratorEngine(
            available_service_types=(_ALL_SERVICE_TYPES if _is_pro_plus else _FREE_SERVICE_TYPES),
            can_dynamic_pricing=_is_pro_plus,
            can_performance_pricing=_is_enterprise,
            can_custom_bundle=_is_enterprise,
        )
        self.conversion = ConversionEngine(
            can_outreach=_is_pro_plus,
            can_sms=_is_enterprise,
            can_ai_closing=_is_enterprise,
            can_booking=_is_enterprise,
            max_outreach_per_day=(None if _is_enterprise else (50 if _is_pro_plus else 0)),
            require_human_approval=(not _is_enterprise),
        )
        self.fulfillment = FulfillmentEngine(
            can_landing_pages=_is_pro_plus,
            can_email_sequences=_is_pro_plus,
            can_funnels=_is_enterprise,
            can_automation_setup=_is_enterprise,
            can_brand_kit=_is_enterprise,
            can_bulk_generate=_is_enterprise,
        )
        self.retention = RetentionEngine(
            can_auto_checkins=_is_pro_plus,
            can_upsell_detection=_is_pro_plus,
            can_referral_engine=_is_enterprise,
            can_churn_prediction=_is_enterprise,
            can_mrr_dashboard=_is_enterprise,
        )

        # Bootstrap memory profile for the primary user
        try:
            self.memory.create_profile(
                user_id=user_id,
                display_name=user_name,
                preferred_language=active_language,
            )
        except MemorySystemError:
            pass  # Profile may already exist in long-running sessions

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        """Raise BuddyBotTierError if *feature* is not available on the current tier."""
        if not self.config.has_feature(feature):
            raise BuddyBotTierError(
                f"Feature '{feature}' is not available on the {self.config.name} tier. "
                f"Upgrade to unlock this capability."
            )

    # ------------------------------------------------------------------
    # Primary chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str, tone: str = "neutral") -> dict:
        """
        The primary conversational interface for Buddy Bot.

        Buddy automatically:
        1. Detects emotion in the user's message.
        2. Selects an appropriate conversational tone.
        3. Generates a natural, human-like response.
        4. Renders an avatar frame matching the response emotion.
        5. Records the interaction in memory.
        6. Applies personality flavouring.

        Parameters
        ----------
        message : str
            The user's message.
        tone : str
            Optional tone override (e.g. ``"empathetic"``, ``"humorous"``).

        Returns
        -------
        dict with keys: ``message``, ``emotion``, ``tone``, ``avatar_frame``,
        ``persona``, ``tier``, ``language``.
        """
        self._require_feature(FEATURE_CONVERSATIONAL_AI)

        # 1. Emotion detection
        emotion_reading = self.emotion.detect_from_text(message)
        detected_emotion = emotion_reading.label

        # 2. Resolve tone
        tone_map: dict[str, ConversationTone] = {
            "neutral": ConversationTone.NEUTRAL,
            "happy": ConversationTone.HAPPY,
            "empathetic": ConversationTone.EMPATHETIC,
            "humorous": ConversationTone.HUMOROUS,
            "calm": ConversationTone.CALM,
            "excited": ConversationTone.EXCITED,
            "serious": ConversationTone.SERIOUS,
            "encouraging": ConversationTone.ENCOURAGING,
        }
        resolved_tone = tone_map.get(tone.lower(), ConversationTone.NEUTRAL)

        # Auto-override tone based on detected emotion for empathetic responses
        if self.config.has_feature(FEATURE_EMPATHY_ENGINE):
            emotion_tone_map: dict[EmotionLabel, ConversationTone] = {
                EmotionLabel.SADNESS: ConversationTone.EMPATHETIC,
                EmotionLabel.ANGER: ConversationTone.CALM,
                EmotionLabel.FEAR: ConversationTone.EMPATHETIC,
                EmotionLabel.STRESS: ConversationTone.CALM,
                EmotionLabel.ANXIETY: ConversationTone.EMPATHETIC,
                EmotionLabel.LONELINESS: ConversationTone.EMPATHETIC,
                EmotionLabel.JOY: ConversationTone.HAPPY,
                EmotionLabel.EXCITEMENT: ConversationTone.EXCITED,
                EmotionLabel.GRATITUDE: ConversationTone.HAPPY,
            }
            if resolved_tone == ConversationTone.NEUTRAL and detected_emotion in emotion_tone_map:
                resolved_tone = emotion_tone_map[detected_emotion]

        # 3. Generate conversational response
        turn = self.conversation.respond(message, tone=resolved_tone)
        base_response = turn.response

        # 4. Mood sync (PRO+)
        mood_response = ""
        if self.config.has_feature(FEATURE_MOOD_SYNC):
            mood_response = self.emotion.sync_mood(detected_emotion)
            if mood_response and mood_response not in base_response:
                base_response = f"{mood_response}\n\n{base_response}"

        # 5. Personality flavouring
        final_response = self.personality.flavour_response(base_response)

        # 6. Avatar frame
        avatar_frame = self.avatar.render_frame(
            emotion=detected_emotion.value,
            speech_text=final_response[:100],
        )

        # 7. Memory: record interaction
        try:
            self.memory.record_interaction(self.user_id)
            # Dynamically learn topics mentioned
            if self.config.has_feature(FEATURE_ADVANCED_MEMORY):
                self._extract_interests(message)
        except MemorySystemError:
            pass

        return {
            "message": final_response,
            "emotion": detected_emotion.value,
            "tone": resolved_tone.value,
            "avatar_frame": avatar_frame.to_dict(),
            "persona": self.personality.config.active_persona.value,
            "tier": self.tier.value,
            "language": self.conversation.active_language,
        }

    def process(self, message: str, **kwargs) -> dict:
        """Alias for chat() — BuddyAI process() compatibility."""
        return self.chat(message, **kwargs)

    # ------------------------------------------------------------------
    # Greeting & introduction
    # ------------------------------------------------------------------

    def greet(self) -> str:
        """Return a persona-appropriate greeting for the primary user."""
        try:
            profile = self.memory.get_profile(self.user_id)
            name = profile.display_name
        except MemorySystemError:
            name = "Friend"
        return self.personality.get_greeting(name)

    def introduce(self) -> str:
        """Return Buddy's full self-introduction."""
        return self.personality.introduce()

    # ------------------------------------------------------------------
    # Emotion features
    # ------------------------------------------------------------------

    def detect_emotion_from_voice(self, voice_descriptors: dict) -> dict:
        """
        Detect emotion from voice feature descriptors.

        Parameters
        ----------
        voice_descriptors : dict
            Keys: ``pitch_hz``, ``tempo_wpm``, ``energy_db``, ``tremor``,
            ``pause_ratio``.

        Returns
        -------
        dict
        """
        self._require_feature(FEATURE_EMOTION_DETECTION)
        reading = self.emotion.detect_from_voice(voice_descriptors)
        return reading.to_dict()

    def detect_emotion_from_camera(self, facial_signals: dict) -> dict:
        """
        Detect emotion from facial expression signals.

        Parameters
        ----------
        facial_signals : dict
            Keys: ``smile_score``, ``brow_furrow``, ``eye_openness``,
            ``lip_compression``, ``head_tilt``.

        Returns
        -------
        dict
        """
        self._require_feature(FEATURE_EMOTION_DETECTION)
        reading = self.emotion.detect_from_camera(facial_signals)
        return reading.to_dict()

    def boost_mood(self) -> dict:
        """Return a mood boost package for the user's current emotional state."""
        self._require_feature(FEATURE_MOOD_SYNC)
        current = self.emotion.get_current_mood()
        return self.emotion.boost_mood(current)

    # ------------------------------------------------------------------
    # Memory features
    # ------------------------------------------------------------------

    def add_life_milestone(
        self,
        title: str,
        description: str,
        category: MilestoneCategory,
        date_achieved: str,
        recurring_annually: bool = False,
    ) -> dict:
        """
        Add a life milestone for the primary user.

        Requires PRO+ (FEATURE_MILESTONE_TRACKER).
        """
        self._require_feature(FEATURE_MILESTONE_TRACKER)
        milestone = self.memory.add_milestone(
            user_id=self.user_id,
            title=title,
            description=description,
            category=category,
            date_achieved=date_achieved,
            recurring_annually=recurring_annually,
        )
        return milestone.to_dict()

    def add_anniversary(
        self,
        label: str,
        month: int,
        day: int,
        year_started: int = None,
    ) -> dict:
        """
        Add an important recurring anniversary or date.

        Requires PRO+ (FEATURE_MILESTONE_TRACKER).
        """
        self._require_feature(FEATURE_MILESTONE_TRACKER)
        date_obj = self.memory.add_important_date(
            user_id=self.user_id,
            label=label,
            month=month,
            day=day,
            year_started=year_started,
        )
        return date_obj.to_dict()

    def recall_user_context(self) -> str:
        """Return a natural-language summary of what Buddy knows about the user."""
        self._require_feature(FEATURE_BASIC_MEMORY)
        try:
            return self.memory.recall_context(self.user_id)
        except MemorySystemError as exc:
            return str(exc)

    def record_episode(self, title: str, summary: str, emotion: str = "neutral") -> dict:
        """Record a significant life episode in Buddy's memory."""
        self._require_feature(FEATURE_ADVANCED_MEMORY)
        episode = self.memory.record_episode(
            user_id=self.user_id,
            title=title,
            summary=summary,
            emotion_at_time=emotion,
        )
        return episode.to_dict()

    def _extract_interests(self, text: str) -> None:
        """Heuristically extract topics of interest from user text."""
        interest_keywords = {
            "music", "coding", "programming", "art", "travel", "food", "fitness",
            "sports", "reading", "writing", "film", "gaming", "fashion", "business",
            "investing", "meditation", "yoga", "cooking", "photography", "science",
            "history", "philosophy", "nature", "technology",
        }
        for word in text.lower().split():
            clean = word.strip(".,!?;:\"'")
            if clean in interest_keywords:
                try:
                    self.memory.learn_interest(self.user_id, clean)
                except MemorySystemError:
                    pass

    # ------------------------------------------------------------------
    # Avatar features
    # ------------------------------------------------------------------

    def enter_ar_mode(self) -> dict:
        """Switch Buddy's avatar to Augmented Reality mode (PRO+)."""
        self._require_feature(FEATURE_AR_VR_PRESENCE)
        return self.avatar.enter_ar_mode()

    def enter_vr_mode(self) -> dict:
        """Switch Buddy's avatar to full VR presence (PRO+)."""
        self._require_feature(FEATURE_AR_VR_PRESENCE)
        return self.avatar.enter_vr_mode()

    def enter_holographic_mode(self) -> dict:
        """Activate holographic projection (ENTERPRISE)."""
        self._require_feature(FEATURE_HOLOGRAPHIC_PROJECTION)
        return self.avatar.enter_holographic_mode()

    def customise_avatar(self, **kwargs) -> dict:
        """Customise Buddy's visual appearance."""
        result = self.avatar.customise_appearance(**kwargs)
        return result.to_dict()

    def request_digital_twin_consent(self) -> str:
        """Generate the consent request for Digital Twin / GAN mimicry."""
        self._require_feature(FEATURE_GAN_IMAGE_MIMICRY)
        return self.avatar.request_digital_twin_consent(self.user_id)

    def grant_digital_twin_consent(self, consent_text: str) -> dict:
        """Record Digital Twin consent and confirm activation."""
        self._require_feature(FEATURE_GAN_IMAGE_MIMICRY)
        record = self.avatar.grant_consent(self.user_id, "digital_twin", consent_text)
        return record.to_dict()

    def create_digital_twin(self, image_data_reference: str) -> dict:
        """Create a GAN-powered digital twin (ENTERPRISE, consent required)."""
        self._require_feature(FEATURE_GAN_IMAGE_MIMICRY)
        return self.avatar.create_digital_twin(self.user_id, image_data_reference)

    # ------------------------------------------------------------------
    # Voice features
    # ------------------------------------------------------------------

    def synthesise_speech(self, text: str, profile_id: str = None) -> dict:
        """Synthesise text to speech using Buddy's voice engine (PRO+)."""
        self._require_feature(FEATURE_VOICE_SYNTHESIS)
        output = self.voice.synthesise(text, profile_id=profile_id)
        return output.to_dict()

    def morph_voice(
        self,
        tone: str = None,
        accent: str = None,
        pitch_delta: float = 0.0,
        speed_delta: int = 0,
    ) -> dict:
        """Adjust Buddy's voice in real time (PRO+)."""
        self._require_feature(FEATURE_VOICE_SYNTHESIS)
        tone_enum = VoiceTone(tone) if tone else None
        accent_enum = AccentStyle(accent) if accent else None
        profile = self.voice.morph_voice(
            tone=tone_enum,
            accent=accent_enum,
            pitch_delta=pitch_delta,
            speed_delta=speed_delta,
        )
        return profile.to_dict()

    def request_voice_clone_consent(self) -> str:
        """Generate the voice cloning consent request text (ENTERPRISE)."""
        self._require_feature(FEATURE_VOICE_CLONING)
        return self.voice.request_voice_clone_consent(self.user_id)

    def grant_voice_clone_consent(
        self,
        consent_text: str,
        voice_sample_reference: str,
    ) -> dict:
        """Record voice cloning consent and create the cloned voice profile (ENTERPRISE)."""
        self._require_feature(FEATURE_VOICE_CLONING)
        return self.voice.grant_voice_clone_consent(
            self.user_id,
            consent_text,
            voice_sample_reference,
        )

    # ------------------------------------------------------------------
    # Multilingual / translation
    # ------------------------------------------------------------------

    def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        """Translate *text* between two languages (PRO+)."""
        self._require_feature(FEATURE_REAL_TIME_TRANSLATION)
        result = self.conversation.translate(text, source_lang, target_lang)
        return result.to_dict()

    def set_language(self, lang_code: str) -> None:
        """Switch the active conversation language (PRO+)."""
        self._require_feature(FEATURE_MULTILINGUAL)
        self.conversation.set_language(lang_code)

    def list_supported_languages(self) -> list[dict]:
        """Return all supported languages."""
        self._require_feature(FEATURE_MULTILINGUAL)
        return self.conversation.list_supported_languages()

    # ------------------------------------------------------------------
    # Adaptive context: casual ↔ business language switching
    # ------------------------------------------------------------------

    def set_communication_context(self, context: str) -> dict:
        """
        Set the communication context for Buddy's language register.

        Parameters
        ----------
        context : str
            ``"casual"`` — relaxed, slang-friendly responses.
            ``"business"`` — professional, polished, profanity-free responses.

        Returns
        -------
        dict
            Confirmation with the new context value.
        """
        try:
            ctx = CommunicationContext(context.lower())
        except ValueError:
            raise ValueError(
                f"Invalid context '{context}'. Choose 'casual' or 'business'."
            )
        self.conversation.set_context(ctx)
        return {"context": ctx.value, "status": "updated"}

    def get_communication_context(self) -> dict:
        """Return the current communication context."""
        return {
            "context": self.conversation.context.value,
            "auto_detect": self.conversation.auto_detect_context,
        }

    def detect_communication_context(self, text: str) -> dict:
        """
        Analyse *text* and return the detected communication context
        without modifying the engine state.

        Parameters
        ----------
        text : str
            A message or phrase to analyse.

        Returns
        -------
        dict
            ``{"detected_context": "casual" | "business"}``
        """
        ctx = self.conversation.detect_context(text)
        return {"detected_context": ctx.value}


    def start_story(
        self,
        genre: str = "inspirational",
        protagonist_name: str = "Alex",
    ) -> dict:
        """Begin an interactive story (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        genre_enum = StoryGenre(genre)
        chapter = self.creativity.start_story(genre_enum, protagonist_name)
        self.creativity.award_xp(10, "story_started")
        return chapter.to_dict()

    def continue_story(self, choice_index: int, protagonist_name: str = "Alex") -> dict:
        """Advance the active story (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        chapter = self.creativity.continue_story(choice_index, protagonist_name)
        self.creativity.award_xp(5, "story_advanced")
        return chapter.to_dict()

    def write_song(
        self,
        theme: str,
        mood: str = "uplifting",
        title: str = None,
    ) -> dict:
        """Generate an original song (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        mood_enum = SongMood(mood)
        song = self.creativity.write_song(theme, mood_enum, title)
        self.creativity.award_xp(20, "song_written")
        return song.to_dict()

    def get_art_tip(self, medium: str = "digital_painting") -> str:
        """Return an art mentorship tip for *medium* (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        medium_enum = ArtMedium(medium)
        return self.creativity.get_art_tip(medium_enum)

    def brainstorm(self, topic: str, count: int = 5) -> list[str]:
        """Generate creative brainstorming ideas around *topic* (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        return self.creativity.brainstorm(topic, count)

    def write_poem(self, theme: str, lines: int = 8) -> str:
        """Generate an original poem (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        return self.creativity.write_poem(theme, lines)

    def get_daily_challenge(self) -> dict:
        """Issue today's gamified productivity challenge (PRO+)."""
        self._require_feature(FEATURE_GAMIFIED_PRODUCTIVITY)
        challenge = self.creativity.get_daily_challenge()
        return challenge.to_dict()

    def complete_challenge(self, challenge_id: str) -> dict:
        """Mark a challenge as completed and award XP (PRO+)."""
        self._require_feature(FEATURE_GAMIFIED_PRODUCTIVITY)
        return self.creativity.complete_challenge(challenge_id)

    def get_achievements(self) -> list[dict]:
        """Return all achievements (locked and unlocked) (PRO+)."""
        self._require_feature(FEATURE_GAMIFIED_PRODUCTIVITY)
        return self.creativity.get_achievements()

    def unlock_achievement(self, achievement_id: str) -> dict:
        """Unlock an achievement by ID (PRO+)."""
        self._require_feature(FEATURE_GAMIFIED_PRODUCTIVITY)
        ach = self.creativity.unlock_achievement(achievement_id)
        return ach.to_dict()

    def podcast_intro(self, show_title: str, episode_topic: str) -> str:
        """Generate a podcast intro with Buddy as co-host (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        return self.creativity.podcast_intro(show_title, episode_topic)

    # ------------------------------------------------------------------
    # Personality
    # ------------------------------------------------------------------

    def set_persona(self, persona: str, blend_with: str = None, blend_ratio: float = 1.0) -> dict:
        """Switch Buddy's active persona mode (PRO+)."""
        self._require_feature(FEATURE_PERSONALITY_MODES)
        persona_enum = PersonaMode(persona)
        blend_enum = PersonaMode(blend_with) if blend_with else None
        config = self.personality.set_persona(persona_enum, blend_enum, blend_ratio)
        return config.to_dict()

    def list_personas(self) -> list[dict]:
        """Return all available persona modes."""
        return self.personality.list_personas()

    def conflict_resolution(self, situation: str) -> str:
        """Provide AI-powered conflict resolution guidance (PRO+)."""
        self._require_feature(FEATURE_CONFLICT_RESOLUTION)
        return self.conversation.resolve_conflict(situation)

    def ethical_check(self, request: str) -> dict:
        """Check if a request is within Buddy's ethical boundaries."""
        is_ethical, reasoning = self.personality.is_request_ethical(request)
        return {"is_ethical": is_ethical, "reasoning": reasoning}

    # ------------------------------------------------------------------
    # Wellness
    # ------------------------------------------------------------------

    def wellness_check_in(self, how_are_you: str) -> dict:
        """
        Conduct a wellness check-in based on the user's self-report.

        Parameters
        ----------
        how_are_you : str
            The user's free-text response to "How are you?"

        Returns
        -------
        dict with ``message``, ``music_recommendation``, ``emotion``.
        """
        self._require_feature(FEATURE_WELLNESS_TRACKER)
        reading = self.emotion.detect_from_text(how_are_you)
        boost = self.emotion.boost_mood(reading.label)
        return boost

    # ------------------------------------------------------------------
    # System status
    # ------------------------------------------------------------------

    def system_status(self) -> dict:
        """Return a comprehensive status snapshot of Buddy Bot."""
        try:
            profile = self.memory.get_profile(self.user_id)
            user_dict = profile.to_dict()
        except MemorySystemError:
            user_dict = {"user_id": self.user_id}

        return {
            "tier": self.tier.value,
            "tier_name": self.config.name,
            "user": user_dict,
            "conversation": self.conversation.to_dict(),
            "emotion": self.emotion.to_dict(),
            "memory": self.memory.to_dict(),
            "avatar": self.avatar.to_dict(),
            "voice": self.voice.to_dict(),
            "creativity": self.creativity.to_dict(),
            "personality": self.personality.to_dict(),
            "lead_finder": self.lead_finder.to_dict(),
            "offer_generator": self.offer_generator.to_dict(),
            "conversion": self.conversion.to_dict(),
            "fulfillment": self.fulfillment.to_dict(),
            "retention": self.retention.to_dict(),
            "features_enabled": self.config.features,
        }

    # ------------------------------------------------------------------
    # Autonomous SaaS — Lead Finder
    # ------------------------------------------------------------------

    def find_leads(
        self,
        vertical: "BusinessVertical | None" = None,
        location: "str | None" = None,
        min_value: float = 0.0,
    ) -> list:
        """Scan for business leads that need marketing services (PRO+).

        Parameters
        ----------
        vertical : BusinessVertical | None
            Filter by business vertical (requires PRO).
        location : str | None
            Optional location hint.
        min_value : float
            Minimum estimated monthly value.

        Returns
        -------
        list[BusinessLead]
        """
        self._require_feature(FEATURE_LEAD_FINDER)
        return self.lead_finder.scan(
            vertical=vertical, location=location, min_value=min_value
        )

    def get_top_leads(self, n: int = 5) -> list:
        """Return the top *n* leads by estimated value (PRO+)."""
        self._require_feature(FEATURE_LEAD_FINDER)
        return self.lead_finder.get_top_leads(n)

    # ------------------------------------------------------------------
    # Autonomous SaaS — Offer Generator
    # ------------------------------------------------------------------

    def build_offer(
        self,
        business_name: str,
        service_type: "ServiceType | None" = None,
        estimated_lead_value: float = 1000.0,
    ) -> "ServiceOffer":
        """Build a tailored service offer for a lead (PRO+).

        Parameters
        ----------
        business_name : str
            Target business name.
        service_type : ServiceType | None
            Specific service type (auto-selected if None).
        estimated_lead_value : float
            Lead's estimated monthly value.

        Returns
        -------
        ServiceOffer
        """
        self._require_feature(FEATURE_OFFER_GENERATOR)
        return self.offer_generator.build_offer(
            business_name=business_name,
            service_type=service_type,
            estimated_lead_value=estimated_lead_value,
        )

    # ------------------------------------------------------------------
    # Autonomous SaaS — Conversion
    # ------------------------------------------------------------------

    def generate_proposal(
        self,
        business_name: str,
        service_headline: str,
        deliverables: list,
        monthly_fee_usd: float,
        setup_fee_usd: float,
        guarantee: str,
        channel: "OutreachChannel" = None,
    ) -> "Proposal":
        """Generate a conversion proposal for a lead (PRO+).

        Parameters
        ----------
        business_name : str
            Target business.
        service_headline : str
            Primary pitch headline.
        deliverables : list[str]
            Service deliverables to include.
        monthly_fee_usd : float
            Monthly fee.
        setup_fee_usd : float
            One-time setup fee.
        guarantee : str
            Guarantee statement.
        channel : OutreachChannel | None
            Contact channel (defaults to EMAIL).

        Returns
        -------
        Proposal
        """
        self._require_feature(FEATURE_CONVERSION_ENGINE)
        ch = channel if channel is not None else OutreachChannel.EMAIL
        return self.conversion.generate_proposal(
            business_name=business_name,
            service_headline=service_headline,
            deliverables=deliverables,
            monthly_fee_usd=monthly_fee_usd,
            setup_fee_usd=setup_fee_usd,
            guarantee=guarantee,
            channel=ch,
        )

    def handle_objection(self, business_name: str, objection_text: str) -> str:
        """Get an AI response to a lead's objection (PRO+)."""
        self._require_feature(FEATURE_CONVERSION_ENGINE)
        return self.conversion.handle_objection(business_name, objection_text)

    # ------------------------------------------------------------------
    # Autonomous SaaS — Fulfillment
    # ------------------------------------------------------------------

    def deliver_ad_copy(self, client_name: str, industry: str = "local business") -> "Deliverable":
        """Generate ad copy for a client (PRO+)."""
        self._require_feature(FEATURE_FULFILLMENT_ENGINE)
        return self.fulfillment.generate_ad_copy(client_name, industry)

    def deliver_ad_campaign(
        self,
        client_name: str,
        budget_usd: float = 1000.0,
        duration_days: int = 30,
    ) -> "Deliverable":
        """Generate a full ad campaign structure (PRO+)."""
        self._require_feature(FEATURE_FULFILLMENT_ENGINE)
        return self.fulfillment.generate_ad_campaign(client_name, budget_usd, duration_days)

    def deliver_landing_page(
        self, client_name: str, headline: str, offer_summary: str
    ) -> "Deliverable":
        """Build a landing page layout for a client (PRO+)."""
        self._require_feature(FEATURE_FULFILLMENT_ENGINE)
        return self.fulfillment.build_landing_page(client_name, headline, offer_summary)

    def deliver_email_sequence(
        self, client_name: str, sequence_length: int = 5, goal: str = "onboarding"
    ) -> "Deliverable":
        """Generate an email drip sequence (PRO+)."""
        self._require_feature(FEATURE_FULFILLMENT_ENGINE)
        return self.fulfillment.generate_email_sequence(client_name, sequence_length, goal)

    # ------------------------------------------------------------------
    # Autonomous SaaS — Retention
    # ------------------------------------------------------------------

    def add_retained_client(
        self,
        client_name: str,
        plan_name: str,
        monthly_value_usd: float,
        months_active: int = 1,
        satisfaction_score: float = 7.0,
        results_delivered: int = 0,
        last_contact_days_ago: int = 0,
    ) -> "ClientHealthRecord":
        """Register a retained client in the retention system (PRO+)."""
        self._require_feature(FEATURE_RETENTION_ENGINE)
        return self.retention.add_client(
            client_name=client_name,
            plan_name=plan_name,
            monthly_value_usd=monthly_value_usd,
            months_active=months_active,
            satisfaction_score=satisfaction_score,
            results_delivered=results_delivered,
            last_contact_days_ago=last_contact_days_ago,
        )

    def detect_upsell_moment(self, client_name: str) -> "UpsellStage":
        """Detect if a client is ready for an upsell (PRO+)."""
        self._require_feature(FEATURE_RETENTION_ENGINE)
        return self.retention.detect_upsell_moment(client_name)

    def build_upsell_offer(self, client_name: str) -> "UpsellOffer":
        """Generate a personalised upsell offer (PRO+)."""
        self._require_feature(FEATURE_RETENTION_ENGINE)
        return self.retention.build_upsell_offer(client_name)

    def get_revenue_summary(self) -> dict:
        """Return basic revenue summary from retained clients (PRO+)."""
        self._require_feature(FEATURE_RETENTION_ENGINE)
        return self.retention.simple_revenue_summary()

    # ------------------------------------------------------------------
    # Autonomous loop — convenience orchestrator
    # ------------------------------------------------------------------

    def run_autonomous_cycle(self, location: "str | None" = None) -> dict:
        """Run one full autonomous money cycle (PRO+).

        Finds leads → selects best lead → builds offer → generates proposal.

        Parameters
        ----------
        location : str | None
            Optional location filter for lead scanning.

        Returns
        -------
        dict
            Summary with ``leads_found``, ``best_lead``, ``offer``, ``proposal``.
        """
        self._require_feature(FEATURE_LEAD_FINDER)
        self._require_feature(FEATURE_OFFER_GENERATOR)
        self._require_feature(FEATURE_CONVERSION_ENGINE)

        leads = self.lead_finder.scan(location=location)
        if not leads:
            return {"status": "no_leads_found", "action": "retrying_next_cycle"}

        best = max(leads, key=lambda l: l.estimated_monthly_value_usd)
        offer = self.offer_generator.build_offer(
            business_name=best.business_name,
            estimated_lead_value=best.estimated_monthly_value_usd,
        )
        proposal = self.conversion.generate_proposal(
            business_name=best.business_name,
            service_headline=offer.headline,
            deliverables=offer.deliverables,
            monthly_fee_usd=offer.monthly_fee_usd,
            setup_fee_usd=offer.setup_fee_usd,
            guarantee=offer.guarantee,
            channel=OutreachChannel.EMAIL,
        )
        return {
            "status": "cycle_complete",
            "leads_found": len(leads),
            "best_lead": best.to_dict(),
            "offer": offer.to_dict(),
            "proposal": proposal.to_dict(),
        }

    def describe_tier(self) -> str:
        """Return a human-readable tier description."""
        cfg = self.config
        lines = [
            f"=== Buddy Bot — {cfg.name} Tier ===",
            f"Price      : ${cfg.price_usd_monthly:.2f}/month",
            f"Memory     : {'Unlimited' if cfg.is_unlimited_memory() else str(cfg.max_memory_profiles)} profiles",
            f"Languages  : {cfg.max_languages}+",
            f"Personas   : {'Unlimited' if cfg.max_personas is None else str(cfg.max_personas)}",
            f"Support    : {cfg.support_level}",
            "",
            "Features:",
        ]
        for feat in cfg.features:
            lines.append(f"  ✓ {feat.replace('_', ' ').title()}")
        return "\n".join(lines)

    def show_upgrade_path(self) -> str:
        """Return information about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            return f"You're already on the top Buddy Bot tier: {self.config.name}."
        current_features = set(self.config.features)
        new_features = [f for f in next_cfg.features if f not in current_features]
        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features unlocked:",
        ]
        for f in new_features:
            lines.append(f"  + {f.replace('_', ' ').title()}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # BuddyAI / BuddyOS integration
    # ------------------------------------------------------------------

    def register_with_buddy(self, buddy_bot_instance: object) -> None:
        """Register this BuddyBot instance with a BuddyAI orchestrator."""
        buddy_bot_instance.register_bot("buddy_bot", self)
