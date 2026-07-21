"""
Tests for bots/211-resource-eligibility-bot/bot.py and tiers.py.
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
BOT_DIR = os.path.join(REPO_ROOT, 'bots', '211-resource-eligibility-bot')
sys.path.insert(0, BOT_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest

from tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    list_tiers,
    get_upgrade_path,
    TIER_CATALOGUE,
    FREE_FEATURES,
    PRO_FEATURES,
    ENTERPRISE_FEATURES,
    FEATURE_RESOURCE_SEARCH,
    FEATURE_GPS_MAP,
    FEATURE_BUILDING_INTEL_PANELS,
    FEATURE_ADVANCED_FILTERING,
    FEATURE_ROUTE_PLANNING,
    FEATURE_RIDESHARE_COST_ESTIMATE,
    FEATURE_CROWD_REPORTING,
    FEATURE_SUPPLY_ALERTS,
    FEATURE_SAFETY_SCORE,
    FEATURE_AI_RESOURCE_MATCHING,
    FEATURE_FAMILY_GPS,
    FEATURE_PANIC_BUTTON,
    FEATURE_ARRIVAL_ALERTS,
    FEATURE_SPONSORED_LISTINGS,
    FEATURE_AFFILIATE_PROGRAMS,
    FEATURE_WHITE_LABEL,
    FREE_DATA_SOURCES,
    PRO_DATA_SOURCES,
    DATA_SOURCE_211,
    DATA_SOURCE_FEEDING_AMERICA,
    DATA_SOURCE_HUD,
    DATA_SOURCE_AMERICAN_JOB_CENTERS,
    FREE_MAX_RESULTS,
    PRO_MAX_RESULTS,
    ENTERPRISE_MAX_RESULTS,
    RESOURCE_CATEGORIES,
)
from bot import (
    ResourceBot,
    ResourceFilter,
    UserProfile,
    Resource,
    BuildingIntelPanel,
    RouteInfo,
    ResourcePlan,
    FamilyAlert,
    ResourceBotTierError,
    ResourceNotFoundError,
    InvalidLocationError,
    _haversine_km,
)


# ===========================================================================
# Tier configuration tests
# ===========================================================================

class TestTierConfig:
    def test_all_tiers_present(self):
        assert set(TIER_CATALOGUE.keys()) == {"free", "pro", "enterprise"}

    def test_free_price_is_zero(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 29.0

    def test_enterprise_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_free_max_results(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_results == FREE_MAX_RESULTS

    def test_pro_max_results(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_results == PRO_MAX_RESULTS

    def test_enterprise_unlimited(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_results is None
        assert cfg.is_unlimited()

    def test_free_has_basic_features(self):
        cfg = get_tier_config(Tier.FREE)
        assert FEATURE_RESOURCE_SEARCH in cfg.features
        assert FEATURE_GPS_MAP in cfg.features

    def test_free_lacks_advanced_features(self):
        cfg = get_tier_config(Tier.FREE)
        assert FEATURE_BUILDING_INTEL_PANELS not in cfg.features
        assert FEATURE_ADVANCED_FILTERING not in cfg.features
        assert FEATURE_ROUTE_PLANNING not in cfg.features

    def test_pro_has_advanced_features(self):
        cfg = get_tier_config(Tier.PRO)
        for feat in [
            FEATURE_BUILDING_INTEL_PANELS,
            FEATURE_ADVANCED_FILTERING,
            FEATURE_ROUTE_PLANNING,
            FEATURE_RIDESHARE_COST_ESTIMATE,
            FEATURE_CROWD_REPORTING,
            FEATURE_SUPPLY_ALERTS,
            FEATURE_SAFETY_SCORE,
            FEATURE_AI_RESOURCE_MATCHING,
            FEATURE_FAMILY_GPS,
            FEATURE_PANIC_BUTTON,
            FEATURE_ARRIVAL_ALERTS,
        ]:
            assert feat in cfg.features, f"Expected {feat} in PRO features"

    def test_enterprise_has_monetisation_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert FEATURE_SPONSORED_LISTINGS in cfg.features
        assert FEATURE_AFFILIATE_PROGRAMS in cfg.features
        assert FEATURE_WHITE_LABEL in cfg.features

    def test_pro_lacks_enterprise_only_features(self):
        cfg = get_tier_config(Tier.PRO)
        assert FEATURE_SPONSORED_LISTINGS not in cfg.features
        assert FEATURE_WHITE_LABEL not in cfg.features

    def test_free_data_sources(self):
        cfg = get_tier_config(Tier.FREE)
        assert DATA_SOURCE_211 in cfg.data_sources

    def test_pro_data_sources(self):
        cfg = get_tier_config(Tier.PRO)
        assert DATA_SOURCE_FEEDING_AMERICA in cfg.data_sources
        assert DATA_SOURCE_HUD in cfg.data_sources
        assert DATA_SOURCE_AMERICAN_JOB_CENTERS in cfg.data_sources

    def test_has_feature(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_ROUTE_PLANNING)
        assert not cfg.has_feature(FEATURE_WHITE_LABEL)

    def test_has_data_source(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_data_source(DATA_SOURCE_FEEDING_AMERICA)
        assert not cfg.has_data_source("nonexistent_source")

    def test_list_tiers_order(self):
        tiers = list_tiers()
        prices = [t.price_usd_monthly for t in tiers]
        assert prices == sorted(prices)

    def test_upgrade_path_free_to_pro(self):
        next_cfg = get_upgrade_path(Tier.FREE)
        assert next_cfg is not None
        assert next_cfg.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        next_cfg = get_upgrade_path(Tier.PRO)
        assert next_cfg is not None
        assert next_cfg.tier == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_resource_categories_not_empty(self):
        assert len(RESOURCE_CATEGORIES) > 0


# ===========================================================================
# Utility helper tests
# ===========================================================================

class TestHaversine:
    def test_same_point_is_zero(self):
        assert _haversine_km(40.0, -74.0, 40.0, -74.0) == pytest.approx(0.0)

    def test_known_distance(self):
        # Approx distance between NYC (40.7128, -74.006) and a point ~10 km away
        dist = _haversine_km(40.7128, -74.0060, 40.8000, -74.0060)
        assert 8.0 < dist < 12.0

    def test_symmetrical(self):
        d1 = _haversine_km(40.0, -74.0, 41.0, -75.0)
        d2 = _haversine_km(41.0, -75.0, 40.0, -74.0)
        assert d1 == pytest.approx(d2)


# ===========================================================================
# ResourceBot — basic construction & tier info
# ===========================================================================

class TestResourceBotConstruction:
    def test_default_tier_is_free(self):
        bot = ResourceBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = ResourceBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = ResourceBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_describe_tier_returns_string(self):
        bot = ResourceBot(tier=Tier.FREE)
        result = bot.describe_tier()
        assert isinstance(result, str)
        assert "Free" in result

    def test_describe_tier_pro(self):
        bot = ResourceBot(tier=Tier.PRO)
        result = bot.describe_tier()
        assert "Pro" in result

    def test_show_upgrade_path_free(self):
        bot = ResourceBot(tier=Tier.FREE)
        result = bot.show_upgrade_path()
        assert "Pro" in result

    def test_show_upgrade_path_enterprise_is_top(self):
        bot = ResourceBot(tier=Tier.ENTERPRISE)
        result = bot.show_upgrade_path()
        assert "top-tier" in result.lower() or "Enterprise" in result


# ===========================================================================
# Resource search
# ===========================================================================

class TestResourceSearch:
    def setup_method(self):
        self.free_bot = ResourceBot(tier=Tier.FREE)
        self.pro_bot = ResourceBot(tier=Tier.PRO)

    def test_basic_search_returns_list(self):
        results = self.free_bot.search_resources(lat=40.7128, lon=-74.0060)
        assert isinstance(results, list)

    def test_basic_search_not_empty(self):
        results = self.free_bot.search_resources(lat=40.7128, lon=-74.0060)
        assert len(results) > 0

    def test_results_are_resource_instances(self):
        results = self.free_bot.search_resources(lat=40.7128, lon=-74.0060)
        for r in results:
            assert isinstance(r, Resource)

    def test_free_tier_result_limit(self):
        results = self.free_bot.search_resources(lat=40.7128, lon=-74.0060)
        assert len(results) <= FREE_MAX_RESULTS

    def test_pro_tier_higher_limit(self):
        results = self.pro_bot.search_resources(lat=40.7128, lon=-74.0060)
        assert len(results) <= PRO_MAX_RESULTS

    def test_category_filter(self):
        results = self.free_bot.search_resources(lat=40.7128, lon=-74.0060, category="food")
        for r in results:
            assert r.category == "food"

    def test_category_shelter(self):
        results = self.free_bot.search_resources(lat=40.7128, lon=-74.0060, category="shelter")
        for r in results:
            assert r.category == "shelter"

    def test_results_sorted_by_distance(self):
        results = self.free_bot.search_resources(lat=40.7128, lon=-74.0060)
        distances = [_haversine_km(40.7128, -74.0060, r.lat, r.lon) for r in results]
        assert distances == sorted(distances)

    def test_invalid_lat_raises(self):
        with pytest.raises(InvalidLocationError):
            self.free_bot.search_resources(lat=100.0, lon=-74.0)

    def test_invalid_lon_raises(self):
        with pytest.raises(InvalidLocationError):
            self.free_bot.search_resources(lat=40.0, lon=200.0)

    def test_advanced_filter_requires_pro(self):
        filt = ResourceFilter(kid_friendly=True)
        with pytest.raises(ResourceBotTierError):
            self.free_bot.search_resources(lat=40.7128, lon=-74.0060, filters=filt)

    def test_advanced_filter_works_on_pro(self):
        filt = ResourceFilter(kid_friendly=True)
        results = self.pro_bot.search_resources(lat=40.7128, lon=-74.0060, filters=filt)
        for r in results:
            assert r.kid_friendly

    def test_filter_handicap_accessible(self):
        filt = ResourceFilter(handicap_accessible=True)
        results = self.pro_bot.search_resources(lat=40.7128, lon=-74.0060, filters=filt)
        for r in results:
            assert r.handicap_accessible

    def test_filter_spanish_speaking(self):
        filt = ResourceFilter(spanish_speaking=True)
        results = self.pro_bot.search_resources(lat=40.7128, lon=-74.0060, filters=filt)
        for r in results:
            assert r.spanish_speaking

    def test_filter_max_distance(self):
        filt = ResourceFilter(max_distance_km=0.1)
        results = self.pro_bot.search_resources(lat=40.7128, lon=-74.0060, filters=filt)
        for r in results:
            dist = _haversine_km(40.7128, -74.0060, r.lat, r.lon)
            assert dist <= 0.1

    def test_no_results_for_unknown_category(self):
        results = self.free_bot.search_resources(
            lat=40.7128, lon=-74.0060, category="nonexistent_category"
        )
        assert results == []


# ===========================================================================
# Building Intelligence Panel
# ===========================================================================

class TestBuildingIntelPanel:
    def setup_method(self):
        self.free_bot = ResourceBot(tier=Tier.FREE)
        self.pro_bot = ResourceBot(tier=Tier.PRO)

    def test_panel_requires_pro(self):
        with pytest.raises(ResourceBotTierError):
            self.free_bot.get_building_intel_panel("r001")

    def test_panel_returns_correct_type(self):
        panel = self.pro_bot.get_building_intel_panel("r001")
        assert isinstance(panel, BuildingIntelPanel)

    def test_panel_resource_matches(self):
        panel = self.pro_bot.get_building_intel_panel("r001")
        assert panel.resource.resource_id == "r001"

    def test_panel_type_label_not_empty(self):
        panel = self.pro_bot.get_building_intel_panel("r001")
        assert len(panel.type_label) > 0

    def test_panel_eligibility_summary(self):
        panel = self.pro_bot.get_building_intel_panel("r001")
        assert isinstance(panel.eligibility_summary, str)

    def test_panel_documents_needed(self):
        panel = self.pro_bot.get_building_intel_panel("r001")
        assert isinstance(panel.documents_needed, list)

    def test_panel_optimal_visit_times(self):
        panel = self.pro_bot.get_building_intel_panel("r001")
        assert isinstance(panel.optimal_visit_times, list)

    def test_panel_wait_time_label(self):
        panel = self.pro_bot.get_building_intel_panel("r001")
        assert "minute" in panel.wait_time_label or "wait" in panel.wait_time_label.lower()

    def test_panel_success_instructions(self):
        panel = self.pro_bot.get_building_intel_panel("r001")
        assert len(panel.success_instructions) > 0

    def test_panel_video_url(self):
        panel = self.pro_bot.get_building_intel_panel("r001")
        assert isinstance(panel.video_walkthrough_url, str)

    def test_panel_crowd_level_valid(self):
        panel = self.pro_bot.get_building_intel_panel("r001")
        assert panel.crowd_level in ("low", "medium", "high")

    def test_panel_supply_status_valid(self):
        panel = self.pro_bot.get_building_intel_panel("r001")
        assert panel.supply_status in ("available", "unavailable")

    def test_panel_safety_score_on_pro(self):
        panel = self.pro_bot.get_building_intel_panel("r001")
        assert panel.safety_score is not None
        assert 0.0 <= panel.safety_score <= 10.0

    def test_panel_not_found_raises(self):
        with pytest.raises(ResourceNotFoundError):
            self.pro_bot.get_building_intel_panel("nonexistent")

    def test_panel_zero_wait_resource(self):
        # Add a resource with 0 wait time
        bot = ResourceBot(tier=Tier.PRO)
        r = Resource(
            resource_id="r_test_wait",
            name="Test Resource",
            category="food",
            address="1 Test St",
            lat=40.71,
            lon=-74.01,
            average_wait_minutes=0,
        )
        bot.add_resource(r)
        panel = bot.get_building_intel_panel("r_test_wait")
        assert "no wait" in panel.wait_time_label.lower() or "minimal" in panel.wait_time_label.lower()


# ===========================================================================
# Route planning
# ===========================================================================

class TestRoutePlanning:
    def setup_method(self):
        self.free_bot = ResourceBot(tier=Tier.FREE)
        self.pro_bot = ResourceBot(tier=Tier.PRO)

    def test_route_requires_pro(self):
        with pytest.raises(ResourceBotTierError):
            self.free_bot.get_route_info(40.7000, -74.0000, "r001")

    def test_route_returns_route_info(self):
        route = self.pro_bot.get_route_info(40.7000, -74.0000, "r001")
        assert isinstance(route, RouteInfo)

    def test_route_resource_id_matches(self):
        route = self.pro_bot.get_route_info(40.7000, -74.0000, "r001")
        assert route.resource_id == "r001"

    def test_route_distance_positive(self):
        route = self.pro_bot.get_route_info(40.7000, -74.0000, "r001")
        assert route.distance_km > 0

    def test_route_drive_minutes_positive(self):
        route = self.pro_bot.get_route_info(40.7000, -74.0000, "r001")
        assert route.estimated_drive_minutes >= 1

    def test_route_walk_minutes_positive(self):
        route = self.pro_bot.get_route_info(40.7000, -74.0000, "r001")
        assert route.estimated_walk_minutes >= 1

    def test_route_walk_longer_than_drive(self):
        route = self.pro_bot.get_route_info(40.7000, -74.0000, "r001")
        assert route.estimated_walk_minutes >= route.estimated_drive_minutes

    def test_route_uber_estimate_on_pro(self):
        route = self.pro_bot.get_route_info(40.7000, -74.0000, "r001")
        assert route.uber_estimate_usd is not None
        assert route.uber_estimate_usd > 0

    def test_route_lyft_estimate_on_pro(self):
        route = self.pro_bot.get_route_info(40.7000, -74.0000, "r001")
        assert route.lyft_estimate_usd is not None
        assert route.lyft_estimate_usd > 0

    def test_route_lyft_cheaper_than_uber(self):
        route = self.pro_bot.get_route_info(40.7000, -74.0000, "r001")
        assert route.lyft_estimate_usd <= route.uber_estimate_usd

    def test_route_maps_url_format(self):
        route = self.pro_bot.get_route_info(40.7000, -74.0000, "r001")
        assert "google.com/maps" in route.maps_url

    def test_route_safe_route_on_pro(self):
        route = self.pro_bot.get_route_info(40.7000, -74.0000, "r001")
        assert route.safe_route is True

    def test_route_not_found_raises(self):
        with pytest.raises(ResourceNotFoundError):
            self.pro_bot.get_route_info(40.7000, -74.0000, "nonexistent")

    def test_route_invalid_origin_raises(self):
        with pytest.raises(InvalidLocationError):
            self.pro_bot.get_route_info(999.0, -74.0000, "r001")


# ===========================================================================
# Crowd reporting & supply alerts
# ===========================================================================

class TestCrowdAndSupply:
    def setup_method(self):
        self.free_bot = ResourceBot(tier=Tier.FREE)
        self.pro_bot = ResourceBot(tier=Tier.PRO)

    def test_crowd_report_requires_pro(self):
        with pytest.raises(ResourceBotTierError):
            self.free_bot.report_crowd_level("r001", "high")

    def test_crowd_report_updates_level(self):
        self.pro_bot.report_crowd_level("r001", "high")
        resource = self.pro_bot.get_resource_by_id("r001")
        assert resource.current_crowd_level == "high"

    def test_crowd_report_invalid_level(self):
        with pytest.raises(ValueError):
            self.pro_bot.report_crowd_level("r001", "extreme")

    def test_supply_alert_requires_pro(self):
        with pytest.raises(ResourceBotTierError):
            self.free_bot.report_supply_status("r001", False)

    def test_supply_alert_updates_status(self):
        self.pro_bot.report_supply_status("r001", False)
        resource = self.pro_bot.get_resource_by_id("r001")
        assert resource.supply_available is False

    def test_supply_alert_restore(self):
        self.pro_bot.report_supply_status("r001", False)
        self.pro_bot.report_supply_status("r001", True)
        resource = self.pro_bot.get_resource_by_id("r001")
        assert resource.supply_available is True


# ===========================================================================
# Neighbourhood safety score
# ===========================================================================

class TestSafetyScore:
    def setup_method(self):
        self.free_bot = ResourceBot(tier=Tier.FREE)
        self.pro_bot = ResourceBot(tier=Tier.PRO)

    def test_safety_score_requires_pro(self):
        with pytest.raises(ResourceBotTierError):
            self.free_bot.get_safety_score("r001")

    def test_safety_score_returns_float(self):
        score = self.pro_bot.get_safety_score("r001")
        assert isinstance(score, float)

    def test_safety_score_in_range(self):
        score = self.pro_bot.get_safety_score("r001")
        assert 0.0 <= score <= 10.0

    def test_safety_score_not_found_raises(self):
        with pytest.raises(ResourceNotFoundError):
            self.pro_bot.get_safety_score("nonexistent")


# ===========================================================================
# AI resource matching
# ===========================================================================

class TestAIResourceMatching:
    def setup_method(self):
        self.free_bot = ResourceBot(tier=Tier.FREE)
        self.pro_bot = ResourceBot(tier=Tier.PRO)

    def test_plan_requires_pro(self):
        profile = UserProfile()
        with pytest.raises(ResourceBotTierError):
            self.free_bot.generate_resource_plan(profile=profile, lat=40.7128, lon=-74.0060)

    def test_plan_returns_resource_plan(self):
        profile = UserProfile()
        plan = self.pro_bot.generate_resource_plan(profile=profile, lat=40.7128, lon=-74.0060)
        assert isinstance(plan, ResourcePlan)

    def test_plan_has_summary(self):
        profile = UserProfile()
        plan = self.pro_bot.generate_resource_plan(profile=profile, lat=40.7128, lon=-74.0060)
        assert len(plan.summary) > 0

    def test_plan_has_priority_categories(self):
        profile = UserProfile()
        plan = self.pro_bot.generate_resource_plan(profile=profile, lat=40.7128, lon=-74.0060)
        assert isinstance(plan.priority_categories, list)
        assert len(plan.priority_categories) > 0

    def test_homeless_profile_includes_shelter(self):
        profile = UserProfile(housing_status="homeless", income_level="very_low")
        plan = self.pro_bot.generate_resource_plan(profile=profile, lat=40.7128, lon=-74.0060)
        assert "shelter" in plan.priority_categories

    def test_unemployed_profile_includes_jobs(self):
        profile = UserProfile(employed=False, income_level="low")
        plan = self.pro_bot.generate_resource_plan(profile=profile, lat=40.7128, lon=-74.0060)
        assert "job_assistance" in plan.priority_categories

    def test_low_income_includes_food(self):
        profile = UserProfile(income_level="very_low")
        plan = self.pro_bot.generate_resource_plan(profile=profile, lat=40.7128, lon=-74.0060)
        assert "food" in plan.priority_categories

    def test_plan_has_financial_literacy_tips(self):
        profile = UserProfile(income_level="low")
        plan = self.pro_bot.generate_resource_plan(profile=profile, lat=40.7128, lon=-74.0060)
        assert len(plan.financial_literacy_tips) > 0

    def test_plan_profile_stored(self):
        profile = UserProfile(household_size=4, has_children=True)
        plan = self.pro_bot.generate_resource_plan(profile=profile, lat=40.7128, lon=-74.0060)
        assert plan.profile.household_size == 4

    def test_plan_invalid_location_raises(self):
        profile = UserProfile()
        with pytest.raises(InvalidLocationError):
            self.pro_bot.generate_resource_plan(profile=profile, lat=999.0, lon=-74.0)


# ===========================================================================
# Family GPS & safety alerts
# ===========================================================================

class TestFamilyGPS:
    def setup_method(self):
        self.free_bot = ResourceBot(tier=Tier.FREE)
        self.pro_bot = ResourceBot(tier=Tier.PRO)

    def test_register_requires_pro(self):
        with pytest.raises(ResourceBotTierError):
            self.free_bot.register_family_member("Alice", 40.71, -74.00)

    def test_register_stores_location(self):
        self.pro_bot.register_family_member("Alice", 40.71, -74.00)
        locations = self.pro_bot.get_family_locations()
        assert "Alice" in locations
        assert locations["Alice"] == (40.71, -74.00)

    def test_get_locations_requires_pro(self):
        with pytest.raises(ResourceBotTierError):
            self.free_bot.get_family_locations()

    def test_register_invalid_location_raises(self):
        with pytest.raises(InvalidLocationError):
            self.pro_bot.register_family_member("Alice", 999.0, -74.00)

    def test_panic_alert_requires_pro(self):
        with pytest.raises(ResourceBotTierError):
            self.free_bot.send_panic_alert("Alice")

    def test_panic_alert_returns_alert(self):
        self.pro_bot.register_family_member("Alice", 40.71, -74.00)
        alert = self.pro_bot.send_panic_alert("Alice")
        assert isinstance(alert, FamilyAlert)

    def test_panic_alert_type(self):
        self.pro_bot.register_family_member("Alice", 40.71, -74.00)
        alert = self.pro_bot.send_panic_alert("Alice")
        assert alert.alert_type == "panic"

    def test_panic_alert_member_name(self):
        self.pro_bot.register_family_member("Alice", 40.71, -74.00)
        alert = self.pro_bot.send_panic_alert("Alice")
        assert alert.member_name == "Alice"

    def test_panic_alert_message_not_empty(self):
        self.pro_bot.register_family_member("Alice", 40.71, -74.00)
        alert = self.pro_bot.send_panic_alert("Alice")
        assert len(alert.message) > 0

    def test_arrival_alert_requires_pro(self):
        with pytest.raises(ResourceBotTierError):
            self.free_bot.send_arrival_alert("Alice", "Food Pantry")

    def test_arrival_alert_returns_alert(self):
        self.pro_bot.register_family_member("Bob", 40.72, -74.01)
        alert = self.pro_bot.send_arrival_alert("Bob", "City Food Pantry")
        assert isinstance(alert, FamilyAlert)

    def test_arrival_alert_type(self):
        self.pro_bot.register_family_member("Bob", 40.72, -74.01)
        alert = self.pro_bot.send_arrival_alert("Bob", "City Food Pantry")
        assert alert.alert_type == "arrival"

    def test_arrival_alert_message_contains_destination(self):
        self.pro_bot.register_family_member("Bob", 40.72, -74.01)
        alert = self.pro_bot.send_arrival_alert("Bob", "City Food Pantry")
        assert "City Food Pantry" in alert.message


# ===========================================================================
# Resource layers
# ===========================================================================

class TestResourceLayers:
    def setup_method(self):
        self.bot = ResourceBot(tier=Tier.FREE)

    def test_homeless_resources_returns_list(self):
        results = self.bot.get_homeless_resources(lat=40.7128, lon=-74.0060)
        assert isinstance(results, list)

    def test_homeless_resources_shelter_only(self):
        results = self.bot.get_homeless_resources(lat=40.7128, lon=-74.0060)
        for r in results:
            assert r.category == "shelter"

    def test_job_resources_returns_list(self):
        results = self.bot.get_job_resources(lat=40.7128, lon=-74.0060)
        assert isinstance(results, list)

    def test_job_resources_category(self):
        results = self.bot.get_job_resources(lat=40.7128, lon=-74.0060)
        for r in results:
            assert r.category == "job_assistance"

    def test_financial_literacy_resources(self):
        results = self.bot.get_financial_literacy_resources(lat=40.7128, lon=-74.0060)
        assert isinstance(results, list)

    def test_financial_literacy_category(self):
        results = self.bot.get_financial_literacy_resources(lat=40.7128, lon=-74.0060)
        for r in results:
            assert r.category == "financial_literacy"

    def test_layers_invalid_location_raises(self):
        with pytest.raises(InvalidLocationError):
            self.bot.get_homeless_resources(lat=999.0, lon=-74.0)


# ===========================================================================
# Monetisation — sponsored listings & affiliates
# ===========================================================================

class TestMonetisation:
    def setup_method(self):
        self.free_bot = ResourceBot(tier=Tier.FREE)
        self.pro_bot = ResourceBot(tier=Tier.PRO)
        self.ent_bot = ResourceBot(tier=Tier.ENTERPRISE)

    def _make_sponsored_resource(self) -> Resource:
        return Resource(
            resource_id="sponsored_001",
            name="Sponsor Corp Food Bank",
            category="food",
            address="999 Sponsor Way",
            lat=40.72,
            lon=-74.01,
        )

    def test_sponsored_listing_requires_enterprise(self):
        r = self._make_sponsored_resource()
        with pytest.raises(ResourceBotTierError):
            self.free_bot.add_sponsored_resource(r)

    def test_sponsored_listing_pro_also_blocked(self):
        r = self._make_sponsored_resource()
        with pytest.raises(ResourceBotTierError):
            self.pro_bot.add_sponsored_resource(r)

    def test_sponsored_listing_enterprise_allowed(self):
        r = self._make_sponsored_resource()
        self.ent_bot.add_sponsored_resource(r)
        fetched = self.ent_bot.get_resource_by_id("sponsored_001")
        assert fetched.sponsored is True

    def test_affiliate_requires_enterprise(self):
        with pytest.raises(ResourceBotTierError):
            self.free_bot.register_affiliate("Local Nonprofit")

    def test_affiliate_registration(self):
        self.ent_bot.register_affiliate("Local Nonprofit A")
        affiliates = self.ent_bot.get_affiliates()
        assert "Local Nonprofit A" in affiliates

    def test_affiliate_no_duplicates(self):
        self.ent_bot.register_affiliate("Org X")
        self.ent_bot.register_affiliate("Org X")
        affiliates = self.ent_bot.get_affiliates()
        assert affiliates.count("Org X") == 1

    def test_get_affiliates_requires_enterprise(self):
        with pytest.raises(ResourceBotTierError):
            self.free_bot.get_affiliates()


# ===========================================================================
# Custom resource management
# ===========================================================================

class TestResourceManagement:
    def setup_method(self):
        self.bot = ResourceBot(tier=Tier.FREE)

    def test_add_resource(self):
        r = Resource(
            resource_id="custom_001",
            name="Custom Resource",
            category="healthcare",
            address="1 Health St",
            lat=40.71,
            lon=-74.00,
        )
        self.bot.add_resource(r)
        fetched = self.bot.get_resource_by_id("custom_001")
        assert fetched.name == "Custom Resource"

    def test_get_resource_not_found_raises(self):
        with pytest.raises(ResourceNotFoundError):
            self.bot.get_resource_by_id("does_not_exist")

    def test_added_resource_appears_in_search(self):
        r = Resource(
            resource_id="custom_food_001",
            name="New Food Bank",
            category="food",
            address="2 Food Ave",
            lat=40.7128,
            lon=-74.0060,
        )
        self.bot.add_resource(r)
        results = self.bot.search_resources(lat=40.7128, lon=-74.0060, category="food")
        ids = [res.resource_id for res in results]
        assert "custom_food_001" in ids
