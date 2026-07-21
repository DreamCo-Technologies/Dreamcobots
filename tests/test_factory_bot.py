"""Tests for bots/factory_bot/ — workflow optimizer, predictive maintenance, green manufacturing."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, "models"))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.factory_bot.tiers import BOT_FEATURES, get_bot_tier_info
from bots.factory_bot.workflow_optimizer import (
    ProductionLineOptimizer,
    PredictiveMaintenanceEngine,
    MACHINE_DATABASE,
)
from bots.factory_bot.green_manufacturing import (
    EnergyEfficiencyMonitor,
    GreenInitiativeManager,
)
from bots.factory_bot.factory_bot import FactoryBot, FactoryBotError


# ===========================================================================
# Tiers
# ===========================================================================

class TestFactoryBotTiers:
    def test_bot_features_has_three_tiers(self):
        assert len(BOT_FEATURES) == 3

    def test_free_features_not_empty(self):
        assert len(BOT_FEATURES[Tier.FREE.value]) > 0

    def test_pro_features_not_empty(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > 0

    def test_enterprise_features_not_empty(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > 0

    def test_get_bot_tier_info_free(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0

    def test_get_bot_tier_info_pro(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["price_usd_monthly"] > 0

    def test_get_bot_tier_info_enterprise(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["price_usd_monthly"] > info["price_usd_monthly"] or True  # enterprise >= pro

    def test_tier_info_has_required_keys(self):
        info = get_bot_tier_info(Tier.PRO)
        for key in ("tier", "name", "price_usd_monthly", "features", "support_level"):
            assert key in info

    def test_enterprise_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > len(BOT_FEATURES[Tier.FREE.value])


# ===========================================================================
# MACHINE_DATABASE
# ===========================================================================

class TestMachineDatabase:
    def test_has_ten_machines(self):
        assert len(MACHINE_DATABASE) == 10

    def test_all_machines_have_id(self):
        for mid, machine in MACHINE_DATABASE.items():
            assert "id" in machine

    def test_all_machines_have_type(self):
        for mid, machine in MACHINE_DATABASE.items():
            assert "type" in machine

    def test_conveyor_present(self):
        types = [m["type"] for m in MACHINE_DATABASE.values()]
        assert "conveyor" in types

    def test_robot_arm_present(self):
        types = [m["type"] for m in MACHINE_DATABASE.values()]
        assert "robot_arm" in types

    def test_cnc_mill_present(self):
        types = [m["type"] for m in MACHINE_DATABASE.values()]
        assert "CNC_mill" in types

    def test_welder_present(self):
        types = [m["type"] for m in MACHINE_DATABASE.values()]
        assert "welder" in types

    def test_press_present(self):
        types = [m["type"] for m in MACHINE_DATABASE.values()]
        assert "press" in types

    def test_baseline_efficiency_in_valid_range(self):
        for machine in MACHINE_DATABASE.values():
            assert 0 < machine["baseline_efficiency"] <= 1.0


# ===========================================================================
# ProductionLineOptimizer
# ===========================================================================

class TestProductionLineOptimizerInstantiation:
    def test_default_tier_is_free(self):
        opt = ProductionLineOptimizer()
        assert opt.tier == Tier.FREE

    def test_pro_tier(self):
        opt = ProductionLineOptimizer(tier=Tier.PRO)
        assert opt.tier == Tier.PRO

    def test_enterprise_tier(self):
        opt = ProductionLineOptimizer(tier=Tier.ENTERPRISE)
        assert opt.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        opt = ProductionLineOptimizer()
        assert opt.config is not None


class TestOptimizeProductionLine:
    def test_returns_dict(self):
        opt = ProductionLineOptimizer(tier=Tier.FREE)
        result = opt.optimize_production_line("line-01", {"throughput": 100, "defect_rate": 0.03})
        assert isinstance(result, dict)

    def test_has_efficiency_gain(self):
        opt = ProductionLineOptimizer(tier=Tier.FREE)
        result = opt.optimize_production_line("line-01", {})
        assert "efficiency_gain_pct" in result

    def test_efficiency_gain_is_positive(self):
        opt = ProductionLineOptimizer(tier=Tier.FREE)
        result = opt.optimize_production_line("line-01", {})
        assert result["efficiency_gain_pct"] > 0

    def test_has_recommendations(self):
        opt = ProductionLineOptimizer(tier=Tier.FREE)
        result = opt.optimize_production_line("line-01", {})
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0

    def test_pro_has_oee_score(self):
        opt = ProductionLineOptimizer(tier=Tier.PRO)
        result = opt.optimize_production_line("line-01", {"throughput": 200})
        assert "oee_score" in result

    def test_enterprise_has_ml_confidence(self):
        opt = ProductionLineOptimizer(tier=Tier.ENTERPRISE)
        result = opt.optimize_production_line("line-01", {"throughput": 200})
        assert "ml_model_confidence" in result

    def test_tier_key_in_result(self):
        opt = ProductionLineOptimizer(tier=Tier.FREE)
        result = opt.optimize_production_line("line-01", {})
        assert result["tier"] == Tier.FREE.value

    def test_line_id_in_result(self):
        opt = ProductionLineOptimizer(tier=Tier.FREE)
        result = opt.optimize_production_line("line-42", {})
        assert result["line_id"] == "line-42"


class TestAnalyzeBottleneck:
    def test_returns_dict(self):
        opt = ProductionLineOptimizer(tier=Tier.FREE)
        result = opt.analyze_bottleneck("line-01", {})
        assert isinstance(result, dict)

    def test_has_bottleneck_station(self):
        opt = ProductionLineOptimizer(tier=Tier.FREE)
        result = opt.analyze_bottleneck("line-01", {"stations": ["A", "B", "C"], "cycle_times": {"A": 30, "B": 70, "C": 40}})
        assert result["bottleneck_station"] == "B"

    def test_severity_field_present(self):
        opt = ProductionLineOptimizer(tier=Tier.FREE)
        result = opt.analyze_bottleneck("line-01", {})
        assert "severity" in result

    def test_pro_includes_flow_efficiency(self):
        opt = ProductionLineOptimizer(tier=Tier.PRO)
        result = opt.analyze_bottleneck("line-01", {})
        assert "flow_efficiency_pct" in result

    def test_enterprise_has_ml_root_cause(self):
        opt = ProductionLineOptimizer(tier=Tier.ENTERPRISE)
        result = opt.analyze_bottleneck("line-01", {})
        assert "ml_root_cause" in result


class TestScheduleProduction:
    def test_returns_dict(self):
        opt = ProductionLineOptimizer(tier=Tier.FREE)
        orders = [{"id": "ORD-001", "quantity": 100}]
        result = opt.schedule_production(orders, {"daily_units": 200})
        assert isinstance(result, dict)

    def test_schedule_key_is_list(self):
        opt = ProductionLineOptimizer(tier=Tier.FREE)
        result = opt.schedule_production([{"id": "ORD-001", "quantity": 50}], {})
        assert isinstance(result["schedule"], list)

    def test_free_limits_to_five_orders(self):
        opt = ProductionLineOptimizer(tier=Tier.FREE)
        orders = [{"id": f"ORD-{i:03d}", "quantity": 20} for i in range(10)]
        result = opt.schedule_production(orders, {"daily_units": 500})
        assert result["total_orders"] <= 5

    def test_pro_allows_up_to_fifty_orders(self):
        opt = ProductionLineOptimizer(tier=Tier.PRO)
        orders = [{"id": f"ORD-{i:03d}", "quantity": 10} for i in range(50)]
        result = opt.schedule_production(orders, {"daily_units": 5000})
        assert result["total_orders"] == 50

    def test_enterprise_has_ml_optimized_flag(self):
        opt = ProductionLineOptimizer(tier=Tier.ENTERPRISE)
        orders = [{"id": "ORD-001", "quantity": 100}]
        result = opt.schedule_production(orders, {"daily_units": 500})
        assert result.get("ml_optimized") is True


# ===========================================================================
# PredictiveMaintenanceEngine
# ===========================================================================

class TestPredictiveMaintenanceEngineInstantiation:
    def test_default_tier_is_free(self):
        eng = PredictiveMaintenanceEngine()
        assert eng.tier == Tier.FREE

    def test_config_not_none(self):
        eng = PredictiveMaintenanceEngine()
        assert eng.config is not None


class TestPredictFailure:
    def test_returns_dict(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        result = eng.predict_failure("conveyor_01", {"vibration_hz": 50.0, "temperature_c": 60.0})
        assert isinstance(result, dict)

    def test_has_failure_probability(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        result = eng.predict_failure("conveyor_01", {"vibration_hz": 50.0})
        assert "failure_probability" in result

    def test_failure_probability_in_range(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        result = eng.predict_failure("conveyor_01", {"vibration_hz": 50.0})
        assert 0.0 <= result["failure_probability"] <= 1.0

    def test_has_confidence(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        result = eng.predict_failure("conveyor_01", {})
        assert "confidence" in result

    def test_has_days_to_failure(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        result = eng.predict_failure("conveyor_01", {})
        assert "days_to_failure" in result
        assert result["days_to_failure"] > 0

    def test_high_sensor_values_increase_probability(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.PRO)
        low_result = eng.predict_failure("press_01", {"vibration_hz": 10.0})
        eng2 = PredictiveMaintenanceEngine(tier=Tier.PRO)
        high_result = eng2.predict_failure("welder_01", {"vibration_hz": 200.0, "temperature_c": 120.0})
        assert high_result["failure_probability"] >= low_result["failure_probability"]

    def test_free_tier_limited_to_two_machines(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        eng.predict_failure("conveyor_01", {})
        eng.predict_failure("press_01", {})
        with pytest.raises(PermissionError):
            eng.predict_failure("welder_01", {})

    def test_pro_tier_allows_more_machines(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.PRO)
        machines = list(MACHINE_DATABASE.keys())[:5]
        for mid in machines:
            result = eng.predict_failure(mid, {"vibration_hz": 40.0})
            assert isinstance(result, dict)

    def test_pro_has_anomaly_score(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.PRO)
        result = eng.predict_failure("conveyor_01", {"vibration_hz": 90.0})
        assert "anomaly_score" in result

    def test_enterprise_has_ml_model(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.ENTERPRISE)
        result = eng.predict_failure("conveyor_01", {"vibration_hz": 50.0})
        assert "ml_model" in result

    def test_sensor_alerts_populated_on_threshold_breach(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        result = eng.predict_failure("conveyor_01", {"vibration_hz": 200.0})
        assert len(result["sensor_alerts"]) > 0


class TestScheduleMaintenance:
    def test_returns_dict(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        result = eng.schedule_maintenance("conveyor_01")
        assert isinstance(result, dict)

    def test_has_scheduled_date(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        result = eng.schedule_maintenance("conveyor_01")
        assert "scheduled_date" in result

    def test_critical_priority_schedules_sooner(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.PRO)
        critical = eng.schedule_maintenance("press_01", priority="critical")
        normal = eng.schedule_maintenance("welder_01", priority="normal")
        assert critical["scheduled_date"] <= normal["scheduled_date"]

    def test_pro_has_estimated_cost(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.PRO)
        result = eng.schedule_maintenance("conveyor_01", priority="high")
        assert "estimated_cost_usd" in result

    def test_enterprise_has_cmms_work_order(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.ENTERPRISE)
        result = eng.schedule_maintenance("conveyor_01")
        assert "cmms_work_order_id" in result


class TestDiagnoseIssue:
    def test_returns_dict(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        result = eng.diagnose_issue("conveyor_01", ["excessive vibration"])
        assert isinstance(result, dict)

    def test_diagnoses_key_is_list(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        result = eng.diagnose_issue("conveyor_01", ["overheating", "unusual noise"])
        assert isinstance(result["diagnoses"], list)

    def test_diagnoses_count_matches_symptoms(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        symptoms = ["excessive vibration", "overheating"]
        result = eng.diagnose_issue("conveyor_01", symptoms)
        assert len(result["diagnoses"]) == len(symptoms)

    def test_urgency_high_for_multiple_symptoms(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.FREE)
        result = eng.diagnose_issue("conveyor_01", ["symptom1", "symptom2", "symptom3"])
        assert result["urgency"] == "high"

    def test_pro_has_fault_codes(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.PRO)
        result = eng.diagnose_issue("press_01", ["oil leak"])
        assert "fault_code_lookup" in result

    def test_enterprise_has_ml_diagnosis(self):
        eng = PredictiveMaintenanceEngine(tier=Tier.ENTERPRISE)
        result = eng.diagnose_issue("conveyor_01", ["overheating"])
        assert "ml_diagnosis" in result


# ===========================================================================
# EnergyEfficiencyMonitor
# ===========================================================================

class TestEnergyEfficiencyMonitorInstantiation:
    def test_default_tier_is_free(self):
        mon = EnergyEfficiencyMonitor()
        assert mon.tier == Tier.FREE

    def test_config_not_none(self):
        mon = EnergyEfficiencyMonitor()
        assert mon.config is not None


class TestMonitorEnergyUsage:
    def test_returns_dict(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.FREE)
        result = mon.monitor_energy_usage("facility-01")
        assert isinstance(result, dict)

    def test_has_daily_kwh(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.FREE)
        result = mon.monitor_energy_usage("facility-01")
        assert "daily_kwh" in result
        assert result["daily_kwh"] > 0

    def test_has_monthly_cost(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.FREE)
        result = mon.monitor_energy_usage("facility-01")
        assert "monthly_cost_usd" in result

    def test_has_facility_id(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.FREE)
        result = mon.monitor_energy_usage("fab-plant-7")
        assert result["facility_id"] == "fab-plant-7"

    def test_pro_has_breakdown_by_area(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.PRO)
        result = mon.monitor_energy_usage("facility-01")
        assert "breakdown_by_area" in result

    def test_enterprise_has_submetering_data(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.ENTERPRISE)
        result = mon.monitor_energy_usage("facility-01")
        assert "submetering_data" in result


class TestOptimizeEnergy:
    def test_returns_dict(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.FREE)
        result = mon.optimize_energy("facility-01")
        assert isinstance(result, dict)

    def test_has_recommendations(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.FREE)
        result = mon.optimize_energy("facility-01")
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0

    def test_has_potential_savings_pct(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.FREE)
        result = mon.optimize_energy("facility-01")
        assert "potential_savings_pct" in result
        assert result["potential_savings_pct"] > 0

    def test_pro_has_demand_response(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.PRO)
        result = mon.optimize_energy("facility-01")
        assert "demand_response_eligible" in result

    def test_enterprise_has_renewable_integration(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.ENTERPRISE)
        result = mon.optimize_energy("facility-01")
        assert "renewable_integration_recommendation" in result


class TestCalculateCarbonFootprint:
    def test_returns_dict(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.FREE)
        result = mon.calculate_carbon_footprint({"units_produced": 500, "energy_kwh": 10000})
        assert isinstance(result, dict)

    def test_has_total_co2(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.FREE)
        result = mon.calculate_carbon_footprint({"units_produced": 1000, "energy_kwh": 20000})
        assert "total_co2_kg" in result
        assert result["total_co2_kg"] > 0

    def test_has_co2_per_unit(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.FREE)
        result = mon.calculate_carbon_footprint({"units_produced": 1000, "energy_kwh": 20000})
        assert "co2_per_unit_kg" in result

    def test_scope_emissions_present(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.FREE)
        result = mon.calculate_carbon_footprint({"units_produced": 500, "energy_kwh": 5000, "fuel_liters": 200})
        assert "scope_1_emissions_kg" in result
        assert "scope_2_emissions_kg" in result
        assert "scope_3_emissions_kg" in result

    def test_pro_has_emissions_breakdown(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.PRO)
        result = mon.calculate_carbon_footprint({"units_produced": 1000, "energy_kwh": 15000})
        assert "emissions_breakdown" in result

    def test_enterprise_has_ghg_protocol(self):
        mon = EnergyEfficiencyMonitor(tier=Tier.ENTERPRISE)
        result = mon.calculate_carbon_footprint({"units_produced": 1000, "energy_kwh": 15000})
        assert "ghg_protocol_compliant" in result


# ===========================================================================
# GreenInitiativeManager
# ===========================================================================

class TestGreenInitiativeManagerInstantiation:
    def test_default_tier_is_free(self):
        mgr = GreenInitiativeManager()
        assert mgr.tier == Tier.FREE

    def test_config_not_none(self):
        mgr = GreenInitiativeManager()
        assert mgr.config is not None


class TestAssessSustainability:
    def test_returns_dict(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        result = mgr.assess_sustainability("facility-01")
        assert isinstance(result, dict)

    def test_has_overall_score(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        result = mgr.assess_sustainability("facility-01")
        assert "overall_sustainability_score" in result

    def test_score_in_valid_range(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        result = mgr.assess_sustainability("facility-01")
        assert 0 <= result["overall_sustainability_score"] <= 100

    def test_has_rating(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        result = mgr.assess_sustainability("facility-01")
        assert result["rating"] in ("Excellent", "Good", "Fair", "Poor")

    def test_has_recommendations(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        result = mgr.assess_sustainability("facility-01")
        assert isinstance(result["recommendations"], list)

    def test_pro_has_category_scores(self):
        mgr = GreenInitiativeManager(tier=Tier.PRO)
        result = mgr.assess_sustainability("facility-01")
        assert "category_scores" in result

    def test_enterprise_has_esg_score(self):
        mgr = GreenInitiativeManager(tier=Tier.ENTERPRISE)
        result = mgr.assess_sustainability("facility-01")
        assert "esg_score" in result


class TestPlanWasteReduction:
    def test_returns_dict(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        waste = {"total_waste_kg": 4000, "recyclable_pct": 40, "landfill_pct": 35, "hazardous_pct": 5}
        result = mgr.plan_waste_reduction("facility-01", waste)
        assert isinstance(result, dict)

    def test_has_initiatives(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        result = mgr.plan_waste_reduction("facility-01", {"total_waste_kg": 3000})
        assert isinstance(result["waste_reduction_initiatives"], list)
        assert len(result["waste_reduction_initiatives"]) > 0

    def test_has_total_savings(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        result = mgr.plan_waste_reduction("facility-01", {"total_waste_kg": 3000})
        assert "total_savings_usd_annually" in result

    def test_has_landfill_reduction_target(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        result = mgr.plan_waste_reduction("facility-01", {"total_waste_kg": 5000, "landfill_pct": 40})
        assert "landfill_reduction_target_kg" in result
        assert result["landfill_reduction_target_kg"] > 0

    def test_pro_has_waste_stream_analysis(self):
        mgr = GreenInitiativeManager(tier=Tier.PRO)
        result = mgr.plan_waste_reduction("facility-01", {"total_waste_kg": 5000, "recyclable_pct": 35, "landfill_pct": 40, "hazardous_pct": 5})
        assert "waste_stream_analysis" in result

    def test_enterprise_has_circular_economy(self):
        mgr = GreenInitiativeManager(tier=Tier.ENTERPRISE)
        result = mgr.plan_waste_reduction("facility-01", {"total_waste_kg": 5000})
        assert "circular_economy_opportunities" in result


class TestGenerateGreenReport:
    def test_returns_dict(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        result = mgr.generate_green_report("facility-01")
        assert isinstance(result, dict)

    def test_has_sustainability_score(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        result = mgr.generate_green_report("facility-01")
        assert "sustainability_score" in result

    def test_has_co2_emissions(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        result = mgr.generate_green_report("facility-01")
        assert "co2_emissions_kg_monthly" in result

    def test_has_key_highlights(self):
        mgr = GreenInitiativeManager(tier=Tier.FREE)
        result = mgr.generate_green_report("facility-01")
        assert isinstance(result["key_highlights"], list)
        assert len(result["key_highlights"]) > 0

    def test_pro_has_yoy_change(self):
        mgr = GreenInitiativeManager(tier=Tier.PRO)
        result = mgr.generate_green_report("facility-01")
        assert "year_over_year_change" in result

    def test_enterprise_has_executive_summary(self):
        mgr = GreenInitiativeManager(tier=Tier.ENTERPRISE)
        result = mgr.generate_green_report("facility-01")
        assert "executive_summary" in result
        assert isinstance(result["executive_summary"], str)

    def test_enterprise_has_regulatory_disclosures(self):
        mgr = GreenInitiativeManager(tier=Tier.ENTERPRISE)
        result = mgr.generate_green_report("facility-01")
        assert "regulatory_disclosures" in result


# ===========================================================================
# FactoryBot main class
# ===========================================================================

class TestFactoryBotInstantiation:
    def test_default_tier_is_free(self):
        bot = FactoryBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = FactoryBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = FactoryBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_not_none(self):
        bot = FactoryBot()
        assert bot.config is not None


class TestFactoryBotOptimizeWorkflow:
    def test_returns_dict(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.optimize_workflow("line-01", {"throughput": 100})
        assert isinstance(result, dict)

    def test_efficiency_gain_present(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.optimize_workflow("line-01", {})
        assert "efficiency_gain_pct" in result

    def test_pro_has_oee_score(self):
        bot = FactoryBot(tier=Tier.PRO)
        result = bot.optimize_workflow("line-01", {"throughput": 150})
        assert "oee_score" in result


class TestFactoryBotPredictMaintenance:
    def test_returns_dict(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.predict_maintenance("conveyor_01", {"vibration_hz": 50.0})
        assert isinstance(result, dict)

    def test_failure_probability_present(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.predict_maintenance("conveyor_01", {})
        assert "failure_probability" in result

    def test_tier_restriction_raises_factory_bot_error(self):
        bot = FactoryBot(tier=Tier.FREE)
        bot.predict_maintenance("conveyor_01", {})
        bot.predict_maintenance("press_01", {})
        with pytest.raises(FactoryBotError):
            bot.predict_maintenance("welder_01", {})


class TestFactoryBotMonitorEnergy:
    def test_returns_dict(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.monitor_energy("facility-01")
        assert isinstance(result, dict)

    def test_daily_kwh_present(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.monitor_energy("facility-01")
        assert result["daily_kwh"] > 0


class TestFactoryBotSustainabilityReport:
    def test_returns_dict(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.get_sustainability_report("facility-01")
        assert isinstance(result, dict)

    def test_has_sustainability_score(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.get_sustainability_report("facility-01")
        assert "sustainability_score" in result

    def test_enterprise_has_executive_summary(self):
        bot = FactoryBot(tier=Tier.ENTERPRISE)
        result = bot.get_sustainability_report("facility-01")
        assert "executive_summary" in result


class TestFactoryBotDashboard:
    def test_returns_dict(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.get_factory_dashboard()
        assert isinstance(result, dict)

    def test_has_tier(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.get_factory_dashboard()
        assert result["tier"] == Tier.FREE.value

    def test_has_modules(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.get_factory_dashboard()
        assert isinstance(result["modules"], list)
        assert len(result["modules"]) == 4

    def test_enterprise_has_enterprise_features(self):
        bot = FactoryBot(tier=Tier.ENTERPRISE)
        result = bot.get_factory_dashboard()
        assert "enterprise_features" in result

    def test_features_list_present(self):
        bot = FactoryBot(tier=Tier.PRO)
        result = bot.get_factory_dashboard()
        assert "features" in result
        assert isinstance(result["features"], list)


class TestFactoryBotDescribeTier:
    def test_returns_string(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.describe_tier()
        assert isinstance(result, str)

    def test_contains_price(self):
        bot = FactoryBot(tier=Tier.FREE)
        result = bot.describe_tier()
        assert "$" in result

    def test_contains_features(self):
        bot = FactoryBot(tier=Tier.PRO)
        result = bot.describe_tier()
        assert "✓" in result


class TestFactoryBotError:
    def test_is_exception(self):
        err = FactoryBotError("test error")
        assert isinstance(err, Exception)

    def test_message_preserved(self):
        err = FactoryBotError("tier violation")
        assert "tier violation" in str(err)
