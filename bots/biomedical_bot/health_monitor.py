"""Wearable Health Technology Monitoring — heart rate, glucose, vitals, and anomaly detection."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from framework import GlobalAISourcesFlow  # noqa: F401

_flow = GlobalAISourcesFlow(bot_name="WearableHealthMonitor")

# Normal vital-sign thresholds  {metric: (low, high)}
VITAL_THRESHOLDS = {
    "heart_rate":       (60, 100),      # bpm
    "glucose":          (70, 140),      # mg/dL
    "systolic_bp":      (90, 120),      # mmHg
    "diastolic_bp":     (60, 80),       # mmHg
    "spo2":             (95, 100),      # %
    "respiratory_rate": (12, 20),       # breaths/min
    "temperature":      (36.1, 37.2),   # °C
    "steps":            (0, 20_000),    # steps/day — upper is soft limit
}

# Metrics available per tier
_FREE_METRICS = {"heart_rate", "steps", "sleep"}
_PRO_METRICS = _FREE_METRICS | {"glucose", "systolic_bp", "diastolic_bp", "spo2", "respiratory_rate", "temperature"}
_ENTERPRISE_METRICS = _PRO_METRICS  # enterprise adds ML on top


class WearableHealthMonitorError(Exception):
    """Raised when a tier limit is exceeded."""


class WearableHealthMonitor:
    """Tier-aware wearable health-tech monitoring system."""

    _PATIENT_LIMITS = {Tier.FREE: 1, Tier.PRO: 20, Tier.ENTERPRISE: None}
    _METRIC_SETS = {Tier.FREE: _FREE_METRICS, Tier.PRO: _PRO_METRICS, Tier.ENTERPRISE: _ENTERPRISE_METRICS}

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._patient_data: dict = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_patient_limit(self, patient_id: str) -> None:
        limit = self._PATIENT_LIMITS[self.tier]
        if patient_id not in self._patient_data:
            if limit is not None and len(self._patient_data) >= limit:
                raise WearableHealthMonitorError(
                    f"{self.tier.value.upper()} tier allows only {limit} patient(s). "
                    "Upgrade to PRO or ENTERPRISE for more patients."
                )
            self._patient_data[patient_id] = {}

    def _check_metric(self, metric: str) -> None:
        allowed = self._METRIC_SETS[self.tier]
        if metric not in allowed:
            raise WearableHealthMonitorError(
                f"Metric '{metric}' is not available on the {self.tier.value.upper()} tier. "
                "Upgrade to PRO or ENTERPRISE to access all metrics."
            )

    def _is_anomalous(self, metric: str, value: float) -> bool:
        if metric not in VITAL_THRESHOLDS:
            return False
        low, high = VITAL_THRESHOLDS[metric]
        return value < low or value > high

    def _severity(self, metric: str, value: float) -> str:
        if metric not in VITAL_THRESHOLDS:
            return "unknown"
        low, high = VITAL_THRESHOLDS[metric]
        deviation = max(low - value, value - high, 0)
        span = (high - low) or 1
        ratio = deviation / span
        if ratio > 0.5:
            return "critical"
        if ratio > 0.2:
            return "high"
        return "moderate"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def monitor_heart_rate(self, patient_id: str, readings: list) -> dict:
        """Analyse a list of heart-rate readings (bpm) for a patient."""
        self._check_patient_limit(patient_id)
        self._check_metric("heart_rate")

        if not readings:
            return {"patient_id": patient_id, "metric": "heart_rate", "status": "no_data", "readings": []}

        avg = sum(readings) / len(readings)
        minimum = min(readings)
        maximum = max(readings)
        anomalies = [r for r in readings if self._is_anomalous("heart_rate", r)]

        result = {
            "patient_id": patient_id,
            "metric": "heart_rate",
            "average_bpm": round(avg, 1),
            "min_bpm": minimum,
            "max_bpm": maximum,
            "reading_count": len(readings),
            "anomaly_count": len(anomalies),
            "status": "alert" if anomalies else "normal",
            "normal_range": VITAL_THRESHOLDS["heart_rate"],
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["trend"] = "increasing" if readings[-1] > readings[0] else "decreasing" if readings[-1] < readings[0] else "stable"
            result["anomalous_readings"] = anomalies

        if self.tier == Tier.ENTERPRISE:
            result["ml_risk_score"] = round(min(len(anomalies) / max(len(readings), 1) * 100, 100), 1)
            result["prediction"] = "elevated_risk" if result["ml_risk_score"] > 20 else "normal_risk"

        self._patient_data[patient_id]["heart_rate"] = result
        return result

    def monitor_glucose(self, patient_id: str, readings: list) -> dict:
        """Analyse glucose-level readings (mg/dL) for a patient."""
        self._check_patient_limit(patient_id)
        self._check_metric("glucose")

        if not readings:
            return {"patient_id": patient_id, "metric": "glucose", "status": "no_data", "readings": []}

        avg = sum(readings) / len(readings)
        anomalies = [r for r in readings if self._is_anomalous("glucose", r)]
        hypoglycemic = [r for r in readings if r < VITAL_THRESHOLDS["glucose"][0]]
        hyperglycemic = [r for r in readings if r > VITAL_THRESHOLDS["glucose"][1]]

        result = {
            "patient_id": patient_id,
            "metric": "glucose",
            "average_mg_dl": round(avg, 1),
            "min_mg_dl": min(readings),
            "max_mg_dl": max(readings),
            "reading_count": len(readings),
            "anomaly_count": len(anomalies),
            "hypoglycemic_events": len(hypoglycemic),
            "hyperglycemic_events": len(hyperglycemic),
            "status": "alert" if anomalies else "normal",
            "normal_range": VITAL_THRESHOLDS["glucose"],
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["trend"] = "increasing" if readings[-1] > readings[0] else "decreasing" if readings[-1] < readings[0] else "stable"
            result["anomalous_readings"] = anomalies

        if self.tier == Tier.ENTERPRISE:
            result["ml_risk_score"] = round(min(len(anomalies) / max(len(readings), 1) * 100, 100), 1)
            result["diabetes_risk"] = "elevated" if avg > 126 else "normal"

        self._patient_data[patient_id]["glucose"] = result
        return result

    def track_vitals(self, patient_id: str, vitals_dict: dict) -> dict:
        """Track multiple vitals at once from a dict of {metric: value}."""
        self._check_patient_limit(patient_id)

        results = {}
        alerts = []
        for metric, value in vitals_dict.items():
            try:
                self._check_metric(metric)
            except WearableHealthMonitorError:
                results[metric] = {"status": "unavailable_on_tier"}
                continue

            anomalous = self._is_anomalous(metric, value)
            entry = {
                "value": value,
                "status": "alert" if anomalous else "normal",
                "normal_range": VITAL_THRESHOLDS.get(metric),
            }
            if anomalous:
                entry["severity"] = self._severity(metric, value)
                alerts.append(metric)
            results[metric] = entry
            self._patient_data[patient_id][metric] = {"value": value, "status": entry["status"]}

        return {
            "patient_id": patient_id,
            "vitals": results,
            "alert_metrics": alerts,
            "overall_status": "alert" if alerts else "normal",
            "tier": self.tier.value,
        }

    def generate_health_report(self, patient_id: str) -> dict:
        """Generate a health summary report for a patient."""
        self._check_patient_limit(patient_id)

        data = self._patient_data.get(patient_id, {})
        alert_metrics = [m for m, v in data.items() if isinstance(v, dict) and v.get("status") == "alert"]

        report = {
            "patient_id": patient_id,
            "report_type": "health_summary",
            "tier": self.tier.value,
            "metrics_tracked": list(data.keys()),
            "metrics_count": len(data),
            "alert_count": len(alert_metrics),
            "alert_metrics": alert_metrics,
            "overall_health": "needs_attention" if alert_metrics else "good",
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            report["detailed_data"] = data
            report["recommendations"] = (
                [f"Consult physician about {m}" for m in alert_metrics]
                if alert_metrics else ["Continue current health regimen"]
            )

        if self.tier == Tier.ENTERPRISE:
            report["ml_insights"] = {
                "risk_stratification": "high" if len(alert_metrics) > 2 else "medium" if alert_metrics else "low",
                "predicted_trend": "deteriorating" if len(alert_metrics) > 2 else "stable",
            }

        return report

    def alert_anomaly(self, patient_id: str, metric: str, value: float) -> dict:
        """Detect and return an anomaly alert for a specific metric/value."""
        self._check_patient_limit(patient_id)
        self._check_metric(metric)

        anomalous = self._is_anomalous(metric, value)
        alert = {
            "patient_id": patient_id,
            "metric": metric,
            "value": value,
            "anomaly_detected": anomalous,
            "normal_range": VITAL_THRESHOLDS.get(metric),
            "alert_level": self._severity(metric, value) if anomalous else "none",
            "action_required": anomalous,
        }

        if anomalous and self.tier in (Tier.PRO, Tier.ENTERPRISE):
            low, high = VITAL_THRESHOLDS.get(metric, (None, None))
            if low is not None and value < low:
                alert["direction"] = "below_normal"
                alert["message"] = f"{metric} value {value} is below the normal minimum of {low}"
            elif high is not None and value > high:
                alert["direction"] = "above_normal"
                alert["message"] = f"{metric} value {value} is above the normal maximum of {high}"

        if self.tier == Tier.ENTERPRISE and anomalous:
            alert["auto_escalate"] = True
            alert["notify_channels"] = ["ehr_system", "attending_physician", "emergency_contact"]

        return alert
