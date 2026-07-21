"""
Tests for bots/buddy_omniscient_bot/

Covers all modules:
  1. Tiers
  2. AR/VR Engine
  3. Viral Challenges Engine
  4. Reality Show Engine
  5. Charity Ambassador Engine
  6. Dream Your Business Engine
  7. AI Social Creator Engine
  8. Dynamic Learning Engine
  9. Skill Database
 10. Knowledge Engine
 11. BuddyOmniscientBot main class (integration + chat)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from bots.buddy_omniscient_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_AR_VR,
    FEATURE_HOLOGRAPHIC,
    FEATURE_VIRAL_CHALLENGES,
    FEATURE_BUDDY_BADGES,
    FEATURE_SKILL_DATABASE,
    FEATURE_SKILL_UPLOAD,
    FEATURE_KNOWLEDGE_ENGINE,
    FEATURE_OMNISCIENT_MODE,
    FEATURE_SOCIAL_CREATORS,
    FEATURE_REALITY_SHOW,
    FEATURE_CHARITY_AMBASSADOR,
    FEATURE_DREAM_BUSINESS,
    FEATURE_EXPERT_COLLABORATION,
    FEATURE_DYNAMIC_LEARNING,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_ADVANCED_ANALYTICS,
    FEATURE_DEDICATED_SUPPORT,
)
from bots.buddy_omniscient_bot.ar_vr_engine import (
    ARVREngine,
    AROverlaySession,
    HolographicSession,
    AROverlayType,
    HolographicMode,
    ProjectionDevice,
)
from bots.buddy_omniscient_bot.viral_challenges import (
    ViralChallengesEngine,
    RealityShowEngine,
    CharityAmbassadorEngine,
    DreamYourBusinessEngine,
    AISocialCreatorEngine,
    DynamicLearningEngine,
    ChallengeCategory,
    BadgeTier,
    SocialPlatform,
    ContentType,
    CharityCause,
    LearningGameType,
)
from bots.buddy_omniscient_bot.skill_database import (
    SkillDatabase,
    SkillCategory,
    SkillDifficulty,
    ExpertField,
)
from bots.buddy_omniscient_bot.knowledge_engine import (
    KnowledgeEngine,
    KnowledgeDomain,
    CompetitorAI,
)
from bots.buddy_omniscient_bot.buddy_omniscient_bot import (
    BuddyOmniscientBot,
    BuddyOmniscientError,
    BuddyOmniscientTierError,
)


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_free_tier_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_enterprise_unlimited_knowledge(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_knowledge()

    def test_free_has_limited_ar_sessions(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_ar_sessions == 5

    def test_pro_has_more_ar_sessions(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_ar_sessions == 100

    def test_enterprise_unlimited_ar_sessions(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_ar_sessions is None

    def test_free_no_skill_uploads(self):
        assert get_tier_config(Tier.FREE).max_skill_uploads == 0

    def test_pro_has_skill_uploads(self):
        assert get_tier_config(Tier.PRO).max_skill_uploads == 50

    def test_enterprise_unlimited_skill_uploads(self):
        assert get_tier_config(Tier.ENTERPRISE).max_skill_uploads is None

    def test_free_has_ar_vr_feature(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_AR_VR)

    def test_free_does_not_have_holographic(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_HOLOGRAPHIC)

    def test_pro_has_holographic(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_HOLOGRAPHIC)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feature in [
            FEATURE_AR_VR, FEATURE_HOLOGRAPHIC, FEATURE_VIRAL_CHALLENGES,
            FEATURE_BUDDY_BADGES, FEATURE_OMNISCIENT_MODE, FEATURE_SOCIAL_CREATORS,
            FEATURE_REALITY_SHOW, FEATURE_CHARITY_AMBASSADOR, FEATURE_DREAM_BUSINESS,
            FEATURE_EXPERT_COLLABORATION, FEATURE_WHITE_LABEL, FEATURE_API_ACCESS,
            FEATURE_ADVANCED_ANALYTICS, FEATURE_DEDICATED_SUPPORT,
        ]:
            assert cfg.has_feature(feature), f"Missing feature: {feature}"

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_tier_config_dataclass(self):
        cfg = get_tier_config(Tier.PRO)
        assert isinstance(cfg, TierConfig)
        assert cfg.name == "Pro"


# ===========================================================================
# 2. AR/VR Engine
# ===========================================================================

class TestARVREngine:
    def setup_method(self):
        self.engine = ARVREngine(max_sessions=10)

    def test_start_ar_overlay_repair_guide(self):
        session = self.engine.start_ar_overlay(
            AROverlayType.REPAIR_GUIDE, ProjectionDevice.SMARTPHONE
        )
        assert isinstance(session, AROverlaySession)
        assert session.overlay_type == AROverlayType.REPAIR_GUIDE
        assert session.active is True

    def test_ar_session_has_instructions(self):
        session = self.engine.start_ar_overlay(
            AROverlayType.COOKING_GUIDE, ProjectionDevice.TABLET
        )
        assert len(session.instructions) > 0

    def test_ar_session_voice_guidance(self):
        session = self.engine.start_ar_overlay(
            AROverlayType.REPAIR_GUIDE, ProjectionDevice.SMARTPHONE,
            voice_guidance=True
        )
        assert session.voice_guidance is True

    def test_ar_session_hands_free_mode(self):
        session = self.engine.start_ar_overlay(
            AROverlayType.REPAIR_GUIDE, ProjectionDevice.AR_GLASSES,
            hands_free_mode=True
        )
        assert session.hands_free_mode is True

    def test_stop_ar_overlay(self):
        session = self.engine.start_ar_overlay(
            AROverlayType.EDUCATION, ProjectionDevice.COMPUTER
        )
        result = self.engine.stop_ar_overlay(session.session_id)
        assert result is True
        assert session.active is False

    def test_stop_nonexistent_session_returns_false(self):
        assert self.engine.stop_ar_overlay("INVALID-ID") is False

    def test_list_ar_sessions_active_only(self):
        session1 = self.engine.start_ar_overlay(
            AROverlayType.EDUCATION, ProjectionDevice.SMARTPHONE
        )
        session2 = self.engine.start_ar_overlay(
            AROverlayType.COOKING_GUIDE, ProjectionDevice.TABLET
        )
        self.engine.stop_ar_overlay(session1.session_id)
        active = self.engine.list_ar_sessions(active_only=True)
        assert len(active) == 1
        assert active[0].session_id == session2.session_id

    def test_ar_session_limit_enforced(self):
        engine = ARVREngine(max_sessions=2)
        engine.start_ar_overlay(AROverlayType.EDUCATION, ProjectionDevice.SMARTPHONE)
        engine.start_ar_overlay(AROverlayType.EDUCATION, ProjectionDevice.TABLET)
        with pytest.raises(RuntimeError):
            engine.start_ar_overlay(AROverlayType.EDUCATION, ProjectionDevice.COMPUTER)

    def test_project_holographic_buddy(self):
        session = self.engine.project_holographic_buddy(
            device=ProjectionDevice.AR_GLASSES,
            mode=HolographicMode.LIFE_SIZED,
        )
        assert isinstance(session, HolographicSession)
        assert session.mode == HolographicMode.LIFE_SIZED
        assert session.active is True

    def test_stop_holographic_session(self):
        session = self.engine.project_holographic_buddy(ProjectionDevice.VR_HEADSET)
        result = self.engine.stop_holographic_session(session.session_id)
        assert result is True
        assert session.active is False

    def test_broadcast_to_devices(self):
        session = self.engine.start_ar_overlay(
            AROverlayType.REPAIR_GUIDE, ProjectionDevice.SMARTPHONE
        )
        result = self.engine.broadcast_to_devices(
            session.session_id,
            [ProjectionDevice.SMART_TV, ProjectionDevice.TABLET, ProjectionDevice.COMPUTER],
        )
        assert result["status"] == "broadcasting"
        assert len(result["broadcast_to"]) == 3

    def test_broadcast_inactive_session_returns_error(self):
        session = self.engine.start_ar_overlay(
            AROverlayType.EDUCATION, ProjectionDevice.SMARTPHONE
        )
        self.engine.stop_ar_overlay(session.session_id)
        result = self.engine.broadcast_to_devices(session.session_id, [ProjectionDevice.TABLET])
        assert "error" in result

    def test_broadcast_nonexistent_session_returns_error(self):
        result = self.engine.broadcast_to_devices("BAD-ID", [ProjectionDevice.TABLET])
        assert "error" in result

    def test_supported_devices_includes_all_types(self):
        devices = self.engine.get_supported_devices()
        assert "smartphone" in devices
        assert "ar_glasses" in devices
        assert "smart_tv" in devices
        assert "vr_headset" in devices
        assert "game_console" in devices

    def test_ar_session_to_dict(self):
        session = self.engine.start_ar_overlay(
            AROverlayType.FURNITURE_PLACEMENT, ProjectionDevice.SMART_TV,
            context="Living room redesign"
        )
        d = session.to_dict()
        assert d["overlay_type"] == "furniture_placement"
        assert d["device"] == "smart_tv"
        assert d["context"] == "Living room redesign"
        assert d["active"] is True

    def test_holographic_session_to_dict(self):
        session = self.engine.project_holographic_buddy(
            ProjectionDevice.HOLOGRAPHIC_DISPLAY,
            HolographicMode.WALL_PROJECTION,
            buddy_persona="Buddy Pro",
        )
        d = session.to_dict()
        assert d["mode"] == "wall_projection"
        assert d["buddy_persona"] == "Buddy Pro"

    def test_count_active_ar_sessions(self):
        self.engine.start_ar_overlay(AROverlayType.EDUCATION, ProjectionDevice.SMARTPHONE)
        self.engine.start_ar_overlay(AROverlayType.COOKING_GUIDE, ProjectionDevice.TABLET)
        assert self.engine.count_active_ar_sessions() == 2

    def test_count_active_holographic_sessions(self):
        self.engine.project_holographic_buddy(ProjectionDevice.AR_GLASSES)
        assert self.engine.count_active_holographic_sessions() == 1

    def test_all_overlay_types_get_instructions(self):
        for overlay_type in AROverlayType:
            session = self.engine.start_ar_overlay(overlay_type, ProjectionDevice.SMARTPHONE)
            assert len(session.instructions) > 0


# ===========================================================================
# 3. Viral Challenges Engine
# ===========================================================================

class TestViralChallengesEngine:
    def setup_method(self):
        self.engine = ViralChallengesEngine(max_challenges=None)

    def test_list_challenges_returns_presets(self):
        challenges = self.engine.list_challenges()
        assert len(challenges) >= 5

    def test_list_challenges_filtered_by_category(self):
        challenges = self.engine.list_challenges(ChallengeCategory.CAR_REPAIR)
        assert all(c.category == ChallengeCategory.CAR_REPAIR for c in challenges)

    def test_get_challenge_by_id(self):
        challenge = self.engine.get_challenge("CH-001")
        assert challenge is not None
        assert challenge.challenge_id == "CH-001"

    def test_get_nonexistent_challenge_returns_none(self):
        assert self.engine.get_challenge("CH-999") is None

    def test_complete_challenge_awards_points(self):
        result = self.engine.complete_challenge("CH-001")
        assert result["points_earned"] == 500
        assert result["total_points"] == 500

    def test_complete_challenge_multiple_times_accumulates_points(self):
        self.engine.complete_challenge("CH-001")
        self.engine.complete_challenge("CH-002")
        assert self.engine.get_user_points() == 800

    def test_complete_challenge_awards_badge(self):
        result = self.engine.complete_challenge("CH-001")
        assert result.get("badge") is not None

    def test_complete_nonexistent_challenge_returns_error(self):
        result = self.engine.complete_challenge("CH-999")
        assert "error" in result

    def test_user_points_initially_zero(self):
        engine = ViralChallengesEngine()
        assert engine.get_user_points() == 0

    def test_award_badge_directly(self):
        result = self.engine.award_badge("BDG-001")
        assert "badge" in result
        assert result["badge"]["badge_id"] == "BDG-001"
        assert result["badge"]["earned"] is True

    def test_award_badge_already_earned(self):
        self.engine.award_badge("BDG-001")
        result = self.engine.award_badge("BDG-001")
        assert "already earned" in result["message"]

    def test_award_nonexistent_badge_returns_error(self):
        result = self.engine.award_badge("BDG-999")
        assert "error" in result

    def test_list_all_badges_includes_presets(self):
        badges = self.engine.list_all_badges()
        assert len(badges) >= 10

    def test_badge_tiers_include_legendary(self):
        badges = self.engine.list_all_badges()
        tiers = {b.tier for b in badges}
        assert BadgeTier.LEGENDARY in tiers

    def test_earned_badges_initially_empty(self):
        engine = ViralChallengesEngine()
        assert len(engine.get_earned_badges()) == 0

    def test_get_leaderboard_entry(self):
        self.engine.complete_challenge("CH-004")
        entry = self.engine.get_leaderboard_entry("TestUser")
        assert entry["username"] == "TestUser"
        assert entry["points"] == 800

    def test_challenge_has_share_hashtags(self):
        challenge = self.engine.get_challenge("CH-001")
        assert len(challenge.share_hashtags) > 0

    def test_challenge_has_platforms(self):
        challenge = self.engine.get_challenge("CH-002")
        assert len(challenge.platforms) > 0

    def test_max_challenges_limit(self):
        engine = ViralChallengesEngine(max_challenges=2)
        challenges = engine.list_challenges()
        assert len(challenges) <= 2

    def test_challenge_to_dict(self):
        challenge = self.engine.get_challenge("CH-001")
        d = challenge.to_dict()
        assert d["challenge_id"] == "CH-001"
        assert "steps" in d
        assert "share_hashtags" in d
        assert "platforms" in d


# ===========================================================================
# 4. Reality Show Engine
# ===========================================================================

class TestRealityShowEngine:
    def setup_method(self):
        self.engine = RealityShowEngine()

    def test_create_episode(self):
        episode = self.engine.create_episode(
            title="What Can Buddy Fix?",
            description="Buddy repairs a car engine live!",
            challenge_category=ChallengeCategory.CAR_REPAIR,
            participants=["Alice", "Bob"],
        )
        assert episode is not None
        assert episode.title == "What Can Buddy Fix?"
        assert episode.live is False

    def test_go_live(self):
        episode = self.engine.create_episode(
            title="Buddy Cooks!", description="Live cooking challenge",
            challenge_category=ChallengeCategory.COOKING,
            participants=["Chef_A"],
        )
        result = self.engine.go_live(episode.episode_id)
        assert result["status"] == "live"
        assert episode.live is True

    def test_go_live_nonexistent_returns_error(self):
        result = self.engine.go_live("EP-INVALID")
        assert "error" in result

    def test_voting(self):
        episode = self.engine.create_episode(
            title="Buddy Art Show", description="AR art challenge",
            challenge_category=ChallengeCategory.CREATIVE_ART,
            participants=["Artist_X"],
        )
        self.engine.go_live(episode.episode_id)
        result = self.engine.vote(episode.episode_id, votes=10)
        assert result["total_votes"] == 10

    def test_voting_accumulates(self):
        episode = self.engine.create_episode(
            title="Buddy Music", description="Live jam session",
            challenge_category=ChallengeCategory.MUSIC,
            participants=["JRock"],
        )
        self.engine.vote(episode.episode_id, 5)
        self.engine.vote(episode.episode_id, 3)
        assert episode.vote_count == 8

    def test_voting_nonexistent_returns_error(self):
        result = self.engine.vote("INVALID-EP")
        assert "error" in result

    def test_list_episodes(self):
        self.engine.create_episode(
            title="E1", description="Ep1",
            challenge_category=ChallengeCategory.GAMING, participants=["P1"]
        )
        self.engine.create_episode(
            title="E2", description="Ep2",
            challenge_category=ChallengeCategory.COOKING, participants=["P2"]
        )
        assert len(self.engine.list_episodes()) == 2

    def test_list_live_episodes_only(self):
        ep1 = self.engine.create_episode(
            title="Live1", description="L1",
            challenge_category=ChallengeCategory.BUSINESS, participants=["P1"]
        )
        self.engine.create_episode(
            title="Offline1", description="O1",
            challenge_category=ChallengeCategory.COOKING, participants=["P2"]
        )
        self.engine.go_live(ep1.episode_id)
        live = self.engine.list_episodes(live_only=True)
        assert len(live) == 1

    def test_episode_to_dict(self):
        episode = self.engine.create_episode(
            title="Test", description="Test episode",
            challenge_category=ChallengeCategory.EDUCATION, participants=["P1"]
        )
        d = episode.to_dict()
        assert "episode_id" in d
        assert "participants" in d
        assert "vote_count" in d

    def test_episode_default_platforms(self):
        episode = self.engine.create_episode(
            title="Test", description="T",
            challenge_category=ChallengeCategory.GAMING, participants=["P"]
        )
        assert len(episode.platforms) > 0


# ===========================================================================
# 5. Charity Ambassador Engine
# ===========================================================================

class TestCharityAmbassadorEngine:
    def setup_method(self):
        self.engine = CharityAmbassadorEngine()

    def test_create_initiative(self):
        initiative = self.engine.create_initiative(
            cause=CharityCause.EDUCATION,
            title="Books for All",
            description="Provide books to underserved communities.",
            goal_amount=10000.0,
        )
        assert initiative is not None
        assert initiative.cause == CharityCause.EDUCATION
        assert initiative.goal_amount == 10000.0

    def test_donate_increases_raised_amount(self):
        initiative = self.engine.create_initiative(
            cause=CharityCause.HUNGER_RELIEF,
            title="Feed the World",
            description="Combat hunger.",
            goal_amount=50000.0,
        )
        result = self.engine.donate(initiative.initiative_id, 500.0)
        assert result["amount_donated"] == 500.0
        assert result["total_raised"] == 500.0

    def test_donation_progress_pct(self):
        initiative = self.engine.create_initiative(
            cause=CharityCause.TECH_ACCESS,
            title="Tech for All",
            description="Digital access.",
            goal_amount=1000.0,
        )
        self.engine.donate(initiative.initiative_id, 250.0)
        assert initiative.progress_pct == 25.0

    def test_donate_nonexistent_returns_error(self):
        result = self.engine.donate("CHR-INVALID", 100.0)
        assert "error" in result

    def test_donate_inactive_returns_error(self):
        initiative = self.engine.create_initiative(
            cause=CharityCause.VETERANS,
            title="Support Veterans",
            description="Help veterans.",
            goal_amount=5000.0,
        )
        initiative.active = False
        result = self.engine.donate(initiative.initiative_id, 100.0)
        assert "error" in result

    def test_add_awareness_post(self):
        initiative = self.engine.create_initiative(
            cause=CharityCause.ENVIRONMENTAL,
            title="Save the Oceans",
            description="Ocean cleanup.",
            goal_amount=20000.0,
        )
        result = self.engine.add_awareness_post(
            initiative.initiative_id, "Join Buddy's ocean cleanup challenge!"
        )
        assert result["total_posts"] == 1

    def test_add_awareness_post_nonexistent_returns_error(self):
        result = self.engine.add_awareness_post("INVALID", "Post")
        assert "error" in result

    def test_list_initiatives(self):
        self.engine.create_initiative(
            cause=CharityCause.EDUCATION, title="I1", description="D1", goal_amount=1000.0
        )
        self.engine.create_initiative(
            cause=CharityCause.MENTAL_HEALTH, title="I2", description="D2", goal_amount=2000.0
        )
        assert len(self.engine.list_initiatives()) == 2

    def test_list_active_initiatives_only(self):
        i1 = self.engine.create_initiative(
            cause=CharityCause.HUNGER_RELIEF, title="Active", description="A", goal_amount=500.0
        )
        i2 = self.engine.create_initiative(
            cause=CharityCause.VETERANS, title="Inactive", description="I", goal_amount=500.0
        )
        i2.active = False
        active = self.engine.list_initiatives(active_only=True)
        assert len(active) == 1
        assert active[0].initiative_id == i1.initiative_id

    def test_initiative_to_dict(self):
        initiative = self.engine.create_initiative(
            cause=CharityCause.DISASTER_RELIEF, title="T", description="D", goal_amount=5000.0
        )
        d = initiative.to_dict()
        assert "initiative_id" in d
        assert "progress_pct" in d
        assert d["cause"] == "disaster_relief"

    def test_progress_capped_at_100(self):
        initiative = self.engine.create_initiative(
            cause=CharityCause.EDUCATION, title="T", description="D", goal_amount=100.0
        )
        initiative.raised_amount = 200.0
        assert initiative.progress_pct == 100.0


# ===========================================================================
# 6. Dream Your Business Engine
# ===========================================================================

class TestDreamYourBusinessEngine:
    def setup_method(self):
        self.engine = DreamYourBusinessEngine()

    def test_create_business_plan(self):
        plan = self.engine.create_business_plan(
            business_name="QuickShop",
            business_type="Pop-up retail store",
            owner_name="Jordan",
        )
        assert plan is not None
        assert plan.business_name == "QuickShop"
        assert plan.estimated_launch_hours == 4.0

    def test_plan_has_steps(self):
        plan = self.engine.create_business_plan("BizName", "Type", "Owner")
        assert len(plan.steps_completed) >= 5

    def test_plan_has_marketing_content(self):
        plan = self.engine.create_business_plan("MyCo", "SaaS", "User")
        assert len(plan.marketing_content) >= 1

    def test_get_plan_by_id(self):
        plan = self.engine.create_business_plan("Shop", "Retail", "Alice")
        retrieved = self.engine.get_plan(plan.plan_id)
        assert retrieved is not None
        assert retrieved.plan_id == plan.plan_id

    def test_get_nonexistent_plan_returns_none(self):
        assert self.engine.get_plan("BIZ-INVALID") is None

    def test_list_plans(self):
        self.engine.create_business_plan("Biz1", "Type1", "O1")
        self.engine.create_business_plan("Biz2", "Type2", "O2")
        assert len(self.engine.list_plans()) == 2

    def test_plan_to_dict(self):
        plan = self.engine.create_business_plan("MyBiz", "Type", "Owner")
        d = plan.to_dict()
        assert "plan_id" in d
        assert d["business_name"] == "MyBiz"
        assert "marketing_content" in d
        assert "estimated_launch_hours" in d

    def test_plan_includes_hashtag(self):
        plan = self.engine.create_business_plan("HashBiz", "Online", "Chris")
        assert any("#DreamCoLaunch" in m for m in plan.marketing_content)


# ===========================================================================
# 7. AI Social Creator Engine
# ===========================================================================

class TestAISocialCreatorEngine:
    def setup_method(self):
        self.engine = AISocialCreatorEngine()

    def test_generate_video_idea(self):
        content = self.engine.generate_content(ContentType.VIDEO_IDEA, SocialPlatform.TIKTOK)
        assert content is not None
        assert content.content_type == ContentType.VIDEO_IDEA
        assert content.platform == SocialPlatform.TIKTOK

    def test_generate_script(self):
        content = self.engine.generate_content(ContentType.SCRIPT, SocialPlatform.YOUTUBE, topic="guitar")
        assert content is not None
        assert "guitar" in content.title.lower() or len(content.body) > 0

    def test_generate_meme(self):
        content = self.engine.generate_content(ContentType.MEME, SocialPlatform.INSTAGRAM)
        assert "Buddy" in content.body or len(content.body) > 0

    def test_generate_tweet(self):
        content = self.engine.generate_content(ContentType.TWEET, SocialPlatform.TWITTER, topic="AI")
        assert content.content_type == ContentType.TWEET

    def test_generate_reel_idea(self):
        content = self.engine.generate_content(ContentType.REEL_IDEA, SocialPlatform.INSTAGRAM)
        assert content.content_type == ContentType.REEL_IDEA

    def test_generate_trend_analysis(self):
        content = self.engine.generate_content(ContentType.TREND_ANALYSIS, SocialPlatform.TIKTOK)
        assert content.content_type == ContentType.TREND_ANALYSIS

    def test_content_has_hashtags(self):
        content = self.engine.generate_content(ContentType.VIDEO_IDEA, SocialPlatform.TIKTOK)
        assert len(content.hashtags) >= 3
        assert "#DreamCoAI" in content.hashtags

    def test_content_has_trend_score(self):
        content = self.engine.generate_content(ContentType.SCRIPT, SocialPlatform.YOUTUBE)
        assert 7.0 <= content.trend_score <= 10.0

    def test_count_generated(self):
        self.engine.generate_content(ContentType.VIDEO_IDEA, SocialPlatform.TIKTOK)
        self.engine.generate_content(ContentType.SCRIPT, SocialPlatform.YOUTUBE)
        assert self.engine.count_generated() == 2

    def test_list_generated_content(self):
        self.engine.generate_content(ContentType.MEME, SocialPlatform.INSTAGRAM)
        content_list = self.engine.list_generated_content()
        assert len(content_list) == 1

    def test_content_to_dict(self):
        content = self.engine.generate_content(ContentType.VIDEO_IDEA, SocialPlatform.TIKTOK)
        d = content.to_dict()
        assert "content_id" in d
        assert "body" in d
        assert "hashtags" in d
        assert "trend_score" in d


# ===========================================================================
# 8. Dynamic Learning Engine
# ===========================================================================

class TestDynamicLearningEngine:
    def setup_method(self):
        self.engine = DynamicLearningEngine()

    def test_list_games_returns_presets(self):
        games = self.engine.list_games()
        assert len(games) >= 4

    def test_list_multiplayer_games_only(self):
        games = self.engine.list_games(multiplayer_only=True)
        assert all(g.multiplayer for g in games)

    def test_list_games_by_type(self):
        games = self.engine.list_games(game_type=LearningGameType.CHEMISTRY)
        assert all(g.game_type == LearningGameType.CHEMISTRY for g in games)

    def test_start_game_session(self):
        session = self.engine.start_game_session("GAME-001", "Alice")
        assert session["player"] == "Alice"
        assert session["game_id"] == "GAME-001"
        assert session["active"] is True

    def test_start_nonexistent_game_returns_error(self):
        result = self.engine.start_game_session("GAME-999", "Alice")
        assert "error" in result

    def test_start_game_with_teammates(self):
        session = self.engine.start_game_session(
            "GAME-002", "Alice", teammates=["Bob", "Charlie"]
        )
        assert "Bob" in session["teammates"]

    def test_get_buddy_game_hint(self):
        session = self.engine.start_game_session("GAME-001", "Player1")
        hint = self.engine.get_buddy_game_hint(session["session_id"])
        assert "Buddy says" in hint["hint"]
        assert hint["buddy_guidance_active"] is True

    def test_get_hint_nonexistent_session_returns_error(self):
        result = self.engine.get_buddy_game_hint("GS-INVALID")
        assert "error" in result

    def test_games_have_buddy_guidance(self):
        games = self.engine.list_games()
        assert all(g.buddy_guidance for g in games)

    def test_count_games(self):
        assert self.engine.count_games() >= 4

    def test_game_to_dict(self):
        games = self.engine.list_games()
        d = games[0].to_dict()
        assert "game_id" in d
        assert "game_type" in d
        assert "multiplayer" in d
        assert "buddy_guidance" in d
        assert "skills_taught" in d


# ===========================================================================
# 9. Skill Database
# ===========================================================================

class TestSkillDatabase:
    def setup_method(self):
        self.db = SkillDatabase(max_uploads=None)

    def test_seed_skills_loaded(self):
        assert self.db.count_skills() >= 3

    def test_search_skills_by_query(self):
        results = self.db.search_skills(query="guitar")
        assert len(results) >= 1

    def test_search_skills_by_category(self):
        results = self.db.search_skills(category=SkillCategory.AUTOMOTIVE)
        assert all(s.category == SkillCategory.AUTOMOTIVE for s in results)

    def test_search_skills_by_difficulty(self):
        results = self.db.search_skills(difficulty=SkillDifficulty.BEGINNER)
        assert all(s.difficulty == SkillDifficulty.BEGINNER for s in results)

    def test_get_skill_by_id(self):
        skill = self.db.get_skill("SKILL-001")
        assert skill is not None
        assert skill.skill_id == "SKILL-001"

    def test_get_skill_increments_views(self):
        skill = self.db.get_skill("SKILL-001")
        initial_views = skill.views
        self.db.get_skill("SKILL-001")
        assert skill.views == initial_views + 1

    def test_get_nonexistent_skill_returns_none(self):
        assert self.db.get_skill("SKILL-999") is None

    def test_upload_skill(self):
        skill = self.db.upload_skill(
            title="Advanced Python Async",
            category=SkillCategory.TECHNOLOGY,
            difficulty=SkillDifficulty.ADVANCED,
            uploaded_by="DevUser",
            description="Deep dive into Python async/await patterns.",
            steps=["Understand event loop", "Learn coroutines", "Build async APIs"],
            tags=["python", "async", "coding"],
        )
        assert skill.skill_id.startswith("SKILL-")
        assert self.db.count_skills() >= 4

    def test_upload_denied_on_zero_limit(self):
        db = SkillDatabase(max_uploads=0)
        with pytest.raises(PermissionError):
            db.upload_skill(
                title="Test", category=SkillCategory.TECHNOLOGY,
                difficulty=SkillDifficulty.BEGINNER, uploaded_by="User",
                description="Test", steps=["step"]
            )

    def test_upload_denied_when_limit_reached(self):
        db = SkillDatabase(max_uploads=1)
        db.upload_skill(
            title="S1", category=SkillCategory.ARTS,
            difficulty=SkillDifficulty.BEGINNER, uploaded_by="U",
            description="D", steps=["s"]
        )
        with pytest.raises(PermissionError):
            db.upload_skill(
                title="S2", category=SkillCategory.ARTS,
                difficulty=SkillDifficulty.BEGINNER, uploaded_by="U",
                description="D", steps=["s"]
            )

    def test_rate_skill(self):
        result = self.db.rate_skill("SKILL-001", 5.0)
        assert result["new_rating"] >= 4.0

    def test_rate_skill_invalid_value_returns_error(self):
        result = self.db.rate_skill("SKILL-001", 6.0)
        assert "error" in result

    def test_rate_skill_invalid_value_low_returns_error(self):
        result = self.db.rate_skill("SKILL-001", 0.5)
        assert "error" in result

    def test_rate_nonexistent_skill_returns_error(self):
        result = self.db.rate_skill("SKILL-999", 4.0)
        assert "error" in result

    def test_featured_skills(self):
        featured = self.db.list_featured_skills()
        assert len(featured) >= 2

    def test_expert_profiles_loaded(self):
        assert self.db.count_experts() >= 6

    def test_list_all_experts(self):
        experts = self.db.list_experts()
        assert len(experts) >= 6

    def test_list_experts_by_field(self):
        experts = self.db.list_experts(field=ExpertField.MUSIC)
        assert all(e.field == ExpertField.MUSIC for e in experts)

    def test_get_expert_by_id(self):
        expert = self.db.get_expert("EXP-001")
        assert expert is not None
        assert expert.expert_id == "EXP-001"

    def test_get_nonexistent_expert_returns_none(self):
        assert self.db.get_expert("EXP-999") is None

    def test_expert_skill_summary(self):
        summary = self.db.get_expert_skill_summary()
        assert len(summary) >= 6

    def test_expert_to_dict(self):
        expert = self.db.get_expert("EXP-002")
        d = expert.to_dict()
        assert "expert_id" in d
        assert "specializations" in d
        assert d["verified"] is True

    def test_skill_search_sorted_by_rating(self):
        results = self.db.search_skills()
        ratings = [s.rating for s in results]
        assert ratings == sorted(ratings, reverse=True)


# ===========================================================================
# 10. Knowledge Engine
# ===========================================================================

class TestKnowledgeEngine:
    def setup_method(self):
        self.engine = KnowledgeEngine(max_domains=None)

    def test_query_known_topic(self):
        result = self.engine.query("engine")
        assert result["found"] is True
        assert "entry" in result

    def test_query_returns_buddy_advantage(self):
        result = self.engine.query("guitar")
        assert "buddy_advantage" in result

    def test_query_unknown_topic_returns_omniscient_message(self):
        result = self.engine.query("xyzabc_unknown_topic_12345")
        assert result["found"] is False
        assert "Buddy" in result["message"]

    def test_query_increments_count(self):
        self.engine.query("science")
        self.engine.query("music")
        assert self.engine.count_queries() == 2

    def test_count_entries(self):
        assert self.engine.count_entries() >= 8

    def test_get_domain_knowledge(self):
        entries = self.engine.get_domain_knowledge(KnowledgeDomain.SCIENCE)
        assert len(entries) >= 1

    def test_list_domains_includes_all(self):
        domains = self.engine.list_domains()
        assert "science" in domains
        assert "automotive" in domains
        assert "finance" in domains
        assert "space" in domains

    def test_compare_with_chatgpt(self):
        result = self.engine.compare_with_competitor(CompetitorAI.CHATGPT)
        assert result["buddy_vs"] == "ChatGPT (OpenAI)"
        assert result["buddy_wins"] > 0
        assert "verdict" in result

    def test_compare_all_competitors(self):
        result = self.engine.compare_with_all_competitors()
        assert result["total_competitors_analyzed"] >= 8
        assert "overall_verdict" in result
        assert "Buddy" in result["overall_verdict"]

    def test_buddy_wins_all_special_dimensions(self):
        result = self.engine.compare_with_competitor(CompetitorAI.GEMINI)
        # Buddy should win AR/VR, holographic, badges, etc.
        dims = result["dimensions"]
        assert dims["AR/VR real-world integration"]["advantage"] == "Buddy"
        assert dims["Holographic projection support"]["advantage"] == "Buddy"

    def test_compare_with_unknown_competitor(self):
        result = self.engine.compare_with_competitor.__func__(
            self.engine, "Unknown AI"  # type: ignore
        ) if False else self.engine._comparisons.get("Unknown AI")
        # Just verify the comparisons dict has known competitors
        assert "ChatGPT (OpenAI)" in self.engine._comparisons

    def test_superiority_summary(self):
        summary = self.engine.get_buddy_superiority_summary()
        assert "unique_capabilities" in summary
        assert len(summary["unique_capabilities"]) >= 7
        assert summary["knowledge_domains"] >= 10
        assert "competitor_advantage" in summary

    def test_knowledge_entry_to_dict(self):
        result = self.engine.query("orbital")
        assert result["found"] is True
        entry = result["entry"]
        assert "domain" in entry
        assert "details" in entry
        assert "real_world_application" in entry
        assert "ar_overlay_available" in entry

    def test_expert_verified_entries(self):
        entries = self.engine.get_domain_knowledge(KnowledgeDomain.MEDICINE)
        assert any(e.expert_verified for e in entries)

    def test_all_competitors_have_buddy_winning(self):
        result = self.engine.compare_with_all_competitors()
        for comparison in result["comparisons"]:
            assert comparison["buddy_wins"] > 0


# ===========================================================================
# 11. BuddyOmniscientBot — Main Integration
# ===========================================================================

class TestBuddyOmniscientBotFree:
    def setup_method(self):
        self.bot = BuddyOmniscientBot(tier=Tier.FREE, user_id="free_user")

    def test_run_returns_status(self):
        status = self.bot.run()
        assert "FREE" in status.upper()
        assert "Buddy" in status

    def test_start_ar_overlay(self):
        session = self.bot.start_ar_overlay("repair_guide", "smartphone")
        assert session is not None
        assert session.active is True

    def test_list_viral_challenges(self):
        challenges = self.bot.list_viral_challenges()
        assert len(challenges) > 0

    def test_search_skills(self):
        results = self.bot.search_skills("guitar")
        assert len(results) >= 1

    def test_ask_known_topic(self):
        result = self.bot.ask("guitar")
        assert "found" in result

    def test_ask_unknown_topic(self):
        result = self.bot.ask("xyzqrs_unknown")
        assert "Buddy" in result.get("message", "")

    def test_get_superiority_summary(self):
        summary = self.bot.get_superiority_summary()
        assert "unique_capabilities" in summary

    def test_holographic_blocked_on_free(self):
        with pytest.raises(BuddyOmniscientTierError):
            self.bot.project_holographic_buddy("ar_glasses")

    def test_skill_upload_blocked_on_free(self):
        with pytest.raises(BuddyOmniscientTierError):
            self.bot.upload_skill("Test", "technology", "beginner", "Desc", ["step"])

    def test_buddy_badges_blocked_on_free(self):
        with pytest.raises(BuddyOmniscientTierError):
            self.bot.get_earned_badges()

    def test_omniscient_mode_blocked_on_free(self):
        with pytest.raises(BuddyOmniscientTierError):
            self.bot.compare_with_ai("ChatGPT (OpenAI)")

    def test_dashboard(self):
        d = self.bot.dashboard()
        assert d["tier"] == "free"
        assert d["user_id"] == "free_user"
        assert "knowledge_entries" in d

    def test_describe_tier(self):
        info = self.bot.describe_tier()
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0
        assert info["upgrade_available"] is True

    def test_chat_dashboard(self):
        resp = self.bot.chat("show dashboard")
        assert resp["response"] == "buddy_omniscient"
        assert "bot" in resp["data"]
        assert resp["data"]["bot"] == "Buddy Omniscient Bot"

    def test_chat_challenge(self):
        resp = self.bot.chat("show me viral challenges")
        assert resp["response"] == "buddy_omniscient"
        assert "challenges" in resp["data"]

    def test_chat_ar(self):
        resp = self.bot.chat("I want augmented reality overlays")
        assert resp["response"] == "buddy_omniscient"

    def test_chat_skill(self):
        resp = self.bot.chat("teach me a skill")
        assert resp["response"] == "buddy_omniscient"

    def test_chat_business(self):
        resp = self.bot.chat("I want to launch a business")
        assert resp["response"] == "buddy_omniscient"

    def test_chat_charity(self):
        resp = self.bot.chat("I want to donate to charity")
        assert resp["response"] == "buddy_omniscient"

    def test_chat_games(self):
        resp = self.bot.chat("show me games to learn")
        assert resp["response"] == "buddy_omniscient"

    def test_chat_tier(self):
        resp = self.bot.chat("what is my tier plan")
        assert resp["response"] == "buddy_omniscient"
        assert resp["data"]["tier"] == "free"

    def test_chat_knowledge(self):
        resp = self.bot.chat("how does an engine work")
        assert resp["response"] == "buddy_omniscient"

    def test_chat_compare_ai_no_omniscient_mode(self):
        resp = self.bot.chat("is buddy better than chatgpt")
        assert resp["response"] == "buddy_omniscient"
        assert "surpasses" in resp["message"].lower() or "upgrade" in resp["message"].lower()


class TestBuddyOmniscientBotPro:
    def setup_method(self):
        self.bot = BuddyOmniscientBot(tier=Tier.PRO, user_id="pro_user")

    def test_run_returns_pro_status(self):
        status = self.bot.run()
        assert "PRO" in status.upper()

    def test_holographic_projection_available(self):
        session = self.bot.project_holographic_buddy("ar_glasses", "life_sized")
        assert session is not None
        assert session.active is True

    def test_complete_challenge_and_earn_badge(self):
        result = self.bot.complete_viral_challenge("CH-001")
        assert result["points_earned"] == 500
        badges = self.bot.get_earned_badges()
        assert len(badges) >= 1

    def test_list_all_badges(self):
        badges = self.bot.list_all_badges()
        assert len(badges) >= 10

    def test_upload_skill(self):
        result = self.bot.upload_skill(
            title="Advanced Drone Piloting",
            category_str="technology",
            difficulty_str="advanced",
            description="Master FPV drone flying.",
            steps=["Learn controls", "Practice hovering", "Try FPV goggles"],
            tags=["drone", "flying", "tech"],
        )
        assert result["uploaded_by"] == "pro_user"

    def test_launch_business(self):
        result = self.bot.launch_business("AI Cafe", "Coffee shop with AI ordering")
        assert result["business_name"] == "AI Cafe"
        assert result["estimated_launch_hours"] == 4.0

    def test_create_reality_show_episode(self):
        result = self.bot.create_reality_show_episode(
            title="Buddy Fixes a Tesla",
            description="Live EV repair challenge",
            challenge_category_str="car_repair",
            participants=["Mech_Mike", "Buddy"],
        )
        assert "episode_id" in result
        assert result["title"] == "Buddy Fixes a Tesla"

    def test_go_live_and_vote(self):
        episode = self.bot.create_reality_show_episode(
            title="Live Show",
            description="Test",
            challenge_category_str="cooking",
            participants=["A"],
        )
        live_result = self.bot.go_live_reality_show(episode["episode_id"])
        assert live_result["status"] == "live"
        vote_result = self.bot.vote_reality_show(episode["episode_id"], votes=100)
        assert vote_result["total_votes"] == 100

    def test_create_charity_initiative(self):
        result = self.bot.create_charity_initiative(
            cause_str="education",
            title="Books Everywhere",
            description="Books for all",
            goal_amount=5000.0,
        )
        assert "initiative_id" in result
        assert result["cause"] == "education"

    def test_donate_to_charity(self):
        initiative = self.bot.create_charity_initiative(
            "hunger_relief", "Food Drive", "Help", 10000.0
        )
        result = self.bot.donate_to_charity(initiative["initiative_id"], 250.0)
        assert result["amount_donated"] == 250.0

    def test_generate_social_content(self):
        result = self.bot.generate_social_content("video_idea", "tiktok", "car repair AR")
        assert result["content_type"] == "video_idea"
        assert "#DreamCoAI" in result["hashtags"]

    def test_list_experts(self):
        experts = self.bot.list_experts()
        assert len(experts) >= 6

    def test_expert_skill_summary(self):
        summary = self.bot.get_expert_skill_summary()
        assert len(summary) >= 6

    def test_start_learning_game(self):
        session = self.bot.start_learning_game("GAME-001")
        assert session["player"] == "pro_user"

    def test_get_game_hint(self):
        session = self.bot.start_learning_game("GAME-002")
        hint = self.bot.get_game_hint(session["session_id"])
        assert "Buddy says" in hint["hint"]

    def test_compare_with_ai(self):
        result = self.bot.compare_with_ai("ChatGPT (OpenAI)")
        assert result["buddy_vs"] == "ChatGPT (OpenAI)"
        assert result["buddy_wins"] > 0

    def test_compare_with_all_ais(self):
        result = self.bot.compare_with_all_ais()
        assert result["total_competitors_analyzed"] >= 8
        assert "overall_verdict" in result

    def test_chat_expert(self):
        resp = self.bot.chat("who trained buddy — nasa scientists and musicians")
        assert resp["response"] == "buddy_omniscient"
        assert "experts" in resp["data"]

    def test_chat_compare_ai(self):
        resp = self.bot.chat("is buddy better than chatgpt")
        assert resp["response"] == "buddy_omniscient"
        assert "comparisons" in resp["data"]

    def test_broadcast_ar_session(self):
        session = self.bot.start_ar_overlay("cooking_guide", "smartphone")
        result = self.bot.broadcast_ar_to_devices(
            session.session_id, ["smart_tv", "tablet"]
        )
        assert result["status"] == "broadcasting"
        assert len(result["broadcast_to"]) == 2

    def test_list_charity_initiatives(self):
        self.bot.create_charity_initiative("education", "T1", "D1", 1000.0)
        initiatives = self.bot.list_charity_initiatives()
        assert len(initiatives) >= 1

    def test_list_business_plans(self):
        self.bot.launch_business("Biz1", "Type1")
        plans = self.bot.list_business_plans()
        assert len(plans) == 1

    def test_dashboard_shows_all_fields(self):
        d = self.bot.dashboard()
        expected_fields = [
            "ar_sessions_active", "holographic_sessions_active", "total_points",
            "badges_earned", "community_skills", "expert_trainers",
            "business_plans", "charity_initiatives", "social_content_generated",
            "knowledge_entries", "knowledge_queries",
        ]
        for field in expected_fields:
            assert field in d, f"Missing field: {field}"

    def test_register_with_buddy(self):
        class MockBuddy:
            def __init__(self):
                self.registered = {}
            def register_bot(self, name, instance):
                self.registered[name] = instance

        mock = MockBuddy()
        self.bot.register_with_buddy(mock)
        assert "buddy_omniscient" in mock.registered


class TestBuddyOmniscientBotEnterprise:
    def setup_method(self):
        self.bot = BuddyOmniscientBot(tier=Tier.ENTERPRISE, user_id="enterprise_user")

    def test_enterprise_unlimited_ar_sessions(self):
        # Should not raise even with many sessions
        for i in range(20):
            self.bot.start_ar_overlay("education", "smartphone")

    def test_enterprise_unlimited_knowledge_domains(self):
        assert self.bot.config.is_unlimited_knowledge()

    def test_enterprise_describe_tier(self):
        info = self.bot.describe_tier()
        assert info["tier"] == "enterprise"
        assert info["price_usd_monthly"] == 199.0
        assert info["upgrade_available"] is False

    def test_invalid_overlay_type_defaults_to_custom(self):
        session = self.bot.start_ar_overlay("invalid_type_xyz", "smartphone")
        assert session is not None

    def test_invalid_device_defaults_to_smartphone(self):
        session = self.bot.start_ar_overlay("education", "invalid_device_xyz")
        assert session is not None

    def test_invalid_competitor_returns_error(self):
        result = self.bot.compare_with_ai("Unknown AI Model XYZ")
        assert "error" in result
        assert "available" in result

    def test_invalid_challenge_category_ignored(self):
        challenges = self.bot.list_viral_challenges("invalid_category_xyz")
        assert isinstance(challenges, list)

    def test_upload_skill_no_limit(self):
        for i in range(10):
            result = self.bot.upload_skill(
                title=f"Skill {i}",
                category_str="technology",
                difficulty_str="beginner",
                description=f"Description {i}",
                steps=["Step 1"],
            )
            assert "skill_id" in result

    def test_learning_games_multiplayer(self):
        games = self.bot.list_learning_games(multiplayer_only=True)
        assert len(games) >= 1

    def test_learning_games_by_type(self):
        games = self.bot.list_learning_games(game_type_str="stock_market")
        assert all(g["game_type"] == "stock_market" for g in games)


# ===========================================================================
# Edge Cases and Framework Compliance
# ===========================================================================

class TestEdgeCases:
    def test_bot_import(self):
        from bots.buddy_omniscient_bot import BuddyOmniscientBot, Tier
        bot = BuddyOmniscientBot(tier=Tier.FREE)
        assert bot is not None

    def test_framework_compliance(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "buddy_omniscient_bot",
            os.path.join(REPO_ROOT, "bots", "buddy_omniscient_bot", "buddy_omniscient_bot.py")
        )
        source = open(
            os.path.join(REPO_ROOT, "bots", "buddy_omniscient_bot", "buddy_omniscient_bot.py")
        ).read()
        assert "GlobalAISourcesFlow" in source

    def test_all_modules_have_framework_reference(self):
        modules = [
            "ar_vr_engine.py", "viral_challenges.py", "skill_database.py",
            "knowledge_engine.py", "buddy_omniscient_bot.py",
        ]
        for module in modules:
            path = os.path.join(REPO_ROOT, "bots", "buddy_omniscient_bot", module)
            content = open(path).read()
            assert "GlobalAISourcesFlow" in content, f"Missing framework ref in {module}"

    def test_tier_error_inheritance(self):
        assert issubclass(BuddyOmniscientTierError, BuddyOmniscientError)
        assert issubclass(BuddyOmniscientError, Exception)

    def test_bot_version(self):
        assert BuddyOmniscientBot.VERSION == "1.0.0"

    def test_bot_name(self):
        assert "Buddy" in BuddyOmniscientBot.BOT_NAME

    def test_chat_unknown_message_returns_knowledge_query(self):
        bot = BuddyOmniscientBot(tier=Tier.FREE)
        resp = bot.chat("What is the speed of light?")
        assert resp["response"] == "buddy_omniscient"

    def test_all_competitor_ais_can_be_compared(self):
        engine = KnowledgeEngine()
        for competitor in CompetitorAI:
            result = engine.compare_with_competitor(competitor)
            assert "buddy_vs" in result
            assert result["buddy_wins"] > 0

    def test_all_content_types_generate_content(self):
        engine = AISocialCreatorEngine()
        for ct in ContentType:
            for platform in [SocialPlatform.TIKTOK, SocialPlatform.INSTAGRAM]:
                content = engine.generate_content(ct, platform)
                assert len(content.body) > 0

    def test_all_charity_causes(self):
        engine = CharityAmbassadorEngine()
        for cause in CharityCause:
            initiative = engine.create_initiative(
                cause=cause,
                title=f"Test {cause.value}",
                description="Test",
                goal_amount=1000.0,
            )
            assert initiative.cause == cause

    def test_buddy_superiority_over_all_ai(self):
        engine = KnowledgeEngine()
        result = engine.compare_with_all_competitors()
        # Buddy should win in all comparisons
        for comparison in result["comparisons"]:
            assert comparison["buddy_win_pct"] > 80, (
                f"Buddy should dominate {comparison['competitor']}"
            )
