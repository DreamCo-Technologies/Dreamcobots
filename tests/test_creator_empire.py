"""
Tests for the CreatorEmpire bot.

Covers:
  - bots/creator_empire/tiers.py        (tier config + feature flags)
  - bots/creator_empire/onboarding.py   (OnboardingEngine)
  - bots/creator_empire/streamer.py     (StreamerEngine)
  - bots/creator_empire/event_planning.py (EventPlanningEngine)
  - bots/creator_empire/monetization.py  (MonetizationEngine)
  - bots/creator_empire/creator_empire.py (CreatorEmpireBot)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest

from tiers import Tier
from bots.creator_empire.tiers import (
    get_creator_tier_info,
    CREATOR_ROLES,
    CREATOR_FEATURES_BY_TIER,
    MONETIZATION_MODELS_BY_TIER,
    FEATURE_BASIC_PROFILE,
    FEATURE_ROLE_ONBOARDING,
    FEATURE_STREAM_SETUP,
    FEATURE_EVENT_PLANNER,
    FEATURE_MONETIZATION_BASIC,
    FEATURE_MONETIZATION_ADVANCED,
    FEATURE_SPONSORSHIP_TOOLS,
)
from bots.creator_empire.onboarding import OnboardingEngine, OnboardingError
from bots.creator_empire.streamer import (
    StreamerEngine, StreamerError,
    STREAMING_PLATFORMS, GO_LIVE_CHECKLIST,
)
from bots.creator_empire.event_planning import (
    EventPlanningEngine, EventError,
    EVENT_TYPES, EVENT_STATUS_PLANNED, EVENT_STATUS_PROMOTED,
    EVENT_STATUS_LIVE, EVENT_STATUS_COMPLETED, EVENT_STATUS_CANCELLED,
)
from bots.creator_empire.monetization import (
    MonetizationEngine, MonetizationError, REVENUE_MODEL_INFO,
)
from bots.creator_empire.creator_empire import CreatorEmpireBot


# ===========================================================================
# Tier configuration tests
# ===========================================================================

class TestCreatorTiers:
    def test_tier_info_keys(self):
        for tier in Tier:
            info = get_creator_tier_info(tier)
            for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                        "platform_features", "creator_features",
                        "monetization_models", "support_level"):
                assert key in info, f"Missing key '{key}' for {tier}"

    def test_free_price_is_zero(self):
        assert get_creator_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_pro_price(self):
        assert get_creator_tier_info(Tier.PRO)["price_usd_monthly"] == 49.0

    def test_enterprise_unlimited_requests(self):
        assert get_creator_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_free_has_basic_profile_feature(self):
        assert FEATURE_BASIC_PROFILE in CREATOR_FEATURES_BY_TIER[Tier.FREE.value]

    def test_pro_has_stream_setup_feature(self):
        assert FEATURE_STREAM_SETUP in CREATOR_FEATURES_BY_TIER[Tier.PRO.value]

    def test_enterprise_has_sponsorship_tools(self):
        assert FEATURE_SPONSORSHIP_TOOLS in CREATOR_FEATURES_BY_TIER[Tier.ENTERPRISE.value]

    def test_free_lacks_event_planner(self):
        assert FEATURE_EVENT_PLANNER not in CREATOR_FEATURES_BY_TIER[Tier.FREE.value]

    def test_enterprise_features_superset_of_pro(self):
        pro = set(CREATOR_FEATURES_BY_TIER[Tier.PRO.value])
        ent = set(CREATOR_FEATURES_BY_TIER[Tier.ENTERPRISE.value])
        assert pro.issubset(ent)

    def test_free_monetization_models_subset_of_pro(self):
        free = set(MONETIZATION_MODELS_BY_TIER[Tier.FREE.value])
        pro = set(MONETIZATION_MODELS_BY_TIER[Tier.PRO.value])
        assert free.issubset(pro)

    def test_enterprise_monetization_includes_brand_deal(self):
        assert "brand_deal" in MONETIZATION_MODELS_BY_TIER[Tier.ENTERPRISE.value]

    def test_creator_roles_is_non_empty_list(self):
        assert isinstance(CREATOR_ROLES, list)
        assert len(CREATOR_ROLES) > 0

    def test_streamer_role_in_creator_roles(self):
        assert "streamer" in CREATOR_ROLES

    def test_rapper_role_in_creator_roles(self):
        assert "rapper" in CREATOR_ROLES

    def test_athlete_role_in_creator_roles(self):
        assert "athlete" in CREATOR_ROLES


# ===========================================================================
# Onboarding engine tests
# ===========================================================================

class TestOnboardingEngine:
    def setup_method(self):
        self.engine = OnboardingEngine(tier=Tier.FREE)

    def test_create_profile_returns_profile(self):
        profile = self.engine.create_profile("Alex", role="streamer")
        assert profile.name == "Alex"
        assert profile.role == "streamer"

    def test_create_profile_role_normalised(self):
        profile = self.engine.create_profile("BobRap", role="  RAPPER  ")
        assert profile.role == "rapper"

    def test_create_profile_unsupported_role_raises(self):
        with pytest.raises(OnboardingError):
            self.engine.create_profile("X", role="unicorn_rider")

    def test_create_profile_duplicate_name_raises(self):
        self.engine.create_profile("Alex", role="streamer")
        with pytest.raises(OnboardingError):
            self.engine.create_profile("Alex", role="rapper")

    def test_profile_has_default_goals(self):
        profile = self.engine.create_profile("Jay", role="streamer")
        assert len(profile.goals) > 0

    def test_profile_custom_goals(self):
        profile = self.engine.create_profile(
            "Jay", role="streamer", goals=["win championship"]
        )
        assert profile.goals == ["win championship"]

    def test_profile_has_default_platforms(self):
        profile = self.engine.create_profile("Jay2", role="streamer")
        assert "twitch" in profile.platforms

    def test_complete_onboarding_sets_flag(self):
        self.engine.create_profile("Dana", role="athlete")
        result = self.engine.complete_onboarding("Dana")
        assert result["profile"]["onboarding_complete"] is True

    def test_complete_onboarding_returns_action_plan(self):
        self.engine.create_profile("Dana2", role="athlete")
        result = self.engine.complete_onboarding("Dana2")
        assert isinstance(result["action_plan"], list)
        assert len(result["action_plan"]) > 0

    def test_get_action_plan_streamer(self):
        plan = self.engine.get_action_plan("streamer")
        assert any("stream" in step.lower() or "niche" in step.lower() for step in plan)

    def test_get_action_plan_unsupported_role_raises(self):
        with pytest.raises(OnboardingError):
            self.engine.get_action_plan("unknown_role")

    def test_list_profiles_empty_initially(self):
        engine = OnboardingEngine(tier=Tier.FREE)
        assert engine.list_profiles() == []

    def test_list_profiles_after_creation(self):
        self.engine.create_profile("C1", role="streamer")
        self.engine.create_profile("C2", role="rapper")
        profiles = self.engine.list_profiles()
        assert len(profiles) == 2

    def test_get_profile_returns_correct_profile(self):
        self.engine.create_profile("Eve", role="content_creator")
        p = self.engine.get_profile("Eve")
        assert p.role == "content_creator"

    def test_get_profile_not_found_raises(self):
        with pytest.raises(OnboardingError):
            self.engine.get_profile("Ghost")

    def test_update_profile_bio(self):
        self.engine.create_profile("Fred", role="gamer")
        updated = self.engine.update_profile("Fred", bio="Pro gamer & streamer")
        assert updated.bio == "Pro gamer & streamer"

    def test_update_profile_invalid_field_raises(self):
        self.engine.create_profile("Greg", role="dancer")
        with pytest.raises(OnboardingError):
            self.engine.update_profile("Greg", role="rapper")

    def test_profile_to_dict_has_all_keys(self):
        profile = self.engine.create_profile("Hank", role="podcaster")
        d = profile.to_dict()
        for key in ("name", "role", "bio", "goals", "platforms",
                    "tier", "onboarding_complete", "metadata"):
            assert key in d

    def test_all_roles_have_action_plans(self):
        for role in CREATOR_ROLES:
            plan = self.engine.get_action_plan(role)
            assert len(plan) > 0, f"No action plan for role '{role}'"


# ===========================================================================
# Streamer engine tests
# ===========================================================================

class TestStreamerEngine:
    def setup_method(self):
        self.engine = StreamerEngine(tier=Tier.PRO)

    def test_setup_stream_returns_config(self):
        cfg = self.engine.setup_stream("Alex", platform="twitch", niche="gaming")
        assert cfg.creator_name == "Alex"
        assert cfg.platform == "twitch"

    def test_setup_stream_normalises_platform(self):
        cfg = self.engine.setup_stream("Alex2", platform="  TWITCH  ", niche="gaming")
        assert cfg.platform == "twitch"

    def test_setup_stream_invalid_platform_raises(self):
        with pytest.raises(StreamerError):
            self.engine.setup_stream("Alex3", platform="myspace")

    def test_get_go_live_checklist_returns_list(self):
        checklist = self.engine.get_go_live_checklist()
        assert isinstance(checklist, list)
        assert len(checklist) > 0

    def test_go_live_checklist_mentions_audio(self):
        checklist = self.engine.get_go_live_checklist()
        assert any("audio" in item.lower() for item in checklist)

    def test_get_monetisation_milestones_twitch(self):
        milestones = self.engine.get_monetisation_milestones("twitch")
        assert len(milestones) >= 1
        assert "milestone" in milestones[0]

    def test_get_monetisation_milestones_invalid_platform_raises(self):
        with pytest.raises(StreamerError):
            self.engine.get_monetisation_milestones("badplatform")

    def test_enable_monetisation_sets_flag(self):
        self.engine.setup_stream("Bob", platform="youtube", niche="music")
        cfg = self.engine.enable_monetisation("Bob")
        assert cfg.monetisation_enabled is True

    def test_configure_overlay_sets_flag(self):
        self.engine.setup_stream("Carol", platform="kick", niche="gaming")
        cfg = self.engine.configure_overlay("Carol")
        assert cfg.overlay_configured is True

    def test_configure_overlay_stores_metadata(self):
        self.engine.setup_stream("Dave", platform="twitch", niche="irl")
        cfg = self.engine.configure_overlay("Dave", metadata={"theme": "dark"})
        assert cfg.metadata.get("theme") == "dark"

    def test_get_stream_config_not_found_raises(self):
        with pytest.raises(StreamerError):
            self.engine.get_stream_config("Nobody")

    def test_list_configs_after_setup(self):
        self.engine.setup_stream("Eve2", platform="twitch", niche="fitness")
        configs = self.engine.list_configs()
        assert any(c["creator_name"] == "Eve2" for c in configs)

    def test_get_optimisation_tips_gaming(self):
        tips = self.engine.get_optimisation_tips("gaming")
        assert isinstance(tips, list)
        assert len(tips) > 0

    def test_get_optimisation_tips_unknown_niche_returns_defaults(self):
        tips = self.engine.get_optimisation_tips("underwater_basket_weaving")
        assert isinstance(tips, list)
        assert len(tips) > 0

    def test_free_tier_cannot_setup_stream(self):
        free_engine = StreamerEngine(tier=Tier.FREE)
        with pytest.raises(StreamerError):
            free_engine.setup_stream("Fiona", platform="twitch", niche="gaming")

    def test_all_platforms_listed(self):
        for platform in STREAMING_PLATFORMS:
            milestones = self.engine.get_monetisation_milestones(platform)
            assert isinstance(milestones, list)


# ===========================================================================
# Event planning engine tests
# ===========================================================================

class TestEventPlanningEngine:
    def setup_method(self):
        self.engine = EventPlanningEngine(tier=Tier.PRO)

    def _make_event(self, creator="Alex", title="Test Show",
                    event_type="live_show", date="2025-08-15",
                    venue="The Venue"):
        return self.engine.create_event(creator, title, event_type, date, venue)

    def test_create_event_returns_event(self):
        event = self._make_event()
        assert event.creator_name == "Alex"
        assert event.event_type == "live_show"

    def test_create_event_assigns_id(self):
        event = self._make_event()
        assert event.event_id.startswith("evt_")

    def test_create_event_invalid_type_raises(self):
        with pytest.raises(EventError):
            self.engine.create_event("Alex", "Bad", "rave_party", "2025-01-01", "Club")

    def test_event_starts_in_planned_status(self):
        event = self._make_event()
        assert event.status == EVENT_STATUS_PLANNED

    def test_advance_status_planned_to_promoted(self):
        event = self._make_event()
        event = self.engine.advance_status(event.event_id)
        assert event.status == EVENT_STATUS_PROMOTED

    def test_advance_status_promoted_to_live(self):
        event = self._make_event()
        self.engine.advance_status(event.event_id)
        event = self.engine.advance_status(event.event_id)
        assert event.status == EVENT_STATUS_LIVE

    def test_advance_status_live_to_completed(self):
        event = self._make_event()
        for _ in range(3):
            event = self.engine.advance_status(event.event_id)
        assert event.status == EVENT_STATUS_COMPLETED

    def test_advance_status_completed_raises(self):
        event = self._make_event()
        for _ in range(3):
            self.engine.advance_status(event.event_id)
        with pytest.raises(EventError):
            self.engine.advance_status(event.event_id)

    def test_cancel_event(self):
        event = self._make_event()
        event = self.engine.cancel_event(event.event_id)
        assert event.status == EVENT_STATUS_CANCELLED

    def test_cancel_completed_event_raises(self):
        event = self._make_event()
        for _ in range(3):
            self.engine.advance_status(event.event_id)
        with pytest.raises(EventError):
            self.engine.cancel_event(event.event_id)

    def test_event_has_tasks(self):
        event = self._make_event()
        assert len(event.tasks) > 0

    def test_complete_task_marks_done(self):
        event = self._make_event()
        assert event.tasks[0].startswith("todo:")
        event = self.engine.complete_task(event.event_id, 0)
        assert event.tasks[0].startswith("done:")

    def test_complete_task_invalid_index_raises(self):
        event = self._make_event()
        with pytest.raises(EventError):
            self.engine.complete_task(event.event_id, 9999)

    def test_add_sponsor(self):
        event = self._make_event()
        event = self.engine.add_sponsor(event.event_id, "Nike")
        assert "Nike" in event.sponsors

    def test_add_sponsor_not_duplicated(self):
        event = self._make_event()
        self.engine.add_sponsor(event.event_id, "Nike")
        event = self.engine.add_sponsor(event.event_id, "Nike")
        assert event.sponsors.count("Nike") == 1

    def test_list_events_returns_all(self):
        self._make_event(creator="Alice", title="Show 1")
        self._make_event(creator="Bob", title="Show 2")
        events = self.engine.list_events()
        assert len(events) >= 2

    def test_list_events_filtered_by_creator(self):
        self._make_event(creator="Alice2", title="Show A")
        self._make_event(creator="Bob2", title="Show B")
        events = self.engine.list_events(creator_name="Alice2")
        assert all(e["creator_name"] == "Alice2" for e in events)

    def test_get_pending_tasks(self):
        event = self._make_event()
        pending = self.engine.get_pending_tasks(event.event_id)
        assert len(pending) > 0

    def test_pending_tasks_decrease_after_completion(self):
        event = self._make_event()
        before = len(self.engine.get_pending_tasks(event.event_id))
        self.engine.complete_task(event.event_id, 0)
        after = len(self.engine.get_pending_tasks(event.event_id))
        assert after == before - 1

    def test_free_tier_cannot_create_event(self):
        free_engine = EventPlanningEngine(tier=Tier.FREE)
        with pytest.raises(EventError):
            free_engine.create_event("X", "Y", "live_show", "2025-01-01", "Z")

    def test_all_event_types_accepted(self):
        for event_type in EVENT_TYPES:
            event = self.engine.create_event(
                "Creator", f"Event: {event_type}",
                event_type, "2025-09-01", "Venue"
            )
            assert event.event_type == event_type

    def test_event_to_dict_has_all_keys(self):
        event = self._make_event()
        d = event.to_dict()
        for key in ("event_id", "creator_name", "title", "event_type", "date",
                    "venue_or_platform", "capacity", "ticket_price_usd",
                    "status", "sponsors", "tasks", "metadata"):
            assert key in d

    def test_event_not_found_raises(self):
        with pytest.raises(EventError):
            self.engine.get_event("evt_9999")


# ===========================================================================
# Monetization engine tests
# ===========================================================================

class TestMonetizationEngine:
    def setup_method(self):
        self.engine = MonetizationEngine(tier=Tier.PRO)

    def test_enable_model_tip_jar(self):
        info = self.engine.enable_model("Alex", "tip_jar")
        assert info["id"] == "tip_jar"

    def test_enable_model_not_on_free_tier_raises(self):
        free_engine = MonetizationEngine(tier=Tier.FREE)
        with pytest.raises(MonetizationError):
            free_engine.enable_model("Alex", "subscription_premium")

    def test_enable_model_unknown_raises(self):
        with pytest.raises(MonetizationError):
            self.engine.enable_model("Alex", "magic_money")

    def test_disable_model(self):
        self.engine.enable_model("Alex", "tip_jar")
        self.engine.disable_model("Alex", "tip_jar")
        active = self.engine.get_active_models("Alex")
        assert not any(m["id"] == "tip_jar" for m in active)

    def test_get_active_models_empty_initially(self):
        assert self.engine.get_active_models("NewCreator") == []

    def test_get_active_models_after_enable(self):
        self.engine.enable_model("Bob", "tip_jar")
        self.engine.enable_model("Bob", "subscription_basic")
        active = self.engine.get_active_models("Bob")
        assert len(active) == 2

    def test_enable_model_no_duplicate(self):
        self.engine.enable_model("Carol", "tip_jar")
        self.engine.enable_model("Carol", "tip_jar")
        assert len(self.engine.get_active_models("Carol")) == 1

    def test_get_available_models_on_pro(self):
        models = self.engine.get_available_models()
        ids = [m["id"] for m in models]
        assert "tip_jar" in ids
        assert "subscription_premium" in ids

    def test_get_model_info_has_keys(self):
        info = self.engine.get_model_info("tip_jar")
        for key in ("id", "display_name", "description", "payment_types", "platforms"):
            assert key in info

    def test_record_revenue_returns_entry(self):
        entry = self.engine.record_revenue("Alex", "tip_jar", 10.0, "streamlabs")
        assert entry.amount_usd == 10.0
        assert entry.creator_name == "Alex"

    def test_record_revenue_negative_raises(self):
        with pytest.raises(MonetizationError):
            self.engine.record_revenue("Alex", "tip_jar", -5.0, "ko-fi")

    def test_get_total_revenue_sum(self):
        self.engine.record_revenue("Dana", "tip_jar", 10.0, "ko-fi")
        self.engine.record_revenue("Dana", "subscription_basic", 5.0, "patreon")
        assert self.engine.get_total_revenue("Dana") == 15.0

    def test_get_total_revenue_zero_for_new_creator(self):
        assert self.engine.get_total_revenue("NewPerson") == 0.0

    def test_get_revenue_by_model(self):
        self.engine.record_revenue("Eve3", "tip_jar", 20.0, "ko-fi")
        self.engine.record_revenue("Eve3", "tip_jar", 5.0, "streamlabs")
        self.engine.record_revenue("Eve3", "subscription_basic", 15.0, "patreon")
        breakdown = self.engine.get_revenue_by_model("Eve3")
        assert breakdown["tip_jar"] == 25.0
        assert breakdown["subscription_basic"] == 15.0

    def test_get_ledger_all_entries(self):
        self.engine.record_revenue("Fred2", "tip_jar", 1.0, "ko-fi")
        self.engine.record_revenue("Greg2", "tip_jar", 2.0, "ko-fi")
        ledger = self.engine.get_ledger()
        assert len(ledger) >= 2

    def test_get_ledger_filtered(self):
        self.engine.record_revenue("Hank2", "tip_jar", 1.0, "ko-fi")
        ledger = self.engine.get_ledger(creator_name="Hank2")
        assert all(e["creator_name"] == "Hank2" for e in ledger)

    def test_revenue_entry_ids_are_unique(self):
        e1 = self.engine.record_revenue("Iris", "tip_jar", 1.0, "ko-fi")
        e2 = self.engine.record_revenue("Iris", "tip_jar", 2.0, "ko-fi")
        assert e1.entry_id != e2.entry_id

    def test_get_monetization_strategy_streamer(self):
        strategy = self.engine.get_monetization_strategy("streamer")
        assert isinstance(strategy, list)
        assert len(strategy) > 0

    def test_get_monetization_strategy_unknown_role_returns_defaults(self):
        strategy = self.engine.get_monetization_strategy("unknown_role")
        assert isinstance(strategy, list)
        assert len(strategy) > 0

    def test_all_revenue_models_have_info(self):
        for model_id in REVENUE_MODEL_INFO:
            info = MonetizationEngine.get_model_info(model_id)
            assert info["id"] == model_id


# ===========================================================================
# CreatorEmpireBot integration tests
# ===========================================================================

class TestCreatorEmpireBot:
    def setup_method(self):
        self.bot = CreatorEmpireBot(tier=Tier.PRO)

    def test_onboard_and_complete(self):
        profile = self.bot.onboard_creator("Alex", role="streamer", bio="Gaming streamer")
        result = self.bot.complete_onboarding("Alex")
        assert result["profile"]["onboarding_complete"] is True
        assert len(result["action_plan"]) > 0

    def test_setup_stream_and_get_tips(self):
        self.bot.onboard_creator("Bob", role="streamer")
        cfg = self.bot.setup_stream("Bob", platform="twitch", niche="gaming")
        assert cfg.platform == "twitch"
        tips = self.bot.get_stream_tips("gaming")
        assert len(tips) > 0

    def test_go_live_checklist(self):
        checklist = self.bot.get_go_live_checklist()
        assert len(checklist) > 0

    def test_create_and_advance_event(self):
        event = self.bot.create_event(
            "Carol", "Summer Show", "live_show", "2025-08-01", "Madison Square Garden"
        )
        event = self.bot.advance_event_status(event.event_id)
        assert event.status == EVENT_STATUS_PROMOTED

    def test_event_sponsor_workflow(self):
        event = self.bot.create_event(
            "Dave", "DJ Night", "live_show", "2025-07-04", "Club XYZ"
        )
        event = self.bot.add_event_sponsor(event.event_id, "RedBull")
        assert "RedBull" in event.sponsors

    def test_revenue_workflow(self):
        self.bot.enable_revenue_model("Eve", "tip_jar")
        entry = self.bot.record_revenue("Eve", "tip_jar", 50.0, "streamlabs")
        assert self.bot.get_total_revenue("Eve") == 50.0

    def test_revenue_breakdown(self):
        self.bot.record_revenue("Fred", "tip_jar", 10.0, "ko-fi")
        self.bot.record_revenue("Fred", "subscription_basic", 5.0, "patreon")
        breakdown = self.bot.get_revenue_breakdown("Fred")
        assert breakdown.get("tip_jar") == 10.0
        assert breakdown.get("subscription_basic") == 5.0

    def test_describe_tier_returns_string(self):
        output = self.bot.describe_tier()
        assert "Pro" in output
        assert "49.00" in output

    def test_show_upgrade_path_from_pro(self):
        output = self.bot.show_upgrade_path()
        assert "Enterprise" in output

    def test_show_upgrade_path_from_enterprise_no_upgrade(self):
        ent_bot = CreatorEmpireBot(tier=Tier.ENTERPRISE)
        output = ent_bot.show_upgrade_path()
        assert "top-tier" in output

    def test_list_creators_after_onboard(self):
        self.bot.onboard_creator("Grace", role="rapper")
        creators = self.bot.list_creators()
        assert any(c["name"] == "Grace" for c in creators)

    def test_update_creator_profile(self):
        self.bot.onboard_creator("Hank", role="gamer")
        updated = self.bot.update_creator_profile("Hank", bio="Pro gamer")
        assert updated.bio == "Pro gamer"

    def test_get_monetisation_milestones_twitch(self):
        milestones = self.bot.get_monetisation_milestones("twitch")
        assert len(milestones) >= 1

    def test_monetization_strategy_rapper(self):
        strategy = self.bot.get_monetization_strategy("rapper")
        assert len(strategy) > 0

    def test_available_revenue_models_on_pro(self):
        models = self.bot.get_available_revenue_models()
        ids = [m["id"] for m in models]
        assert "tip_jar" in ids
        assert "merchandise" in ids

    def test_full_creator_journey(self):
        """End-to-end: onboard → stream setup → event → monetize."""
        # Onboarding
        self.bot.onboard_creator("Jordan", role="streamer", bio="Variety streamer")
        self.bot.complete_onboarding("Jordan")

        # Streaming
        cfg = self.bot.setup_stream("Jordan", platform="twitch", niche="gaming",
                                    schedule=["Mon 18:00", "Thu 18:00"])
        self.bot.enable_stream_monetisation("Jordan")
        assert cfg.platform == "twitch"

        # Event
        event = self.bot.create_event(
            "Jordan", "1 Year Anniversary Stream",
            "charity_stream", "2025-12-31", "twitch.tv/jordan"
        )
        self.bot.complete_event_task(event.event_id, 0)
        self.bot.add_event_sponsor(event.event_id, "Logitech")

        # Revenue
        self.bot.enable_revenue_model("Jordan", "subscription_basic")
        self.bot.record_revenue("Jordan", "tip_jar", 100.0, "streamlabs",
                                 "Anniversary stream tips")
        self.bot.record_revenue("Jordan", "subscription_basic", 4.99, "twitch",
                                 "Sub from viewer")

        total = self.bot.get_total_revenue("Jordan")
        assert total == pytest.approx(104.99)

        profile = self.bot.get_creator_profile("Jordan")
        assert profile.onboarding_complete is True
