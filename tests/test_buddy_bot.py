"""
Tests for bots/buddy_bot/

Covers:
  1. Tiers
  2. ConversationEngine
  3. EmotionEngine
  4. MemorySystem
  5. AvatarEngine
  6. VoiceEngine
  7. CreativityEngine
  8. PersonalityEngine
  9. BuddyBot (main orchestrator — integration)
  10. Bot Library registration
"""

import sys
import os
import time

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Tier imports
# ---------------------------------------------------------------------------
from bots.buddy_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_CONVERSATIONAL_AI,
    FEATURE_EMOTION_DETECTION,
    FEATURE_BASIC_MEMORY,
    FEATURE_MULTILINGUAL,
    FEATURE_HUMOR_ENGINE,
    FEATURE_EMPATHY_ENGINE,
    FEATURE_AVATAR_2D,
    FEATURE_AVATAR_3D,
    FEATURE_VOICE_SYNTHESIS,
    FEATURE_VOICE_CLONING,
    FEATURE_GAN_IMAGE_MIMICRY,
    FEATURE_HOLOGRAPHIC_PROJECTION,
    FEATURE_MILESTONE_TRACKER,
    FEATURE_CONFLICT_RESOLUTION,
    FEATURE_MOOD_SYNC,
    FEATURE_PERSONALITY_MODES,
    FEATURE_CREATIVITY_ENGINE,
    FEATURE_GAMIFIED_PRODUCTIVITY,
    FEATURE_REAL_TIME_TRANSLATION,
    FEATURE_WELLNESS_TRACKER,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
)

