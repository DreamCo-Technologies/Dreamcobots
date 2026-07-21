"""Tests for bots/space_ai_bot/ — mission planning, satellite monitoring, and main bot."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, "models"))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.space_ai_bot.mission_planner import MissionPlanner, MissionPlannerError, MISSION_PROFILES
from bots.space_ai_bot.satellite_monitor import (
    SatelliteMonitor,
    SatelliteMonitorError,
    SATELLITE_DATABASE,
)
from bots.space_ai_bot.space_ai_bot import SpaceAIBot, SpaceAIBotError
from bots.space_ai_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ===========================================================================
# Tiers
# ===========================================================================

class TestSpaceAITiers:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_free_tier_info_price(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0

    def test_pro_tier_info_price(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] == 49.0

    def test_enterprise_tier_info_has_api(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert any("API" in f or "api" in f.lower() for f in info["features"])

    def test_tier_info_has_support_level(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert "support_level" in info

    def test_tier_info_has_features_list(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert isinstance(info["features"], list)
            assert len(info["features"]) > 0

    def test_enterprise_has_unlimited_note(self):
        features = BOT_FEATURES[Tier.ENTERPRISE.value]
        assert any("unlimited" in f.lower() for f in features)

    def test_free_features_mention_simulate(self):
        features = BOT_FEATURES[Tier.FREE.value]
        assert any("simulate" in f.lower() for f in features)


# ===========================================================================
# MissionPlanner
# ===========================================================================

class TestMissionPlannerFree:
    def test_default_tier_is_free(self):
        mp = MissionPlanner()
        assert mp.tier == Tier.FREE

    def test_free_plan_mission_raises(self):
        mp = MissionPlanner(Tier.FREE)
        with pytest.raises(MissionPlannerError):
            mp.plan_mission("lunar", "Moon")

    def test_simulate_trajectory_returns_dict(self):
        mp = MissionPlanner(Tier.FREE)
        result = mp.simulate_trajectory("Earth", "Moon", "2025-01-01")
        assert isinstance(result, dict)

    def test_simulate_trajectory_has_required_keys(self):
        mp = MissionPlanner(Tier.FREE)
        result = mp.simulate_trajectory("Earth", "Moon", "2025-01-01")
        for key in ("origin", "destination", "launch_date", "delta_v_km_s", "flight_duration_days"):
            assert key in result

    def test_simulate_trajectory_is_simulation_only_on_free(self):
        mp = MissionPlanner(Tier.FREE)
        result = mp.simulate_trajectory("Earth", "Mars", "2025-06-01")
        assert result["simulation_only"] is True

    def test_free_assess_risk_raises(self):
        mp = MissionPlanner(Tier.FREE)
        with pytest.raises(MissionPlannerError):
            mp.assess_mission_risk({"mission_type": "lunar"})

    def test_free_get_mission_status_not_found(self):
        mp = MissionPlanner(Tier.FREE)
        result = mp.get_mission_status("MSN-9999")
        assert result["status"] == "not_found"


class TestMissionPlannerPro:
    def test_pro_plan_mission_returns_dict(self):
        mp = MissionPlanner(Tier.PRO)
        result = mp.plan_mission("lunar", "Moon", crew_size=2)
        assert isinstance(result, dict)

    def test_pro_plan_mission_has_required_keys(self):
        mp = MissionPlanner(Tier.PRO)
        result = mp.plan_mission("iss_supply", "ISS")
        for key in ("mission_id", "mission_type", "destination", "duration_days", "fuel_kg"):
            assert key in result

    def test_pro_plan_mission_id_format(self):
        mp = MissionPlanner(Tier.PRO)
        result = mp.plan_mission("mars", "Mars")
        assert result["mission_id"].startswith("MSN-")

    def test_pro_mission_limit_is_five(self):
        mp = MissionPlanner(Tier.PRO)
        for i in range(5):
            mp.plan_mission("lunar", f"Destination-{i}")
        with pytest.raises(MissionPlannerError):
            mp.plan_mission("lunar", "Destination-6")

    def test_pro_simulate_not_simulation_only(self):
        mp = MissionPlanner(Tier.PRO)
        result = mp.simulate_trajectory("Earth", "Moon", "2025-01-01")
        assert result["simulation_only"] is False

    def test_pro_simulate_has_launch_windows(self):
        mp = MissionPlanner(Tier.PRO)
        result = mp.simulate_trajectory("Earth", "Mars", "2025-01-01")
        assert "optimal_launch_windows" in result
        assert len(result["optimal_launch_windows"]) > 0

    def test_pro_assess_risk_returns_dict(self):
        mp = MissionPlanner(Tier.PRO)
        result = mp.assess_mission_risk({"mission_type": "lunar", "crew_size": 3})
        assert isinstance(result, dict)

    def test_pro_assess_risk_has_score(self):
        mp = MissionPlanner(Tier.PRO)
        result = mp.assess_mission_risk({"mission_type": "mars", "crew_size": 4})
        assert "overall_risk_score" in result
        assert 0 <= result["overall_risk_score"] <= 1.0

    def test_pro_assess_risk_has_label(self):
        mp = MissionPlanner(Tier.PRO)
        result = mp.assess_mission_risk({"mission_type": "deep_space"})
        assert result["risk_label"] in ("minimal", "low", "moderate", "high", "critical")

    def test_pro_get_mission_status(self):
        mp = MissionPlanner(Tier.PRO)
        plan = mp.plan_mission("satellite_deploy", "LEO")
        status = mp.get_mission_status(plan["mission_id"])
        assert status["status"] == "planned"
        assert status["mission_id"] == plan["mission_id"]

    def test_all_mission_types_accepted(self):
        mp = MissionPlanner(Tier.PRO)
        types = ["lunar", "mars", "iss_supply", "satellite_deploy"]
        for mtype in types:
            result = mp.plan_mission(mtype, f"dest-{mtype}")
            assert result["mission_type"] == mtype


class TestMissionPlannerEnterprise:
    def test_enterprise_plan_unlimited(self):
        mp = MissionPlanner(Tier.ENTERPRISE)
        for i in range(10):
            mp.plan_mission("lunar", f"Moon-{i}")
        assert mp._mission_counter == 10

    def test_enterprise_plan_has_contingency(self):
        mp = MissionPlanner(Tier.ENTERPRISE)
        result = mp.plan_mission("mars", "Mars", crew_size=6)
        assert "contingency_plans" in result
        assert len(result["contingency_plans"]) >= 2

    def test_enterprise_plan_ai_optimized(self):
        mp = MissionPlanner(Tier.ENTERPRISE)
        result = mp.plan_mission("deep_space", "Pluto")
        assert result.get("ai_optimized") is True

    def test_enterprise_simulate_n_body(self):
        mp = MissionPlanner(Tier.ENTERPRISE)
        result = mp.simulate_trajectory("Earth", "Mars", "2025-09-01")
        assert result.get("n_body_simulation") is True

    def test_enterprise_risk_has_monte_carlo(self):
        mp = MissionPlanner(Tier.ENTERPRISE)
        result = mp.assess_mission_risk({"mission_type": "mars", "crew_size": 6})
        assert "monte_carlo_iterations" in result
        assert result["monte_carlo_iterations"] == 100_000

    def test_enterprise_risk_confidence_interval(self):
        mp = MissionPlanner(Tier.ENTERPRISE)
        result = mp.assess_mission_risk({"mission_type": "lunar"})
        assert "confidence_interval_95" in result
        ci = result["confidence_interval_95"]
        assert len(ci) == 2
        assert ci[0] <= ci[1]


# ===========================================================================
# SatelliteMonitor
# ===========================================================================

class TestSatelliteMonitorFree:
    def test_default_tier_is_free(self):
        sm = SatelliteMonitor()
        assert sm.tier == Tier.FREE

    def test_free_track_satellite_returns_dict(self):
        sm = SatelliteMonitor(Tier.FREE)
        result = sm.track_satellite("GPS-IIF-1")
        assert isinstance(result, dict)

    def test_free_track_satellite_has_required_keys(self):
        sm = SatelliteMonitor(Tier.FREE)
        result = sm.track_satellite("NOAA-20")
        for key in ("sat_id", "altitude_km", "velocity_km_s", "status"):
            assert key in result

    def test_free_limit_is_two(self):
        sm = SatelliteMonitor(Tier.FREE)
        sm.track_satellite("GPS-IIF-1")
        sm.track_satellite("NOAA-20")
        with pytest.raises(SatelliteMonitorError):
            sm.track_satellite("ISS")

    def test_free_unknown_satellite_returns_error(self):
        sm = SatelliteMonitor(Tier.FREE)
        result = sm.track_satellite("FAKE-SAT-999")
        assert "error" in result

    def test_free_monitor_environment_raises(self):
        sm = SatelliteMonitor(Tier.FREE)
        with pytest.raises(SatelliteMonitorError):
            sm.monitor_environment("amazon")

    def test_free_map_planet_raises(self):
        sm = SatelliteMonitor(Tier.FREE)
        with pytest.raises(SatelliteMonitorError):
            sm.map_planet_surface("mars", {"lat": 0, "lon": 0})

    def test_free_anomaly_detection_raises(self):
        sm = SatelliteMonitor(Tier.FREE)
        with pytest.raises(SatelliteMonitorError):
            sm.detect_anomalies("ISS")

    def test_satellite_database_has_ten_entries(self):
        assert len(SATELLITE_DATABASE) == 10


class TestSatelliteMonitorPro:
    def test_pro_track_limit_is_twenty(self):
        sm = SatelliteMonitor(Tier.PRO)
        sats = list(SATELLITE_DATABASE.keys())
        for sat in sats:
            sm.track_satellite(sat)
        assert len(sm._tracked) == len(sats)

    def test_pro_track_has_inclination(self):
        sm = SatelliteMonitor(Tier.PRO)
        result = sm.track_satellite("ISS")
        assert "inclination_deg" in result

    def test_pro_track_has_owner(self):
        sm = SatelliteMonitor(Tier.PRO)
        result = sm.track_satellite("Hubble")
        assert "owner" in result

    def test_pro_monitor_environment_returns_dict(self):
        sm = SatelliteMonitor(Tier.PRO)
        result = sm.monitor_environment("amazon")
        assert isinstance(result, dict)

    def test_pro_monitor_environment_has_required_keys(self):
        sm = SatelliteMonitor(Tier.PRO)
        result = sm.monitor_environment("sahara")
        for key in ("region", "temperature_c", "vegetation_index", "pollution_index"):
            assert key in result

    def test_pro_map_planet_returns_dict(self):
        sm = SatelliteMonitor(Tier.PRO)
        result = sm.map_planet_surface("mars", {"lat": 18.65, "lon": 226.2})
        assert isinstance(result, dict)

    def test_pro_map_planet_has_surface_type(self):
        sm = SatelliteMonitor(Tier.PRO)
        result = sm.map_planet_surface("moon", {"lat": 0, "lon": 0})
        assert "surface_type" in result

    def test_pro_detect_anomalies_returns_dict(self):
        sm = SatelliteMonitor(Tier.PRO)
        result = sm.detect_anomalies("ISS")
        assert isinstance(result, dict)

    def test_pro_detect_anomalies_has_scan_status(self):
        sm = SatelliteMonitor(Tier.PRO)
        result = sm.detect_anomalies("Landsat-9")
        assert result["scan_status"] == "complete"

    def test_pro_monitor_unknown_region_defaults(self):
        sm = SatelliteMonitor(Tier.PRO)
        result = sm.monitor_environment("atlantis")
        assert "temperature_c" in result


class TestSatelliteMonitorEnterprise:
    def test_enterprise_track_has_tle(self):
        sm = SatelliteMonitor(Tier.ENTERPRISE)
        result = sm.track_satellite("GPS-IIF-1")
        assert result.get("tle_data_available") is True

    def test_enterprise_track_has_collision_risk(self):
        sm = SatelliteMonitor(Tier.ENTERPRISE)
        result = sm.track_satellite("Starlink-1007")
        assert "collision_risk" in result

    def test_enterprise_environment_has_real_time(self):
        sm = SatelliteMonitor(Tier.ENTERPRISE)
        result = sm.monitor_environment("california")
        assert result.get("real_time") is True

    def test_enterprise_environment_has_deforestation(self):
        sm = SatelliteMonitor(Tier.ENTERPRISE)
        result = sm.monitor_environment("amazon")
        assert "deforestation_rate_pct" in result

    def test_enterprise_map_has_high_resolution(self):
        sm = SatelliteMonitor(Tier.ENTERPRISE)
        result = sm.map_planet_surface("mars", {"lat": 0, "lon": 0})
        assert result.get("high_resolution") is True

    def test_enterprise_map_has_notable_features(self):
        sm = SatelliteMonitor(Tier.ENTERPRISE)
        result = sm.map_planet_surface("europa", {"lat": 10, "lon": 20})
        assert "notable_features" in result
        assert isinstance(result["notable_features"], list)

    def test_enterprise_anomaly_has_ai_model(self):
        sm = SatelliteMonitor(Tier.ENTERPRISE)
        result = sm.detect_anomalies("AQUA")
        assert "ai_model" in result


# ===========================================================================
# SpaceAIBot
# ===========================================================================

class TestSpaceAIBotFree:
    def test_default_tier_is_free(self):
        bot = SpaceAIBot()
        assert bot.tier == Tier.FREE

    def test_free_plan_mission_raises(self):
        bot = SpaceAIBot(Tier.FREE)
        with pytest.raises(SpaceAIBotError):
            bot.plan_mission("lunar", "Moon")

    def test_free_track_satellite_succeeds(self):
        bot = SpaceAIBot(Tier.FREE)
        result = bot.track_satellite("GPS-IIF-1")
        assert isinstance(result, dict)
        assert result["sat_id"] == "GPS-IIF-1"

    def test_free_track_satellite_limit(self):
        bot = SpaceAIBot(Tier.FREE)
        bot.track_satellite("GPS-IIF-1")
        bot.track_satellite("NOAA-20")
        with pytest.raises(SpaceAIBotError):
            bot.track_satellite("ISS")

    def test_free_monitor_earth_raises(self):
        bot = SpaceAIBot(Tier.FREE)
        with pytest.raises(SpaceAIBotError):
            bot.monitor_earth("amazon")

    def test_free_map_planet_raises(self):
        bot = SpaceAIBot(Tier.FREE)
        with pytest.raises(SpaceAIBotError):
            bot.map_planet("mars", {"lat": 0, "lon": 0})

    def test_free_dashboard_returns_dict(self):
        bot = SpaceAIBot(Tier.FREE)
        result = bot.get_space_dashboard()
        assert isinstance(result, dict)

    def test_free_dashboard_has_required_keys(self):
        bot = SpaceAIBot(Tier.FREE)
        result = bot.get_space_dashboard()
        for key in ("bot", "tier", "features", "missions_planned", "satellites_tracked"):
            assert key in result

    def test_free_dashboard_bot_name(self):
        bot = SpaceAIBot(Tier.FREE)
        result = bot.get_space_dashboard()
        assert result["bot"] == "SpaceAIBot"

    def test_free_dashboard_upgrade_available(self):
        bot = SpaceAIBot(Tier.FREE)
        result = bot.get_space_dashboard()
        assert result["upgrade_available"] is not None
        assert result["upgrade_available"]["tier"] == "pro"


class TestSpaceAIBotPro:
    def test_pro_plan_mission_succeeds(self):
        bot = SpaceAIBot(Tier.PRO)
        result = bot.plan_mission("lunar", "Moon", crew_size=3)
        assert isinstance(result, dict)
        assert result["destination"] == "Moon"

    def test_pro_mission_increments_counter(self):
        bot = SpaceAIBot(Tier.PRO)
        bot.plan_mission("iss_supply", "ISS")
        assert bot.get_space_dashboard()["missions_planned"] == 1

    def test_pro_monitor_earth_succeeds(self):
        bot = SpaceAIBot(Tier.PRO)
        result = bot.monitor_earth("amazon")
        assert isinstance(result, dict)
        assert "temperature_c" in result

    def test_pro_map_planet_succeeds(self):
        bot = SpaceAIBot(Tier.PRO)
        result = bot.map_planet("mars", {"lat": 18.65, "lon": 226.2})
        assert isinstance(result, dict)
        assert result["planet"] == "mars"

    def test_pro_activity_log_tracks_actions(self):
        bot = SpaceAIBot(Tier.PRO)
        bot.plan_mission("lunar", "Moon")
        bot.track_satellite("ISS")
        assert len(bot._activity_log) == 2

    def test_pro_dashboard_upgrade_is_enterprise(self):
        bot = SpaceAIBot(Tier.PRO)
        result = bot.get_space_dashboard()
        assert result["upgrade_available"]["tier"] == "enterprise"


class TestSpaceAIBotEnterprise:
    def test_enterprise_unlimited_missions(self):
        bot = SpaceAIBot(Tier.ENTERPRISE)
        for i in range(10):
            bot.plan_mission("lunar", f"Moon-{i}")
        assert bot.get_space_dashboard()["missions_planned"] == 10

    def test_enterprise_plan_has_contingency(self):
        bot = SpaceAIBot(Tier.ENTERPRISE)
        result = bot.plan_mission("mars", "Mars", crew_size=6)
        assert "contingency_plans" in result

    def test_enterprise_environment_real_time(self):
        bot = SpaceAIBot(Tier.ENTERPRISE)
        result = bot.monitor_earth("sahara")
        assert result.get("real_time") is True

    def test_enterprise_map_high_resolution(self):
        bot = SpaceAIBot(Tier.ENTERPRISE)
        result = bot.map_planet("moon", {"lat": 0, "lon": 0})
        assert result.get("high_resolution") is True

    def test_enterprise_dashboard_no_upgrade(self):
        bot = SpaceAIBot(Tier.ENTERPRISE)
        result = bot.get_space_dashboard()
        assert result["upgrade_available"] is None

    def test_enterprise_satellites_tracked_in_dashboard(self):
        bot = SpaceAIBot(Tier.ENTERPRISE)
        bot.track_satellite("ISS")
        bot.track_satellite("Hubble")
        result = bot.get_space_dashboard()
        assert result["satellites_tracked"] == 2
