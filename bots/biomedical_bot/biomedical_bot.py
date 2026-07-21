"""Biomedical Bot — tier-aware wearable health monitoring and precision medicine."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.biomedical_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.biomedical_bot.health_monitor import WearableHealthMonitor, WearableHealthMonitorError
from bots.biomedical_bot.precision_medicine import (
    NanotechDiseaseDetector,
    NanotechDiseaseDetectorError,
    PrecisionMedicineEngine,
    PrecisionMedicineError,
)

_flow = GlobalAISourcesFlow(bot_name="BiomedicalBot")


class BiomedicalBotError(Exception):
    """Raised when a feature is not available on the current tier."""


class BiomedicalBot:
    """Tier-aware Biomedical Bot integrating wearable health monitoring
    and precision medicine services."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.monitor = WearableHealthMonitor(tier=tier)
        self.detector = NanotechDiseaseDetector(tier=tier)
        self.medicine = PrecisionMedicineEngine(tier=tier)
        self._activity_log: list = []

    # ------------------------------------------------------------------
    # Patient monitoring
    # ------------------------------------------------------------------

    def monitor_patient(self, patient_id: str, metrics_data: dict) -> dict:
        """Monitor a patient's wearable health metrics.

        metrics_data: {metric: value_or_list, ...}
        Supports both single-value vitals and list-of-readings for
        heart_rate and glucose.
        """
        try:
            results = {}
            if "heart_rate" in metrics_data:
                readings = metrics_data["heart_rate"]
                if isinstance(readings, list):
                    results["heart_rate"] = self.monitor.monitor_heart_rate(patient_id, readings)
                else:
                    results["heart_rate"] = self.monitor.monitor_heart_rate(patient_id, [readings])

            if "glucose" in metrics_data:
                readings = metrics_data["glucose"]
                if isinstance(readings, list):
                    results["glucose"] = self.monitor.monitor_glucose(patient_id, readings)
                else:
                    results["glucose"] = self.monitor.monitor_glucose(patient_id, [readings])

            # Track remaining metrics as vitals
            vitals = {k: v for k, v in metrics_data.items()
                      if k not in ("heart_rate", "glucose") and not isinstance(v, list)}
            if vitals:
                results["vitals"] = self.monitor.track_vitals(patient_id, vitals)

            self._activity_log.append({"action": "monitor_patient", "patient_id": patient_id})
            return {"patient_id": patient_id, "monitoring_results": results, "tier": self.tier.value}
        except WearableHealthMonitorError as exc:
            raise BiomedicalBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Disease detection
    # ------------------------------------------------------------------

    def detect_disease(self, sample_data: dict) -> dict:
        """Run disease marker screening (PRO+) or genomic analysis (ENTERPRISE).

        sample_data: {marker: value, ...} or {"variants": [...], "patient_id": str}
        """
        try:
            if self.tier == Tier.ENTERPRISE and "variants" in sample_data:
                result = self.detector.analyze_dna_sequence(sample_data)
            else:
                result = self.detector.detect_disease_markers(sample_data)
            self._activity_log.append({"action": "detect_disease"})
            return result
        except NanotechDiseaseDetectorError as exc:
            raise BiomedicalBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Treatment planning
    # ------------------------------------------------------------------

    def get_treatment_plan(self, patient_id: str, condition: str) -> dict:
        """Generate a personalised treatment plan (ENTERPRISE only)."""
        try:
            result = self.medicine.generate_treatment_plan(patient_id, condition)
            self._activity_log.append({"action": "treatment_plan", "patient_id": patient_id})
            return result
        except PrecisionMedicineError as exc:
            raise BiomedicalBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def generate_patient_report(self, patient_id: str) -> dict:
        """Generate a comprehensive health report for a patient."""
        try:
            report = self.monitor.generate_health_report(patient_id)
            self._activity_log.append({"action": "generate_report", "patient_id": patient_id})
            return report
        except WearableHealthMonitorError as exc:
            raise BiomedicalBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def get_medical_dashboard(self) -> dict:
        """Return a high-level medical operations dashboard."""
        upgrade = get_upgrade_path(self.tier)
        tier_info = get_bot_tier_info(self.tier)

        dashboard = {
            "bot": "BiomedicalBot",
            "tier": self.tier.value,
            "tier_name": tier_info["name"],
            "price_usd_monthly": tier_info["price_usd_monthly"],
            "features": tier_info["features"],
            "support_level": tier_info["support_level"],
            "activity_count": len(self._activity_log),
            "services_available": [
                "wearable_health_monitoring",
                "heart_rate_analysis",
                "glucose_monitoring",
                "vitals_tracking",
                "health_report_generation",
                "anomaly_detection",
            ],
            "upgrade_available": upgrade is not None,
        }

        if upgrade:
            dashboard["upgrade_to"] = upgrade.name
            dashboard["upgrade_price_usd_monthly"] = upgrade.price_usd_monthly

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            dashboard["advanced_analytics"] = True
            dashboard["services_available"] += [
                "disease_marker_screening",
                "treatment_recommendations",
                "patient_profiling",
            ]

        if self.tier == Tier.ENTERPRISE:
            dashboard["api_access"] = True
            dashboard["ml_predictions"] = True
            dashboard["nanotech_detection"] = True
            dashboard["genomic_analysis"] = True
            dashboard["services_available"] += [
                "dna_sequence_analysis",
                "drug_efficacy_prediction",
                "full_treatment_planning",
            ]

        return dashboard

    def describe_tier(self) -> str:
        """Print and return a human-readable description of the current tier."""
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Biomedical Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  ✓ {f}")
        output = "\n".join(lines)
        print(output)
        return output