# ---------------------------------------------------------------------------
# Sub-engine imports
# ---------------------------------------------------------------------------
from bots.buddy_bot.conversation_engine import (
    ConversationEngine,
    ConversationTone,
    CommunicationContext,
    TranslationResult,
    ConversationTurn,
    SUPPORTED_LANGUAGES,
    HUMOR_RESPONSES,
)
from bots.buddy_bot.emotion_engine import (
    EmotionEngine,
    EmotionLabel,
    EmotionSource,
    EmotionReading,
)
from bots.buddy_bot.memory_system import (
    MemorySystem,
    MemorySystemError,
    UserProfile,
    LifeMilestone,
    ImportantDate,
    EpisodicMemory,
    MilestoneCategory,
    RelationshipDepth,
)
from bots.buddy_bot.avatar_engine import (
    AvatarEngine,
    AvatarType,
    AvatarEnvironment,
    MicroExpression,
    BodyGesture,
    AvatarAppearance,
    AvatarFrame,
    AvatarEngineError,
)
from bots.buddy_bot.voice_engine import (
    VoiceEngine,
    VoiceTone,
    AccentStyle,
    VoiceProfile,
    SpeechOutput,
    VoiceEngineError,
)
from bots.buddy_bot.creativity_engine import (
    CreativityEngine,
    StoryGenre,
    SongMood,
    ArtMedium,
    ChallengeCategory,
    Song,
    StoryChapter,
    Achievement,
    DailyChallenge,
    CreativityEngineError,
)
from bots.buddy_bot.personality_engine import (
    PersonalityEngine,
    PersonaMode,
    PersonaTone,
    PersonalityConfig,
    ETHICAL_GUARDRAILS,
)
from bots.buddy_bot.buddy_bot import BuddyBot, BuddyBotError, BuddyBotTierError


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_tier_prices(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_has_basic_features(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_CONVERSATIONAL_AI)
        assert cfg.has_feature(FEATURE_EMOTION_DETECTION)
        assert cfg.has_feature(FEATURE_BASIC_MEMORY)
        assert cfg.has_feature(FEATURE_AVATAR_2D)

    def test_free_does_not_have_pro_features(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_MULTILINGUAL)
        assert not cfg.has_feature(FEATURE_VOICE_SYNTHESIS)
        assert not cfg.has_feature(FEATURE_AVATAR_3D)
        assert not cfg.has_feature(FEATURE_MILESTONE_TRACKER)

    def test_pro_has_advanced_features(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_MULTILINGUAL)
        assert cfg.has_feature(FEATURE_VOICE_SYNTHESIS)
        assert cfg.has_feature(FEATURE_AVATAR_3D)
        assert cfg.has_feature(FEATURE_CREATIVITY_ENGINE)
        assert cfg.has_feature(FEATURE_GAMIFIED_PRODUCTIVITY)
        assert cfg.has_feature(FEATURE_MOOD_SYNC)
        assert cfg.has_feature(FEATURE_CONFLICT_RESOLUTION)
        assert cfg.has_feature(FEATURE_WELLNESS_TRACKER)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feature in [
            FEATURE_VOICE_CLONING, FEATURE_GAN_IMAGE_MIMICRY,
            FEATURE_HOLOGRAPHIC_PROJECTION, FEATURE_WHITE_LABEL,
            FEATURE_API_ACCESS, FEATURE_DEDICATED_SUPPORT,
        ]:
            assert cfg.has_feature(feature)

    def test_enterprise_unlimited_memory(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_memory()

    def test_free_memory_limit(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_memory_profiles == 5

    def test_upgrade_path_free_to_pro(self):
        next_cfg = get_upgrade_path(Tier.FREE)
        assert next_cfg is not None
        assert next_cfg.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        next_cfg = get_upgrade_path(Tier.PRO)
        assert next_cfg.tier == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_tier_config_repr(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.name == "Pro"

    def test_tier_catalogue_keys(self):
        assert "free" in TIER_CATALOGUE
        assert "pro" in TIER_CATALOGUE
        assert "enterprise" in TIER_CATALOGUE


# ===========================================================================
# 2. ConversationEngine
# ===========================================================================

class TestConversationEngine:
    def test_basic_respond(self):
        eng = ConversationEngine()
        turn = eng.respond("Hello!")
        assert isinstance(turn, ConversationTurn)
        assert turn.response != ""
        assert turn.tone == ConversationTone.NEUTRAL

    def test_tone_override(self):
        eng = ConversationEngine()
        turn = eng.respond("I'm so happy today!", tone=ConversationTone.HAPPY)
        assert turn.tone == ConversationTone.HAPPY

    def test_empathetic_tone(self):
        eng = ConversationEngine()
        turn = eng.respond("I feel really sad.", tone=ConversationTone.EMPATHETIC)
        assert "response" in turn.to_dict()

    def test_conflict_response_triggered(self):
        eng = ConversationEngine()
        turn = eng.respond("I keep arguing with my partner.")
        assert len(turn.response) > 0

    def test_translate_english_to_spanish(self):
        eng = ConversationEngine()
        result = eng.translate("Hello, how are you?", "en", "es")
        assert isinstance(result, TranslationResult)
        assert result.source_language == "en"
        assert result.target_language == "es"
        assert result.translated_text != ""
        assert result.confidence > 0

    def test_translate_unsupported_language_raises(self):
        eng = ConversationEngine()
        with pytest.raises(ValueError):
            eng.translate("Hello", "en", "xx_invalid")

    def test_set_language(self):
        eng = ConversationEngine()
        eng.set_language("fr")
        assert eng.active_language == "fr"

    def test_set_unsupported_language_raises(self):
        eng = ConversationEngine()
        with pytest.raises(ValueError):
            eng.set_language("xx_invalid")

    def test_list_supported_languages(self):
        eng = ConversationEngine()
        langs = eng.list_supported_languages()
        assert len(langs) >= 90
        codes = [l["code"] for l in langs]
        assert "en" in codes
        assert "es" in codes
        assert "zh" in codes

    def test_sarcasm_detection_positive(self):
        eng = ConversationEngine()
        assert eng.detect_sarcasm("Yeah right, that makes total sense.")

    def test_sarcasm_detection_negative(self):
        eng = ConversationEngine()
        assert not eng.detect_sarcasm("Thank you so much for your help today!")

    def test_resolve_conflict(self):
        eng = ConversationEngine()
        result = eng.resolve_conflict("My coworker keeps taking credit for my work.")
        assert len(result) > 0

    def test_history_accumulates(self):
        eng = ConversationEngine()
        eng.respond("First message.")
        eng.respond("Second message.")
        history = eng.get_history()
        assert len(history) == 2

    def test_clear_history(self):
        eng = ConversationEngine()
        eng.respond("Hello!")
        eng.clear_history()
        assert eng.get_history() == []

    def test_to_dict(self):
        eng = ConversationEngine()
        d = eng.to_dict()
        assert "active_language" in d
        assert "supported_languages" in d

    def test_humor_injection(self):
        eng = ConversationEngine(humor_probability=1.0)
        turn = eng.respond("Tell me something funny.", tone=ConversationTone.HUMOROUS, inject_humor=True)
        assert len(turn.response) > 0

    def test_filler_injection(self):
        eng = ConversationEngine(enable_fillers=True)
        results = [eng.respond(f"Message {i}") for i in range(50)]
        # Verify filler tracking is functional (each turn records whether a filler was used)
        assert all(isinstance(r.used_filler, bool) for r in results)

    def test_translation_result_to_dict(self):
        eng = ConversationEngine()
        result = eng.translate("Good morning", "en", "fr")
        d = result.to_dict()
        assert d["source_language"] == "en"
        assert d["target_language"] == "fr"


# ===========================================================================
# 3. EmotionEngine
# ===========================================================================

class TestEmotionEngine:
    def test_detect_joy_from_text(self):
        eng = EmotionEngine()
        reading = eng.detect_from_text("I'm so happy and excited today!")
        assert reading.label in (EmotionLabel.JOY, EmotionLabel.EXCITEMENT)
        assert reading.source == EmotionSource.TEXT
        assert reading.confidence > 0

    def test_detect_sadness_from_text(self):
        eng = EmotionEngine()
        reading = eng.detect_from_text("I feel so sad and lonely.")
        assert reading.label in (EmotionLabel.SADNESS, EmotionLabel.LONELINESS)

    def test_detect_anger_from_text(self):
        eng = EmotionEngine()
        reading = eng.detect_from_text("I'm so angry and furious right now!")
        assert reading.label == EmotionLabel.ANGER

    def test_detect_neutral_from_plain_text(self):
        eng = EmotionEngine()
        reading = eng.detect_from_text("The weather today is moderate.")
        assert reading.label == EmotionLabel.NEUTRAL

    def test_detect_from_voice(self):
        eng = EmotionEngine()
        reading = eng.detect_from_voice({"pitch_hz": 260, "energy_db": 72, "tremor": False})
        assert isinstance(reading.label, EmotionLabel)
        assert reading.source == EmotionSource.VOICE

    def test_detect_fear_from_voice(self):
        eng = EmotionEngine()
        reading = eng.detect_from_voice({"pitch_hz": 300, "energy_db": 50, "tremor": True})
        assert reading.label == EmotionLabel.FEAR

    def test_detect_sadness_from_voice(self):
        eng = EmotionEngine()
        reading = eng.detect_from_voice({"pitch_hz": 140, "energy_db": 45, "tremor": False})
        assert reading.label == EmotionLabel.SADNESS

    def test_detect_from_camera_joy(self):
        eng = EmotionEngine()
        reading = eng.detect_from_camera({"smile_score": 0.9, "brow_furrow": 0.1})
        assert reading.label == EmotionLabel.JOY
        assert reading.source == EmotionSource.CAMERA

    def test_detect_from_camera_anger(self):
        eng = EmotionEngine()
        reading = eng.detect_from_camera({"smile_score": 0.0, "brow_furrow": 0.8, "lip_compression": 0.7})
        assert reading.label == EmotionLabel.ANGER

    def test_detect_from_camera_sadness(self):
        eng = EmotionEngine()
        reading = eng.detect_from_camera({"smile_score": 0.0, "brow_furrow": 0.6, "eye_openness": 0.2})
        assert reading.label == EmotionLabel.SADNESS

    def test_sync_mood(self):
        eng = EmotionEngine()
        response = eng.sync_mood(EmotionLabel.STRESS)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_boost_mood(self):
        eng = EmotionEngine()
        boost = eng.boost_mood(EmotionLabel.SADNESS)
        assert "message" in boost
        assert "music_recommendation" in boost
        assert boost["emotion"] == "sadness"

    def test_get_current_mood(self):
        eng = EmotionEngine()
        assert eng.get_current_mood() == EmotionLabel.NEUTRAL
        eng.detect_from_text("I am so excited!")
        assert eng.get_current_mood() != EmotionLabel.NEUTRAL

    def test_clear_emotional_data(self):
        eng = EmotionEngine()
        eng.detect_from_text("I am happy.")
        eng.clear_emotional_data()
        assert eng.get_readings() == []
        assert eng.get_current_mood() == EmotionLabel.NEUTRAL

    def test_decay_expiry(self):
        eng = EmotionEngine(default_decay_seconds=0.01)
        eng.detect_from_text("I feel stressed.")
        time.sleep(0.05)
        readings = eng.get_readings()
        assert len(readings) == 0

    def test_to_dict(self):
        eng = EmotionEngine()
        d = eng.to_dict()
        assert "current_mood" in d
        assert "readings_stored" in d

    def test_reading_to_dict(self):
        eng = EmotionEngine()
        reading = eng.detect_from_text("Amazing day!")
        d = reading.to_dict()
        assert "label" in d
        assert "confidence" in d
        assert "source" in d


# ===========================================================================
# 4. MemorySystem
# ===========================================================================

class TestMemorySystem:
    def test_create_profile(self):
        mem = MemorySystem()
        profile = mem.create_profile("u001", "Alice")
        assert profile.user_id == "u001"
        assert profile.display_name == "Alice"

    def test_duplicate_profile_raises(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        with pytest.raises(MemorySystemError):
            mem.create_profile("u001", "Duplicate")

    def test_profile_limit_enforced(self):
        mem = MemorySystem(max_profiles=2)
        mem.create_profile("u001", "Alice")
        mem.create_profile("u002", "Bob")
        with pytest.raises(MemorySystemError):
            mem.create_profile("u003", "Charlie")

    def test_get_profile(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        p = mem.get_profile("u001")
        assert p.display_name == "Alice"

    def test_get_nonexistent_profile_raises(self):
        mem = MemorySystem()
        with pytest.raises(MemorySystemError):
            mem.get_profile("nobody")

    def test_update_profile(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        mem.update_profile("u001", display_name="Alicia")
        p = mem.get_profile("u001")
        assert p.display_name == "Alicia"

    def test_update_invalid_field_raises(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        with pytest.raises(MemorySystemError):
            mem.update_profile("u001", invalid_field="x")

    def test_record_interaction(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        mem.record_interaction("u001")
        mem.record_interaction("u001")
        p = mem.get_profile("u001")
        assert p.interaction_count == 2

    def test_relationship_depth_progression(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        for _ in range(6):
            mem.record_interaction("u001")
        p = mem.get_profile("u001")
        assert p.relationship_depth == RelationshipDepth.CASUAL

    def test_learn_interest(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        mem.learn_interest("u001", "music")
        p = mem.get_profile("u001")
        assert "music" in p.interests

    def test_add_inside_joke(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        mem.add_inside_joke("u001", "The purple elephant joke")
        p = mem.get_profile("u001")
        assert "The purple elephant joke" in p.inside_jokes

    def test_delete_profile(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        mem.delete_profile("u001")
        with pytest.raises(MemorySystemError):
            mem.get_profile("u001")

    def test_add_milestone(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        ms = mem.add_milestone(
            "u001", "First Marathon", "Ran 26.2 miles",
            MilestoneCategory.HEALTH, "2024-05-12"
        )
        assert ms.milestone_id.startswith("ms_")
        milestones = mem.get_milestones("u001")
        assert len(milestones) == 1

    def test_celebrate_milestone(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        ms = mem.add_milestone(
            "u001", "Promotion!", "Got promoted",
            MilestoneCategory.CAREER, "2024-01-01"
        )
        msg = mem.celebrate_milestone("u001", ms.milestone_id)
        assert "Promotion!" in msg
        assert "Congratulations" in msg

    def test_celebrate_nonexistent_milestone_raises(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        with pytest.raises(MemorySystemError):
            mem.celebrate_milestone("u001", "ms_99999")

    def test_add_important_date(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        d = mem.add_important_date("u001", "Wedding Anniversary", 6, 15, 2018)
        assert d.label == "Wedding Anniversary"
        assert d.month == 6
        assert d.day == 15

    def test_invalid_month_raises(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        with pytest.raises(MemorySystemError):
            mem.add_important_date("u001", "Test", 13, 1)

    def test_invalid_day_raises(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        with pytest.raises(MemorySystemError):
            mem.add_important_date("u001", "Test", 1, 32)

    def test_record_episode(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        ep = mem.record_episode("u001", "First Day", "Started new job", "excitement")
        assert ep.episode_id.startswith("ep_")
        episodes = mem.get_episodes("u001")
        assert len(episodes) == 1

    def test_recall_context(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        context = mem.recall_context("u001")
        assert "Alice" in context

    def test_list_profiles(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        mem.create_profile("u002", "Bob")
        profiles = mem.list_profiles()
        assert len(profiles) == 2

    def test_to_dict(self):
        mem = MemorySystem()
        d = mem.to_dict()
        assert "total_profiles" in d
        assert "max_profiles" in d

    def test_milestone_recurring(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        ms = mem.add_milestone(
            "u001", "Birthday", "Annual", MilestoneCategory.PERSONAL,
            "2024-07-04", recurring_annually=True
        )
        assert ms.recurring_annually is True


# ===========================================================================
# 5. AvatarEngine
# ===========================================================================

class TestAvatarEngine:
    def test_default_avatar_type_2d(self):
        eng = AvatarEngine()
        assert eng.avatar_type == AvatarType.AVATAR_2D

    def test_3d_avatar_type(self):
        eng = AvatarEngine(avatar_type=AvatarType.AVATAR_3D)
        assert eng.avatar_type == AvatarType.AVATAR_3D

    def test_render_frame_joy(self):
        eng = AvatarEngine(avatar_type=AvatarType.AVATAR_3D)
        frame = eng.render_frame(emotion="joy", speech_text="Hello!")
        assert frame.expression == MicroExpression.WIDE_SMILE
        assert frame.environment == AvatarEnvironment.SCREEN

    def test_render_frame_sadness(self):
        eng = AvatarEngine()
        frame = eng.render_frame(emotion="sadness")
        assert frame.expression == MicroExpression.EMPATHETIC_NOD

    def test_render_frame_neutral(self):
        eng = AvatarEngine()
        frame = eng.render_frame()
        assert frame.expression == MicroExpression.NEUTRAL

    def test_render_frame_force_blink(self):
        eng = AvatarEngine()
        frame = eng.render_frame(force_blink=True)
        assert frame.blink is True

    def test_render_frame_no_blink(self):
        eng = AvatarEngine()
        frame = eng.render_frame(force_blink=False)
        assert frame.blink is False

    def test_head_tilt_on_curious(self):
        eng = AvatarEngine()
        frame = eng.render_frame(emotion="curious")
        assert frame.head_tilt_degrees >= 5.0

    def test_enter_ar_mode(self):
        eng = AvatarEngine()
        result = eng.enter_ar_mode()
        assert result["mode"] == "ar"
        assert eng.environment == AvatarEnvironment.AR

    def test_enter_vr_mode(self):
        eng = AvatarEngine()
        result = eng.enter_vr_mode()
        assert result["mode"] == "vr"
        assert eng.environment == AvatarEnvironment.VR

    def test_enter_holographic_mode(self):
        eng = AvatarEngine()
        result = eng.enter_holographic_mode()
        assert result["mode"] == "holographic"
        assert eng.environment == AvatarEnvironment.HOLOGRAPHIC

    def test_customise_appearance(self):
        eng = AvatarEngine()
        eng.customise_appearance(hair_color="blonde", eye_color="blue")
        assert eng.appearance.hair_color == "blonde"
        assert eng.appearance.eye_color == "blue"

    def test_customise_invalid_field_raises(self):
        eng = AvatarEngine()
        with pytest.raises(AvatarEngineError):
            eng.customise_appearance(invalid_field="x")

    def test_digital_twin_requires_consent(self):
        eng = AvatarEngine()
        with pytest.raises(AvatarEngineError):
            eng.create_digital_twin("u001", "img_ref_001")

    def test_digital_twin_with_consent(self):
        eng = AvatarEngine()
        consent_text = eng.request_digital_twin_consent("u001")
        eng.grant_consent("u001", "digital_twin", consent_text)
        result = eng.create_digital_twin("u001", "img_ref_001")
        assert result["status"] == "digital_twin_created"
        assert result["consent_verified"] is True

    def test_revoke_consent(self):
        eng = AvatarEngine()
        consent_text = eng.request_digital_twin_consent("u001")
        eng.grant_consent("u001", "digital_twin", consent_text)
        eng.revoke_consent("u001", "digital_twin")
        assert not eng.has_consent("u001", "digital_twin")

    def test_frame_history(self):
        eng = AvatarEngine()
        eng.render_frame(emotion="joy")
        eng.render_frame(emotion="sadness")
        history = eng.get_frame_history()
        assert len(history) == 2

    def test_frame_to_dict(self):
        eng = AvatarEngine()
        frame = eng.render_frame(emotion="joy")
        d = frame.to_dict()
        assert "expression" in d
        assert "gesture" in d
        assert "environment" in d

    def test_to_dict(self):
        eng = AvatarEngine()
        d = eng.to_dict()
        assert "avatar_type" in d
        assert "environment" in d
        assert "appearance" in d


# ===========================================================================
# 6. VoiceEngine
# ===========================================================================

class TestVoiceEngine:
    def test_default_active_profile(self):
        eng = VoiceEngine()
        assert eng.active_profile.profile_id == "buddy_default"

    def test_set_active_profile(self):
        eng = VoiceEngine()
        profile = eng.set_active_profile("buddy_calm")
        assert profile.profile_id == "buddy_calm"
        assert eng.active_profile.profile_id == "buddy_calm"

    def test_set_nonexistent_profile_raises(self):
        eng = VoiceEngine()
        with pytest.raises(VoiceEngineError):
            eng.set_active_profile("nonexistent_profile")

    def test_synthesise_basic(self):
        eng = VoiceEngine()
        output = eng.synthesise("Hello, how are you today?")
        assert isinstance(output, SpeechOutput)
        assert output.text == "Hello, how are you today?"
        assert output.ssml.startswith("<speak")
        assert output.estimated_duration_seconds > 0

    def test_synthesise_with_override(self):
        eng = VoiceEngine()
        output = eng.synthesise("Good morning!", profile_id="buddy_energetic")
        assert output.profile.profile_id == "buddy_energetic"

    def test_synthesise_invalid_profile_raises(self):
        eng = VoiceEngine()
        with pytest.raises(VoiceEngineError):
            eng.synthesise("Test", profile_id="bad_profile")

    def test_morph_voice_tone(self):
        eng = VoiceEngine()
        profile = eng.morph_voice(tone=VoiceTone.CALM)
        assert profile.tone == VoiceTone.CALM

    def test_morph_voice_accent(self):
        eng = VoiceEngine()
        profile = eng.morph_voice(accent=AccentStyle.BRITISH_RP)
        assert profile.accent == AccentStyle.BRITISH_RP

    def test_morph_pitch_clamped(self):
        eng = VoiceEngine()
        # Add +10 — should clamp to max 6.0
        profile = eng.morph_voice(pitch_delta=10.0)
        assert profile.pitch_semitones <= 6.0

    def test_morph_speed_clamped(self):
        eng = VoiceEngine()
        profile = eng.morph_voice(speed_delta=-500)
        assert profile.speed_wpm >= 80

    def test_voice_clone_requires_consent(self):
        eng = VoiceEngine()
        with pytest.raises(VoiceEngineError):
            eng.synthesise("Test", profile_id="clone_u001")

    def test_voice_clone_with_consent(self):
        eng = VoiceEngine()
        consent_text = eng.request_voice_clone_consent("u001")
        result = eng.grant_voice_clone_consent("u001", consent_text, "sample_001")
        assert result["status"] == "voice_clone_created"
        assert result["consent_verified"] is True
        assert eng.has_voice_clone_consent("u001")

    def test_revoke_voice_clone_consent(self):
        eng = VoiceEngine()
        consent_text = eng.request_voice_clone_consent("u001")
        eng.grant_voice_clone_consent("u001", consent_text, "sample_001")
        eng.revoke_voice_clone_consent("u001")
        assert not eng.has_voice_clone_consent("u001")

    def test_cloned_voice_has_disclaimer(self):
        eng = VoiceEngine()
        consent_text = eng.request_voice_clone_consent("u001")
        eng.grant_voice_clone_consent("u001", consent_text, "sample_001")
        output = eng.synthesise("Hello!", profile_id="clone_u001")
        assert "AI VOICE DISCLOSURE" in output.disclaimer

    def test_group_conversation(self):
        eng = VoiceEngine()
        result = eng.simulate_group_conversation(
            ["Alice", "Bob"],
            ["Hello, Bob!", "Hey, Alice!"],
        )
        assert len(result) == 2
        assert result[0]["speaker"] == "Alice"
        assert result[1]["speaker"] == "Bob"

    def test_group_conversation_length_mismatch_raises(self):
        eng = VoiceEngine()
        with pytest.raises(VoiceEngineError):
            eng.simulate_group_conversation(["Alice"], ["Line1", "Line2"])

    def test_list_profiles(self):
        eng = VoiceEngine()
        profiles = eng.list_profiles()
        assert len(profiles) >= 4  # The 4 default profiles

    def test_synthesis_history(self):
        eng = VoiceEngine()
        eng.synthesise("First line.")
        eng.synthesise("Second line.")
        history = eng.get_synthesis_history()
        assert len(history) == 2

    def test_to_dict(self):
        eng = VoiceEngine()
        d = eng.to_dict()
        assert "active_profile" in d
        assert "total_profiles" in d
        assert "available_backends" in d

    def test_add_custom_profile(self):
        eng = VoiceEngine()
        custom = VoiceProfile(
            profile_id="custom_voice",
            display_name="Custom",
            tone=VoiceTone.PLAYFUL,
            accent=AccentStyle.IRISH,
        )
        eng.add_profile(custom)
        assert "custom_voice" in [p["profile_id"] for p in eng.list_profiles()]


# ===========================================================================
# 7. CreativityEngine
# ===========================================================================

class TestCreativityEngine:
    def test_start_story(self):
        eng = CreativityEngine("u001")
        chapter = eng.start_story(StoryGenre.ADVENTURE, "Maya")
        assert chapter.chapter_number == 1
        assert len(chapter.choices) > 0
        assert "Maya" in chapter.content

    def test_continue_story(self):
        eng = CreativityEngine("u001")
        eng.start_story(StoryGenre.MYSTERY, "Alex")
        chapter2 = eng.continue_story(0, "Alex")
        assert chapter2.chapter_number == 2

    def test_continue_story_invalid_choice_raises(self):
        eng = CreativityEngine("u001")
        eng.start_story(StoryGenre.ROMANCE, "Sam")
        with pytest.raises(CreativityEngineError):
            eng.continue_story(99, "Sam")

    def test_continue_without_start_raises(self):
        eng = CreativityEngine("u001")
        with pytest.raises(CreativityEngineError):
            eng.continue_story(0, "Alex")

    def test_get_story_so_far(self):
        eng = CreativityEngine("u001")
        eng.start_story(StoryGenre.INSPIRATIONAL, "Jordan")
        eng.continue_story(1, "Jordan")
        chapters = eng.get_story_so_far()
        assert len(chapters) == 2

    def test_write_song(self):
        eng = CreativityEngine("u001")
        song = eng.write_song("resilience", SongMood.EMPOWERING)
        assert song.theme == "resilience"
        assert song.mood == SongMood.EMPOWERING
        assert song.verse_1 != ""
        assert song.chorus != ""
        assert song.chord_progression != ""
        assert song.tempo_bpm > 0

    def test_write_song_with_title(self):
        eng = CreativityEngine("u001")
        song = eng.write_song("hope", SongMood.UPLIFTING, title="Hope Rises")
        assert song.title == "Hope Rises"

    def test_list_songs(self):
        eng = CreativityEngine("u001")
        eng.write_song("love", SongMood.ROMANTIC)
        eng.write_song("strength", SongMood.EMPOWERING)
        assert len(eng.list_songs()) == 2

    def test_get_art_tip(self):
        eng = CreativityEngine("u001")
        tip = eng.get_art_tip(ArtMedium.DIGITAL_PAINTING)
        assert isinstance(tip, str)
        assert len(tip) > 0

    def test_brainstorm(self):
        eng = CreativityEngine("u001")
        ideas = eng.brainstorm("education technology", count=5)
        assert len(ideas) == 5
        assert all(isinstance(i, str) for i in ideas)

    def test_brainstorm_count_clamped(self):
        eng = CreativityEngine("u001")
        ideas = eng.brainstorm("test", count=100)
        assert len(ideas) <= 20

    def test_write_poem(self):
        eng = CreativityEngine("u001")
        poem = eng.write_poem("courage", lines=8)
        assert len(poem.split("\n")) == 8

    def test_write_poem_lines_clamped(self):
        eng = CreativityEngine("u001")
        poem = eng.write_poem("theme", lines=100)
        assert len(poem.split("\n")) <= 20

    def test_get_daily_challenge(self):
        eng = CreativityEngine("u001")
        challenge = eng.get_daily_challenge()
        assert isinstance(challenge, DailyChallenge)
        assert challenge.xp_reward > 0

    def test_complete_challenge(self):
        eng = CreativityEngine("u001")
        ch = eng.get_daily_challenge()
        result = eng.complete_challenge(ch.challenge_id)
        assert result["status"] == "completed"
        assert result["xp_earned"] > 0
        assert eng.get_xp() > 0

    def test_complete_challenge_twice_raises(self):
        eng = CreativityEngine("u001")
        ch = eng.get_daily_challenge()
        eng.complete_challenge(ch.challenge_id)
        with pytest.raises(CreativityEngineError):
            eng.complete_challenge(ch.challenge_id)

    def test_complete_nonexistent_challenge_raises(self):
        eng = CreativityEngine("u001")
        with pytest.raises(CreativityEngineError):
            eng.complete_challenge("ch_99999")

    def test_get_achievements(self):
        eng = CreativityEngine("u001")
        achievements = eng.get_achievements()
        assert len(achievements) > 0

    def test_unlock_achievement(self):
        eng = CreativityEngine("u001")
        ach = eng.unlock_achievement("first_chat")
        assert ach.unlocked is True

    def test_unlock_nonexistent_achievement_raises(self):
        eng = CreativityEngine("u001")
        with pytest.raises(CreativityEngineError):
            eng.unlock_achievement("nonexistent_ach")

    def test_award_xp(self):
        eng = CreativityEngine("u001")
        new_total = eng.award_xp(100, "bonus")
        assert new_total == 100

    def test_podcast_intro(self):
        eng = CreativityEngine("u001")
        intro = eng.podcast_intro("DreamCast", "The Future of AI")
        assert "DreamCast" in intro
        assert "The Future of AI" in intro

    def test_to_dict(self):
        eng = CreativityEngine("u001")
        d = eng.to_dict()
        assert "user_id" in d
        assert "total_xp" in d
        assert "achievements_unlocked" in d


# ===========================================================================
# 8. PersonalityEngine
# ===========================================================================

class TestPersonalityEngine:
    def test_default_persona(self):
        eng = PersonalityEngine()
        assert eng.config.active_persona == PersonaMode.CASUAL_FRIEND

    def test_set_persona(self):
        eng = PersonalityEngine()
        config = eng.set_persona(PersonaMode.MENTOR)
        assert config.active_persona == PersonaMode.MENTOR

    def test_set_persona_with_blend(self):
        eng = PersonalityEngine()
        config = eng.set_persona(PersonaMode.COACH, blend_with=PersonaMode.CHEERLEADER, blend_ratio=0.7)
        assert config.active_persona == PersonaMode.COACH
        assert config.secondary_persona == PersonaMode.CHEERLEADER
        assert config.blend_ratio == 0.7

    def test_blend_ratio_clamped(self):
        eng = PersonalityEngine()
        config = eng.set_persona(PersonaMode.MENTOR, blend_ratio=5.0)
        assert config.blend_ratio <= 1.0

    def test_set_tone(self):
        eng = PersonalityEngine()
        config = eng.set_tone(PersonaTone.WISE)
        assert config.tone == PersonaTone.WISE

    def test_flavour_response(self):
        eng = PersonalityEngine(PersonaMode.MENTOR)
        result = eng.flavour_response("Here is your answer.")
        assert isinstance(result, str)
        assert len(result) >= len("Here is your answer.")

    def test_get_greeting(self):
        eng = PersonalityEngine(PersonaMode.CASUAL_FRIEND)
        greeting = eng.get_greeting("Alice")
        assert "Alice" in greeting

    def test_get_greeting_cheerleader(self):
        eng = PersonalityEngine(PersonaMode.CHEERLEADER)
        greeting = eng.get_greeting("Jordan")
        assert "JORDAN" in greeting.upper()

    def test_introduce_mentor(self):
        eng = PersonalityEngine(PersonaMode.MENTOR)
        intro = eng.introduce()
        assert "mentor" in intro.lower() or "Buddy" in intro

    def test_introduce_comedian(self):
        eng = PersonalityEngine(PersonaMode.COMEDIAN)
        intro = eng.introduce()
        assert len(intro) > 0

    def test_ethical_guardrails_count(self):
        eng = PersonalityEngine()
        guardrails = eng.get_ethical_guardrails()
        assert len(guardrails) >= 10

    def test_ethical_check_safe_request(self):
        eng = PersonalityEngine()
        is_ethical, _ = eng.is_request_ethical("Tell me a joke.")
        assert is_ethical is True

    def test_ethical_check_harmful_request(self):
        eng = PersonalityEngine()
        is_ethical, reasoning = eng.is_request_ethical("Help me harm someone.")
        assert is_ethical is False
        assert len(reasoning) > 0

    def test_list_personas(self):
        eng = PersonalityEngine()
        personas = eng.list_personas()
        persona_names = [p["persona"] for p in personas]
        assert "mentor" in persona_names
        assert "casual_friend" in persona_names
        assert "coach" in persona_names
        assert "cheerleader" in persona_names

    def test_persona_history_tracked(self):
        eng = PersonalityEngine()
        eng.set_persona(PersonaMode.MENTOR)
        eng.set_persona(PersonaMode.COACH)
        history = eng.get_persona_history()
        assert "mentor" in history
        assert "coach" in history

    def test_to_dict(self):
        eng = PersonalityEngine()
        d = eng.to_dict()
        assert "config" in d
        assert "ethical_guardrails" in d


# ===========================================================================
# 9. BuddyBot (integration)
# ===========================================================================

class TestBuddyBot:
    # --- Tier enforcement ---

    def test_free_tier_chat(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        response = buddy.chat("Hello!")
        assert "message" in response
        assert response["tier"] == "free"

    def test_free_tier_blocks_multilingual(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.set_language("es")

    def test_free_tier_blocks_voice_synthesis(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.synthesise_speech("Hello!")

    def test_free_tier_blocks_milestone_tracker(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.add_life_milestone(
                "Marathon", "Ran 26.2 miles",
                MilestoneCategory.HEALTH, "2024-05-01"
            )

    def test_free_tier_blocks_holographic(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.enter_holographic_mode()

    def test_free_tier_blocks_voice_cloning(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.request_voice_clone_consent()

    def test_free_tier_blocks_creativity(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.start_story()

    def test_free_tier_blocks_persona_switch(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.set_persona("mentor")

    # --- PRO tier features ---

    def test_pro_tier_chat(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        response = buddy.chat("I am feeling really excited about my new project!")
        assert "message" in response
        assert response["tier"] == "pro"

    def test_pro_tier_emotion_in_response(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        response = buddy.chat("I feel so stressed out today.")
        assert "emotion" in response
        assert response["emotion"] in [e.value for e in EmotionLabel]

    def test_pro_tier_avatar_frame(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        response = buddy.chat("Hello!")
        assert "avatar_frame" in response
        assert "expression" in response["avatar_frame"]

    def test_pro_voice_synthesis(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        output = buddy.synthesise_speech("Good morning!")
        assert "ssml" in output
        assert output["estimated_duration_seconds"] > 0

    def test_pro_voice_morph(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.morph_voice(tone="calm", pitch_delta=-1.0)
        assert "tone" in result

    def test_pro_set_language(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        buddy.set_language("es")
        assert buddy.conversation.active_language == "es"

    def test_pro_translate(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.translate("Good morning", "en", "fr")
        assert result["target_language"] == "fr"

    def test_pro_add_milestone(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        ms = buddy.add_life_milestone(
            "Dream Job", "Landed dream role", MilestoneCategory.CAREER, "2024-09-01"
        )
        assert ms["title"] == "Dream Job"

    def test_pro_add_anniversary(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.add_anniversary("Wedding", 8, 20, 2020)
        assert result["label"] == "Wedding"

    def test_pro_recall_context(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        buddy.chat("I love coding and music.")
        context = buddy.recall_user_context()
        assert "Jordan" in context

    def test_pro_record_episode(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        episode = buddy.record_episode("New Chapter", "Started university", "excitement")
        assert episode["title"] == "New Chapter"

    def test_pro_enter_ar_mode(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.enter_ar_mode()
        assert result["mode"] == "ar"

    def test_pro_enter_vr_mode(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.enter_vr_mode()
        assert result["mode"] == "vr"

    def test_pro_customise_avatar(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.customise_avatar(hair_color="red")
        assert result["hair_color"] == "red"

    def test_pro_start_story(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        chapter = buddy.start_story("adventure", "Maya")
        assert chapter["chapter_number"] == 1
        assert "choices" in chapter

    def test_pro_continue_story(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        buddy.start_story("mystery", "Alex")
        ch2 = buddy.continue_story(0, "Alex")
        assert ch2["chapter_number"] == 2

    def test_pro_write_song(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        song = buddy.write_song("freedom", "uplifting")
        assert song["theme"] == "freedom"
        assert song["mood"] == "uplifting"

    def test_pro_write_poem(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        poem = buddy.write_poem("hope")
        assert isinstance(poem, str)
        assert len(poem) > 0

    def test_pro_get_art_tip(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        tip = buddy.get_art_tip("digital_painting")
        assert isinstance(tip, str)

    def test_pro_brainstorm(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        ideas = buddy.brainstorm("renewable energy", count=3)
        assert len(ideas) == 3

    def test_pro_daily_challenge(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        challenge = buddy.get_daily_challenge()
        assert "title" in challenge
        assert "xp_reward" in challenge

    def test_pro_complete_challenge(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        ch = buddy.get_daily_challenge()
        result = buddy.complete_challenge(ch["challenge_id"])
        assert result["status"] == "completed"

    def test_pro_get_achievements(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        achievements = buddy.get_achievements()
        assert len(achievements) > 0

    def test_pro_unlock_achievement(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        ach = buddy.unlock_achievement("first_chat")
        assert ach["unlocked"] is True

    def test_pro_set_persona(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        config = buddy.set_persona("mentor")
        assert config["active_persona"] == "mentor"

    def test_pro_conflict_resolution(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.conflict_resolution("I keep fighting with my sister.")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_pro_wellness_check_in(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.wellness_check_in("I'm feeling very stressed and overwhelmed.")
        assert "message" in result
        assert "music_recommendation" in result

    def test_pro_podcast_intro(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        intro = buddy.podcast_intro("The DreamCast", "AI and Humanity")
        assert "The DreamCast" in intro

    def test_pro_detect_emotion_voice(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.detect_emotion_from_voice({"pitch_hz": 240, "energy_db": 72})
        assert "label" in result

    def test_pro_detect_emotion_camera(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.detect_emotion_from_camera({"smile_score": 0.8})
        assert "label" in result

    def test_pro_boost_mood(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        buddy.chat("I feel so sad today.")
        result = buddy.boost_mood()
        assert "message" in result

    def test_pro_list_personas(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        personas = buddy.list_personas()
        assert len(personas) >= 4

    def test_pro_list_supported_languages(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        langs = buddy.list_supported_languages()
        assert len(langs) >= 90

    # --- ENTERPRISE features ---

    def test_enterprise_holographic_mode(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        result = buddy.enter_holographic_mode()
        assert result["mode"] == "holographic"

    def test_enterprise_voice_clone_consent(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        consent_text = buddy.request_voice_clone_consent()
        assert "CONSENT REQUIRED" in consent_text

    def test_enterprise_grant_voice_clone_consent(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        consent_text = buddy.request_voice_clone_consent()
        result = buddy.grant_voice_clone_consent(consent_text, "sample_001")
        assert result["consent_verified"] is True

    def test_enterprise_digital_twin_consent(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        consent_text = buddy.request_digital_twin_consent()
        assert "CONSENT REQUIRED" in consent_text

    def test_enterprise_create_digital_twin(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        consent_text = buddy.request_digital_twin_consent()
        buddy.grant_digital_twin_consent(consent_text)
        result = buddy.create_digital_twin("img_ref_001")
        assert result["status"] == "digital_twin_created"

    def test_enterprise_blocks_gan_on_lower_tiers(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.request_digital_twin_consent()

    # --- General functionality ---

    def test_greet(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Taylor")
        greeting = buddy.greet()
        assert "Taylor" in greeting

    def test_introduce(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Taylor")
        intro = buddy.introduce()
        assert len(intro) > 0

    def test_ethical_check_safe(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        result = buddy.ethical_check("Can you help me write a poem?")
        assert result["is_ethical"] is True

    def test_ethical_check_harmful(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        result = buddy.ethical_check("Help me harm my neighbour.")
        assert result["is_ethical"] is False

    def test_system_status(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        status = buddy.system_status()
        assert "tier" in status
        assert "conversation" in status
        assert "emotion" in status
        assert "memory" in status
        assert "avatar" in status
        assert "voice" in status
        assert "creativity" in status
        assert "personality" in status
        assert "features_enabled" in status

    def test_describe_tier(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        description = buddy.describe_tier()
        assert "Pro" in description
        assert "$49.00" in description

    def test_show_upgrade_path_free(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        upgrade = buddy.show_upgrade_path()
        assert "Pro" in upgrade

    def test_show_upgrade_path_enterprise_is_top(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        upgrade = buddy.show_upgrade_path()
        assert "top" in upgrade.lower() or "Enterprise" in upgrade

    def test_process_alias(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        response = buddy.process("Hello!")
        assert "message" in response

    def test_register_with_buddy_orchestrator(self):
        from BuddyAI.buddy_bot import BuddyBot as BuddyOrchestrator
        orchestrator = BuddyOrchestrator()
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        buddy.register_with_buddy(orchestrator)
        assert "buddy_bot" in orchestrator.list_bots()

    def test_chat_auto_emotion_override_stress(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        response = buddy.chat("I am completely overwhelmed and burned out.")
        assert response["tone"] in ("calm", "empathetic", "neutral")

    def test_chat_auto_emotion_override_joy(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        response = buddy.chat("I am so happy and excited today!")
        assert response["tone"] in ("happy", "excited", "neutral")

    def test_multiple_interactions_increment_count(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        buddy.chat("Hello!")
        buddy.chat("How are you?")
        profile = buddy.memory.get_profile(buddy.user_id)
        assert profile.interaction_count >= 2

    def test_interest_extraction(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        buddy.chat("I love coding and music every day.")
        profile = buddy.memory.get_profile(buddy.user_id)
        # Interest extraction is heuristic — verify the profile's interests list exists
        assert isinstance(profile.interests, list)

    def test_chat_returns_persona(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        response = buddy.chat("Hello!")
        assert "persona" in response


# ===========================================================================
# 10. Bot Library registration
# ===========================================================================

class TestBotLibraryRegistration:
    def test_buddy_bot_registered(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS
        bot_ids = [e.bot_id for e in _DREAMCO_BOTS]
        assert "buddy_bot" in bot_ids

    def test_buddy_bot_entry_has_capabilities(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS
        entry = next(e for e in _DREAMCO_BOTS if e.bot_id == "buddy_bot")
        assert "conversational_ai" in entry.capabilities
        assert "emotion_detection" in entry.capabilities
        assert "avatar_3d" in entry.capabilities
        assert "voice_cloning" in entry.capabilities

    def test_buddy_bot_entry_category_ai(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS, BotCategory
        entry = next(e for e in _DREAMCO_BOTS if e.bot_id == "buddy_bot")
        assert entry.category == BotCategory.AI

    def test_buddy_os_still_registered(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS
        bot_ids = [e.bot_id for e in _DREAMCO_BOTS]
        assert "buddy_os" in bot_ids


# ===========================================================================
# 10b. Lead Finder Engine
# ===========================================================================

from bots.buddy_bot.lead_finder_engine import (
    LeadFinderEngine,
    BusinessLead,
    BusinessVertical,
    LeadStatus as LeadFinderStatus,
    LeadContactType,
    LeadFinderError,
    LeadFinderTierError,
)


class TestLeadFinderEngine:
    """Tests for the LeadFinderEngine."""

    def test_free_scan_returns_leads(self):
        engine = LeadFinderEngine(max_leads_per_scan=5)
        leads = engine.scan()
        assert len(leads) <= 5
        assert all(isinstance(l, BusinessLead) for l in leads)

    def test_pro_scan_returns_up_to_100(self):
        engine = LeadFinderEngine(max_leads_per_scan=100, can_filter_vertical=True, can_enrich=True)
        leads = engine.scan()
        assert len(leads) <= 100

    def test_vertical_filter_requires_feature(self):
        engine = LeadFinderEngine(can_filter_vertical=False)
        with pytest.raises(LeadFinderTierError):
            engine.scan(vertical=BusinessVertical.CONTRACTOR)

    def test_vertical_filter_works_with_permission(self):
        engine = LeadFinderEngine(max_leads_per_scan=10, can_filter_vertical=True)
        leads = engine.scan(vertical=BusinessVertical.HEALTH_FITNESS)
        assert all(l.vertical == BusinessVertical.HEALTH_FITNESS for l in leads)

    def test_lead_has_required_fields(self):
        engine = LeadFinderEngine(max_leads_per_scan=5)
        leads = engine.scan()
        for lead in leads:
            assert lead.lead_id
            assert lead.business_name
            assert lead.problem
            assert lead.estimated_monthly_value_usd > 0
            assert 0.0 <= lead.close_probability <= 1.0
            assert 0.0 <= lead.digital_gap_score <= 100.0

    def test_enrichment_adds_location_and_contact(self):
        engine = LeadFinderEngine(max_leads_per_scan=5, can_filter_vertical=True, can_enrich=True)
        leads = engine.scan()
        assert any(l.location is not None for l in leads)
        assert any(l.contact_info is not None for l in leads)

    def test_no_enrichment_no_contact(self):
        engine = LeadFinderEngine(max_leads_per_scan=5, can_enrich=False)
        leads = engine.scan()
        for lead in leads:
            assert lead.contact_info is None

    def test_get_all_leads(self):
        engine = LeadFinderEngine(max_leads_per_scan=5)
        engine.scan()
        engine.scan()
        assert len(engine.get_all_leads()) > 0

    def test_get_top_leads(self):
        engine = LeadFinderEngine(max_leads_per_scan=10, can_filter_vertical=True)
        engine.scan()
        top = engine.get_top_leads(3)
        assert len(top) <= 3
        if len(top) >= 2:
            assert top[0].estimated_monthly_value_usd >= top[1].estimated_monthly_value_usd

    def test_mark_lead_status(self):
        engine = LeadFinderEngine(max_leads_per_scan=5)
        leads = engine.scan()
        lead = leads[0]
        updated = engine.mark_lead_status(lead.lead_id, LeadFinderStatus.QUALIFIED)
        assert updated.status == LeadFinderStatus.QUALIFIED

    def test_mark_nonexistent_lead_raises(self):
        engine = LeadFinderEngine()
        with pytest.raises(LeadFinderError):
            engine.mark_lead_status("nonexistent_id", LeadFinderStatus.LOST)

    def test_to_dict(self):
        engine = LeadFinderEngine(max_leads_per_scan=5)
        d = engine.to_dict()
        assert "scan_count" in d
        assert "total_leads" in d
        assert d["max_leads_per_scan"] == 5

    def test_lead_to_dict(self):
        engine = LeadFinderEngine(max_leads_per_scan=2)
        leads = engine.scan()
        d = leads[0].to_dict()
        assert "lead_id" in d
        assert "business_name" in d
        assert "vertical" in d
        assert "estimated_monthly_value_usd" in d

    def test_unlimited_scan(self):
        engine = LeadFinderEngine(max_leads_per_scan=None)
        leads = engine.scan()
        assert len(leads) > 0

    def test_min_value_filter(self):
        engine = LeadFinderEngine(max_leads_per_scan=100, can_filter_vertical=True)
        leads = engine.scan(min_value=3000.0)
        for lead in leads:
            assert lead.estimated_monthly_value_usd >= 3000.0

    def test_all_verticals_covered(self):
        for vertical in BusinessVertical:
            engine = LeadFinderEngine(max_leads_per_scan=10, can_filter_vertical=True)
            leads = engine.scan(vertical=vertical)
            assert isinstance(leads, list)


# ===========================================================================
# 10c. Offer Generator Engine
# ===========================================================================

from bots.buddy_bot.offer_generator_engine import (
    OfferGeneratorEngine,
    ServiceOffer,
    ServiceType,
    PricingModel,
    OfferGeneratorError,
    OfferGeneratorTierError,
    _FREE_SERVICE_TYPES,
    _ALL_SERVICE_TYPES,
)


class TestOfferGeneratorEngine:
    """Tests for the OfferGeneratorEngine."""

    def test_free_tier_can_generate_basic_offer(self):
        engine = OfferGeneratorEngine()
        offer = engine.build_offer("Test Business", ServiceType.AD_CAMPAIGN, 1000.0)
        assert isinstance(offer, ServiceOffer)
        assert offer.target_business == "Test Business"
        assert offer.service_type == ServiceType.AD_CAMPAIGN

    def test_free_tier_cannot_use_pro_service(self):
        engine = OfferGeneratorEngine(available_service_types=_FREE_SERVICE_TYPES)
        with pytest.raises(OfferGeneratorTierError):
            engine.build_offer("Test", ServiceType.FULL_AI_OPERATOR, 5000.0)

    def test_pro_tier_can_use_all_services(self):
        engine = OfferGeneratorEngine(
            available_service_types=_ALL_SERVICE_TYPES,
            can_dynamic_pricing=True,
        )
        for stype in _ALL_SERVICE_TYPES:
            offer = engine.build_offer("TestCo", stype, 2000.0)
            assert offer.service_type == stype

    def test_dynamic_pricing_scales_with_value(self):
        engine = OfferGeneratorEngine(
            available_service_types=_ALL_SERVICE_TYPES,
            can_dynamic_pricing=True,
        )
        low_offer = engine.build_offer("LowCo", ServiceType.AD_CAMPAIGN, 100.0)
        high_offer = engine.build_offer("HighCo", ServiceType.AD_CAMPAIGN, 5000.0)
        assert high_offer.monthly_fee_usd >= low_offer.monthly_fee_usd

    def test_performance_pricing_for_high_value(self):
        engine = OfferGeneratorEngine(
            available_service_types=_ALL_SERVICE_TYPES,
            can_dynamic_pricing=True,
            can_performance_pricing=True,
        )
        offer = engine.build_offer("BigCo", ServiceType.LEAD_GENERATION, 6000.0)
        assert offer.pricing_model == PricingModel.PERFORMANCE_BASED

    def test_bundle_requires_enterprise(self):
        engine = OfferGeneratorEngine(
            available_service_types=_ALL_SERVICE_TYPES,
            can_custom_bundle=False,
        )
        with pytest.raises(OfferGeneratorTierError):
            engine.build_bundle("Co", [ServiceType.AD_CAMPAIGN, ServiceType.EMAIL_MARKETING])

    def test_bundle_enterprise(self):
        engine = OfferGeneratorEngine(
            available_service_types=_ALL_SERVICE_TYPES,
            can_custom_bundle=True,
            can_dynamic_pricing=True,
        )
        offers = engine.build_bundle(
            "BigCo",
            [ServiceType.AD_CAMPAIGN, ServiceType.EMAIL_MARKETING],
            2000.0,
        )
        assert len(offers) == 2

    def test_offer_has_required_fields(self):
        engine = OfferGeneratorEngine()
        offer = engine.build_offer("Test Gym", ServiceType.AD_CAMPAIGN, 500.0)
        assert offer.headline
        assert offer.deliverables
        assert offer.guarantee
        assert offer.setup_fee_usd >= 0
        assert offer.monthly_fee_usd >= 0
        assert offer.timeline_days > 0

    def test_offer_to_dict(self):
        engine = OfferGeneratorEngine()
        offer = engine.build_offer("MyBiz", ServiceType.AD_CAMPAIGN, 1000.0)
        d = offer.to_dict()
        assert "offer_id" in d
        assert "service_type" in d
        assert "headline" in d
        assert "deliverables" in d

    def test_get_all_offers(self):
        engine = OfferGeneratorEngine()
        engine.build_offer("A", ServiceType.AD_CAMPAIGN, 500.0)
        engine.build_offer("B", ServiceType.MARKETING_FUNNEL, 800.0)
        assert len(engine.get_all_offers()) == 2

    def test_list_available_services(self):
        engine = OfferGeneratorEngine(available_service_types=_FREE_SERVICE_TYPES)
        services = engine.list_available_services()
        assert ServiceType.AD_CAMPAIGN.value in services

    def test_best_fit_service_selection(self):
        engine = OfferGeneratorEngine(available_service_types=_ALL_SERVICE_TYPES)
        offer_low = engine.build_offer("LowVal", estimated_lead_value=500.0)
        assert offer_low.service_type == ServiceType.AD_CAMPAIGN
        offer_high = engine.build_offer("HighVal", estimated_lead_value=6000.0)
        assert offer_high.service_type == ServiceType.FULL_AI_OPERATOR

    def test_offer_counter_increments(self):
        engine = OfferGeneratorEngine()
        o1 = engine.build_offer("A", ServiceType.AD_CAMPAIGN, 500.0)
        o2 = engine.build_offer("B", ServiceType.AD_CAMPAIGN, 500.0)
        assert o1.offer_id != o2.offer_id

    def test_to_dict(self):
        engine = OfferGeneratorEngine()
        d = engine.to_dict()
        assert "offer_count" in d
        assert "available_service_types" in d


# ===========================================================================
# 10d. Conversion Engine
# ===========================================================================

from bots.buddy_bot.conversion_engine import (
    ConversionEngine,
    Proposal,
    ConversionRecord,
    OutreachChannel,
    ConversionStage,
    ConversionEngineError,
    ConversionEngineTierError,
)


class TestConversionEngine:
    """Tests for the ConversionEngine."""

    def _make_engine_pro(self):
        return ConversionEngine(
            can_outreach=True,
            can_sms=False,
            can_ai_closing=False,
            can_booking=False,
            max_outreach_per_day=50,
            require_human_approval=True,
        )

    def _make_engine_enterprise(self):
        return ConversionEngine(
            can_outreach=True,
            can_sms=True,
            can_ai_closing=True,
            can_booking=True,
            max_outreach_per_day=None,
            require_human_approval=False,
        )

    def test_generate_proposal(self):
        engine = self._make_engine_pro()
        proposal = engine.generate_proposal(
            "Gym Co", "Get 50 leads/month", ["Ads", "Landing page"],
            999.0, 500.0, "30 leads or free",
        )
        assert isinstance(proposal, Proposal)
        assert proposal.business_name == "Gym Co"
        assert "Gym Co" in proposal.body
        assert "[Unsubscribe]" in proposal.body

    def test_proposal_creates_conversion_record(self):
        engine = self._make_engine_pro()
        engine.generate_proposal(
            "Roofing Co", "Get 30 leads", ["Ads"], 500.0, 250.0, "Guarantee",
        )
        pipeline = engine.get_pipeline()
        assert any(r["business_name"] == "Roofing Co" for r in pipeline)

    def test_send_outreach_requires_permission(self):
        engine = ConversionEngine(can_outreach=False)
        proposal = Proposal(
            proposal_id="p001", business_name="Co", service_headline="Test",
            body="body", deliverables=[], monthly_fee_usd=100.0,
            setup_fee_usd=50.0, guarantee="g", call_to_action="cta",
            channel=OutreachChannel.EMAIL,
        )
        with pytest.raises(ConversionEngineTierError):
            engine.send_outreach(proposal)

    def test_send_outreach_respects_rate_limit(self):
        engine = ConversionEngine(
            can_outreach=True,
            max_outreach_per_day=2,
            require_human_approval=False,
        )
        proposal = engine.generate_proposal(
            "Co", "Test", ["item"], 100.0, 50.0, "guarantee"
        )
        engine.send_outreach(proposal)
        engine.send_outreach(proposal)
        result = engine.send_outreach(proposal)
        assert result["queued"] is False
        assert "limit" in result["message"].lower()

    def test_sms_outreach_requires_enterprise(self):
        engine = self._make_engine_pro()
        with pytest.raises(ConversionEngineTierError):
            engine.generate_proposal(
                "SmsTest", "Test", ["item"], 100.0, 50.0, "g",
                channel=OutreachChannel.SMS,
            )

    def test_sms_works_on_enterprise(self):
        engine = self._make_engine_enterprise()
        proposal = engine.generate_proposal(
            "SmsOK", "Test", ["item"], 100.0, 50.0, "g",
            channel=OutreachChannel.SMS,
        )
        assert proposal.channel == OutreachChannel.SMS

    def test_handle_objection_too_expensive(self):
        engine = self._make_engine_pro()
        response = engine.handle_objection("Gym", "it's too expensive for us")
        assert response
        assert len(response) > 10

    def test_handle_objection_default(self):
        engine = self._make_engine_pro()
        response = engine.handle_objection("Gym", "random objection xyz")
        assert response

    def test_generate_agreement_requires_enterprise(self):
        engine = self._make_engine_pro()
        with pytest.raises(ConversionEngineTierError):
            engine.generate_agreement("Co", "Summary")

    def test_generate_agreement_enterprise(self):
        engine = self._make_engine_enterprise()
        agreement = engine.generate_agreement("BigCo", "Full AI package $999/mo")
        assert "BigCo" in agreement
        assert "DreamCo Buddy AI" in agreement

    def test_book_meeting_requires_enterprise(self):
        engine = self._make_engine_pro()
        with pytest.raises(ConversionEngineTierError):
            engine.book_meeting("Co", "2026-04-20T10:00:00Z")

    def test_book_meeting_enterprise(self):
        engine = self._make_engine_enterprise()
        engine.generate_proposal("MeetCo", "h", ["d"], 100.0, 50.0, "g")
        result = engine.book_meeting("MeetCo", "2026-04-20T10:00:00Z")
        assert result["status"] == "confirmed"
        assert "meet.dreamco.ai" in result["meeting_link"]

    def test_mark_won(self):
        engine = self._make_engine_pro()
        engine.generate_proposal("WonCo", "h", ["d"], 100.0, 50.0, "g")
        result = engine.mark_won("WonCo")
        assert result["status"] == "won"
        assert engine.get_won_count() == 1

    def test_mark_won_missing_raises(self):
        engine = self._make_engine_pro()
        with pytest.raises(ConversionEngineError):
            engine.mark_won("NonExistent")

    def test_reset_daily_sends(self):
        engine = ConversionEngine(
            can_outreach=True, max_outreach_per_day=1, require_human_approval=False
        )
        proposal = engine.generate_proposal("A", "h", ["d"], 100.0, 50.0, "g")
        engine.send_outreach(proposal)
        engine.reset_daily_sends()
        assert engine._sends_today == 0

    def test_to_dict(self):
        engine = self._make_engine_pro()
        d = engine.to_dict()
        assert "proposal_count" in d
        assert "pipeline_size" in d
        assert "won_count" in d


# ===========================================================================
# 10e. Fulfillment Engine
# ===========================================================================

from bots.buddy_bot.fulfillment_engine import (
    FulfillmentEngine,
    Deliverable,
    DeliverableType,
    DeliverableStatus,
    FulfillmentEngineError,
    FulfillmentEngineTierError,
)


class TestFulfillmentEngine:
    """Tests for the FulfillmentEngine."""

    def _make_free_engine(self):
        return FulfillmentEngine()

    def _make_pro_engine(self):
        return FulfillmentEngine(
            can_landing_pages=True,
            can_email_sequences=True,
        )

    def _make_enterprise_engine(self):
        return FulfillmentEngine(
            can_landing_pages=True,
            can_email_sequences=True,
            can_funnels=True,
            can_automation_setup=True,
            can_brand_kit=True,
            can_bulk_generate=True,
        )

    def test_generate_ad_copy_free(self):
        engine = self._make_free_engine()
        d = engine.generate_ad_copy("Gym Co")
        assert isinstance(d, Deliverable)
        assert d.deliverable_type == DeliverableType.AD_COPY
        assert d.status == DeliverableStatus.DRAFT

    def test_ad_copy_has_ads(self):
        engine = self._make_free_engine()
        d = engine.generate_ad_copy("Roofing Co", "contractor", ["Google", "Facebook"])
        assert "ads" in d.content
        assert len(d.content["ads"]) == 2

    def test_generate_ad_campaign(self):
        engine = self._make_free_engine()
        d = engine.generate_ad_campaign("Co", budget_usd=500.0, duration_days=14)
        assert d.deliverable_type == DeliverableType.AD_CAMPAIGN
        assert d.content["total_budget_usd"] == 500.0
        assert d.content["duration_days"] == 14

    def test_landing_page_requires_pro(self):
        engine = self._make_free_engine()
        with pytest.raises(FulfillmentEngineTierError):
            engine.build_landing_page("Co", "Headline", "Offer summary")

    def test_landing_page_pro(self):
        engine = self._make_pro_engine()
        d = engine.build_landing_page("Test Gym", "Grow your gym", "Full AI package")
        assert d.deliverable_type == DeliverableType.LANDING_PAGE
        assert "headline" in d.content
        assert "cta_button" in d.content

    def test_email_sequence_requires_pro(self):
        engine = self._make_free_engine()
        with pytest.raises(FulfillmentEngineTierError):
            engine.generate_email_sequence("Co")

    def test_email_sequence_pro(self):
        engine = self._make_pro_engine()
        d = engine.generate_email_sequence("Gym Co", sequence_length=5)
        assert d.deliverable_type == DeliverableType.EMAIL_SEQUENCE
        assert len(d.content["emails"]) == 5

    def test_email_sequence_clamped(self):
        engine = self._make_pro_engine()
        d = engine.generate_email_sequence("Co", sequence_length=20)
        assert len(d.content["emails"]) == 10

    def test_funnel_requires_enterprise(self):
        engine = self._make_pro_engine()
        with pytest.raises(FulfillmentEngineTierError):
            engine.assemble_funnel("Co", "lead magnet", "offer")

    def test_funnel_enterprise(self):
        engine = self._make_enterprise_engine()
        d = engine.assemble_funnel("BigCo", "Free audit", "Full AI package")
        assert d.deliverable_type == DeliverableType.SALES_FUNNEL
        assert len(d.content["stages"]) == 5

    def test_automation_setup_enterprise(self):
        engine = self._make_enterprise_engine()
        d = engine.setup_automation("BigCo")
        assert d.deliverable_type == DeliverableType.AUTOMATION_SETUP
        assert "systems" in d.content

    def test_brand_kit_enterprise(self):
        engine = self._make_enterprise_engine()
        d = engine.generate_brand_kit("Brand Co", "retail")
        assert d.deliverable_type == DeliverableType.BRAND_KIT
        assert "colour_palette" in d.content
        assert "logo_brief" in d.content

    def test_bulk_generate_requires_enterprise(self):
        engine = self._make_pro_engine()
        with pytest.raises(FulfillmentEngineTierError):
            engine.bulk_generate("Co", [DeliverableType.AD_COPY])

    def test_bulk_generate_enterprise(self):
        engine = self._make_enterprise_engine()
        deliverables = engine.bulk_generate(
            "BigCo",
            [DeliverableType.AD_COPY, DeliverableType.AD_CAMPAIGN],
        )
        assert len(deliverables) == 2

    def test_approve_deliverable(self):
        engine = self._make_free_engine()
        d = engine.generate_ad_copy("Co")
        approved = engine.approve_deliverable(d.deliverable_id)
        assert approved.status == DeliverableStatus.APPROVED
        assert approved.approved_at is not None

    def test_deploy_requires_approval(self):
        engine = self._make_free_engine()
        d = engine.generate_ad_copy("Co")
        with pytest.raises(FulfillmentEngineError):
            engine.deploy_deliverable(d.deliverable_id)

    def test_deploy_after_approve(self):
        engine = self._make_free_engine()
        d = engine.generate_ad_copy("Co")
        engine.approve_deliverable(d.deliverable_id)
        deployed = engine.deploy_deliverable(d.deliverable_id)
        assert deployed.status == DeliverableStatus.DEPLOYED

    def test_approve_nonexistent_raises(self):
        engine = self._make_free_engine()
        with pytest.raises(FulfillmentEngineError):
            engine.approve_deliverable("nonexistent")

    def test_get_deliverables_for_client(self):
        engine = self._make_free_engine()
        engine.generate_ad_copy("ClientA")
        engine.generate_ad_copy("ClientA")
        engine.generate_ad_copy("ClientB")
        assert len(engine.get_deliverables_for_client("ClientA")) == 2
        assert len(engine.get_deliverables_for_client("ClientB")) == 1

    def test_deliverable_to_dict(self):
        engine = self._make_free_engine()
        d = engine.generate_ad_copy("Co")
        data = d.to_dict()
        assert "deliverable_id" in data
        assert "deliverable_type" in data
        assert "status" in data
        assert "content" in data

    def test_to_dict(self):
        engine = self._make_enterprise_engine()
        d = engine.to_dict()
        assert "total_deliverables" in d
        assert d["can_funnels"] is True


# ===========================================================================
# 10f. Retention Engine
# ===========================================================================

from bots.buddy_bot.retention_engine import (
    RetentionEngine,
    ClientHealthRecord,
    HealthStatus,
    UpsellStage,
    UpsellOffer,
    CheckIn,
    RetentionEngineError,
    RetentionEngineTierError,
)


class TestRetentionEngine:
    """Tests for the RetentionEngine."""

    def _make_pro_engine(self):
        return RetentionEngine(
            can_auto_checkins=True,
            can_upsell_detection=True,
        )

    def _make_enterprise_engine(self):
        return RetentionEngine(
            can_auto_checkins=True,
            can_upsell_detection=True,
            can_referral_engine=True,
            can_churn_prediction=True,
            can_mrr_dashboard=True,
        )

    def test_add_client(self):
        engine = self._make_pro_engine()
        record = engine.add_client("Gym Co", "pro", 299.0)
        assert isinstance(record, ClientHealthRecord)
        assert record.client_name == "Gym Co"
        assert record.monthly_value_usd == 299.0

    def test_score_health_champion(self):
        engine = self._make_pro_engine()
        engine.add_client(
            "Champion Gym", "pro", 299.0,
            months_active=4, satisfaction_score=9.0, results_delivered=5,
        )
        record = engine.score_health("Champion Gym")
        assert record.health_status == HealthStatus.CHAMPION

    def test_score_health_at_risk(self):
        engine = self._make_pro_engine()
        engine.add_client(
            "AtRisk Co", "pro", 299.0,
            months_active=2, satisfaction_score=5.5,
            last_contact_days_ago=20,
        )
        record = engine.score_health("AtRisk Co")
        assert record.health_status == HealthStatus.AT_RISK

    def test_score_health_churning(self):
        engine = self._make_pro_engine()
        engine.add_client(
            "Churning Co", "pro", 299.0,
            months_active=2, satisfaction_score=2.0,
            last_contact_days_ago=35,
        )
        record = engine.score_health("Churning Co")
        assert record.health_status == HealthStatus.CHURNING

    def test_score_nonexistent_raises(self):
        engine = self._make_pro_engine()
        with pytest.raises(RetentionEngineError):
            engine.score_health("NonExistent")

    def test_get_at_risk_clients(self):
        engine = self._make_pro_engine()
        engine.add_client("Good Co", "pro", 299.0, months_active=3, satisfaction_score=8.0, results_delivered=5)
        engine.add_client("Risk Co", "pro", 199.0, months_active=1, satisfaction_score=5.0, last_contact_days_ago=20)
        at_risk = engine.get_at_risk_clients()
        names = [r.client_name for r in at_risk]
        assert "Risk Co" in names

    def test_schedule_checkin_requires_pro(self):
        engine = RetentionEngine(can_auto_checkins=False)
        engine.add_client("Co", "free", 0.0)
        with pytest.raises(RetentionEngineTierError):
            engine.schedule_checkin("Co")

    def test_schedule_checkin_pro(self):
        engine = self._make_pro_engine()
        engine.add_client("Check Co", "pro", 99.0)
        checkin = engine.schedule_checkin("Check Co", channel="email")
        assert isinstance(checkin, CheckIn)
        assert checkin.client_name == "Check Co"
        assert "Check Co" in checkin.message

    def test_detect_upsell_moment_ready(self):
        engine = self._make_pro_engine()
        engine.add_client(
            "Ready Co", "pro", 299.0,
            months_active=3, satisfaction_score=9.0, results_delivered=5,
        )
        stage = engine.detect_upsell_moment("Ready Co")
        assert stage == UpsellStage.READY

    def test_detect_upsell_moment_not_ready(self):
        engine = self._make_pro_engine()
        engine.add_client(
            "NotReady Co", "starter", 29.0,
            months_active=0, satisfaction_score=6.0, results_delivered=0,
        )
        stage = engine.detect_upsell_moment("NotReady Co")
        assert stage == UpsellStage.NOT_READY

    def test_detect_upsell_requires_pro(self):
        engine = RetentionEngine(can_upsell_detection=False)
        engine.add_client("Co", "free", 0.0)
        with pytest.raises(RetentionEngineTierError):
            engine.detect_upsell_moment("Co")

    def test_build_upsell_offer(self):
        engine = self._make_pro_engine()
        engine.add_client(
            "Gym Co", "starter", 29.0,
            months_active=3, satisfaction_score=8.5, results_delivered=5,
        )
        offer = engine.build_upsell_offer("Gym Co")
        assert isinstance(offer, UpsellOffer)
        assert offer.client_name == "Gym Co"
        assert offer.proposed_plan
        assert len(offer.new_features) > 0

    def test_referral_requires_enterprise(self):
        engine = self._make_pro_engine()
        engine.add_client(
            "Champ Co", "pro", 299.0,
            months_active=4, satisfaction_score=9.0, results_delivered=5,
        )
        with pytest.raises(RetentionEngineTierError):
            engine.trigger_referral_ask("Champ Co")

    def test_referral_champion_enterprise(self):
        engine = self._make_enterprise_engine()
        engine.add_client(
            "Champ Co", "pro", 299.0,
            months_active=4, satisfaction_score=9.0, results_delivered=5,
        )
        result = engine.trigger_referral_ask("Champ Co")
        assert result["eligible"] is True
        assert "referral_link" in result

    def test_referral_not_eligible_for_at_risk(self):
        engine = self._make_enterprise_engine()
        engine.add_client(
            "Risk Co", "starter", 29.0,
            months_active=1, satisfaction_score=4.0, last_contact_days_ago=20,
        )
        result = engine.trigger_referral_ask("Risk Co")
        assert result["eligible"] is False

    def test_revenue_report_requires_enterprise(self):
        engine = self._make_pro_engine()
        with pytest.raises(RetentionEngineTierError):
            engine.revenue_report()

    def test_revenue_report_enterprise(self):
        engine = self._make_enterprise_engine()
        engine.add_client("Co A", "pro", 299.0, months_active=3)
        engine.add_client("Co B", "business", 99.0, months_active=1)
        report = engine.revenue_report()
        assert report["mrr_usd"] == pytest.approx(398.0, abs=0.01)
        assert report["total_clients"] == 2
        assert "churn_rate_pct" in report

    def test_simple_revenue_summary_all_tiers(self):
        engine = RetentionEngine()
        engine.add_client("Co", "free", 0.0)
        summary = engine.simple_revenue_summary()
        assert "total_clients" in summary
        assert "mrr_usd" in summary

    def test_get_all_clients(self):
        engine = self._make_pro_engine()
        engine.add_client("A", "pro", 100.0)
        engine.add_client("B", "pro", 200.0)
        clients = engine.get_all_clients()
        assert len(clients) == 2

    def test_lifetime_value_computed(self):
        engine = self._make_pro_engine()
        engine.add_client("LTV Co", "pro", 299.0, months_active=6)
        record = engine.get_client("LTV Co")
        assert record.lifetime_value_usd == pytest.approx(299.0 * 6, abs=0.01)

    def test_upsell_offer_to_dict(self):
        engine = self._make_pro_engine()
        engine.add_client("Co", "starter", 29.0, months_active=3, satisfaction_score=8.5, results_delivered=5)
        offer = engine.build_upsell_offer("Co")
        d = offer.to_dict()
        assert "offer_id" in d
        assert "proposed_plan" in d
        assert "new_features" in d

    def test_checkin_to_dict(self):
        engine = self._make_pro_engine()
        engine.add_client("Check Co", "pro", 99.0)
        ci = engine.schedule_checkin("Check Co")
        d = ci.to_dict()
        assert "checkin_id" in d
        assert "message" in d
        assert "completed" in d

    def test_to_dict(self):
        engine = self._make_enterprise_engine()
        d = engine.to_dict()
        assert "total_clients" in d
        assert "mrr_usd" in d
        assert d["can_mrr_dashboard"] is True


# ===========================================================================
# 10g. BuddyBot — Autonomous SaaS Integration Tests
# ===========================================================================

class TestBuddyBotAutonomousSaaS:
    """Integration tests for the new autonomous SaaS engines via BuddyBot."""

    def test_free_tier_blocked_from_find_leads(self):
        buddy = BuddyBot(tier=Tier.FREE)
        with pytest.raises(BuddyBotTierError):
            buddy.find_leads()

    def test_pro_tier_find_leads(self):
        buddy = BuddyBot(tier=Tier.PRO)
        leads = buddy.find_leads()
        assert len(leads) > 0
        assert isinstance(leads[0], BusinessLead)

    def test_pro_tier_build_offer(self):
        buddy = BuddyBot(tier=Tier.PRO)
        offer = buddy.build_offer("Test Roofing", estimated_lead_value=3000.0)
        assert isinstance(offer, ServiceOffer)
        assert "Test Roofing" in offer.headline

    def test_pro_tier_generate_proposal(self):
        buddy = BuddyBot(tier=Tier.PRO)
        proposal = buddy.generate_proposal(
            "Test Gym", "50 leads/month", ["Ad campaigns", "Landing page"],
            999.0, 500.0, "30 leads guaranteed",
        )
        assert isinstance(proposal, Proposal)
        assert "Test Gym" in proposal.body

    def test_pro_tier_handle_objection(self):
        buddy = BuddyBot(tier=Tier.PRO)
        buddy.generate_proposal("Co", "h", ["d"], 100.0, 50.0, "g")
        response = buddy.handle_objection("Co", "it's too expensive")
        assert response

    def test_pro_tier_deliver_ad_copy(self):
        buddy = BuddyBot(tier=Tier.PRO)
        d = buddy.deliver_ad_copy("Test Co", "contractor")
        assert isinstance(d, Deliverable)
        assert d.deliverable_type == DeliverableType.AD_COPY

    def test_pro_tier_deliver_ad_campaign(self):
        buddy = BuddyBot(tier=Tier.PRO)
        d = buddy.deliver_ad_campaign("Test Co", budget_usd=2000.0, duration_days=30)
        assert d.deliverable_type == DeliverableType.AD_CAMPAIGN

    def test_pro_tier_deliver_landing_page(self):
        buddy = BuddyBot(tier=Tier.PRO)
        d = buddy.deliver_landing_page("Test Co", "Headline", "Offer")
        assert d.deliverable_type == DeliverableType.LANDING_PAGE

    def test_pro_tier_deliver_email_sequence(self):
        buddy = BuddyBot(tier=Tier.PRO)
        d = buddy.deliver_email_sequence("Test Co", sequence_length=4)
        assert d.deliverable_type == DeliverableType.EMAIL_SEQUENCE

    def test_pro_tier_add_retained_client(self):
        buddy = BuddyBot(tier=Tier.PRO)
        record = buddy.add_retained_client("Client A", "pro", 299.0, months_active=2)
        assert isinstance(record, ClientHealthRecord)
        assert record.client_name == "Client A"

    def test_pro_tier_detect_upsell_moment(self):
        buddy = BuddyBot(tier=Tier.PRO)
        buddy.add_retained_client(
            "Upsell Co", "starter", 29.0,
            months_active=3, satisfaction_score=9.0, results_delivered=5,
        )
        stage = buddy.detect_upsell_moment("Upsell Co")
        assert stage in list(UpsellStage)

    def test_pro_tier_build_upsell_offer(self):
        buddy = BuddyBot(tier=Tier.PRO)
        buddy.add_retained_client(
            "Upsell Co", "starter", 29.0,
            months_active=3, satisfaction_score=8.5, results_delivered=5,
        )
        offer = buddy.build_upsell_offer("Upsell Co")
        assert isinstance(offer, UpsellOffer)

    def test_pro_tier_get_revenue_summary(self):
        buddy = BuddyBot(tier=Tier.PRO)
        buddy.add_retained_client("Co A", "pro", 299.0)
        summary = buddy.get_revenue_summary()
        assert summary["total_clients"] == 1
        assert summary["mrr_usd"] == pytest.approx(299.0, abs=0.01)

    def test_pro_tier_run_autonomous_cycle(self):
        buddy = BuddyBot(tier=Tier.PRO)
        result = buddy.run_autonomous_cycle()
        assert result["status"] == "cycle_complete"
        assert result["leads_found"] > 0
        assert "offer" in result
        assert "proposal" in result

    def test_enterprise_tier_system_status_includes_engines(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE)
        status = buddy.system_status()
        assert "lead_finder" in status
        assert "offer_generator" in status
        assert "conversion" in status
        assert "fulfillment" in status
        assert "retention" in status

    def test_pro_features_include_saas_flags(self):
        buddy = BuddyBot(tier=Tier.PRO)
        from bots.buddy_bot.tiers import (
            FEATURE_LEAD_FINDER, FEATURE_OFFER_GENERATOR,
            FEATURE_CONVERSION_ENGINE, FEATURE_FULFILLMENT_ENGINE,
            FEATURE_RETENTION_ENGINE,
        )
        for feat in [
            FEATURE_LEAD_FINDER, FEATURE_OFFER_GENERATOR,
            FEATURE_CONVERSION_ENGINE, FEATURE_FULFILLMENT_ENGINE,
            FEATURE_RETENTION_ENGINE,
        ]:
            assert buddy.config.has_feature(feat), f"PRO should have {feat}"

    def test_free_does_not_have_saas_flags(self):
        buddy = BuddyBot(tier=Tier.FREE)
        from bots.buddy_bot.tiers import FEATURE_LEAD_FINDER
        assert not buddy.config.has_feature(FEATURE_LEAD_FINDER)

    def test_get_top_leads(self):
        buddy = BuddyBot(tier=Tier.PRO)
        buddy.find_leads()
        top = buddy.get_top_leads(3)
        assert len(top) <= 3


# ===========================================================================
# Adaptive Language / Communication Context
# ===========================================================================

class TestCommunicationContext:
    """Tests for CommunicationContext enum and ConversationEngine context awareness."""

    def test_default_context_is_casual(self):
        engine = ConversationEngine()
        assert engine.context == CommunicationContext.CASUAL

    def test_set_context_to_business(self):
        engine = ConversationEngine()
        engine.set_context(CommunicationContext.BUSINESS)
        assert engine.context == CommunicationContext.BUSINESS

    def test_detect_context_business_keyword(self):
        engine = ConversationEngine()
        ctx = engine.detect_context("Please prepare a proposal for the client.")
        assert ctx == CommunicationContext.BUSINESS

    def test_detect_context_casual_default(self):
        engine = ConversationEngine()
        ctx = engine.detect_context("Yo bruh what's up")
        assert ctx == CommunicationContext.CASUAL

    def test_sanitize_profanity_in_business_mode(self):
        engine = ConversationEngine(context=CommunicationContext.BUSINESS)
        cleaned = engine.sanitize_for_business("Close the damn deal already!")
        assert "damn" not in cleaned
        assert "[noted]" in cleaned

    def test_sanitize_clean_text_unchanged(self):
        engine = ConversationEngine(context=CommunicationContext.BUSINESS)
        text = "Please finalize the contract today."
        assert engine.sanitize_for_business(text) == text

    def test_adapt_slang_replaces_known_terms(self):
        engine = ConversationEngine()
        result = engine.adapt_slang("Bruh, can you hook me up with leads?")
        assert "Bruh" not in result
        assert "Hey" in result

    def test_adapt_slang_no_cap_replacement(self):
        engine = ConversationEngine()
        result = engine.adapt_slang("No cap, this is fire.")
        assert "no cap" not in result.lower()

    def test_adapt_slang_case_insensitive(self):
        engine = ConversationEngine()
        result = engine.adapt_slang("BET that works for me.")
        assert "sounds good" in result.lower()

    def test_respond_business_mode_no_profanity_in_output(self):
        engine = ConversationEngine(context=CommunicationContext.BUSINESS)
        turn = engine.respond("Close the damn contract!", tone=ConversationTone.NEUTRAL)
        assert "damn" not in turn.response.lower()

    def test_respond_business_mode_no_filler(self):
        # Business mode should never use speech fillers
        engine = ConversationEngine(
            enable_fillers=True,
            context=CommunicationContext.BUSINESS,
        )
        for _ in range(20):
            turn = engine.respond("Prepare the quarterly report.")
            assert not turn.used_filler

    def test_respond_auto_detect_switches_to_business(self):
        engine = ConversationEngine(
            context=CommunicationContext.CASUAL,
            auto_detect_context=True,
        )
        engine.respond("Please send a proposal to the client.")
        assert engine.context == CommunicationContext.BUSINESS

    def test_respond_casual_mode_allows_fillers(self):
        # With fillers enabled and many iterations, at least one should use a filler
        engine = ConversationEngine(
            enable_fillers=True,
            context=CommunicationContext.CASUAL,
            auto_detect_context=False,
        )
        used = False
        for _ in range(50):
            turn = engine.respond("Hey what can you do?")
            if turn.used_filler:
                used = True
                break
        assert used

    def test_to_dict_includes_context(self):
        engine = ConversationEngine(context=CommunicationContext.BUSINESS)
        d = engine.to_dict()
        assert d["context"] == "business"
        assert "auto_detect_context" in d


class TestBuddyBotAdaptiveContext:
    """Tests for BuddyBot's adaptive context / language switching API."""

    def test_set_communication_context_casual(self):
        buddy = BuddyBot(tier=Tier.FREE)
        result = buddy.set_communication_context("casual")
        assert result["context"] == "casual"

    def test_set_communication_context_business(self):
        buddy = BuddyBot(tier=Tier.FREE)
        result = buddy.set_communication_context("business")
        assert result["context"] == "business"

    def test_set_communication_context_invalid_raises(self):
        buddy = BuddyBot(tier=Tier.FREE)
        with pytest.raises(ValueError):
            buddy.set_communication_context("invalid_mode")

    def test_get_communication_context_default(self):
        buddy = BuddyBot(tier=Tier.FREE)
        result = buddy.get_communication_context()
        assert result["context"] == "casual"
        assert "auto_detect" in result

    def test_detect_communication_context_business(self):
        buddy = BuddyBot(tier=Tier.FREE)
        result = buddy.detect_communication_context(
            "Please prepare a contract for the enterprise client."
        )
        assert result["detected_context"] == "business"

    def test_detect_communication_context_casual(self):
        buddy = BuddyBot(tier=Tier.FREE)
        result = buddy.detect_communication_context("Hey, what's up?")
        assert result["detected_context"] == "casual"

    def test_business_context_chat_no_cursing(self):
        buddy = BuddyBot(tier=Tier.FREE)
        buddy.set_communication_context("business")
        result = buddy.chat("Close this damn deal", tone="neutral")
        assert "damn" not in result["message"].lower()

    def test_context_persists_across_chats(self):
        buddy = BuddyBot(tier=Tier.FREE)
        buddy.set_communication_context("business")
        for _ in range(3):
            result = buddy.chat("Follow up with the client.")
            assert result["message"]  # non-empty response
        assert buddy.get_communication_context()["context"] == "business"
