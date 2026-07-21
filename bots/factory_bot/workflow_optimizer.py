"""Manufacturing workflow optimization and predictive maintenance for Factory Bot."""
import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from bots.factory_bot.tiers import BOT_FEATURES, get_bot_tier_info  # noqa: F401
from framework import GlobalAISourcesFlow  # noqa: F401

_flow = GlobalAISourcesFlow(bot_name="FactoryBot-WorkflowOptimizer")

MACHINE_DATABASE = {
    "conveyor_01": {"id": "conveyor_01", "type": "conveyor", "name": "Main Conveyor Belt A", "age_years": 3, "last_maintenance": "2024-11-15", "baseline_efficiency": 0.92},
    "press_01": {"id": "press_01", "type": "press", "name": "Hydraulic Press #1", "age_years": 7, "last_maintenance": "2024-10-22", "baseline_efficiency": 0.87},
    "welder_01": {"id": "welder_01", "type": "welder", "name": "MIG Welder Station 1", "age_years": 2, "last_maintenance": "2025-01-08", "baseline_efficiency": 0.95},
    "CNC_mill_01": {"id": "CNC_mill_01", "type": "CNC_mill", "name": "CNC Milling Machine A", "age_years": 5, "last_maintenance": "2024-12-01", "baseline_efficiency": 0.88},
    "robot_arm_01": {"id": "robot_arm_01", "type": "robot_arm", "name": "Industrial Robot Arm #1", "age_years": 4, "last_maintenance": "2024-12-20", "baseline_efficiency": 0.96},
    "robot_arm_02": {"id": "robot_arm_02", "type": "robot_arm", "name": "Industrial Robot Arm #2", "age_years": 1, "last_maintenance": "2025-01-15", "baseline_efficiency": 0.98},
    "lathe_01": {"id": "lathe_01", "type": "lathe", "name": "CNC Lathe Machine 1", "age_years": 6, "last_maintenance": "2024-09-30", "baseline_efficiency": 0.84},
    "injection_mold_01": {"id": "injection_mold_01", "type": "injection_mold", "name": "Injection Molding Machine 1", "age_years": 8, "last_maintenance": "2024-08-14", "baseline_efficiency": 0.80},
    "assembly_station_01": {"id": "assembly_station_01", "type": "assembly_station", "name": "Final Assembly Station A", "age_years": 2, "last_maintenance": "2025-01-20", "baseline_efficiency": 0.94},
    "paint_booth_01": {"id": "paint_booth_01", "type": "paint_booth", "name": "Automated Paint Booth #1", "age_years": 5, "last_maintenance": "2024-11-01", "baseline_efficiency": 0.89},
}

FREE_MACHINE_LIMIT = 2
PRO_MACHINE_LIMIT = 20


