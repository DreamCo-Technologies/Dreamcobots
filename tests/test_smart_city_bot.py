"""Tests for bots/smart_city_bot/ — infrastructure, government AI, and main bot."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, "models"))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.smart_city_bot.city_infrastructure import (
    TrafficManagementSystem,
    EnergyManagementSystem,
    PublicSafetyMonitor,
    SmartCityInfrastructureError,
)
from bots.smart_city_bot.government_ai import (
    TaxSystemAI,
    CensusCollector,
    PolicyModelingBot,
    GovernmentAIError,
)
from bots.smart_city_bot.smart_city_bot import SmartCityBot, SmartCityBotError
from bots.smart_city_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ===========================================================================
# Tiers
# ===========================================================================

class TestSmartCityTiers:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_free_tier_info(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0
        assert len(info["features"]) > 0

    def test_pro_tier_info(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] == 49.0

    def test_enterprise_tier_info_has_api(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert any("API" in f or "api" in f.lower() for f in info["features"])

    def test_tier_info_has_support(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert "support_level" in info


# ===========================================================================
# TrafficManagementSystem
# ===========================================================================

class TestTrafficManagementSystem:
    def test_default_tier_is_free(self):
        tms = TrafficManagementSystem()
        assert tms.tier == Tier.FREE

    def test_monitor_congestion_returns_dict(self):
        tms = TrafficManagementSystem(Tier.FREE)
        result = tms.monitor_congestion("downtown")
        assert isinstance(result, dict)

    def test_monitor_congestion_has_required_keys(self):
        tms = TrafficManagementSystem(Tier.FREE)
        result = tms.monitor_congestion("downtown")
        for key in ("zone", "congestion_index", "status", "avg_speed_kmh"):
            assert key in result

    def test_optimize_traffic_returns_dict(self):
        tms = TrafficManagementSystem(Tier.FREE)
        result = tms.optimize_traffic("north")
        assert isinstance(result, dict)

    def test_optimize_traffic_has_action(self):
        tms = TrafficManagementSystem(Tier.PRO)
        result = tms.optimize_traffic("downtown")
        assert "recommended_action" in result

    def test_free_tier_limited_to_one_zone(self):
        tms = TrafficManagementSystem(Tier.FREE)
        tms.monitor_congestion("downtown")
        with pytest.raises(SmartCityInfrastructureError):
            tms.monitor_congestion("north")

    def test_pro_tier_allows_10_zones(self):
        tms = TrafficManagementSystem(Tier.PRO)
        zones = ["downtown", "north", "south", "east", "west",
                 "industrial", "residential", "port", "airport", "suburbs"]
        for zone in zones:
            tms.monitor_congestion(zone)
        assert len(tms._monitored_zones) == 10

    def test_enterprise_tier_unlimited_zones(self):
        tms = TrafficManagementSystem(Tier.ENTERPRISE)
        zones = ["downtown", "north", "south", "east", "west",
                 "industrial", "residential", "port", "airport", "suburbs"]
        for zone in zones:
            tms.monitor_congestion(zone)
        assert len(tms._monitored_zones) == 10

    def test_predict_traffic_flow_free_raises(self):
        tms = TrafficManagementSystem(Tier.FREE)
        tms.monitor_congestion("downtown")
        with pytest.raises(SmartCityInfrastructureError):
            tms.predict_traffic_flow("downtown", 8)

    def test_predict_traffic_flow_pro(self):
        tms = TrafficManagementSystem(Tier.PRO)
        result = tms.predict_traffic_flow("downtown", 8)
        assert "predicted_flow_rate" in result
        assert result["confidence_pct"] == 85

    def test_predict_traffic_flow_enterprise(self):
        tms = TrafficManagementSystem(Tier.ENTERPRISE)
        result = tms.predict_traffic_flow("downtown", 8)
        assert result["confidence_pct"] == 95
        assert "7day_trend" in result

    def test_pro_optimize_has_alternate_routes(self):
        tms = TrafficManagementSystem(Tier.PRO)
        result = tms.optimize_traffic("downtown")
        assert "alternate_routes" in result

    def test_congestion_status_heavy(self):
        tms = TrafficManagementSystem(Tier.PRO)
        result = tms.monitor_congestion("downtown")
        assert result["status"] == "heavy"

    def test_congestion_status_light(self):
        tms = TrafficManagementSystem(Tier.PRO)
        result = tms.monitor_congestion("suburbs")
        assert result["status"] == "light"


# ===========================================================================
# EnergyManagementSystem
# ===========================================================================

class TestEnergyManagementSystem:
    def test_default_tier_is_free(self):
        ems = EnergyManagementSystem()
        assert ems.tier == Tier.FREE

    def test_monitor_grid_returns_dict(self):
        ems = EnergyManagementSystem(Tier.FREE)
        result = ems.monitor_grid("commercial_center")
        assert isinstance(result, dict)

    def test_monitor_grid_has_required_keys(self):
        ems = EnergyManagementSystem(Tier.FREE)
        result = ems.monitor_grid("commercial_center")
        for key in ("district", "load_mw", "capacity_mw", "utilization_pct", "grid_status"):
            assert key in result

    def test_optimize_energy_returns_dict(self):
        ems = EnergyManagementSystem(Tier.FREE)
        result = ems.optimize_energy("commercial_center")
        assert isinstance(result, dict)

    def test_free_tier_limited_to_one_district(self):
        ems = EnergyManagementSystem(Tier.FREE)
        ems.monitor_grid("commercial_center")
        with pytest.raises(SmartCityInfrastructureError):
            ems.monitor_grid("residential_north")

    def test_pro_tier_allows_10_districts(self):
        ems = EnergyManagementSystem(Tier.PRO)
        districts = list(EnergyManagementSystem.GRID_DATA.keys())[:10]
        for d in districts:
            ems.monitor_grid(d)
        assert len(ems._monitored_districts) == 10

    def test_predict_demand_free_raises(self):
        ems = EnergyManagementSystem(Tier.FREE)
        ems.monitor_grid("commercial_center")
        with pytest.raises(SmartCityInfrastructureError):
            ems.predict_demand("commercial_center", 9)

    def test_predict_demand_pro(self):
        ems = EnergyManagementSystem(Tier.PRO)
        result = ems.predict_demand("commercial_center", 9)
        assert "predicted_load_mw" in result
        assert "headroom_mw" in result

    def test_pro_monitor_grid_has_renewable_pct(self):
        ems = EnergyManagementSystem(Tier.PRO)
        result = ems.monitor_grid("university")
        assert "renewable_pct" in result

    def test_enterprise_predict_demand_has_forecast(self):
        ems = EnergyManagementSystem(Tier.ENTERPRISE)
        result = ems.predict_demand("hospital_district", 10)
        assert result.get("30day_forecast_available") is True

    def test_optimize_energy_has_strategy(self):
        ems = EnergyManagementSystem(Tier.PRO)
        result = ems.optimize_energy("industrial_east")
        assert "optimization_strategy" in result
        assert "estimated_savings_pct" in result


# ===========================================================================
# PublicSafetyMonitor
# ===========================================================================

class TestPublicSafetyMonitor:
    def test_default_tier_is_free(self):
        psm = PublicSafetyMonitor()
        assert psm.tier == Tier.FREE

    def test_monitor_safety_returns_dict(self):
        psm = PublicSafetyMonitor(Tier.FREE)
        result = psm.monitor_safety("downtown")
        assert isinstance(result, dict)

    def test_monitor_safety_has_required_keys(self):
        psm = PublicSafetyMonitor(Tier.FREE)
        result = psm.monitor_safety("downtown")
        for key in ("zone", "crime_index", "safety_level", "incidents_last_24h"):
            assert key in result

    def test_safety_level_high_risk(self):
        psm = PublicSafetyMonitor(Tier.PRO)
        result = psm.monitor_safety("port")
        assert result["safety_level"] == "high_risk"

    def test_safety_level_low_risk(self):
        psm = PublicSafetyMonitor(Tier.PRO)
        result = psm.monitor_safety("suburbs")
        assert result["safety_level"] == "low_risk"

    def test_alert_incidents_returns_dict(self):
        psm = PublicSafetyMonitor(Tier.FREE)
        result = psm.alert_incidents("downtown")
        assert isinstance(result, dict)
        assert "alerts" in result

    def test_free_alerts_capped_at_3(self):
        psm = PublicSafetyMonitor(Tier.FREE)
        result = psm.alert_incidents("port")
        assert len(result["alerts"]) <= 3

    def test_pro_alerts_not_capped(self):
        psm = PublicSafetyMonitor(Tier.PRO)
        result = psm.alert_incidents("port")
        assert result["total_active_incidents"] == len(result["alerts"])

    def test_deploy_resources_free_raises(self):
        psm = PublicSafetyMonitor(Tier.FREE)
        psm.monitor_safety("downtown")
        with pytest.raises(SmartCityInfrastructureError):
            psm.deploy_resources("downtown", "fire")

    def test_deploy_resources_pro(self):
        psm = PublicSafetyMonitor(Tier.PRO)
        result = psm.deploy_resources("downtown", "fire")
        assert result["dispatch_confirmed"] is True
        assert "resources_deployed" in result

    def test_deploy_resources_enterprise_has_optimal_route(self):
        psm = PublicSafetyMonitor(Tier.ENTERPRISE)
        result = psm.deploy_resources("downtown", "accident")
        assert "optimal_route" in result

    def test_free_limited_to_one_zone(self):
        psm = PublicSafetyMonitor(Tier.FREE)
        psm.monitor_safety("downtown")
        with pytest.raises(SmartCityInfrastructureError):
            psm.monitor_safety("north")


# ===========================================================================
# TaxSystemAI
# ===========================================================================

class TestTaxSystemAI:
    def test_calculate_tax_returns_dict(self):
        tax = TaxSystemAI(Tier.FREE)
        result = tax.calculate_tax({"citizen_id": "C001", "annual_income": 60000})
        assert isinstance(result, dict)

    def test_calculate_tax_has_required_keys(self):
        tax = TaxSystemAI(Tier.FREE)
        result = tax.calculate_tax({"citizen_id": "C001", "annual_income": 60000})
        for key in ("tax_owed", "effective_rate_pct", "taxable_income"):
            assert key in result

    def test_tax_owed_positive(self):
        tax = TaxSystemAI(Tier.FREE)
        result = tax.calculate_tax({"annual_income": 80000})
        assert result["tax_owed"] > 0

    def test_zero_income_zero_tax(self):
        tax = TaxSystemAI(Tier.FREE)
        result = tax.calculate_tax({"annual_income": 0})
        assert result["tax_owed"] == 0

    def test_pro_applies_deductions(self):
        tax = TaxSystemAI(Tier.PRO)
        result = tax.calculate_tax({"annual_income": 80000, "deductions": 10000})
        assert result["taxable_income"] == 70000

    def test_enterprise_has_optimizations(self):
        tax = TaxSystemAI(Tier.ENTERPRISE)
        result = tax.calculate_tax({"annual_income": 150000})
        assert "optimization_opportunities" in result

    def test_optimize_policy_free_raises(self):
        tax = TaxSystemAI(Tier.FREE)
        with pytest.raises(GovernmentAIError):
            tax.optimize_tax_policy({"population": 100000})

    def test_optimize_policy_pro(self):
        tax = TaxSystemAI(Tier.PRO)
        result = tax.optimize_tax_policy({"population": 100000, "current_revenue_usd": 500_000_000})
        assert "recommended_rate_adjustment_pct" in result

    def test_generate_report_free_raises(self):
        tax = TaxSystemAI(Tier.FREE)
        with pytest.raises(GovernmentAIError):
            tax.generate_tax_report("2024-Q1")

    def test_generate_report_pro(self):
        tax = TaxSystemAI(Tier.PRO)
        result = tax.generate_tax_report("2024-Q1")
        assert result["period"] == "2024-Q1"
        assert "total_revenue_collected_usd" in result

    def test_enterprise_report_has_audit(self):
        tax = TaxSystemAI(Tier.ENTERPRISE)
        result = tax.generate_tax_report("2024-Q1")
        assert "audit_recommendations" in result


# ===========================================================================
# CensusCollector
# ===========================================================================

class TestCensusCollector:
    def test_collect_census_returns_dict(self):
        cc = CensusCollector(Tier.FREE)
        result = cc.collect_census("city_center")
        assert isinstance(result, dict)

    def test_collect_census_has_population(self):
        cc = CensusCollector(Tier.FREE)
        result = cc.collect_census("city_center")
        assert "population" in result and result["population"] > 0

    def test_pro_census_has_median_age(self):
        cc = CensusCollector(Tier.PRO)
        result = cc.collect_census("north_district")
        assert "median_age" in result

    def test_analyze_demographics_free_raises(self):
        cc = CensusCollector(Tier.FREE)
        with pytest.raises(GovernmentAIError):
            cc.analyze_demographics("city_center")

    def test_analyze_demographics_pro(self):
        cc = CensusCollector(Tier.PRO)
        result = cc.analyze_demographics("city_center")
        assert "age_distribution" in result

    def test_enterprise_demographics_has_income_quintiles(self):
        cc = CensusCollector(Tier.ENTERPRISE)
        result = cc.analyze_demographics("suburbs")
        assert "income_quintiles" in result

    def test_project_population_free_raises(self):
        cc = CensusCollector(Tier.FREE)
        with pytest.raises(GovernmentAIError):
            cc.project_population("city_center", 10)

    def test_project_population_pro(self):
        cc = CensusCollector(Tier.PRO)
        result = cc.project_population("city_center", 5)
        assert result["projected_population"] > result["current_population"]

    def test_enterprise_projection_has_scenarios(self):
        cc = CensusCollector(Tier.ENTERPRISE)
        result = cc.project_population("suburbs", 10)
        assert "scenarios" in result
        assert "optimistic" in result["scenarios"]


# ===========================================================================
# PolicyModelingBot
# ===========================================================================

class TestPolicyModelingBot:
    def test_model_policy_returns_dict(self):
        pmb = PolicyModelingBot(Tier.FREE)
        result = pmb.model_policy({"name": "Green Energy Act", "domain": "environment"})
        assert isinstance(result, dict)

    def test_model_policy_has_feasibility(self):
        pmb = PolicyModelingBot(Tier.FREE)
        result = pmb.model_policy({"name": "Housing Reform", "budget_usd": 2_000_000})
        assert "feasibility" in result

    def test_pro_policy_has_risk_level(self):
        pmb = PolicyModelingBot(Tier.PRO)
        result = pmb.model_policy({"name": "Transit Expansion", "budget_usd": 50_000_000})
        assert "risk_level" in result

    def test_simulate_impact_free_raises(self):
        pmb = PolicyModelingBot(Tier.FREE)
        with pytest.raises(GovernmentAIError):
            pmb.simulate_impact({"name": "Test"}, 100000)

    def test_simulate_impact_pro(self):
        pmb = PolicyModelingBot(Tier.PRO)
        result = pmb.simulate_impact({"name": "Transit", "budget_usd": 10_000_000}, 500000)
        assert "roi_pct" in result
        assert result["estimated_benefit_usd"] > 0

    def test_enterprise_simulation_has_gdp_impact(self):
        pmb = PolicyModelingBot(Tier.ENTERPRISE)
        result = pmb.simulate_impact({"name": "Green Deal", "budget_usd": 100_000_000}, 1_000_000)
        assert "gdp_impact_pct" in result
        assert result["simulation_runs"] == 10000

    def test_recommend_policy_free_raises(self):
        pmb = PolicyModelingBot(Tier.FREE)
        with pytest.raises(GovernmentAIError):
            pmb.recommend_policy("transportation")

    def test_recommend_policy_pro(self):
        pmb = PolicyModelingBot(Tier.PRO)
        result = pmb.recommend_policy("transportation")
        assert "top_recommendations" in result
        assert len(result["top_recommendations"]) == 2

    def test_recommend_policy_enterprise_more_items(self):
        pmb = PolicyModelingBot(Tier.ENTERPRISE)
        result = pmb.recommend_policy("transportation")
        assert len(result["top_recommendations"]) > 2

    def test_enterprise_recommendation_has_cities(self):
        pmb = PolicyModelingBot(Tier.ENTERPRISE)
        result = pmb.recommend_policy("environment")
        assert "similar_cities_adopted" in result


# ===========================================================================
# SmartCityBot — main bot
# ===========================================================================

class TestSmartCityBotInstantiation:
    def test_default_tier_is_free(self):
        bot = SmartCityBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = SmartCityBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = SmartCityBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = SmartCityBot()
        assert bot.config is not None

    def test_subsystems_initialized(self):
        bot = SmartCityBot(tier=Tier.PRO)
        assert isinstance(bot.traffic, TrafficManagementSystem)
        assert isinstance(bot.energy, EnergyManagementSystem)
        assert isinstance(bot.safety, PublicSafetyMonitor)
        assert isinstance(bot.tax, TaxSystemAI)
        assert isinstance(bot.census, CensusCollector)
        assert isinstance(bot.policy, PolicyModelingBot)


class TestSmartCityBotMonitorTraffic:
    def test_monitor_traffic_returns_dict(self):
        bot = SmartCityBot(Tier.PRO)
        result = bot.monitor_traffic("downtown")
        assert isinstance(result, dict)

    def test_monitor_traffic_has_service_key(self):
        bot = SmartCityBot(Tier.PRO)
        result = bot.monitor_traffic("downtown")
        assert result["service"] == "traffic"

    def test_free_tier_second_zone_raises(self):
        bot = SmartCityBot(Tier.FREE)
        bot.monitor_traffic("downtown")
        with pytest.raises(SmartCityBotError):
            bot.monitor_traffic("north")

    def test_logs_activity(self):
        bot = SmartCityBot(Tier.PRO)
        bot.monitor_traffic("downtown")
        assert len(bot._activity_log) == 1


class TestSmartCityBotManageEnergy:
    def test_manage_energy_returns_dict(self):
        bot = SmartCityBot(Tier.PRO)
        result = bot.manage_energy("commercial_center")
        assert isinstance(result, dict)

    def test_manage_energy_has_service_key(self):
        bot = SmartCityBot(Tier.PRO)
        result = bot.manage_energy("commercial_center")
        assert result["service"] == "energy"

    def test_free_second_district_raises(self):
        bot = SmartCityBot(Tier.FREE)
        bot.manage_energy("commercial_center")
        with pytest.raises(SmartCityBotError):
            bot.manage_energy("industrial_east")


class TestSmartCityBotMonitorSafety:
    def test_monitor_safety_returns_dict(self):
        bot = SmartCityBot(Tier.PRO)
        result = bot.monitor_safety("downtown")
        assert isinstance(result, dict)

    def test_monitor_safety_has_alerts(self):
        bot = SmartCityBot(Tier.PRO)
        result = bot.monitor_safety("downtown")
        assert "alerts" in result


class TestSmartCityBotGovernmentService:
    def test_tax_calculate_service(self):
        bot = SmartCityBot(Tier.FREE)
        result = bot.government_service("tax_calculate", {"annual_income": 50000})
        assert "tax_owed" in result

    def test_census_collect_service(self):
        bot = SmartCityBot(Tier.FREE)
        result = bot.government_service("census_collect", {"region": "city_center"})
        assert "population" in result

    def test_policy_model_service(self):
        bot = SmartCityBot(Tier.FREE)
        result = bot.government_service("policy_model", {"name": "Green Act", "budget_usd": 1_000_000})
        assert "feasibility" in result

    def test_tax_report_requires_pro(self):
        bot = SmartCityBot(Tier.FREE)
        with pytest.raises(SmartCityBotError):
            bot.government_service("tax_report", {"period": "2024-Q1"})

    def test_census_demographics_requires_pro(self):
        bot = SmartCityBot(Tier.FREE)
        with pytest.raises(SmartCityBotError):
            bot.government_service("census_demographics", {"region": "city_center"})

    def test_unknown_service_raises(self):
        bot = SmartCityBot(Tier.PRO)
        with pytest.raises(SmartCityBotError):
            bot.government_service("launch_rockets", {})

    def test_policy_recommend_pro(self):
        bot = SmartCityBot(Tier.PRO)
        result = bot.government_service("policy_recommend", {"domain": "housing"})
        assert "top_recommendations" in result


class TestSmartCityBotDashboard:
    def test_dashboard_returns_dict(self):
        bot = SmartCityBot(Tier.FREE)
        result = bot.get_city_dashboard()
        assert isinstance(result, dict)

    def test_dashboard_has_required_keys(self):
        bot = SmartCityBot(Tier.FREE)
        result = bot.get_city_dashboard()
        for key in ("bot", "tier", "features", "services_available", "upgrade_available"):
            assert key in result

    def test_free_dashboard_has_upgrade(self):
        bot = SmartCityBot(Tier.FREE)
        result = bot.get_city_dashboard()
        assert result["upgrade_available"] is True
        assert "upgrade_to" in result

    def test_enterprise_dashboard_no_upgrade(self):
        bot = SmartCityBot(Tier.ENTERPRISE)
        result = bot.get_city_dashboard()
        assert result["upgrade_available"] is False

    def test_enterprise_dashboard_has_api_access(self):
        bot = SmartCityBot(Tier.ENTERPRISE)
        result = bot.get_city_dashboard()
        assert result.get("api_access") is True

    def test_pro_dashboard_has_analytics(self):
        bot = SmartCityBot(Tier.PRO)
        result = bot.get_city_dashboard()
        assert result.get("advanced_analytics") is True

    def test_activity_count_increments(self):
        bot = SmartCityBot(Tier.PRO)
        bot.monitor_traffic("downtown")
        bot.manage_energy("commercial_center")
        result = bot.get_city_dashboard()
        assert result["activity_count"] == 2

    def test_describe_tier_returns_string(self):
        bot = SmartCityBot(Tier.FREE)
        output = bot.describe_tier()
        assert isinstance(output, str)
        assert "Free" in output
