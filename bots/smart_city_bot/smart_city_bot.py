"""Smart City Bot — tier-aware smart city management and government AI services."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.smart_city_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401

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

_flow = GlobalAISourcesFlow(bot_name="SmartCityBot")


class SmartCityBotError(Exception):
    """Raised when a feature is not available on the current tier."""


class SmartCityBot:
    """Tier-aware Smart City Bot integrating infrastructure and government AI services."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.traffic = TrafficManagementSystem(tier=tier)
        self.energy = EnergyManagementSystem(tier=tier)
        self.safety = PublicSafetyMonitor(tier=tier)
        self.tax = TaxSystemAI(tier=tier)
        self.census = CensusCollector(tier=tier)
        self.policy = PolicyModelingBot(tier=tier)
        self._activity_log: list = []

    # ------------------------------------------------------------------
    # Infrastructure services
    # ------------------------------------------------------------------

    def monitor_traffic(self, zone: str) -> dict:
        """Monitor and optimize traffic for a zone."""
        try:
            congestion = self.traffic.monitor_congestion(zone)
            optimization = self.traffic.optimize_traffic(zone)
            result = {
                "service": "traffic",
                "zone": zone,
                "congestion": congestion,
                "optimization": optimization,
            }
            self._activity_log.append({"service": "traffic", "zone": zone})
            return result
        except SmartCityInfrastructureError as exc:
            raise SmartCityBotError(str(exc)) from exc

    def manage_energy(self, district: str) -> dict:
        """Monitor and optimize energy for a district."""
        try:
            grid = self.energy.monitor_grid(district)
            optimization = self.energy.optimize_energy(district)
            result = {
                "service": "energy",
                "district": district,
                "grid_status": grid,
                "optimization": optimization,
            }
            self._activity_log.append({"service": "energy", "district": district})
            return result
        except SmartCityInfrastructureError as exc:
            raise SmartCityBotError(str(exc)) from exc

    def monitor_safety(self, zone: str) -> dict:
        """Monitor public safety and active alerts for a zone."""
        try:
            status = self.safety.monitor_safety(zone)
            alerts = self.safety.alert_incidents(zone)
            result = {
                "service": "safety",
                "zone": zone,
                "safety_status": status,
                "alerts": alerts,
            }
            self._activity_log.append({"service": "safety", "zone": zone})
            return result
        except SmartCityInfrastructureError as exc:
            raise SmartCityBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Government services
    # ------------------------------------------------------------------

    def government_service(self, service_type: str, data: dict) -> dict:
        """
        Dispatch to a government AI service.

        service_type options: 'tax_calculate', 'tax_report', 'census_collect',
        'census_demographics', 'policy_model', 'policy_recommend'
        """
        try:
            if service_type == "tax_calculate":
                return self.tax.calculate_tax(data)
            elif service_type == "tax_report":
                return self.tax.generate_tax_report(data.get("period", "2024-Q1"))
            elif service_type == "census_collect":
                return self.census.collect_census(data.get("region", "city_center"))
            elif service_type == "census_demographics":
                return self.census.analyze_demographics(data.get("region", "city_center"))
            elif service_type == "policy_model":
                return self.policy.model_policy(data)
            elif service_type == "policy_recommend":
                return self.policy.recommend_policy(data.get("domain", "transportation"))
            else:
                raise SmartCityBotError(
                    f"Unknown government service: '{service_type}'. "
                    "Valid options: tax_calculate, tax_report, census_collect, "
                    "census_demographics, policy_model, policy_recommend."
                )
        except (GovernmentAIError, SmartCityInfrastructureError) as exc:
            raise SmartCityBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def get_city_dashboard(self) -> dict:
        """Return a high-level city operations dashboard."""
        upgrade = get_upgrade_path(self.tier)
        tier_info = get_bot_tier_info(self.tier)

        dashboard = {
            "bot": "SmartCityBot",
            "tier": self.tier.value,
            "tier_name": tier_info["name"],
            "price_usd_monthly": tier_info["price_usd_monthly"],
            "features": tier_info["features"],
            "support_level": tier_info["support_level"],
            "activity_count": len(self._activity_log),
            "services_available": [
                "traffic_monitoring",
                "energy_management",
                "public_safety",
                "tax_calculation",
                "census_collection",
                "policy_modeling",
            ],
            "upgrade_available": upgrade is not None,
        }

        if upgrade:
            dashboard["upgrade_to"] = upgrade.name
            dashboard["upgrade_price_usd_monthly"] = upgrade.price_usd_monthly

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            dashboard["advanced_analytics"] = True
            dashboard["zones_monitored"] = len(self.traffic._monitored_zones)
            dashboard["districts_monitored"] = len(self.energy._monitored_districts)

        if self.tier == Tier.ENTERPRISE:
            dashboard["api_access"] = True
            dashboard["real_time_data"] = True
            dashboard["ai_optimization"] = True

        return dashboard

    def describe_tier(self) -> str:
        """Print and return a human-readable description of the current tier."""
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Smart City Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  ✓ {f}")
        output = "\n".join(lines)
        print(output)
        return output
