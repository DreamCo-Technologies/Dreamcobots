"""Smart City Infrastructure Management — traffic, energy, and public safety."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from framework import GlobalAISourcesFlow  # noqa: F401

_flow = GlobalAISourcesFlow(bot_name="SmartCityInfrastructure")


class SmartCityInfrastructureError(Exception):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Traffic Management
# ---------------------------------------------------------------------------

class TrafficManagementSystem:
    """Tier-aware traffic monitoring and optimization system."""

    ZONE_LIMITS = {Tier.FREE: 1, Tier.PRO: 10, Tier.ENTERPRISE: None}

    TRAFFIC_DATA = {
        "downtown":     {"congestion": 0.78, "avg_speed_kmh": 22, "incidents": 3, "flow_rate": 1200},
        "north":        {"congestion": 0.42, "avg_speed_kmh": 58, "incidents": 0, "flow_rate": 850},
        "south":        {"congestion": 0.55, "avg_speed_kmh": 41, "incidents": 1, "flow_rate": 960},
        "east":         {"congestion": 0.31, "avg_speed_kmh": 72, "incidents": 0, "flow_rate": 700},
        "west":         {"congestion": 0.63, "avg_speed_kmh": 34, "incidents": 2, "flow_rate": 1050},
        "industrial":   {"congestion": 0.47, "avg_speed_kmh": 50, "incidents": 1, "flow_rate": 800},
        "residential":  {"congestion": 0.28, "avg_speed_kmh": 45, "incidents": 0, "flow_rate": 620},
        "port":         {"congestion": 0.69, "avg_speed_kmh": 28, "incidents": 2, "flow_rate": 980},
        "airport":      {"congestion": 0.72, "avg_speed_kmh": 30, "incidents": 1, "flow_rate": 1100},
        "suburbs":      {"congestion": 0.22, "avg_speed_kmh": 80, "incidents": 0, "flow_rate": 450},
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._monitored_zones: list = []

    def _check_zone_limit(self, zone: str) -> None:
        limit = self.ZONE_LIMITS[self.tier]
        if zone not in self._monitored_zones:
            if limit is not None and len(self._monitored_zones) >= limit:
                raise SmartCityInfrastructureError(
                    f"{self.tier.value.upper()} tier allows only {limit} zone(s). "
                    "Upgrade to PRO or ENTERPRISE for more zones."
                )
            self._monitored_zones.append(zone)

    def optimize_traffic(self, zone: str) -> dict:
        """Return optimization recommendations for the given zone."""
        self._check_zone_limit(zone)
        data = self.TRAFFIC_DATA.get(zone, self.TRAFFIC_DATA["downtown"])
        congestion = data["congestion"]

        if congestion > 0.70:
            action = "activate_alternate_routes"
            signal_phase = "extended_green_on_arterials"
        elif congestion > 0.50:
            action = "adjust_signal_timing"
            signal_phase = "balanced_cycle"
        else:
            action = "normal_operations"
            signal_phase = "standard_cycle"

        result = {
            "zone": zone,
            "tier": self.tier.value,
            "congestion_level": congestion,
            "recommended_action": action,
            "signal_phase": signal_phase,
            "estimated_improvement_pct": round((1 - congestion) * 40, 1),
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["alternate_routes"] = [f"{zone}_bypass_A", f"{zone}_bypass_B"]
            result["signal_override_capable"] = True

        if self.tier == Tier.ENTERPRISE:
            result["ai_optimized"] = True
            result["predicted_clearance_minutes"] = round(congestion * 45, 0)

        return result

    def monitor_congestion(self, zone: str) -> dict:
        """Return live congestion metrics for a zone."""
        self._check_zone_limit(zone)
        data = self.TRAFFIC_DATA.get(zone, self.TRAFFIC_DATA["downtown"])

        if data["congestion"] > 0.70:
            status = "heavy"
        elif data["congestion"] > 0.45:
            status = "moderate"
        else:
            status = "light"

        result = {
            "zone": zone,
            "congestion_index": data["congestion"],
            "status": status,
            "avg_speed_kmh": data["avg_speed_kmh"],
            "active_incidents": data["incidents"],
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["flow_rate_vehicles_per_hour"] = data["flow_rate"]
            result["sensor_count"] = 12

        if self.tier == Tier.ENTERPRISE:
            result["heat_map_available"] = True
            result["api_endpoint"] = f"/api/v1/traffic/{zone}/congestion"

        return result

    def predict_traffic_flow(self, zone: str, hour: int) -> dict:
        """Predict traffic flow for a zone at a given hour (0-23)."""
        if self.tier == Tier.FREE:
            raise SmartCityInfrastructureError(
                "Traffic flow prediction requires PRO or ENTERPRISE tier."
            )
        self._check_zone_limit(zone)
        base = self.TRAFFIC_DATA.get(zone, self.TRAFFIC_DATA["downtown"])
        peak_factor = 1.4 if hour in (7, 8, 9, 17, 18, 19) else 0.8 if hour < 6 or hour > 22 else 1.0
        predicted_flow = round(base["flow_rate"] * peak_factor)
        predicted_congestion = min(round(base["congestion"] * peak_factor, 2), 1.0)

        result = {
            "zone": zone,
            "hour": hour,
            "predicted_flow_rate": predicted_flow,
            "predicted_congestion": predicted_congestion,
            "confidence_pct": 85 if self.tier == Tier.PRO else 95,
        }

        if self.tier == Tier.ENTERPRISE:
            result["7day_trend"] = "increasing" if hour in range(7, 20) else "stable"
            result["model_version"] = "v3.2"

        return result


# ---------------------------------------------------------------------------
# Energy Management
# ---------------------------------------------------------------------------

class EnergyManagementSystem:
    """Tier-aware smart grid energy monitoring and optimization."""

    DISTRICT_LIMITS = {Tier.FREE: 1, Tier.PRO: 10, Tier.ENTERPRISE: None}

    GRID_DATA = {
        "residential_north": {"load_mw": 45.2, "capacity_mw": 80.0, "renewable_pct": 32, "outages": 0},
        "residential_south": {"load_mw": 38.7, "capacity_mw": 75.0, "renewable_pct": 28, "outages": 0},
        "commercial_center": {"load_mw": 120.5, "capacity_mw": 150.0, "renewable_pct": 18, "outages": 1},
        "industrial_east":   {"load_mw": 210.0, "capacity_mw": 250.0, "renewable_pct": 12, "outages": 0},
        "industrial_west":   {"load_mw": 185.3, "capacity_mw": 220.0, "renewable_pct": 15, "outages": 2},
        "hospital_district": {"load_mw": 55.0,  "capacity_mw": 70.0,  "renewable_pct": 40, "outages": 0},
        "university":        {"load_mw": 28.4,  "capacity_mw": 45.0,  "renewable_pct": 55, "outages": 0},
        "port_logistics":    {"load_mw": 95.0,  "capacity_mw": 120.0, "renewable_pct": 10, "outages": 1},
        "suburbs_east":      {"load_mw": 22.1,  "capacity_mw": 40.0,  "renewable_pct": 45, "outages": 0},
        "suburbs_west":      {"load_mw": 19.8,  "capacity_mw": 38.0,  "renewable_pct": 50, "outages": 0},
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._monitored_districts: list = []

    def _check_district_limit(self, district: str) -> None:
        limit = self.DISTRICT_LIMITS[self.tier]
        if district not in self._monitored_districts:
            if limit is not None and len(self._monitored_districts) >= limit:
                raise SmartCityInfrastructureError(
                    f"{self.tier.value.upper()} tier allows only {limit} district(s). "
                    "Upgrade for more districts."
                )
            self._monitored_districts.append(district)

    def monitor_grid(self, district: str) -> dict:
        """Return current grid status for a district."""
        self._check_district_limit(district)
        data = self.GRID_DATA.get(district, self.GRID_DATA["commercial_center"])
        utilization = round(data["load_mw"] / data["capacity_mw"] * 100, 1)

        if utilization > 85:
            grid_status = "critical"
        elif utilization > 70:
            grid_status = "high_load"
        else:
            grid_status = "normal"

        result = {
            "district": district,
            "tier": self.tier.value,
            "load_mw": data["load_mw"],
            "capacity_mw": data["capacity_mw"],
            "utilization_pct": utilization,
            "grid_status": grid_status,
            "active_outages": data["outages"],
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["renewable_pct"] = data["renewable_pct"]
            result["carbon_intensity_gco2_kwh"] = round(400 * (1 - data["renewable_pct"] / 100), 1)

        if self.tier == Tier.ENTERPRISE:
            result["smart_meter_count"] = 1200
            result["api_endpoint"] = f"/api/v1/energy/{district}/grid"

        return result

    def optimize_energy(self, district: str) -> dict:
        """Return energy optimization recommendations."""
        self._check_district_limit(district)
        data = self.GRID_DATA.get(district, self.GRID_DATA["commercial_center"])
        utilization = data["load_mw"] / data["capacity_mw"]

        if utilization > 0.85:
            strategy = "demand_response_emergency"
            savings_est_pct = 18
        elif utilization > 0.70:
            strategy = "load_shifting"
            savings_est_pct = 10
        else:
            strategy = "renewable_maximization"
            savings_est_pct = 5

        result = {
            "district": district,
            "optimization_strategy": strategy,
            "estimated_savings_pct": savings_est_pct,
            "recommended_renewable_target_pct": min(data["renewable_pct"] + 10, 80),
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["load_shift_windows"] = ["02:00-06:00", "13:00-15:00"]
            result["battery_storage_recommendation_mwh"] = round(data["load_mw"] * 0.1, 1)

        if self.tier == Tier.ENTERPRISE:
            result["ai_optimized"] = True
            result["real_time_adjustments"] = True

        return result

    def predict_demand(self, district: str, hour: int) -> dict:
        """Predict energy demand for a district at a given hour."""
        if self.tier == Tier.FREE:
            raise SmartCityInfrastructureError(
                "Energy demand prediction requires PRO or ENTERPRISE tier."
            )
        self._check_district_limit(district)
        data = self.GRID_DATA.get(district, self.GRID_DATA["commercial_center"])
        peak_factor = 1.3 if hour in (8, 9, 10, 18, 19, 20) else 0.7 if hour < 5 else 1.0
        predicted_load = round(data["load_mw"] * peak_factor, 2)

        result = {
            "district": district,
            "hour": hour,
            "predicted_load_mw": predicted_load,
            "capacity_mw": data["capacity_mw"],
            "headroom_mw": round(data["capacity_mw"] - predicted_load, 2),
            "confidence_pct": 88 if self.tier == Tier.PRO else 96,
        }

        if self.tier == Tier.ENTERPRISE:
            result["30day_forecast_available"] = True
            result["model_version"] = "energy-v2.1"

        return result


# ---------------------------------------------------------------------------
# Public Safety
# ---------------------------------------------------------------------------

class PublicSafetyMonitor:
    """Tier-aware public safety monitoring and incident management."""

    ZONE_LIMITS = {Tier.FREE: 1, Tier.PRO: 10, Tier.ENTERPRISE: None}

    SAFETY_DATA = {
        "downtown":    {"crime_index": 0.62, "incidents_24h": 8, "cameras": 42, "patrol_units": 6},
        "north":       {"crime_index": 0.31, "incidents_24h": 2, "cameras": 18, "patrol_units": 3},
        "south":       {"crime_index": 0.45, "incidents_24h": 4, "cameras": 24, "patrol_units": 4},
        "east":        {"crime_index": 0.28, "incidents_24h": 1, "cameras": 15, "patrol_units": 2},
        "west":        {"crime_index": 0.55, "incidents_24h": 6, "cameras": 30, "patrol_units": 5},
        "industrial":  {"crime_index": 0.48, "incidents_24h": 3, "cameras": 20, "patrol_units": 3},
        "residential": {"crime_index": 0.22, "incidents_24h": 1, "cameras": 10, "patrol_units": 2},
        "port":        {"crime_index": 0.71, "incidents_24h": 9, "cameras": 38, "patrol_units": 7},
        "airport":     {"crime_index": 0.35, "incidents_24h": 2, "cameras": 85, "patrol_units": 8},
        "suburbs":     {"crime_index": 0.18, "incidents_24h": 0, "cameras": 8,  "patrol_units": 1},
    }

    INCIDENT_RESOURCES = {
        "theft":    {"police": 2, "detective": 1},
        "fire":     {"fire_truck": 2, "ambulance": 1, "police": 1},
        "accident": {"ambulance": 2, "police": 2, "tow_truck": 1},
        "protest":  {"police": 8, "supervisor": 1},
        "medical":  {"ambulance": 2, "fire_truck": 1},
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._monitored_zones: list = []

    def _check_zone_limit(self, zone: str) -> None:
        limit = self.ZONE_LIMITS[self.tier]
        if zone not in self._monitored_zones:
            if limit is not None and len(self._monitored_zones) >= limit:
                raise SmartCityInfrastructureError(
                    f"{self.tier.value.upper()} tier allows only {limit} zone(s). "
                    "Upgrade for more zones."
                )
            self._monitored_zones.append(zone)

    def monitor_safety(self, zone: str) -> dict:
        """Return current safety status for a zone."""
        self._check_zone_limit(zone)
        data = self.SAFETY_DATA.get(zone, self.SAFETY_DATA["downtown"])

        if data["crime_index"] > 0.65:
            safety_level = "high_risk"
        elif data["crime_index"] > 0.40:
            safety_level = "moderate_risk"
        else:
            safety_level = "low_risk"

        result = {
            "zone": zone,
            "tier": self.tier.value,
            "crime_index": data["crime_index"],
            "safety_level": safety_level,
            "incidents_last_24h": data["incidents_24h"],
            "active_cameras": data["cameras"],
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["patrol_units_deployed"] = data["patrol_units"]
            result["response_time_minutes"] = round(5 + data["crime_index"] * 10, 1)

        if self.tier == Tier.ENTERPRISE:
            result["predictive_patrol_enabled"] = True
            result["api_endpoint"] = f"/api/v1/safety/{zone}/status"

        return result

    def alert_incidents(self, zone: str) -> dict:
        """Return active incident alerts for a zone."""
        self._check_zone_limit(zone)
        data = self.SAFETY_DATA.get(zone, self.SAFETY_DATA["downtown"])
        incidents = []
        for i in range(data["incidents_24h"]):
            incidents.append({
                "incident_id": f"INC-{zone[:3].upper()}-{i + 1:03d}",
                "type": ["theft", "accident", "medical", "fire", "protest"][i % 5],
                "severity": "high" if i % 3 == 0 else "medium" if i % 2 == 0 else "low",
            })

        result = {
            "zone": zone,
            "total_active_incidents": data["incidents_24h"],
            "alerts": incidents[:3],  # FREE: capped at 3
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["alerts"] = incidents  # all incidents

        if self.tier == Tier.ENTERPRISE:
            result["predicted_incidents_next_hour"] = round(data["crime_index"] * 3)
            result["ai_risk_score"] = round(data["crime_index"] * 100)

        return result

    def deploy_resources(self, zone: str, incident_type: str) -> dict:
        """Return resource deployment plan for an incident type."""
        if self.tier == Tier.FREE:
            raise SmartCityInfrastructureError(
                "Resource deployment requires PRO or ENTERPRISE tier."
            )
        self._check_zone_limit(zone)
        resources = self.INCIDENT_RESOURCES.get(incident_type, {"police": 2})

        result = {
            "zone": zone,
            "incident_type": incident_type,
            "resources_deployed": resources,
            "eta_minutes": 7 if self.tier == Tier.ENTERPRISE else 12,
            "dispatch_confirmed": True,
        }

        if self.tier == Tier.ENTERPRISE:
            result["optimal_route"] = f"Route-{zone[:3].upper()}-FAST"
            result["coordination_center"] = "City Emergency Operations"

        return result
