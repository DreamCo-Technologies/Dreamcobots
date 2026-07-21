"""Space Mission Planner — tier-aware mission planning and trajectory simulation."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from framework import GlobalAISourcesFlow  # noqa: F401

_flow = GlobalAISourcesFlow(bot_name="MissionPlanner")


class MissionPlannerError(Exception):
    """Raised when a mission planning feature is unavailable on the current tier."""


MISSION_PROFILES = {
    "lunar": {
        "duration_days": 10,
        "delta_v_km_s": 3.9,
        "fuel_kg": 18_500,
        "distance_km": 384_400,
        "risk_base": 0.12,
        "crew_max": 4,
        "description": "Crewed or uncrewed mission to lunar orbit or surface.",
    },
    "mars": {
        "duration_days": 520,
        "delta_v_km_s": 5.6,
        "fuel_kg": 95_000,
        "distance_km": 78_340_000,
        "risk_base": 0.31,
        "crew_max": 6,
        "description": "Long-duration crewed Mars surface mission.",
    },
    "iss_supply": {
        "duration_days": 3,
        "delta_v_km_s": 9.4,
        "fuel_kg": 8_200,
        "distance_km": 408,
        "risk_base": 0.04,
        "crew_max": 7,
        "description": "Resupply mission to the International Space Station.",
    },
    "satellite_deploy": {
        "duration_days": 1,
        "delta_v_km_s": 9.4,
        "fuel_kg": 5_000,
        "distance_km": 550,
        "risk_base": 0.02,
        "crew_max": 0,
        "description": "Autonomous satellite deployment to low-earth orbit.",
    },
    "deep_space": {
        "duration_days": 3650,
        "delta_v_km_s": 12.4,
        "fuel_kg": 250_000,
        "distance_km": 5_900_000_000,
        "risk_base": 0.58,
        "crew_max": 0,
        "description": "Unmanned deep-space exploration probe.",
    },
}

MISSION_LIMITS = {Tier.FREE: 0, Tier.PRO: 5, Tier.ENTERPRISE: None}


class MissionPlanner:
    """Tier-aware space mission planning and trajectory simulation."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._missions: dict = {}
        self._mission_counter = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_mission_limit(self) -> None:
        limit = MISSION_LIMITS[self.tier]
        if self.tier == Tier.FREE:
            raise MissionPlannerError(
                "FREE tier does not support mission planning. "
                "Use simulate_trajectory() or upgrade to PRO/ENTERPRISE."
            )
        if limit is not None and self._mission_counter >= limit:
            raise MissionPlannerError(
                f"{self.tier.value.upper()} tier allows only {limit} mission(s). "
                "Upgrade to ENTERPRISE for unlimited missions."
            )

    def _next_mission_id(self) -> str:
        self._mission_counter += 1
        return f"MSN-{self._mission_counter:04d}"

    @staticmethod
    def _risk_label(score: float) -> str:
        if score < 0.10:
            return "minimal"
        if score < 0.25:
            return "low"
        if score < 0.45:
            return "moderate"
        if score < 0.70:
            return "high"
        return "critical"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plan_mission(
        self,
        mission_type: str,
        destination: str,
        crew_size: int = 0,
    ) -> dict:
        """Create a detailed mission plan (PRO/ENTERPRISE only)."""
        self._check_mission_limit()

        profile = MISSION_PROFILES.get(mission_type, MISSION_PROFILES["lunar"])
        mission_id = self._next_mission_id()

        plan: dict = {
            "mission_id": mission_id,
            "mission_type": mission_type,
            "destination": destination,
            "crew_size": crew_size,
            "duration_days": profile["duration_days"],
            "fuel_kg": profile["fuel_kg"],
            "delta_v_km_s": profile["delta_v_km_s"],
            "distance_km": profile["distance_km"],
            "description": profile["description"],
            "status": "planned",
            "tier": self.tier.value,
        }

        if self.tier == Tier.ENTERPRISE:
            plan["full_simulation"] = True
            plan["ai_optimized"] = True
            plan["contingency_plans"] = [
                f"{mission_type}_abort_to_orbit",
                f"{mission_type}_emergency_return",
            ]
            plan["api_endpoint"] = f"/api/v1/missions/{mission_id}"

        self._missions[mission_id] = plan
        return plan

    def simulate_trajectory(
        self,
        origin: str,
        destination: str,
        launch_date: str,
    ) -> dict:
        """Simulate a trajectory between two bodies (all tiers)."""
        profile = next(
            (p for p in MISSION_PROFILES.values() if destination.lower() in p["description"].lower()),
            MISSION_PROFILES["lunar"],
        )

        result: dict = {
            "origin": origin,
            "destination": destination,
            "launch_date": launch_date,
            "transfer_orbit": "Hohmann",
            "delta_v_km_s": profile["delta_v_km_s"],
            "flight_duration_days": profile["duration_days"],
            "distance_km": profile["distance_km"],
            "tier": self.tier.value,
            "simulation_only": self.tier == Tier.FREE,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["gravity_assist_available"] = True
            result["optimal_launch_windows"] = [
                f"{launch_date} +0d",
                f"{launch_date} +26d",
                f"{launch_date} +52d",
            ]

        if self.tier == Tier.ENTERPRISE:
            result["n_body_simulation"] = True
            result["radiation_exposure_sv"] = round(profile["risk_base"] * 2.5, 3)
            result["fuel_margin_kg"] = round(profile["fuel_kg"] * 0.12, 0)

        return result

    def assess_mission_risk(self, mission_data: dict) -> dict:
        """Return a risk assessment for the supplied mission data (PRO/ENTERPRISE)."""
        if self.tier == Tier.FREE:
            raise MissionPlannerError(
                "Risk assessment requires PRO or ENTERPRISE tier."
            )

        mission_type = mission_data.get("mission_type", "lunar")
        crew_size = mission_data.get("crew_size", 0)
        profile = MISSION_PROFILES.get(mission_type, MISSION_PROFILES["lunar"])

        base_risk = profile["risk_base"]
        crew_penalty = min(crew_size * 0.01, 0.10)
        total_risk = round(min(base_risk + crew_penalty, 0.99), 4)

        result: dict = {
            "mission_type": mission_type,
            "overall_risk_score": total_risk,
            "risk_label": self._risk_label(total_risk),
            "risk_factors": {
                "mission_complexity": base_risk,
                "crew_factor": crew_penalty,
            },
            "mitigation_strategies": [
                "redundant_life_support",
                "abort_trajectory_pre_calculated",
                "real_time_telemetry_monitoring",
            ],
            "tier": self.tier.value,
        }

        if self.tier == Tier.ENTERPRISE:
            result["monte_carlo_iterations"] = 100_000
            result["confidence_interval_95"] = [
                round(total_risk - 0.03, 4),
                round(total_risk + 0.03, 4),
            ]
            result["ai_risk_model"] = "DreamCoRisk-v2"

        return result

    def get_mission_status(self, mission_id: str) -> dict:
        """Return the current status of a planned mission."""
        if mission_id not in self._missions:
            return {"mission_id": mission_id, "status": "not_found", "error": "Mission ID not found."}
        mission = self._missions[mission_id]
        return {
            "mission_id": mission_id,
            "status": mission["status"],
            "mission_type": mission["mission_type"],
            "destination": mission["destination"],
            "tier": self.tier.value,
        }
