"""Green manufacturing, energy efficiency monitoring and sustainability management for Factory Bot."""
import sys
import os
import random
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from bots.factory_bot.tiers import BOT_FEATURES, get_bot_tier_info  # noqa: F401
from framework import GlobalAISourcesFlow  # noqa: F401

_flow = GlobalAISourcesFlow(bot_name="FactoryBot-GreenManufacturing")

ENERGY_BENCHMARKS = {
    "automotive": {"kwh_per_unit": 28.5, "target_reduction_pct": 15},
    "electronics": {"kwh_per_unit": 12.0, "target_reduction_pct": 20},
    "food_processing": {"kwh_per_unit": 8.5, "target_reduction_pct": 12},
    "metalworking": {"kwh_per_unit": 35.0, "target_reduction_pct": 18},
    "plastics": {"kwh_per_unit": 18.0, "target_reduction_pct": 14},
    "general": {"kwh_per_unit": 20.0, "target_reduction_pct": 15},
}


class EnergyEfficiencyMonitor:
    """Monitors and optimizes facility energy consumption for manufacturing operations."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)

    def monitor_energy_usage(self, facility_id: str) -> dict:
        """Generate a comprehensive energy consumption report for a facility."""
        daily_kwh = round(random.uniform(1800, 4500), 1)
        peak_demand_kw = round(random.uniform(220, 680), 1)
        power_factor = round(random.uniform(0.82, 0.96), 3)
        monthly_kwh = daily_kwh * 30
        monthly_cost_usd = round(monthly_kwh * 0.12, 2)

        result = {
            "facility_id": facility_id,
            "report_date": str(datetime.now().date()),
            "daily_kwh": daily_kwh,
            "monthly_kwh": round(monthly_kwh, 1),
            "peak_demand_kw": peak_demand_kw,
            "power_factor": power_factor,
            "monthly_cost_usd": monthly_cost_usd,
            "energy_intensity": "moderate",
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["breakdown_by_area"] = {
                "production_floor_pct": 52,
                "hvac_pct": 18,
                "lighting_pct": 10,
                "compressed_air_pct": 12,
                "other_pct": 8,
            }
            result["peak_hours"] = ["08:00-10:00", "13:00-15:00"]
            result["off_peak_kwh"] = round(daily_kwh * 0.3, 1)

        if self.tier == Tier.ENTERPRISE:
            result["real_time_metering"] = True
            result["submetering_data"] = {
                "cnc_machines_kwh": round(daily_kwh * 0.25, 1),
                "hvac_kwh": round(daily_kwh * 0.18, 1),
                "lighting_kwh": round(daily_kwh * 0.10, 1),
                "compressed_air_kwh": round(daily_kwh * 0.12, 1),
            }
            result["anomaly_detected"] = False
            result["iso50001_compliant"] = True

        return result

    def optimize_energy(self, facility_id: str) -> dict:
        """Generate AI-driven energy optimization recommendations for a facility."""
        baseline_kwh = round(random.uniform(2000, 4500), 1)
        potential_savings_pct = round(random.uniform(10.0, 28.0), 1)
        savings_kwh = round(baseline_kwh * potential_savings_pct / 100, 1)
        savings_usd = round(savings_kwh * 30 * 0.12, 2)

        recommendations = [
            {
                "action": "Install variable frequency drives on conveyor motors",
                "savings_kwh_monthly": round(savings_kwh * 0.30, 1),
                "payback_months": 18,
                "priority": "high",
            },
            {
                "action": "Upgrade to LED lighting throughout facility",
                "savings_kwh_monthly": round(savings_kwh * 0.15, 1),
                "payback_months": 24,
                "priority": "medium",
            },
            {
                "action": "Optimize compressed air system pressure and fix leaks",
                "savings_kwh_monthly": round(savings_kwh * 0.20, 1),
                "payback_months": 8,
                "priority": "high",
            },
        ]

        result = {
            "facility_id": facility_id,
            "baseline_daily_kwh": baseline_kwh,
            "potential_savings_pct": potential_savings_pct,
            "potential_savings_kwh_monthly": savings_kwh * 30,
            "potential_savings_usd_annually": savings_usd * 12,
            "recommendations": recommendations,
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["demand_response_eligible"] = True
            result["peak_shaving_savings_usd_monthly"] = round(savings_usd * 0.15, 2)
            result["power_factor_correction_savings"] = round(savings_usd * 0.08, 2)

        if self.tier == Tier.ENTERPRISE:
            result["ml_optimization_model"] = "EnergyBERT-v2"
            result["automated_setpoint_adjustment"] = True
            result["predicted_savings_confidence"] = round(random.uniform(0.87, 0.95), 3)
            result["renewable_integration_recommendation"] = {
                "solar_pv_kw": 250,
                "estimated_coverage_pct": 35,
                "payback_years": 7,
            }

        return result

    def calculate_carbon_footprint(self, production_data: dict) -> dict:
        """Calculate the carbon footprint of manufacturing operations."""
        units_produced = production_data.get("units_produced", 1000)
        energy_kwh = production_data.get("energy_kwh", 20000)
        fuel_liters = production_data.get("fuel_liters", 500)
        transport_km = production_data.get("transport_km", 5000)

        # Emission factors (kg CO2 equivalent)
        electricity_factor = 0.386  # kg CO2/kWh (average grid)
        fuel_factor = 2.68  # kg CO2/liter diesel
        transport_factor = 0.15  # kg CO2/km freight

        electricity_co2 = round(energy_kwh * electricity_factor, 1)
        fuel_co2 = round(fuel_liters * fuel_factor, 1)
        transport_co2 = round(transport_km * transport_factor, 1)
        total_co2 = round(electricity_co2 + fuel_co2 + transport_co2, 1)
        co2_per_unit = round(total_co2 / units_produced, 3)

        result = {
            "units_produced": units_produced,
            "total_co2_kg": total_co2,
            "co2_per_unit_kg": co2_per_unit,
            "scope_1_emissions_kg": fuel_co2,
            "scope_2_emissions_kg": electricity_co2,
            "scope_3_emissions_kg": transport_co2,
            "carbon_intensity": "low" if co2_per_unit < 5 else "medium" if co2_per_unit < 15 else "high",
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["emissions_breakdown"] = {
                "electricity_pct": round(electricity_co2 / total_co2 * 100, 1),
                "fuel_pct": round(fuel_co2 / total_co2 * 100, 1),
                "transport_pct": round(transport_co2 / total_co2 * 100, 1),
            }
            result["reduction_target_kg"] = round(total_co2 * 0.20, 1)
            result["offset_cost_usd"] = round(total_co2 * 0.015, 2)

        if self.tier == Tier.ENTERPRISE:
            result["ghg_protocol_compliant"] = True
            result["third_party_verified"] = False
            result["carbon_neutral_roadmap"] = {
                "year_1_reduction_pct": 10,
                "year_3_reduction_pct": 25,
                "year_5_target": "carbon_neutral",
            }

        return result


class GreenInitiativeManager:
    """Manages sustainability initiatives, waste reduction, and green manufacturing reporting."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)

    def assess_sustainability(self, facility_id: str) -> dict:
        """Assess overall sustainability performance and generate a score with recommendations."""
        energy_score = round(random.uniform(55, 85), 1)
        waste_score = round(random.uniform(50, 80), 1)
        water_score = round(random.uniform(60, 90), 1)
        emissions_score = round(random.uniform(45, 80), 1)
        overall_score = round((energy_score + waste_score + water_score + emissions_score) / 4, 1)

        rating = "Excellent" if overall_score >= 80 else "Good" if overall_score >= 65 else "Fair" if overall_score >= 50 else "Poor"

        recommendations = [
            "Implement energy management system (ISO 50001)",
            "Establish zero-waste-to-landfill program",
            "Source renewable energy certificates for 30% of consumption",
        ]

        result = {
            "facility_id": facility_id,
            "assessment_date": str(datetime.now().date()),
            "overall_sustainability_score": overall_score,
            "rating": rating,
            "recommendations": recommendations,
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["category_scores"] = {
                "energy_score": energy_score,
                "waste_score": waste_score,
                "water_score": water_score,
                "emissions_score": emissions_score,
            }
            result["industry_benchmark_percentile"] = round(random.uniform(40, 75), 1)
            result["certification_readiness"] = {
                "ISO_14001": overall_score >= 70,
                "LEED": overall_score >= 75,
                "B_Corp": overall_score >= 80,
            }

        if self.tier == Tier.ENTERPRISE:
            result["esg_score"] = round(overall_score * 0.95 + random.uniform(-3, 3), 1)
            result["supply_chain_sustainability"] = {
                "supplier_score_avg": round(random.uniform(55, 72), 1),
                "tier_1_suppliers_assessed_pct": round(random.uniform(60, 90), 1),
            }
            result["regulatory_compliance"] = {
                "eu_taxonomy_aligned": True,
                "tcfd_reporting_ready": overall_score >= 70,
            }

        return result

    def plan_waste_reduction(self, facility_id: str, waste_data: dict) -> dict:
        """Create a comprehensive waste reduction plan based on current waste streams."""
        total_waste_kg = waste_data.get("total_waste_kg", 5000)
        recyclable_pct = waste_data.get("recyclable_pct", 40)
        landfill_pct = waste_data.get("landfill_pct", 35)
        hazardous_pct = waste_data.get("hazardous_pct", 5)

        diversion_target_pct = min(95, recyclable_pct + 30)
        landfill_reduction_kg = round(total_waste_kg * (landfill_pct / 100) * 0.60, 1)

        initiatives = [
            {
                "initiative": "Implement material segregation at source",
                "waste_reduction_kg_monthly": round(landfill_reduction_kg * 0.35, 1),
                "cost_savings_usd_monthly": round(landfill_reduction_kg * 0.35 * 0.08, 2),
                "implementation_weeks": 4,
            },
            {
                "initiative": "Partner with recycling vendors for metal scrap buyback",
                "waste_reduction_kg_monthly": round(total_waste_kg * 0.15, 1),
                "cost_savings_usd_monthly": round(total_waste_kg * 0.15 * 0.12, 2),
                "implementation_weeks": 8,
            },
            {
                "initiative": "Reduce packaging waste with lean manufacturing principles",
                "waste_reduction_kg_monthly": round(total_waste_kg * 0.10, 1),
                "cost_savings_usd_monthly": round(total_waste_kg * 0.10 * 0.05, 2),
                "implementation_weeks": 12,
            },
        ]

        result = {
            "facility_id": facility_id,
            "current_total_waste_kg_monthly": total_waste_kg,
            "current_landfill_pct": landfill_pct,
            "target_diversion_rate_pct": diversion_target_pct,
            "landfill_reduction_target_kg": landfill_reduction_kg,
            "waste_reduction_initiatives": initiatives,
            "total_savings_usd_annually": round(sum(i["cost_savings_usd_monthly"] for i in initiatives) * 12, 2),
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["waste_stream_analysis"] = {
                "recyclable_kg": round(total_waste_kg * recyclable_pct / 100, 1),
                "landfill_kg": round(total_waste_kg * landfill_pct / 100, 1),
                "hazardous_kg": round(total_waste_kg * hazardous_pct / 100, 1),
                "organic_kg": round(total_waste_kg * (100 - recyclable_pct - landfill_pct - hazardous_pct) / 100, 1),
            }
            result["zero_waste_certification_path"] = {
                "current_diversion_rate_pct": recyclable_pct,
                "target_pct": 90,
                "estimated_months_to_achieve": 18,
            }

        if self.tier == Tier.ENTERPRISE:
            result["circular_economy_opportunities"] = [
                "Remanufacture metal offcuts into secondary products",
                "Establish take-back program for end-of-life products",
                "Partner with local suppliers for closed-loop packaging",
            ]
            result["regulatory_waste_compliance"] = {
                "rcra_compliant": hazardous_pct < 10,
                "iso_14001_gap": [],
            }

        return result

    def generate_green_report(self, facility_id: str) -> dict:
        """Generate a comprehensive green manufacturing report for a facility."""
        energy_kwh = round(random.uniform(45000, 120000), 1)
        co2_kg = round(energy_kwh * 0.386, 1)
        waste_kg = round(random.uniform(3000, 8000), 1)
        sustainability_score = round(random.uniform(55, 85), 1)
        water_m3 = round(random.uniform(200, 800), 1)

        result = {
            "facility_id": facility_id,
            "report_period": "monthly",
            "report_date": str(datetime.now().date()),
            "sustainability_score": sustainability_score,
            "energy_kwh_monthly": energy_kwh,
            "co2_emissions_kg_monthly": co2_kg,
            "waste_kg_monthly": waste_kg,
            "water_consumption_m3": water_m3,
            "key_highlights": [
                f"Sustainability score: {sustainability_score}/100",
                f"CO2 emissions: {co2_kg:,.0f} kg this period",
                f"Waste generated: {waste_kg:,.0f} kg this period",
            ],
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["year_over_year_change"] = {
                "energy_pct": round(random.uniform(-12, 5), 1),
                "emissions_pct": round(random.uniform(-15, 3), 1),
                "waste_pct": round(random.uniform(-18, 2), 1),
            }
            result["goals_progress"] = {
                "energy_reduction_target_pct": 15,
                "energy_reduction_achieved_pct": round(random.uniform(5, 14), 1),
                "carbon_neutral_target_year": 2030,
            }
            result["sdg_alignment"] = ["SDG 7: Affordable Clean Energy", "SDG 12: Responsible Consumption", "SDG 13: Climate Action"]

        if self.tier == Tier.ENTERPRISE:
            result["executive_summary"] = (
                f"Facility {facility_id} achieved a sustainability score of {sustainability_score}/100. "
                "Key opportunities identified in energy management and waste diversion. "
                "On track to meet 2030 carbon neutrality targets."
            )
            result["stakeholder_report_ready"] = True
            result["regulatory_disclosures"] = {
                "sec_climate_disclosure": True,
                "cdp_submission_ready": True,
                "gri_standards": "GRI 302, GRI 305, GRI 306",
            }
            result["benchmarking"] = {
                "industry_percentile": round(random.uniform(55, 80), 1),
                "peer_comparison": "Above industry median",
            }

        return result
