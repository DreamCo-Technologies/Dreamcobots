"""Satellite Monitor — tier-aware satellite tracking and environmental monitoring."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from framework import GlobalAISourcesFlow  # noqa: F401

_flow = GlobalAISourcesFlow(bot_name="SatelliteMonitor")


class SatelliteMonitorError(Exception):
    """Raised when a satellite monitoring feature is unavailable on the current tier."""


SATELLITE_DATABASE = {
    "GPS-IIF-1": {
        "type": "navigation",
        "altitude_km": 20_200,
        "inclination_deg": 55.0,
        "orbital_period_min": 718,
        "velocity_km_s": 3.87,
        "status": "operational",
        "owner": "US Space Force",
    },
    "NOAA-20": {
        "type": "weather",
        "altitude_km": 824,
        "inclination_deg": 98.7,
        "orbital_period_min": 101,
        "velocity_km_s": 7.46,
        "status": "operational",
        "owner": "NOAA",
    },
    "Landsat-9": {
        "type": "research",
        "altitude_km": 705,
        "inclination_deg": 98.2,
        "orbital_period_min": 99,
        "velocity_km_s": 7.50,
        "status": "operational",
        "owner": "NASA/USGS",
    },
    "Sentinel-2A": {
        "type": "research",
        "altitude_km": 786,
        "inclination_deg": 98.6,
        "orbital_period_min": 100,
        "velocity_km_s": 7.46,
        "status": "operational",
        "owner": "ESA",
    },
    "GOES-18": {
        "type": "weather",
        "altitude_km": 35_786,
        "inclination_deg": 0.0,
        "orbital_period_min": 1_436,
        "velocity_km_s": 3.07,
        "status": "operational",
        "owner": "NOAA",
    },
    "USA-315": {
        "type": "military",
        "altitude_km": 550,
        "inclination_deg": 45.0,
        "orbital_period_min": 95,
        "velocity_km_s": 7.61,
        "status": "classified",
        "owner": "NRO",
    },
    "Hubble": {
        "type": "research",
        "altitude_km": 547,
        "inclination_deg": 28.5,
        "orbital_period_min": 95,
        "velocity_km_s": 7.59,
        "status": "operational",
        "owner": "NASA/ESA",
    },
    "ISS": {
        "type": "research",
        "altitude_km": 408,
        "inclination_deg": 51.6,
        "orbital_period_min": 92,
        "velocity_km_s": 7.66,
        "status": "crewed",
        "owner": "International",
    },
    "Starlink-1007": {
        "type": "communication",
        "altitude_km": 550,
        "inclination_deg": 53.0,
        "orbital_period_min": 95,
        "velocity_km_s": 7.61,
        "status": "operational",
        "owner": "SpaceX",
    },
    "AQUA": {
        "type": "research",
        "altitude_km": 705,
        "inclination_deg": 98.2,
        "orbital_period_min": 99,
        "velocity_km_s": 7.50,
        "status": "operational",
        "owner": "NASA",
    },
}

TRACKING_LIMITS = {Tier.FREE: 2, Tier.PRO: 20, Tier.ENTERPRISE: None}

ENVIRONMENTAL_DATA = {
    "amazon": {
        "temperature_c": 27.4,
        "vegetation_index": 0.82,
        "deforestation_rate_pct": 1.2,
        "cloud_cover_pct": 68,
        "pollution_index": 0.11,
    },
    "sahara": {
        "temperature_c": 42.1,
        "vegetation_index": 0.03,
        "deforestation_rate_pct": 0.0,
        "cloud_cover_pct": 5,
        "pollution_index": 0.08,
    },
    "arctic": {
        "temperature_c": -18.3,
        "vegetation_index": 0.06,
        "deforestation_rate_pct": 0.0,
        "cloud_cover_pct": 55,
        "pollution_index": 0.04,
    },
    "california": {
        "temperature_c": 22.6,
        "vegetation_index": 0.48,
        "deforestation_rate_pct": 0.3,
        "cloud_cover_pct": 20,
        "pollution_index": 0.38,
    },
    "india_ganges": {
        "temperature_c": 31.0,
        "vegetation_index": 0.55,
        "deforestation_rate_pct": 0.8,
        "cloud_cover_pct": 40,
        "pollution_index": 0.62,
    },
}

PLANET_SURFACES = {
    "mars": {
        "surface_type": "rocky desert",
        "avg_temp_c": -60,
        "atmosphere": "CO2 96%",
        "notable_features": ["Olympus Mons", "Valles Marineris", "Hellas Basin"],
    },
    "moon": {
        "surface_type": "regolith",
        "avg_temp_c": -20,
        "atmosphere": "none",
        "notable_features": ["Tycho Crater", "Sea of Tranquility", "Shackleton Crater"],
    },
    "venus": {
        "surface_type": "volcanic plains",
        "avg_temp_c": 465,
        "atmosphere": "CO2/SO2",
        "notable_features": ["Maxwell Montes", "Ishtar Terra", "Aphrodite Terra"],
    },
    "europa": {
        "surface_type": "ice shell",
        "avg_temp_c": -160,
        "atmosphere": "thin O2",
        "notable_features": ["Conamara Chaos", "Pwyll Crater", "Thera Macula"],
    },
}


class SatelliteMonitor:
    """Tier-aware satellite tracking and environmental monitoring."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._tracked: list = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_tracking_limit(self, sat_id: str) -> None:
        limit = TRACKING_LIMITS[self.tier]
        if sat_id not in self._tracked:
            if limit is not None and len(self._tracked) >= limit:
                raise SatelliteMonitorError(
                    f"{self.tier.value.upper()} tier allows tracking only {limit} satellite(s). "
                    "Upgrade to PRO or ENTERPRISE for more."
                )
            self._tracked.append(sat_id)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def track_satellite(self, sat_id: str) -> dict:
        """Return orbital position, velocity, and status for a satellite."""
        self._check_tracking_limit(sat_id)

        sat = SATELLITE_DATABASE.get(sat_id)
        if sat is None:
            return {
                "sat_id": sat_id,
                "status": "unknown",
                "error": f"Satellite '{sat_id}' not found in database.",
            }

        result: dict = {
            "sat_id": sat_id,
            "type": sat["type"],
            "altitude_km": sat["altitude_km"],
            "velocity_km_s": sat["velocity_km_s"],
            "status": sat["status"],
            "orbital_period_min": sat["orbital_period_min"],
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["inclination_deg"] = sat["inclination_deg"]
            result["owner"] = sat["owner"]
            result["ground_track"] = f"lat={round(sat['inclination_deg'] * 0.7, 2)}, lon=-73.45"

        if self.tier == Tier.ENTERPRISE:
            result["tle_data_available"] = True
            result["collision_risk"] = "low"
            result["api_endpoint"] = f"/api/v1/satellites/{sat_id}/track"

        return result

    def monitor_environment(self, region: str) -> dict:
        """Return environmental data from satellite imagery for a region (PRO/ENTERPRISE)."""
        if self.tier == Tier.FREE:
            raise SatelliteMonitorError(
                "Environmental monitoring requires PRO or ENTERPRISE tier."
            )

        data = ENVIRONMENTAL_DATA.get(region.lower(), ENVIRONMENTAL_DATA["amazon"])

        result: dict = {
            "region": region,
            "temperature_c": data["temperature_c"],
            "vegetation_index": data["vegetation_index"],
            "cloud_cover_pct": data["cloud_cover_pct"],
            "pollution_index": data["pollution_index"],
            "tier": self.tier.value,
        }

        if self.tier == Tier.ENTERPRISE:
            result["deforestation_rate_pct"] = data["deforestation_rate_pct"]
            result["real_time"] = True
            result["resolution_m"] = 10
            result["historical_comparison_available"] = True
            result["api_endpoint"] = f"/api/v1/environment/{region}"

        return result

    def map_planet_surface(self, planet: str, coordinates: dict) -> dict:
        """Return surface mapping data for a planet at given coordinates (PRO/ENTERPRISE)."""
        if self.tier == Tier.FREE:
            raise SatelliteMonitorError(
                "Planet surface mapping requires PRO or ENTERPRISE tier."
            )

        surface = PLANET_SURFACES.get(planet.lower(), PLANET_SURFACES["mars"])

        result: dict = {
            "planet": planet,
            "coordinates": coordinates,
            "surface_type": surface["surface_type"],
            "avg_temp_c": surface["avg_temp_c"],
            "atmosphere": surface["atmosphere"],
            "tier": self.tier.value,
        }

        if self.tier == Tier.ENTERPRISE:
            result["notable_features"] = surface["notable_features"]
            result["high_resolution"] = True
            result["resolution_m"] = 25
            result["3d_model_available"] = True
            result["api_endpoint"] = f"/api/v1/planets/{planet}/surface"

        return result

    def detect_anomalies(self, sat_id: str) -> dict:
        """Detect anomalies in satellite telemetry (PRO/ENTERPRISE)."""
        if self.tier == Tier.FREE:
            raise SatelliteMonitorError(
                "Anomaly detection requires PRO or ENTERPRISE tier."
            )

        sat = SATELLITE_DATABASE.get(sat_id)
        anomalies = []

        if sat and sat["status"] == "classified":
            anomalies.append({"type": "access_restricted", "severity": "info"})

        result: dict = {
            "sat_id": sat_id,
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies,
            "scan_status": "complete",
            "tier": self.tier.value,
        }

        if self.tier == Tier.ENTERPRISE:
            result["ai_model"] = "DreamCoAnomalyNet-v1"
            result["confidence_pct"] = 97.4
            result["next_scan_utc"] = "2024-01-01T06:00:00Z"

        return result
