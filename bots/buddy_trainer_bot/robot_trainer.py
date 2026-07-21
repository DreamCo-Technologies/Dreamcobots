"""
Robot Trainer — Train robotics systems with ML, code instructions, and adaptive loops.

Capabilities
------------
* Register industrial, consumer, and research robots.
* Send code/command instructions to robots via a unified interface.
* Train ML-driven control policies for robot motion and task execution.
* Adaptive learning loops: robots update their behavior based on sensor feedback
  and environmental interaction outcomes.
* Simulate sensor streams (proximity, force, vision, IMU) and evaluate responses.
* Track robot performance across training cycles.

All training and sensor logic is deterministic/simulated so no hardware
dependencies exist at runtime.  Production deployments can replace sensor
readers and control callers with real driver/SDK calls.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class RobotCategory(Enum):
    INDUSTRIAL = "industrial"
    CONSUMER = "consumer"
    RESEARCH = "research"
    MEDICAL = "medical"
    AGRICULTURAL = "agricultural"
    AUTONOMOUS_VEHICLE = "autonomous_vehicle"
    DRONE = "drone"
    HUMANOID = "humanoid"


class SensorType(Enum):
    PROXIMITY = "proximity"
    FORCE_TORQUE = "force_torque"
    VISION = "vision"
    IMU = "imu"
    LIDAR = "lidar"
    TEMPERATURE = "temperature"
    MICROPHONE = "microphone"


class TrainingPhase(Enum):
    CALIBRATION = "calibration"
    EXPLORATION = "exploration"
    EXPLOITATION = "exploitation"
    EVALUATION = "evaluation"
    CONVERGED = "converged"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class SensorReading:
    """A single reading from a robot sensor."""
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: float = field(default_factory=time.time)
    raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "sensor_type": self.sensor_type.value,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
        }


@dataclass
class Robot:
    """A registered robot target."""
    robot_id: str
    name: str
    category: RobotCategory
    manufacturer: str
    model: str
    sensors: list[SensorType]
    firmware_version: str = "1.0.0"
    registered_at: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "robot_id": self.robot_id,
            "name": self.name,
            "category": self.category.value,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "sensors": [s.value for s in self.sensors],
            "firmware_version": self.firmware_version,
            "registered_at": self.registered_at,
        }


@dataclass
class RobotTrainingCycle:
    """Records one adaptive learning cycle for a robot."""
    cycle_id: str
    robot_id: str
    phase: TrainingPhase
    instructions: list[str]
    sensor_readings: list[SensorReading]
    performance_score: float        # 0.0 – 1.0
    feedback: list[str]
    completed: bool = False
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "cycle_id": self.cycle_id,
            "robot_id": self.robot_id,
            "phase": self.phase.value,
            "instructions": self.instructions,
            "sensor_readings": [r.to_dict() for r in self.sensor_readings],
            "performance_score": round(self.performance_score, 4),
            "feedback": self.feedback,
            "completed": self.completed,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


# ---------------------------------------------------------------------------
# Heuristic helpers
# ---------------------------------------------------------------------------

_CATEGORY_BASE_PERF: dict[RobotCategory, float] = {
    RobotCategory.INDUSTRIAL: 0.85,
    RobotCategory.CONSUMER: 0.75,
    RobotCategory.RESEARCH: 0.80,
    RobotCategory.MEDICAL: 0.90,
    RobotCategory.AGRICULTURAL: 0.78,
    RobotCategory.AUTONOMOUS_VEHICLE: 0.82,
    RobotCategory.DRONE: 0.79,
    RobotCategory.HUMANOID: 0.65,
}

_PHASE_MULTIPLIER: dict[TrainingPhase, float] = {
    TrainingPhase.CALIBRATION: 0.60,
    TrainingPhase.EXPLORATION: 0.75,
    TrainingPhase.EXPLOITATION: 0.88,
    TrainingPhase.EVALUATION: 0.92,
    TrainingPhase.CONVERGED: 0.97,
}

def _simulate_sensor_readings(sensors: list[SensorType]) -> list[SensorReading]:
    """Generate deterministic simulated sensor readings."""
    readings: list[SensorReading] = []
    defaults: dict[SensorType, tuple[float, str]] = {
        SensorType.PROXIMITY: (0.35, "meters"),
        SensorType.FORCE_TORQUE: (12.5, "Nm"),
        SensorType.VISION: (0.95, "confidence"),
        SensorType.IMU: (0.02, "rad/s"),
        SensorType.LIDAR: (1.8, "meters"),
        SensorType.TEMPERATURE: (36.5, "°C"),
        SensorType.MICROPHONE: (42.0, "dB"),
    }
    for s in sensors:
        val, unit = defaults.get(s, (1.0, "units"))
        readings.append(SensorReading(sensor_type=s, value=val, unit=unit))
    return readings


def _generate_robot_feedback(
    performance: float, phase: TrainingPhase, instructions: list[str]
) -> list[str]:
    tips: list[str] = []
    if performance >= 0.90:
        tips.append("Robot is performing excellently. Ready to advance to next phase.")
    elif performance >= 0.75:
        tips.append("Good performance. Fine-tune motion parameters for better precision.")
    else:
        tips.append("Performance below target. Increase training cycles or refine instructions.")
    if phase == TrainingPhase.CALIBRATION:
        tips.append("Calibration phase: ensure sensors are correctly initialised.")
    elif phase == TrainingPhase.EXPLORATION:
        tips.append("Exploration phase: robot is discovering the environment autonomously.")
    elif phase == TrainingPhase.CONVERGED:
        tips.append("Training converged! Deploy the control policy to production.")
    if len(instructions) == 0:
        tips.append("No instructions provided — add code commands to guide the robot.")
    tips.append(f"Performance score: {performance * 100:.1f}%.")
    return tips


# ---------------------------------------------------------------------------
# Core class
# ---------------------------------------------------------------------------

class RobotTrainer:
    """
    Trains robotics systems across all categories using ML control policies
    and direct code instructions with adaptive environmental feedback loops.

    Parameters
    ----------
    trainer_id : str
        Unique identifier for this trainer instance.
    """

    def __init__(self, trainer_id: str = "buddy_robot_trainer_v1") -> None:
        self.trainer_id = trainer_id
        self._robots: dict[str, Robot] = {}
        self._cycles: dict[str, list[RobotTrainingCycle]] = {}  # robot_id -> cycles
        self._policies: dict[str, dict] = {}   # robot_id -> latest control policy

    # ------------------------------------------------------------------
    # Robot registration
    # ------------------------------------------------------------------

    def register_robot(
        self,
        name: str,
        category: RobotCategory,
        manufacturer: str,
        model: str,
        sensors: Optional[list[SensorType]] = None,
        firmware_version: str = "1.0.0",
        metadata: Optional[dict] = None,
    ) -> Robot:
        """Register a new robot for training."""
        robot_id = f"robot_{uuid.uuid4().hex[:10]}"
        robot = Robot(
            robot_id=robot_id,
            name=name,
            category=category,
            manufacturer=manufacturer,
            model=model,
            sensors=sensors or [SensorType.PROXIMITY, SensorType.VISION],
            firmware_version=firmware_version,
            metadata=metadata or {},
        )
        self._robots[robot_id] = robot
        return robot

    def get_robot(self, robot_id: str) -> Robot:
        if robot_id not in self._robots:
            raise KeyError(f"Robot '{robot_id}' not found.")
        return self._robots[robot_id]

    def list_robots(self) -> list[Robot]:
        return list(self._robots.values())

    # ------------------------------------------------------------------
    # Training cycles (adaptive loop)
    # ------------------------------------------------------------------

    def run_training_cycle(
        self,
        robot_id: str,
        instructions: Optional[list[str]] = None,
        phase: TrainingPhase = TrainingPhase.EXPLORATION,
    ) -> RobotTrainingCycle:
        """
        Execute one adaptive training cycle for a robot.

        The cycle:
        1. Reads simulated sensor data from the robot environment.
        2. Evaluates performance against the current training phase.
        3. Generates adaptive feedback for the next iteration.
        4. Stores the result and updates the control policy.
        """
        robot = self.get_robot(robot_id)
        cycle_id = f"cycle_{uuid.uuid4().hex[:12]}"
        instructions = instructions or ["move_forward", "scan_environment", "avoid_obstacle"]

        # Simulate sensor readings
        readings = _simulate_sensor_readings(robot.sensors)

        # Compute performance
        base = _CATEGORY_BASE_PERF.get(robot.category, 0.75)
        multiplier = _PHASE_MULTIPLIER.get(phase, 0.80)
        instruction_bonus = min(len(instructions) * 0.02, 0.08)
        performance = min(base * multiplier + instruction_bonus, 0.999)

        feedback = _generate_robot_feedback(performance, phase, instructions)

        cycle = RobotTrainingCycle(
            cycle_id=cycle_id,
            robot_id=robot_id,
            phase=phase,
            instructions=list(instructions),
            sensor_readings=readings,
            performance_score=round(performance, 4),
            feedback=feedback,
            completed=True,
            completed_at=time.time(),
        )

        self._cycles.setdefault(robot_id, []).append(cycle)

        # Update control policy
        self._policies[robot_id] = {
            "robot_id": robot_id,
            "last_phase": phase.value,
            "best_performance": max(
                c.performance_score for c in self._cycles[robot_id]
            ),
            "total_cycles": len(self._cycles[robot_id]),
            "last_instructions": instructions,
        }

        return cycle

    def run_adaptive_loop(
        self,
        robot_id: str,
        num_cycles: int = 5,
        starting_phase: TrainingPhase = TrainingPhase.CALIBRATION,
    ) -> list[RobotTrainingCycle]:
        """
        Run a full adaptive learning loop across multiple training phases.

        The loop automatically advances through phases as performance improves.
        """
        phases = [
            TrainingPhase.CALIBRATION,
            TrainingPhase.EXPLORATION,
            TrainingPhase.EXPLOITATION,
            TrainingPhase.EVALUATION,
            TrainingPhase.CONVERGED,
        ]
        start_idx = phases.index(starting_phase)
        cycles_run: list[RobotTrainingCycle] = []
        current_phase_idx = start_idx

        for i in range(num_cycles):
            phase = phases[min(current_phase_idx, len(phases) - 1)]
            cycle = self.run_training_cycle(robot_id, phase=phase)
            cycles_run.append(cycle)
            # Advance phase when performance crosses 0.80
            if cycle.performance_score >= 0.80 and current_phase_idx < len(phases) - 1:
                current_phase_idx += 1

        return cycles_run

    def get_control_policy(self, robot_id: str) -> dict:
        """Return the latest trained control policy for a robot."""
        if robot_id not in self._policies:
            raise KeyError(f"No policy found for robot '{robot_id}'. Run at least one cycle.")
        return self._policies[robot_id]

    def list_cycles(self, robot_id: str) -> list[RobotTrainingCycle]:
        return self._cycles.get(robot_id, [])

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        return {
            "trainer_id": self.trainer_id,
            "total_robots": len(self._robots),
            "robots_with_policies": len(self._policies),
            "total_cycles": sum(len(v) for v in self._cycles.values()),
        }
