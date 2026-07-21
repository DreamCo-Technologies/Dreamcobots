"""Factory Bot — tier-aware manufacturing workflow optimizer and green manufacturing assistant."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from bots.factory_bot.tiers import BOT_FEATURES, get_bot_tier_info  # noqa: F401
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.factory_bot.workflow_optimizer import (
    ProductionLineOptimizer,
    PredictiveMaintenanceEngine,
    MACHINE_DATABASE,
)
from bots.factory_bot.green_manufacturing import (
    EnergyEfficiencyMonitor,
    GreenInitiativeManager,
)

_flow = GlobalAISourcesFlow(bot_name="FactoryBot")


class FactoryBotError(Exception):
    """Raised when a Factory Bot feature is not available on the current tier."""


class FactoryBot:
    """Tier-aware manufacturing assistant combining workflow optimization and green manufacturing."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._optimizer = ProductionLineOptimizer(tier=tier)
        self._maintenance = PredictiveMaintenanceEngine(tier=tier)
        self._energy = EnergyEfficiencyMonitor(tier=tier)
        self._green = GreenInitiativeManager(tier=tier)

    # ------------------------------------------------------------------
    # Workflow & production
    # ------------------------------------------------------------------

    def optimize_workflow(self, line_id: str, parameters: dict) -> dict:
        """Optimize a production line workflow. Returns recommendations with efficiency gain %."""
        return self._optimizer.optimize_production_line(line_id, parameters)

    def analyze_bottleneck(self, line_id: str, metrics: dict) -> dict:
        """Identify and analyze bottlenecks in a production line."""
        return self._optimizer.analyze_bottleneck(line_id, metrics)

    def schedule_production(self, orders: list, capacity: dict) -> dict:
        """Schedule production orders against available capacity."""
        return self._optimizer.schedule_production(orders, capacity)

    # ------------------------------------------------------------------
    # Predictive maintenance
    # ------------------------------------------------------------------

    def predict_maintenance(self, machine_id: str, sensor_data: dict) -> dict:
        """Predict machine failure risk and return maintenance recommendation."""
        try:
            return self._maintenance.predict_failure(machine_id, sensor_data)
        except PermissionError as exc:
            raise FactoryBotError(str(exc)) from exc

    def schedule_maintenance(self, machine_id: str, priority: str = "normal") -> dict:
        """Schedule maintenance for a machine."""
        try:
            return self._maintenance.schedule_maintenance(machine_id, priority)
        except PermissionError as exc:
            raise FactoryBotError(str(exc)) from exc

    def diagnose_machine(self, machine_id: str, symptoms: list) -> dict:
        """Diagnose a machine issue from reported symptoms."""
        try:
            return self._maintenance.diagnose_issue(machine_id, symptoms)
        except PermissionError as exc:
            raise FactoryBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Energy & sustainability
    # ------------------------------------------------------------------

    def monitor_energy(self, facility_id: str) -> dict:
        """Monitor energy usage for a facility and return a consumption report."""
        return self._energy.monitor_energy_usage(facility_id)

    def optimize_energy(self, facility_id: str) -> dict:
        """Generate energy optimization recommendations for a facility."""
        return self._energy.optimize_energy(facility_id)

    def calculate_carbon_footprint(self, production_data: dict) -> dict:
        """Calculate carbon footprint of manufacturing operations."""
        return self._energy.calculate_carbon_footprint(production_data)

    def get_sustainability_report(self, facility_id: str) -> dict:
        """Generate a comprehensive green manufacturing sustainability report."""
        return self._green.generate_green_report(facility_id)

    def assess_sustainability(self, facility_id: str) -> dict:
        """Assess sustainability performance and return a score with recommendations."""
        return self._green.assess_sustainability(facility_id)

    def plan_waste_reduction(self, facility_id: str, waste_data: dict) -> dict:
        """Create a waste reduction plan for a facility."""
        return self._green.plan_waste_reduction(facility_id, waste_data)

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def get_factory_dashboard(self) -> dict:
        """Return a high-level factory dashboard summary."""
        dashboard = {
            "bot": "FactoryBot",
            "tier": self.tier.value,
            "features": BOT_FEATURES[self.tier.value],
            "machine_count": len(MACHINE_DATABASE),
            "modules": ["WorkflowOptimizer", "PredictiveMaintenance", "EnergyMonitor", "GreenInitiatives"],
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            dashboard["upgrade_path"] = None
            next_tier = get_upgrade_path(self.tier)
            if next_tier:
                dashboard["upgrade_path"] = {
                    "next_tier": next_tier.name,
                    "price_usd_monthly": next_tier.price_usd_monthly,
                }

        if self.tier == Tier.ENTERPRISE:
            dashboard["enterprise_features"] = [
                "ML-powered predictions",
                "Unlimited machine monitoring",
                "Real-time sensor analytics",
                "Comprehensive regulatory reports",
            ]

        return dashboard

    def describe_tier(self) -> str:
        """Print and return a formatted tier description."""
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Factory Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for feature in info["features"]:
            lines.append(f"  ✓ {feature}")
        output = "\n".join(lines)
        print(output)
        return output