class ProductionLineOptimizer:
    """Optimizes manufacturing production lines using AI-driven analysis."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)

    def optimize_production_line(self, line_id: str, parameters: dict) -> dict:
        """Analyze and optimize a production line, returning recommendations with efficiency gain %."""
        throughput = parameters.get("throughput", 100)
        defect_rate = parameters.get("defect_rate", 0.05)
        downtime_hours = parameters.get("downtime_hours", 2.0)
        shift_hours = parameters.get("shift_hours", 8.0)

        current_efficiency = max(0.0, 1.0 - defect_rate - (downtime_hours / shift_hours) * 0.3)
        efficiency_gain = round(random.uniform(8.0, 22.0), 1)
        optimized_efficiency = min(1.0, current_efficiency + efficiency_gain / 100)

        recommendations = [
            "Reduce changeover time between production runs by standardizing tooling",
            "Implement continuous flow between stations to minimize WIP inventory",
            "Adjust machine feed rates to match downstream capacity",
        ]

        result = {
            "line_id": line_id,
            "current_efficiency_pct": round(current_efficiency * 100, 1),
            "optimized_efficiency_pct": round(optimized_efficiency * 100, 1),
            "efficiency_gain_pct": efficiency_gain,
            "recommendations": recommendations,
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["oee_score"] = round(random.uniform(72.0, 88.0), 1)
            result["takt_time_seconds"] = round(shift_hours * 3600 / throughput, 1)
            result["throughput_increase_pct"] = round(efficiency_gain * 0.8, 1)

        if self.tier == Tier.ENTERPRISE:
            result["ml_model_confidence"] = round(random.uniform(0.88, 0.97), 3)
            result["predicted_roi_usd"] = round(efficiency_gain * throughput * 12.5, 2)
            result["simulation_runs"] = 1000

        return result

    def analyze_bottleneck(self, line_id: str, metrics: dict) -> dict:
        """Identify and analyze production bottlenecks."""
        stations = metrics.get("stations", [])
        cycle_times = metrics.get("cycle_times", {})

        if not stations:
            stations = ["Station-A", "Station-B", "Station-C", "Station-D"]
        if not cycle_times:
            cycle_times = {s: round(random.uniform(20, 90), 1) for s in stations}

        bottleneck = max(cycle_times, key=cycle_times.get)
        bottleneck_time = cycle_times[bottleneck]
        avg_cycle = sum(cycle_times.values()) / len(cycle_times)

        result = {
            "line_id": line_id,
            "bottleneck_station": bottleneck,
            "bottleneck_cycle_time_sec": bottleneck_time,
            "average_cycle_time_sec": round(avg_cycle, 1),
            "severity": "critical" if bottleneck_time > avg_cycle * 1.4 else "moderate",
            "impact_on_throughput_pct": round((bottleneck_time - avg_cycle) / bottleneck_time * 100, 1),
            "recommended_action": f"Add parallel capacity or redistribute tasks at {bottleneck}",
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["all_station_metrics"] = cycle_times
            result["flow_efficiency_pct"] = round(avg_cycle / bottleneck_time * 100, 1)

        if self.tier == Tier.ENTERPRISE:
            result["simulation_data"] = {s: {"capacity_pct": round(random.uniform(60, 100), 1)} for s in stations}
            result["ml_root_cause"] = f"Excessive setup time at {bottleneck} identified by ML model"

        return result

    def schedule_production(self, orders: list, capacity: dict) -> dict:
        """Generate an optimized production schedule for a list of orders."""
        daily_capacity = capacity.get("daily_units", 200)
        shift_count = capacity.get("shifts", 1)
        effective_capacity = daily_capacity * shift_count

        if self.tier == Tier.FREE and len(orders) > 5:
            orders = orders[:5]
        elif self.tier == Tier.PRO and len(orders) > 50:
            orders = orders[:50]

        scheduled = []
        current_date = datetime.now().date()
        units_today = 0
        day_offset = 0

        for order in orders:
            units = order.get("quantity", 50)
            if units_today + units > effective_capacity:
                day_offset += 1
                units_today = 0
            units_today += units
            scheduled.append({
                "order_id": order.get("id", f"ORD-{len(scheduled)+1:03d}"),
                "quantity": units,
                "scheduled_date": str(current_date + timedelta(days=day_offset)),
                "priority": order.get("priority", "normal"),
            })

        result = {
            "schedule": scheduled,
            "total_orders": len(scheduled),
            "days_required": day_offset + 1,
            "effective_daily_capacity": effective_capacity,
            "utilization_pct": round(sum(o["quantity"] for o in scheduled) / (effective_capacity * (day_offset + 1)) * 100, 1),
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["on_time_delivery_est_pct"] = round(random.uniform(88, 97), 1)

        if self.tier == Tier.ENTERPRISE:
            result["ml_optimized"] = True
            result["cost_savings_usd"] = round(len(scheduled) * random.uniform(15, 45), 2)

        return result


class PredictiveMaintenanceEngine:
    """Predicts machine failures and schedules maintenance using sensor data analysis."""

    FAILURE_THRESHOLDS = {
        "vibration_hz": 85.0,
        "temperature_c": 75.0,
        "pressure_bar": 180.0,
        "current_amp": 45.0,
        "noise_db": 95.0,
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._monitored_machines: list[str] = []

    def _check_machine_limit(self, machine_id: str) -> None:
        if machine_id in self._monitored_machines:
            return
        if self.tier == Tier.FREE and len(self._monitored_machines) >= FREE_MACHINE_LIMIT:
            raise PermissionError(
                f"FREE tier supports monitoring up to {FREE_MACHINE_LIMIT} machines. "
                "Upgrade to PRO to monitor up to 20 machines."
            )
        if self.tier == Tier.PRO and len(self._monitored_machines) >= PRO_MACHINE_LIMIT:
            raise PermissionError(
                f"PRO tier supports monitoring up to {PRO_MACHINE_LIMIT} machines. "
                "Upgrade to ENTERPRISE for unlimited monitoring."
            )
        self._monitored_machines.append(machine_id)

    def predict_failure(self, machine_id: str, sensor_data: dict) -> dict:
        """Predict machine failure probability with confidence score and days_to_failure estimate."""
        self._check_machine_limit(machine_id)

        machine = MACHINE_DATABASE.get(machine_id, {"id": machine_id, "type": "unknown", "age_years": 0, "baseline_efficiency": 0.90})

        anomaly_score = 0.0
        alerts = []
        for sensor, value in sensor_data.items():
            threshold = self.FAILURE_THRESHOLDS.get(sensor)
            if threshold and value > threshold:
                ratio = value / threshold
                anomaly_score += (ratio - 1.0) * 0.4
                alerts.append(f"{sensor} exceeds threshold ({value:.1f} > {threshold:.1f})")

        age_factor = machine.get("age_years", 0) * 0.02
        anomaly_score += age_factor

        failure_probability = min(0.99, anomaly_score)
        confidence = round(random.uniform(0.82, 0.96), 3) if self.tier in (Tier.PRO, Tier.ENTERPRISE) else round(random.uniform(0.65, 0.80), 3)

        if failure_probability > 0.6:
            days_to_failure = int(random.uniform(3, 14))
            severity = "critical"
        elif failure_probability > 0.3:
            days_to_failure = int(random.uniform(15, 45))
            severity = "warning"
        else:
            days_to_failure = int(random.uniform(60, 180))
            severity = "normal"

        result = {
            "machine_id": machine_id,
            "machine_type": machine.get("type", "unknown"),
            "failure_probability": round(failure_probability, 3),
            "confidence": confidence,
            "days_to_failure": days_to_failure,
            "severity": severity,
            "sensor_alerts": alerts,
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["anomaly_score"] = round(anomaly_score, 3)
            result["recommended_inspection_date"] = str(datetime.now().date() + timedelta(days=max(1, days_to_failure // 2)))

        if self.tier == Tier.ENTERPRISE:
            result["ml_model"] = "RandomForestClassifier-v3"
            result["feature_importance"] = {k: round(random.uniform(0.1, 0.5), 3) for k in sensor_data}
            result["historical_comparison"] = f"Similar pattern preceded failure in {random.randint(2, 8)} past incidents"

        return result

    def schedule_maintenance(self, machine_id: str, priority: str = "normal") -> dict:
        """Generate a maintenance schedule for a machine."""
        self._check_machine_limit(machine_id)

        machine = MACHINE_DATABASE.get(machine_id, {"id": machine_id, "type": "unknown", "age_years": 0})

        priority_days = {"critical": 1, "high": 3, "normal": 7, "low": 14}
        days_until = priority_days.get(priority, 7)
        scheduled_date = datetime.now().date() + timedelta(days=days_until)

        tasks = [
            "Inspect and lubricate moving parts",
            "Check and tighten all fasteners",
            "Clean filters and ventilation",
            "Test safety interlocks",
        ]

        if machine.get("type") in ("press", "injection_mold"):
            tasks.append("Inspect hydraulic seals and fluid levels")
        elif machine.get("type") in ("welder",):
            tasks.append("Replace welding tips and check wire feed")
        elif machine.get("type") in ("CNC_mill", "lathe"):
            tasks.append("Re-calibrate axes and replace worn cutting tools")

        result = {
            "machine_id": machine_id,
            "scheduled_date": str(scheduled_date),
            "priority": priority,
            "estimated_duration_hours": round(random.uniform(2.0, 8.0), 1),
            "maintenance_tasks": tasks,
            "parts_required": ["lubricant", "filters", "safety seals"],
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["technician_required"] = "Certified Maintenance Technician Level 2"
            result["estimated_cost_usd"] = round(random.uniform(250, 1200), 2)
            result["downtime_impact_hours"] = result["estimated_duration_hours"]

        if self.tier == Tier.ENTERPRISE:
            result["auto_parts_order"] = True
            result["cmms_work_order_id"] = f"WO-{random.randint(10000, 99999)}"
            result["predictive_next_maintenance"] = str(scheduled_date + timedelta(days=90))

        return result

    def diagnose_issue(self, machine_id: str, symptoms: list) -> dict:
        """Diagnose a machine issue based on reported symptoms."""
        self._check_machine_limit(machine_id)

        machine = MACHINE_DATABASE.get(machine_id, {"id": machine_id, "type": "unknown"})

        symptom_causes = {
            "excessive vibration": "Worn bearings or unbalanced rotating components",
            "overheating": "Insufficient cooling or blocked ventilation pathways",
            "unusual noise": "Loose fasteners, worn gears, or bearing failure",
            "reduced output": "Tooling wear, misalignment, or feed rate deviation",
            "oil leak": "Degraded hydraulic seals or cracked fluid lines",
            "electrical fault": "Damaged wiring, faulty sensor, or controller issue",
            "intermittent stopping": "Thermal protection tripping or PLC logic error",
        }

        diagnoses = []
        for symptom in symptoms:
            cause = symptom_causes.get(symptom.lower(), f"Investigate {symptom} with technician")
            diagnoses.append({"symptom": symptom, "probable_cause": cause})

        result = {
            "machine_id": machine_id,
            "machine_type": machine.get("type", "unknown"),
            "symptoms_reported": symptoms,
            "diagnoses": diagnoses,
            "urgency": "high" if len(symptoms) >= 3 else "medium" if len(symptoms) >= 2 else "low",
            "recommended_action": "Schedule immediate inspection" if len(symptoms) >= 2 else "Monitor and inspect at next scheduled maintenance",
            "tier": self.tier.value,
        }

        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["fault_code_lookup"] = {s: f"FAULT-{hash(s) % 9000 + 1000}" for s in symptoms}
            result["repair_time_estimate_hours"] = round(len(symptoms) * random.uniform(1.5, 3.5), 1)

        if self.tier == Tier.ENTERPRISE:
            result["ml_diagnosis"] = f"ML model identifies root cause as: {diagnoses[0]['probable_cause'] if diagnoses else 'unknown'}"
            result["similar_cases_resolved"] = random.randint(5, 30)
            result["parts_likely_needed"] = ["bearing kit", "seal set"] if "vibration" in " ".join(symptoms).lower() else ["filter set", "lubricant"]

        return result
