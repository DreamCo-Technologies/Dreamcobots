"""
Tests for bots/buddy_teach_bot/

Covers:
  1. Tiers (FREE, PRO, ENTERPRISE) — config, features, upgrade path
  2. BroadcastEngine — target registration, session management, multi-broadcast
  3. SkillTrainer — lesson library, progress tracking, certificates
  4. ItemDetector — detection, valuation, AI training pipeline
  5. PersonalityEngine — trait scoring, tone selection, milestones
  6. BuddyTeachBot (integration) — tier gating, full workflow, status/upgrade
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Tier imports
# ---------------------------------------------------------------------------
from bots.buddy_teach_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_SKILL_TRAINING,
    FEATURE_ITEM_DETECTION,
    FEATURE_BROADCAST,
    FEATURE_MULTI_BROADCAST,
    FEATURE_PERSONALITY,
    FEATURE_AI_TRAINING,
    FEATURE_CURRICULUM_BUILDER,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FREE_FEATURES,
    PRO_FEATURES,
    ENTERPRISE_FEATURES,
)

# ---------------------------------------------------------------------------
# BroadcastEngine imports
# ---------------------------------------------------------------------------
from bots.buddy_teach_bot.broadcast_engine import (
    BroadcastEngine,
    BroadcastTarget,
    BroadcastSession,
    BroadcastState,
    DeviceCategory,
    ContentFormat,
    BroadcastEngineError,
)

# ---------------------------------------------------------------------------
# SkillTrainer imports
# ---------------------------------------------------------------------------
from bots.buddy_teach_bot.skill_trainer import (
    SkillTrainer,
    Lesson,
    LessonStep,
    LessonProgress,
    LessonStatus,
    SkillDomain,
    DifficultyLevel,
    SkillTrainerError,
    LESSON_LIBRARY,
)

# ---------------------------------------------------------------------------
# ItemDetector imports
# ---------------------------------------------------------------------------
from bots.buddy_teach_bot.item_detector import (
    ItemDetector,
    DetectionResult,
    ItemCategory,
    ConditionGrade,
    TrainingExample,
    ItemDetectorError,
    _CONDITION_MULTIPLIERS,
)

# ---------------------------------------------------------------------------
# PersonalityEngine imports
# ---------------------------------------------------------------------------
from bots.buddy_teach_bot.personality_engine import (
    PersonalityEngine,
    ToneStyle,
    PersonalityTrait,
    Milestone,
    UserInteraction,
    PersonalityEngineError,
)

# ---------------------------------------------------------------------------
# Main bot imports
# ---------------------------------------------------------------------------
from bots.buddy_teach_bot.buddy_teach_bot import (
    BuddyTeachBot,
    BuddyTeachBotError,
    BuddyTeachBotTierError,
)


# ===========================================================================
# 1. TIERS
# ===========================================================================

class TestTiers:
    def test_all_tiers_exist(self):
        tiers = list_tiers()
        names = {t.name for t in tiers}
        assert "Free" in names
        assert "Pro" in names
        assert "Enterprise" in names

    def test_tier_prices(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_features(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_SKILL_TRAINING)
        assert cfg.has_feature(FEATURE_ITEM_DETECTION)
        assert cfg.has_feature(FEATURE_BROADCAST)
        assert cfg.has_feature(FEATURE_PERSONALITY)
        assert not cfg.has_feature(FEATURE_MULTI_BROADCAST)
        assert not cfg.has_feature(FEATURE_AI_TRAINING)
        assert not cfg.has_feature(FEATURE_WHITE_LABEL)

    def test_pro_features(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_MULTI_BROADCAST)
        assert cfg.has_feature(FEATURE_AI_TRAINING)
        assert not cfg.has_feature(FEATURE_WHITE_LABEL)
        assert not cfg.has_feature(FEATURE_CURRICULUM_BUILDER)

    def test_enterprise_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_CURRICULUM_BUILDER)
        assert cfg.has_feature(FEATURE_WHITE_LABEL)
        assert cfg.has_feature(FEATURE_API_ACCESS)

    def test_free_broadcast_limit(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_broadcast_targets == 1

    def test_pro_broadcast_limit(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_broadcast_targets == 10

    def test_enterprise_unlimited_broadcast(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_broadcast_targets is None
        assert cfg.is_unlimited_broadcast()

    def test_upgrade_path_free_to_pro(self):
        next_tier = get_upgrade_path(Tier.FREE)
        assert next_tier is not None
        assert next_tier.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        next_tier = get_upgrade_path(Tier.PRO)
        assert next_tier is not None
        assert next_tier.tier == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_tier_config_dataclass(self):
        cfg = get_tier_config(Tier.PRO)
        assert isinstance(cfg, TierConfig)
        assert cfg.tier == Tier.PRO

    def test_pro_features_superset_of_free(self):
        for f in FREE_FEATURES:
            assert f in PRO_FEATURES

    def test_enterprise_features_superset_of_pro(self):
        for f in PRO_FEATURES:
            assert f in ENTERPRISE_FEATURES

    def test_free_skill_tracks(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_skill_tracks == 3

    def test_enterprise_skill_tracks_unlimited(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_skill_tracks is None

    def test_list_tiers_returns_three(self):
        assert len(list_tiers()) == 3


# ===========================================================================
# 2. BROADCAST ENGINE
# ===========================================================================

class TestBroadcastEngine:
    def test_register_target(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("Living Room TV", DeviceCategory.SMART_TV)
        assert target.name == "Living Room TV"
        assert target.category == DeviceCategory.SMART_TV

    def test_register_multiple_targets(self):
        engine = BroadcastEngine(max_targets=5)
        for i in range(3):
            engine.register_target(f"Device {i}", DeviceCategory.PHONE)
        assert len(engine.list_targets()) == 3

    def test_max_targets_enforced(self):
        engine = BroadcastEngine(max_targets=2)
        engine.register_target("TV", DeviceCategory.SMART_TV)
        engine.register_target("Phone", DeviceCategory.PHONE)
        with pytest.raises(BroadcastEngineError, match="Maximum broadcast targets"):
            engine.register_target("Tablet", DeviceCategory.TABLET)

    def test_remove_target(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("Console", DeviceCategory.GAME_CONSOLE)
        engine.remove_target(target.target_id)
        assert len(engine.list_targets()) == 0

    def test_remove_nonexistent_target_raises(self):
        engine = BroadcastEngine()
        with pytest.raises(BroadcastEngineError):
            engine.remove_target("nonexistent")

    def test_start_broadcast(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("TV", DeviceCategory.SMART_TV)
        session = engine.start_broadcast(
            "Car Repair 101",
            ContentFormat.STEP_BY_STEP,
            [target.target_id],
        )
        assert session.lesson_title == "Car Repair 101"
        assert session.state == BroadcastState.LIVE
        assert target.target_id in session.target_ids

    def test_broadcast_updates_device_state(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("TV", DeviceCategory.SMART_TV)
        engine.start_broadcast("Lesson", ContentFormat.VIDEO_TUTORIAL, [target.target_id])
        assert engine.get_target(target.target_id).state == BroadcastState.LIVE

    def test_pause_broadcast(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("TV", DeviceCategory.SMART_TV)
        session = engine.start_broadcast("Lesson", ContentFormat.QUIZ, [target.target_id])
        paused = engine.pause_broadcast(session.session_id)
        assert paused.state == BroadcastState.PAUSED

    def test_resume_broadcast(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("TV", DeviceCategory.SMART_TV)
        session = engine.start_broadcast("Lesson", ContentFormat.LIVE_DEMO, [target.target_id])
        engine.pause_broadcast(session.session_id)
        resumed = engine.resume_broadcast(session.session_id)
        assert resumed.state == BroadcastState.LIVE

    def test_end_broadcast(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("TV", DeviceCategory.SMART_TV)
        session = engine.start_broadcast("Lesson", ContentFormat.STEP_BY_STEP, [target.target_id])
        ended = engine.end_broadcast(session.session_id)
        assert ended.state == BroadcastState.ENDED
        assert ended.ended_at is not None
        assert len(engine.active_sessions()) == 0
        assert len(engine.session_history()) == 1

    def test_end_broadcast_resets_device_state(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("TV", DeviceCategory.SMART_TV)
        session = engine.start_broadcast("Lesson", ContentFormat.STEP_BY_STEP, [target.target_id])
        engine.end_broadcast(session.session_id)
        assert engine.get_target(target.target_id).state == BroadcastState.IDLE

    def test_pause_non_live_session_raises(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("TV", DeviceCategory.SMART_TV)
        session = engine.start_broadcast("L", ContentFormat.STEP_BY_STEP, [target.target_id])
        engine.pause_broadcast(session.session_id)
        with pytest.raises(BroadcastEngineError):
            engine.pause_broadcast(session.session_id)

    def test_resume_non_paused_session_raises(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("TV", DeviceCategory.SMART_TV)
        session = engine.start_broadcast("L", ContentFormat.STEP_BY_STEP, [target.target_id])
        with pytest.raises(BroadcastEngineError):
            engine.resume_broadcast(session.session_id)

    def test_broadcast_to_all(self):
        engine = BroadcastEngine(max_targets=None)
        tv = engine.register_target("TV", DeviceCategory.SMART_TV)
        phone = engine.register_target("Phone", DeviceCategory.PHONE)
        tablet = engine.register_target("Tablet", DeviceCategory.TABLET)
        session = engine.broadcast_to_all("Lesson", ContentFormat.INTERACTIVE_LESSON)
        assert len(session.target_ids) == 3

    def test_broadcast_to_all_no_targets_raises(self):
        engine = BroadcastEngine(max_targets=None)
        with pytest.raises(BroadcastEngineError, match="No broadcast targets"):
            engine.broadcast_to_all("Lesson", ContentFormat.STEP_BY_STEP)

    def test_update_engagement(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("TV", DeviceCategory.SMART_TV)
        session = engine.start_broadcast("L", ContentFormat.QUIZ, [target.target_id])
        engine.update_engagement(session.session_id, 0.95)
        assert engine._sessions[session.session_id].engagement_score == 0.95

    def test_update_engagement_clamped(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("TV", DeviceCategory.SMART_TV)
        session = engine.start_broadcast("L", ContentFormat.QUIZ, [target.target_id])
        engine.update_engagement(session.session_id, 1.5)
        assert engine._sessions[session.session_id].engagement_score == 1.0

    def test_device_summary(self):
        engine = BroadcastEngine(max_targets=None)
        engine.register_target("TV1", DeviceCategory.SMART_TV)
        engine.register_target("TV2", DeviceCategory.SMART_TV)
        engine.register_target("Phone", DeviceCategory.PHONE)
        summary = engine.get_device_summary()
        assert summary[DeviceCategory.SMART_TV.value] == 2
        assert summary[DeviceCategory.PHONE.value] == 1

    def test_target_to_dict(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("AR Headset", DeviceCategory.AR_VR_HEADSET, ar_capable=True)
        d = target.to_dict()
        assert d["category"] == DeviceCategory.AR_VR_HEADSET.value
        assert d["ar_capable"] is True

    def test_session_to_dict(self):
        engine = BroadcastEngine(max_targets=5)
        target = engine.register_target("TV", DeviceCategory.SMART_TV)
        session = engine.start_broadcast("L", ContentFormat.AR_OVERLAY, [target.target_id])
        d = session.to_dict()
        assert d["lesson_title"] == "L"
        assert d["content_format"] == ContentFormat.AR_OVERLAY.value

    def test_unlimited_targets(self):
        engine = BroadcastEngine(max_targets=None)
        for i in range(50):
            engine.register_target(f"Device {i}", DeviceCategory.COMPUTER)
        assert len(engine.list_targets()) == 50

    def test_device_categories_all_registerable(self):
        engine = BroadcastEngine(max_targets=None)
        for cat in DeviceCategory:
            engine.register_target(f"Test {cat.value}", cat)
        assert len(engine.list_targets()) == len(list(DeviceCategory))


# ===========================================================================
# 3. SKILL TRAINER
# ===========================================================================

class TestSkillTrainer:
    def test_default_lessons_loaded(self):
        trainer = SkillTrainer()
        lessons = trainer.list_lessons()
        assert len(lessons) >= 4

    def test_car_repair_lesson_exists(self):
        trainer = SkillTrainer()
        lessons = trainer.list_lessons(domain=SkillDomain.AUTOMOTIVE)
        assert any("Oil Change" in l.title for l in lessons)

    def test_list_lessons_by_domain(self):
        trainer = SkillTrainer()
        automotive = trainer.list_lessons(domain=SkillDomain.AUTOMOTIVE)
        for l in automotive:
            assert l.domain == SkillDomain.AUTOMOTIVE

    def test_list_lessons_by_difficulty(self):
        trainer = SkillTrainer()
        beginner = trainer.list_lessons(difficulty=DifficultyLevel.BEGINNER)
        for l in beginner:
            assert l.difficulty == DifficultyLevel.BEGINNER

    def test_get_lesson_by_id(self):
        trainer = SkillTrainer()
        lesson = trainer.get_lesson("auto-001")
        assert lesson.lesson_id == "auto-001"

    def test_get_nonexistent_lesson_raises(self):
        trainer = SkillTrainer()
        with pytest.raises(SkillTrainerError):
            trainer.get_lesson("nonexistent-999")

    def test_start_lesson(self):
        trainer = SkillTrainer()
        progress = trainer.start_lesson("learner-1", "auto-001")
        assert progress.learner_id == "learner-1"
        assert progress.lesson_id == "auto-001"
        assert progress.status == LessonStatus.IN_PROGRESS
        assert progress.current_step == 1

    def test_advance_step(self):
        trainer = SkillTrainer()
        progress = trainer.start_lesson("learner-1", "auto-001")
        advanced = trainer.advance_step(progress.progress_id)
        assert advanced.current_step == 2

    def test_advance_step_does_not_exceed_total(self):
        trainer = SkillTrainer()
        lesson = trainer.get_lesson("auto-001")
        progress = trainer.start_lesson("learner-1", "auto-001")
        for _ in range(len(lesson.steps) + 5):
            trainer.advance_step(progress.progress_id)
        assert progress.current_step == len(lesson.steps)

    def test_complete_lesson_pass(self):
        trainer = SkillTrainer()
        progress = trainer.start_lesson("learner-1", "auto-001")
        completed = trainer.complete_lesson(progress.progress_id, 0.85)
        assert completed.status == LessonStatus.COMPLETED
        assert completed.score == 0.85
        assert completed.completed_at is not None

    def test_complete_lesson_fail(self):
        trainer = SkillTrainer()
        progress = trainer.start_lesson("learner-1", "auto-001")
        failed = trainer.complete_lesson(progress.progress_id, 0.50)
        assert failed.status == LessonStatus.FAILED

    def test_certificate_issued_on_pass(self):
        trainer = SkillTrainer()
        progress = trainer.start_lesson("learner-1", "auto-001")
        trainer.complete_lesson(progress.progress_id, 0.80)
        certs = trainer.learner_certificates("learner-1")
        assert len(certs) == 1
        assert certs[0]["lesson_id"] == "auto-001"

    def test_no_certificate_on_fail(self):
        trainer = SkillTrainer()
        progress = trainer.start_lesson("learner-1", "auto-001")
        trainer.complete_lesson(progress.progress_id, 0.30)
        assert len(trainer.learner_certificates("learner-1")) == 0

    def test_feedback_message_on_pass(self):
        trainer = SkillTrainer()
        progress = trainer.start_lesson("learner-1", "auto-001")
        completed = trainer.complete_lesson(progress.progress_id, 1.0)
        assert any("Congratulations" in f for f in completed.feedback)

    def test_feedback_message_on_fail(self):
        trainer = SkillTrainer()
        progress = trainer.start_lesson("learner-1", "auto-001")
        failed = trainer.complete_lesson(progress.progress_id, 0.1)
        assert any("scored" in f.lower() for f in failed.feedback)

    def test_list_learner_progress(self):
        trainer = SkillTrainer()
        p1 = trainer.start_lesson("learner-1", "auto-001")
        p2 = trainer.start_lesson("learner-1", "health-001")
        records = trainer.list_learner_progress("learner-1")
        assert len(records) == 2

    def test_add_custom_lesson(self):
        trainer = SkillTrainer(max_skill_tracks=None)
        custom = Lesson(
            lesson_id="custom-001",
            title="Custom Welding",
            domain=SkillDomain.HOME_IMPROVEMENT,
            difficulty=DifficultyLevel.ADVANCED,
            description="Intro to MIG welding.",
            steps=[LessonStep(1, "Safety", "Wear PPE.", safety_notes=["Arc flash danger."])],
        )
        trainer.add_lesson(custom)
        assert trainer.get_lesson("custom-001").title == "Custom Welding"

    def test_max_skill_tracks_enforced(self):
        trainer = SkillTrainer(max_skill_tracks=1)
        # Auto domain already exists — adding another domain should fail
        new_lesson = Lesson(
            lesson_id="tech-001",
            title="Python Basics",
            domain=SkillDomain.TECHNOLOGY,
            difficulty=DifficultyLevel.BEGINNER,
            description="Learn Python.",
            steps=[LessonStep(1, "Hello World", "Print hello world.")],
        )
        with pytest.raises(SkillTrainerError, match="Max skill tracks"):
            trainer.add_lesson(new_lesson)

    def test_lesson_step_to_dict(self):
        step = LessonStep(1, "Test Step", "Do this.", safety_notes=["Be careful."])
        d = step.to_dict()
        assert d["step_number"] == 1
        assert "Be careful." in d["safety_notes"]

    def test_lesson_to_dict(self):
        trainer = SkillTrainer()
        lesson = trainer.get_lesson("auto-001")
        d = lesson.to_dict()
        assert d["lesson_id"] == "auto-001"
        assert len(d["steps"]) > 0

    def test_progress_to_dict(self):
        trainer = SkillTrainer()
        progress = trainer.start_lesson("learner-1", "auto-001")
        d = progress.to_dict()
        assert d["learner_id"] == "learner-1"

    def test_domain_summary(self):
        trainer = SkillTrainer()
        summary = trainer.domain_summary()
        assert SkillDomain.AUTOMOTIVE.value in summary

    def test_score_clamped_to_zero_one(self):
        trainer = SkillTrainer()
        progress = trainer.start_lesson("learner-1", "auto-001")
        completed = trainer.complete_lesson(progress.progress_id, 1.5)
        assert completed.score == 1.0

    def test_score_clamped_negative(self):
        trainer = SkillTrainer()
        progress = trainer.start_lesson("learner-1", "auto-001")
        completed = trainer.complete_lesson(progress.progress_id, -0.5)
        assert completed.score == 0.0

    def test_cpr_lesson_exists(self):
        trainer = SkillTrainer()
        lesson = trainer.get_lesson("health-001")
        assert "CPR" in lesson.title

    def test_finance_lesson_exists(self):
        trainer = SkillTrainer()
        lesson = trainer.get_lesson("finance-001")
        assert lesson.domain == SkillDomain.FINANCE

    def test_advance_completed_lesson_raises(self):
        trainer = SkillTrainer()
        progress = trainer.start_lesson("learner-1", "auto-001")
        trainer.complete_lesson(progress.progress_id, 1.0)
        with pytest.raises(SkillTrainerError):
            trainer.advance_step(progress.progress_id)


# ===========================================================================
# 4. ITEM DETECTOR
# ===========================================================================

class TestItemDetector:
    def test_detect_penny(self):
        detector = ItemDetector()
        result = detector.detect_and_value("penny")
        assert result.detected_category == ItemCategory.COIN
        assert result.estimated_value_usd >= 0

    def test_detect_pokemon_card(self):
        detector = ItemDetector()
        result = detector.detect_and_value("pokemon card")
        assert result.detected_category == ItemCategory.TRADING_CARD

    def test_detect_charizard(self):
        detector = ItemDetector()
        result = detector.detect_and_value("charizard pokemon card")
        assert result.detected_category == ItemCategory.TRADING_CARD
        assert result.estimated_max_usd > result.estimated_min_usd

    def test_detect_antique_vase(self):
        detector = ItemDetector()
        result = detector.detect_and_value("antique vase")
        assert result.detected_category == ItemCategory.ANTIQUE

    def test_detect_funko_pop(self):
        detector = ItemDetector()
        result = detector.detect_and_value("funko pop")
        assert result.detected_category == ItemCategory.TOY_COLLECTIBLE

    def test_detect_vintage_console(self):
        detector = ItemDetector()
        result = detector.detect_and_value("vintage console Nintendo NES")
        assert result.detected_category == ItemCategory.ELECTRONICS

    def test_condition_mint_higher_than_poor(self):
        detector = ItemDetector()
        mint = detector.detect_and_value("morgan silver dollar", ConditionGrade.MINT)
        poor = detector.detect_and_value("morgan silver dollar", ConditionGrade.POOR)
        assert mint.estimated_value_usd > poor.estimated_value_usd

    def test_condition_multipliers_applied(self):
        detector = ItemDetector()
        result_mint = detector.detect_and_value("penny", ConditionGrade.MINT)
        result_poor = detector.detect_and_value("penny", ConditionGrade.POOR)
        # Mint multiplier = 1.0, Poor = 0.1 — mint should be ~10x poor
        assert result_mint.estimated_value_usd > result_poor.estimated_value_usd

    def test_unknown_item(self):
        detector = ItemDetector()
        result = detector.detect_and_value("xyzzy unknown widget 9999")
        assert result.detected_category == ItemCategory.UNKNOWN
        assert result.estimated_value_usd == 0.0

    def test_extra_context_included(self):
        detector = ItemDetector()
        result = detector.detect_and_value("pokemon card", extra_context="first edition 1999")
        assert "first edition" in result.item_description.lower()

    def test_result_has_comparables(self):
        detector = ItemDetector()
        result = detector.detect_and_value("silver dollar")
        assert len(result.comparable_sales) == 3

    def test_result_has_factors(self):
        detector = ItemDetector()
        result = detector.detect_and_value("penny")
        assert len(result.factors) > 0

    def test_result_to_dict(self):
        detector = ItemDetector()
        result = detector.detect_and_value("quarter")
        d = result.to_dict()
        assert "result_id" in d
        assert "estimated_value_usd" in d

    def test_detection_history(self):
        detector = ItemDetector()
        detector.detect_and_value("penny")
        detector.detect_and_value("charizard")
        assert len(detector.detection_history()) == 2

    def test_add_training_example(self):
        detector = ItemDetector()
        ex = detector.add_training_example(
            ItemCategory.COIN,
            "1943 steel penny",
            ["copper", "wartime", "error"],
            known_value_usd=300.0,
        )
        assert ex.category == ItemCategory.COIN
        assert ex.known_value_usd == 300.0

    def test_training_stats(self):
        detector = ItemDetector()
        detector.add_training_example(ItemCategory.COIN, "penny", ["round", "copper"])
        detector.add_training_example(ItemCategory.TRADING_CARD, "charizard", ["holo"])
        stats = detector.training_stats()
        assert stats["total_examples"] == 2
        assert stats["ai_training_sessions"] == 2
        assert ItemCategory.COIN.value in stats["categories"]

    def test_all_condition_grades_work(self):
        detector = ItemDetector()
        for grade in ConditionGrade:
            result = detector.detect_and_value("penny", grade)
            assert result.estimated_value_usd >= 0

    def test_oil_painting_detected_as_artwork(self):
        detector = ItemDetector()
        result = detector.detect_and_value("oil painting landscape")
        assert result.detected_category in (ItemCategory.ARTWORK, ItemCategory.ANTIQUE)

    def test_confidence_score_present(self):
        detector = ItemDetector()
        result = detector.detect_and_value("morgan silver dollar")
        assert 0.0 <= result.confidence <= 1.0

    def test_high_value_rare_coin(self):
        detector = ItemDetector()
        result = detector.detect_and_value("error coin", ConditionGrade.MINT)
        assert result.estimated_max_usd >= 1000.0

    def test_first_edition_pokemon_high_value(self):
        detector = ItemDetector()
        result = detector.detect_and_value("first edition pokemon card", ConditionGrade.MINT)
        assert result.estimated_max_usd >= 100.0

    def test_black_lotus_mtg(self):
        detector = ItemDetector()
        result = detector.detect_and_value("black lotus mtg")
        assert result.detected_category == ItemCategory.TRADING_CARD

    def test_diamond_jewelry_detected(self):
        detector = ItemDetector()
        result = detector.detect_and_value("diamond ring gold")
        assert result.detected_category in (ItemCategory.JEWELRY, ItemCategory.ANTIQUE)


# ===========================================================================
# 5. PERSONALITY ENGINE
# ===========================================================================

class TestPersonalityEngine:
    def test_default_profile(self):
        engine = PersonalityEngine("Buddy", "user-1")
        profile = engine.get_personality_profile()
        assert profile["bot_name"] == "Buddy"
        assert profile["user_id"] == "user-1"
        assert profile["interaction_count"] == 0

    def test_process_message_returns_string(self):
        engine = PersonalityEngine()
        response = engine.process_message("Hello!")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_interaction_count_increments(self):
        engine = PersonalityEngine()
        engine.process_message("Hi")
        engine.process_message("How are you?")
        assert engine.get_personality_profile()["interaction_count"] == 2

    def test_tone_selection_empathetic(self):
        engine = PersonalityEngine()
        engine.process_message("I'm so frustrated and stressed")
        last = engine.interaction_history()[-1]
        assert last.tone_used == ToneStyle.EMPATHETIC

    def test_tone_selection_humorous(self):
        engine = PersonalityEngine()
        engine.process_message("lol that's funny haha")
        last = engine.interaction_history()[-1]
        assert last.tone_used == ToneStyle.HUMOROUS

    def test_tone_selection_direct(self):
        engine = PersonalityEngine()
        engine.process_message("just give me a quick tldr")
        last = engine.interaction_history()[-1]
        assert last.tone_used == ToneStyle.DIRECT

    def test_trait_nudging_humour(self):
        engine = PersonalityEngine()
        initial = engine.get_trait(PersonalityTrait.HUMOUR)
        engine.process_message("That joke was so funny lol haha")
        updated = engine.get_trait(PersonalityTrait.HUMOUR)
        assert updated > initial

    def test_trait_nudging_empathy(self):
        engine = PersonalityEngine()
        initial = engine.get_trait(PersonalityTrait.EMPATHY)
        engine.process_message("I feel so worried and overwhelmed")
        assert engine.get_trait(PersonalityTrait.EMPATHY) >= initial

    def test_set_tone_preference(self):
        engine = PersonalityEngine()
        engine.set_tone_preference(ToneStyle.FORMAL)
        assert engine._preferred_tone == ToneStyle.FORMAL

    def test_record_milestone(self):
        engine = PersonalityEngine()
        milestone = engine.record_milestone("First Lesson", "Completed first lesson!", "lesson_completed")
        assert milestone.title == "First Lesson"
        assert milestone.category == "lesson_completed"

    def test_list_milestones(self):
        engine = PersonalityEngine()
        engine.record_milestone("M1", "D1", "test")
        engine.record_milestone("M2", "D2", "test")
        assert len(engine.list_milestones()) == 2

    def test_celebrate_milestone_high_enthusiasm(self):
        engine = PersonalityEngine()
        engine._traits[PersonalityTrait.ENTHUSIASM.value] = 0.9
        milestone = engine.record_milestone("Win", "You won!", "win")
        msg = engine.celebrate_milestone(milestone)
        assert "proud" in msg.lower() or "yes" in msg.lower()

    def test_celebrate_milestone_low_enthusiasm(self):
        engine = PersonalityEngine()
        engine._traits[PersonalityTrait.ENTHUSIASM.value] = 0.1
        milestone = engine.record_milestone("Win", "Done.", "win")
        msg = engine.celebrate_milestone(milestone)
        assert "Milestone" in msg

    def test_proactive_suggestions_car(self):
        engine = PersonalityEngine()
        for _ in range(3):
            engine.process_message("How do I fix my car engine oil?")
        suggestions = engine.proactive_suggestions()
        assert any("automotive" in s.lower() or "car" in s.lower() or "maintenance" in s.lower() for s in suggestions)

    def test_proactive_suggestions_interaction_count(self):
        engine = PersonalityEngine()
        for i in range(10):
            engine.process_message(f"Message {i}")
        suggestions = engine.proactive_suggestions()
        assert any("10" in s for s in suggestions)

    def test_interaction_history(self):
        engine = PersonalityEngine()
        engine.process_message("Hello!")
        history = engine.interaction_history()
        assert len(history) == 1
        assert isinstance(history[0], UserInteraction)

    def test_topic_inference_car(self):
        engine = PersonalityEngine()
        engine.process_message("How do I change my car's oil?")
        profile = engine.get_personality_profile()
        assert "car" in profile["top_topics"]

    def test_topic_inference_collectibles(self):
        engine = PersonalityEngine()
        engine.process_message("What is my pokemon card worth?")
        profile = engine.get_personality_profile()
        assert "collectibles" in profile["top_topics"]

    def test_sentiment_positive(self):
        engine = PersonalityEngine()
        engine.process_message("This is amazing and great, thanks!")
        history = engine.interaction_history()
        assert history[-1].sentiment_score > 0.5

    def test_sentiment_negative(self):
        engine = PersonalityEngine()
        engine.process_message("This is bad and I hate it, wrong answer")
        history = engine.interaction_history()
        assert history[-1].sentiment_score < 0.5

    def test_milestone_to_dict(self):
        engine = PersonalityEngine()
        m = engine.record_milestone("T", "D", "cat")
        d = m.to_dict()
        assert "milestone_id" in d
        assert d["category"] == "cat"


# ===========================================================================
# 6. BUDDY TEACH BOT (integration)
# ===========================================================================

class TestBuddyTeachBotFree:
    def test_init_free(self):
        bot = BuddyTeachBot(Tier.FREE, user_id="user-1")
        assert bot.tier == Tier.FREE
        assert bot.user_id == "user-1"

    def test_boot_log(self):
        bot = BuddyTeachBot(Tier.FREE)
        log = bot.get_boot_log()
        assert len(log) > 0
        assert any("Free" in line for line in log)

    def test_list_lessons_free(self):
        bot = BuddyTeachBot(Tier.FREE)
        lessons = bot.list_lessons()
        assert len(lessons) >= 4

    def test_start_lesson_free(self):
        bot = BuddyTeachBot(Tier.FREE)
        progress = bot.start_lesson("auto-001")
        assert progress.status == LessonStatus.IN_PROGRESS

    def test_complete_lesson_free_pass(self):
        bot = BuddyTeachBot(Tier.FREE, user_id="learner-1")
        progress = bot.start_lesson("auto-001")
        completed = bot.complete_lesson(progress.progress_id, 0.9)
        assert completed.status == LessonStatus.COMPLETED
        # Celebration message added
        assert any("Congratulations" in f or "proud" in f.lower() or "YES" in f for f in completed.feedback)

    def test_detect_item_free(self):
        bot = BuddyTeachBot(Tier.FREE)
        result = bot.detect_item("1943 steel penny", ConditionGrade.EXCELLENT)
        assert result.detected_category == ItemCategory.COIN

    def test_chat_free(self):
        bot = BuddyTeachBot(Tier.FREE)
        response = bot.chat("Hello Buddy!")
        assert isinstance(response, str)

    def test_add_broadcast_target_free(self):
        bot = BuddyTeachBot(Tier.FREE)
        target = bot.add_broadcast_target("My TV", DeviceCategory.SMART_TV)
        assert target.name == "My TV"

    def test_free_single_broadcast_limit(self):
        bot = BuddyTeachBot(Tier.FREE)
        bot.add_broadcast_target("TV", DeviceCategory.SMART_TV)
        with pytest.raises(BroadcastEngineError, match="Maximum broadcast targets"):
            bot.add_broadcast_target("Phone", DeviceCategory.PHONE)

    def test_multi_broadcast_blocked_on_free(self):
        bot = BuddyTeachBot(Tier.FREE)
        bot.add_broadcast_target("TV", DeviceCategory.SMART_TV)
        lesson_id = "auto-001"
        target_id = bot.broadcast.list_targets()[0].target_id
        with pytest.raises(BuddyTeachBotTierError):
            # start_lesson_broadcast with two targets requires multi_broadcast
            bot.start_lesson_broadcast(lesson_id, [target_id, "fake-id"])

    def test_ai_training_blocked_on_free(self):
        bot = BuddyTeachBot(Tier.FREE)
        with pytest.raises(BuddyTeachBotTierError):
            bot.add_training_example(ItemCategory.COIN, "penny", ["round"])

    def test_curriculum_builder_blocked_on_free(self):
        bot = BuddyTeachBot(Tier.FREE)
        custom = Lesson(
            lesson_id="custom-001",
            title="Custom",
            domain=SkillDomain.TECHNOLOGY,
            difficulty=DifficultyLevel.BEGINNER,
            description="Custom lesson.",
            steps=[LessonStep(1, "S1", "Do it.")],
        )
        with pytest.raises(BuddyTeachBotTierError):
            bot.add_lesson(custom)

    def test_upgrade_info_from_free(self):
        bot = BuddyTeachBot(Tier.FREE)
        info = bot.upgrade_info()
        assert info is not None
        assert info["next_tier"] == "Pro"

    def test_status_dict(self):
        bot = BuddyTeachBot(Tier.FREE)
        s = bot.status()
        assert "tier" in s
        assert s["tier"] == "Free"
        assert "personality_profile" in s

    def test_set_tone(self):
        bot = BuddyTeachBot(Tier.FREE)
        bot.set_tone(ToneStyle.MOTIVATIONAL)
        assert bot.personality._preferred_tone == ToneStyle.MOTIVATIONAL

    def test_proactive_suggestions(self):
        bot = BuddyTeachBot(Tier.FREE)
        for _ in range(3):
            bot.chat("How do I fix my car oil?")
        suggestions = bot.proactive_suggestions()
        assert isinstance(suggestions, list)

    def test_start_lesson_broadcast_free(self):
        bot = BuddyTeachBot(Tier.FREE)
        target = bot.add_broadcast_target("TV", DeviceCategory.SMART_TV)
        session = bot.start_lesson_broadcast("auto-001", [target.target_id])
        assert session.state == BroadcastState.LIVE

    def test_advance_step(self):
        bot = BuddyTeachBot(Tier.FREE)
        progress = bot.start_lesson("auto-001")
        advanced = bot.advance_step(progress.progress_id)
        assert advanced.current_step == 2


class TestBuddyTeachBotPro:
    def test_init_pro(self):
        bot = BuddyTeachBot(Tier.PRO)
        assert bot.tier == Tier.PRO
        assert bot.config.price_usd_monthly == 49.0

    def test_multi_broadcast_pro(self):
        bot = BuddyTeachBot(Tier.PRO)
        tv = bot.add_broadcast_target("TV", DeviceCategory.SMART_TV)
        phone = bot.add_broadcast_target("Phone", DeviceCategory.PHONE)
        tablet = bot.add_broadcast_target("Tablet", DeviceCategory.TABLET)
        session = bot.start_lesson_broadcast("auto-001", [tv.target_id, phone.target_id, tablet.target_id])
        assert len(session.target_ids) == 3

    def test_broadcast_to_all_devices_pro(self):
        bot = BuddyTeachBot(Tier.PRO)
        bot.add_broadcast_target("TV", DeviceCategory.SMART_TV)
        bot.add_broadcast_target("Phone", DeviceCategory.PHONE)
        session = bot.broadcast_to_all_devices("auto-001")
        assert len(session.target_ids) == 2

    def test_ai_training_pro(self):
        bot = BuddyTeachBot(Tier.PRO)
        ex = bot.add_training_example(
            ItemCategory.TRADING_CARD,
            "holographic charizard",
            ["holo", "rare", "first edition"],
            known_value_usd=5000.0,
        )
        assert ex.contributor_id == "default_user"

    def test_curriculum_builder_blocked_on_pro(self):
        bot = BuddyTeachBot(Tier.PRO)
        custom = Lesson(
            lesson_id="custom-002",
            title="Advanced Lesson",
            domain=SkillDomain.TECHNOLOGY,
            difficulty=DifficultyLevel.ADVANCED,
            description="Advanced.",
            steps=[LessonStep(1, "S", "Do.")],
        )
        with pytest.raises(BuddyTeachBotTierError):
            bot.add_lesson(custom)

    def test_upgrade_info_from_pro(self):
        bot = BuddyTeachBot(Tier.PRO)
        info = bot.upgrade_info()
        assert info["next_tier"] == "Enterprise"

    def test_up_to_ten_targets_pro(self):
        bot = BuddyTeachBot(Tier.PRO)
        for i in range(10):
            bot.add_broadcast_target(f"Device {i}", DeviceCategory.COMPUTER)
        assert len(bot.broadcast.list_targets()) == 10

    def test_eleven_targets_blocked_pro(self):
        bot = BuddyTeachBot(Tier.PRO)
        for i in range(10):
            bot.add_broadcast_target(f"Device {i}", DeviceCategory.COMPUTER)
        with pytest.raises(BroadcastEngineError):
            bot.add_broadcast_target("Device 10", DeviceCategory.TABLET)


class TestBuddyTeachBotEnterprise:
    def test_init_enterprise(self):
        bot = BuddyTeachBot(Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE
        assert bot.config.price_usd_monthly == 199.0

    def test_curriculum_builder_enterprise(self):
        bot = BuddyTeachBot(Tier.ENTERPRISE)
        custom = Lesson(
            lesson_id="ent-001",
            title="Enterprise Custom Lesson",
            domain=SkillDomain.CREATIVE,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Enterprise lesson.",
            steps=[LessonStep(1, "S1", "Do it.")],
        )
        bot.add_lesson(custom)
        lesson = bot.trainer.get_lesson("ent-001")
        assert lesson.title == "Enterprise Custom Lesson"

    def test_unlimited_broadcast_enterprise(self):
        bot = BuddyTeachBot(Tier.ENTERPRISE)
        for i in range(50):
            bot.add_broadcast_target(f"Device {i}", DeviceCategory.SMART_TV)
        assert len(bot.broadcast.list_targets()) == 50

    def test_upgrade_info_enterprise_none(self):
        bot = BuddyTeachBot(Tier.ENTERPRISE)
        assert bot.upgrade_info() is None

    def test_full_workflow_enterprise(self):
        """End-to-end: register devices, broadcast, teach, detect items."""
        bot = BuddyTeachBot(Tier.ENTERPRISE, user_id="power-user", bot_name="Max")
        # Register 3 device types
        tv = bot.add_broadcast_target("Smart TV", DeviceCategory.SMART_TV)
        console = bot.add_broadcast_target("PlayStation 5", DeviceCategory.GAME_CONSOLE, platform="PS5")
        headset = bot.add_broadcast_target("Quest 3", DeviceCategory.AR_VR_HEADSET, ar_capable=True)
        # Start lesson
        progress = bot.start_lesson("auto-001")
        bot.advance_step(progress.progress_id)
        bot.advance_step(progress.progress_id)
        # Broadcast lesson to all
        session = bot.broadcast_to_all_devices("auto-001", ContentFormat.AR_OVERLAY)
        assert len(session.target_ids) == 3
        # Complete lesson
        result = bot.complete_lesson(progress.progress_id, 0.95)
        assert result.status == LessonStatus.COMPLETED
        # Detect an item
        detection = bot.detect_item("first edition pokemon card", ConditionGrade.MINT)
        assert detection.estimated_max_usd > 0
        # Add training data
        ex = bot.add_training_example(ItemCategory.TRADING_CARD, "charizard holo", ["holo", "rare"])
        assert ex.category == ItemCategory.TRADING_CARD
        # Chat
        response = bot.chat("This is amazing!")
        assert isinstance(response, str)
        # Status check
        status = bot.status()
        assert status["broadcast_targets"] == 3
        assert status["total_lessons"] >= 4
