"""Space AI Bot — tier-aware space mission planning and satellite monitoring."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.space_ai_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.space_ai_bot.mission_planner import MissionPlanner, MissionPlannerError
from bots.space_ai_bot.satellite_monitor import SatelliteMonitor, SatelliteMonitorError

_flow = GlobalAISourcesFlow(bot_name="SpaceAIBot")


class SpaceAIBotError(Exception):
    """Raised when a Space AI Bot feature is unavailable on the current tier."""


class SpaceAIBot:
    """Tier-aware Space AI Bot integrating mission planning and satellite monitoring."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.mission_planner = MissionPlanner(tier=tier)
        self.satellite_monitor = SatelliteMonitor(tier=tier)
        self._activity_log: list = []

    # ------------------------------------------------------------------
    # Mission planning
    # ------------------------------------------------------------------

    def plan_mission(self, mission_type: str, destination: str, **kwargs) -> dict:
        """Plan a space mission (PRO/ENTERPRISE only)."""
        crew_size = kwargs.get("crew_size", 0)
        try:
            result = self.mission_planner.plan_mission(mission_type, destination, crew_size)
            self._activity_log.append({"action": "plan_mission", "mission_type": mission_type})
            return result
        except MissionPlannerError as exc:
            raise SpaceAIBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Satellite monitoring
    # ------------------------------------------------------------------

    def track_satellite(self, sat_id: str) -> dict:
        """Track a satellite's orbital position and status."""
        try:
            result = self.satellite_monitor.track_satellite(sat_id)
            self._activity_log.append({"action": "track_satellite", "sat_id": sat_id})
            return result
        except SatelliteMonitorError as exc:
            raise SpaceAIBotError(str(exc)) from exc

    def monitor_earth(self, region: str) -> dict:
        """Monitor Earth's environment via satellite imagery (PRO/ENTERPRISE)."""
        try:
            result = self.satellite_monitor.monitor_environment(region)
            self._activity_log.append({"action": "monitor_earth", "region": region})
            return result
        except SatelliteMonitorError as exc:
            raise SpaceAIBotError(str(exc)) from exc

    def map_planet(self, planet: str, coordinates: dict) -> dict:
        """Map a planet surface at given coordinates (PRO/ENTERPRISE)."""
        try:
            result = self.satellite_monitor.map_planet_surface(planet, coordinates)
            self._activity_log.append({"action": "map_planet", "planet": planet})
            return result
        except SatelliteMonitorError as exc:
            raise SpaceAIBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def get_space_dashboard(self) -> dict:
        """Return a summary dashboard of bot capabilities and activity."""
        tier_info = get_bot_tier_info(self.tier)
        upgrade = get_upgrade_path(self.tier)

        dashboard: dict = {
            "bot": "SpaceAIBot",
            "tier": self.tier.value,
            "tier_name": tier_info["name"],
            "price_usd_monthly": tier_info["price_usd_monthly"],
            "features": tier_info["features"],
            "support_level": tier_info["support_level"],
            "missions_planned": self.mission_planner._mission_counter,
            "satellites_tracked": len(self.satellite_monitor._tracked),
            "activity_count": len(self._activity_log),
        }

        if upgrade:
            dashboard["upgrade_available"] = {
                "tier": upgrade.tier.value,
                "name": upgrade.name,
                "price_usd_monthly": upgrade.price_usd_monthly,
            }
        else:
            dashboard["upgrade_available"] = None

        return dashboard
