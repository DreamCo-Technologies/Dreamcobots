"""
AI Trainer — Real-time AI model training, versioning, and deployment.

Capabilities
------------
* Start and manage AI training sessions with adaptive feedback loops.
* Fine-tune models on user-supplied datasets; track training metrics.
* Version AI models automatically — each session creates a new version snapshot.
* Deploy trained models and roll back to any previous version.
* Conversational interface returns actionable guidance at every step.

All training logic is deterministic/rule-based so there are no external ML
dependencies at runtime.  Production deployments can swap the estimator
methods with real framework calls (PyTorch, TF, HuggingFace, etc.).
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ModelType(Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    REINFORCEMENT = "reinforcement"
    GENERATIVE = "generative"
    ROBOTICS_CONTROL = "robotics_control"


class TrainingStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Dataset:
    """A dataset used for AI model training."""
    dataset_id: str
    name: str
    num_samples: int
    labels: list[str]
    source: str
    created_at: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "dataset_id": self.dataset_id,
            "name": self.name,
            "num_samples": self.num_samples,
            "labels": self.labels,
            "source": self.source,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@dataclass
class ModelVersion:
    """A versioned snapshot of an AI model."""
    version_id: str
    model_name: str
    version_number: int
    accuracy: float          # 0.0 – 1.0
    loss: float
    parameters: dict
    training_session_id: str
    created_at: float = field(default_factory=time.time)
    deployed: bool = False
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "version_id": self.version_id,
            "model_name": self.model_name,
            "version_number": self.version_number,
            "accuracy": round(self.accuracy, 4),
            "loss": round(self.loss, 4),
            "parameters": self.parameters,
            "training_session_id": self.training_session_id,
            "created_at": self.created_at,
            "deployed": self.deployed,
            "notes": self.notes,
        }


@dataclass
class TrainingSession:
    """Records a single AI model training run."""
    session_id: str
    model_name: str
    model_type: ModelType
    dataset_id: str
    epochs: int
    learning_rate: float
    status: TrainingStatus
    accuracy: float = 0.0
    loss: float = 1.0
    feedback: list[str] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    version_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "model_name": self.model_name,
            "model_type": self.model_type.value,
            "dataset_id": self.dataset_id,
            "epochs": self.epochs,
            "learning_rate": self.learning_rate,
            "status": self.status.value,
            "accuracy": round(self.accuracy, 4),
            "loss": round(self.loss, 4),
            "feedback": self.feedback,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "version_id": self.version_id,
        }


# ---------------------------------------------------------------------------
# Heuristic helpers
# ---------------------------------------------------------------------------

_BASE_ACCURACY: dict[ModelType, float] = {
    ModelType.CLASSIFICATION: 0.82,
    ModelType.REGRESSION: 0.78,
    ModelType.NLP: 0.86,
    ModelType.COMPUTER_VISION: 0.80,
    ModelType.REINFORCEMENT: 0.70,
    ModelType.GENERATIVE: 0.75,
    ModelType.ROBOTICS_CONTROL: 0.72,
}

def _simulate_accuracy(
    model_type: ModelType,
    epochs: int,
    learning_rate: float,
    num_samples: int,
) -> tuple[float, float]:
    """Deterministically estimate accuracy and loss for a training run."""
    base = _BASE_ACCURACY.get(model_type, 0.75)
    epoch_bonus = min(epochs * 0.003, 0.12)
    lr_penalty = abs(learning_rate - 0.001) * 5.0
    sample_bonus = min(num_samples / 100_000, 0.05)
    accuracy = min(base + epoch_bonus + sample_bonus - lr_penalty, 0.999)
    loss = max(1.0 - accuracy, 0.001)
    return round(accuracy, 4), round(loss, 4)


def _generate_feedback(
    accuracy: float,
    loss: float,
    epochs: int,
    learning_rate: float,
) -> list[str]:
    """Return a list of adaptive training feedback messages."""
    tips: list[str] = []
    if accuracy >= 0.95:
        tips.append("Excellent accuracy! Consider evaluating on a held-out test set.")
    elif accuracy >= 0.85:
        tips.append("Good accuracy. Try increasing epochs or tuning the learning rate.")
    else:
        tips.append("Accuracy is below target. Consider adding more labelled samples.")
    if loss > 0.3:
        tips.append("High loss detected. Reduce learning rate or add regularisation.")
    if epochs < 10:
        tips.append("Training ran for fewer than 10 epochs — consider longer runs for stability.")
    if learning_rate > 0.1:
        tips.append("Learning rate seems high; try 0.001 – 0.01 for most architectures.")
    tips.append(f"Model reached {accuracy * 100:.1f}% accuracy with loss {loss:.4f}.")
    return tips


# ---------------------------------------------------------------------------
# Core class
# ---------------------------------------------------------------------------

class AITrainer:
    """
    Real-time AI model trainer with adaptive feedback, versioning, and
    deployment capabilities.

    Parameters
    ----------
    trainer_id : str
        Unique identifier for this trainer instance.
    """

    def __init__(self, trainer_id: str = "buddy_ai_trainer_v1") -> None:
        self.trainer_id = trainer_id
        self._datasets: dict[str, Dataset] = {}
        self._sessions: dict[str, TrainingSession] = {}
        self._versions: dict[str, list[ModelVersion]] = {}  # model_name -> versions
        self._deployed: dict[str, str] = {}  # model_name -> version_id

    # ------------------------------------------------------------------
    # Dataset management
    # ------------------------------------------------------------------

    def register_dataset(
        self,
        name: str,
        num_samples: int,
        labels: list[str],
        source: str = "user_upload",
        metadata: Optional[dict] = None,
    ) -> Dataset:
        """Register a new dataset for training."""
        dataset_id = f"ds_{hashlib.md5(f'{name}{time.time()}'.encode()).hexdigest()[:10]}"
        ds = Dataset(
            dataset_id=dataset_id,
            name=name,
            num_samples=num_samples,
            labels=labels,
            source=source,
            metadata=metadata or {},
        )
        self._datasets[dataset_id] = ds
        return ds

    def list_datasets(self) -> list[Dataset]:
        return list(self._datasets.values())

    def get_dataset(self, dataset_id: str) -> Dataset:
        if dataset_id not in self._datasets:
            raise KeyError(f"Dataset '{dataset_id}' not found.")
        return self._datasets[dataset_id]

    # ------------------------------------------------------------------
    # Training sessions
    # ------------------------------------------------------------------

    def start_training(
        self,
        model_name: str,
        model_type: ModelType,
        dataset_id: str,
        epochs: int = 20,
        learning_rate: float = 0.001,
    ) -> TrainingSession:
        """
        Start a new AI training session with adaptive feedback.

        Returns the completed session (training is synchronous/simulated).
        """
        if dataset_id not in self._datasets:
            raise KeyError(f"Dataset '{dataset_id}' not found.")

        dataset = self._datasets[dataset_id]
        session_id = f"sess_{uuid.uuid4().hex[:12]}"

        session = TrainingSession(
            session_id=session_id,
            model_name=model_name,
            model_type=model_type,
            dataset_id=dataset_id,
            epochs=epochs,
            learning_rate=learning_rate,
            status=TrainingStatus.IN_PROGRESS,
        )
        self._sessions[session_id] = session

        # Simulate training
        accuracy, loss = _simulate_accuracy(
            model_type, epochs, learning_rate, dataset.num_samples
        )
        session.accuracy = accuracy
        session.loss = loss
        session.feedback = _generate_feedback(accuracy, loss, epochs, learning_rate)
        session.status = TrainingStatus.COMPLETED
        session.completed_at = time.time()

        # Auto-version the result
        version = self._create_version(session, accuracy, loss)
        session.version_id = version.version_id

        return session

    def get_session(self, session_id: str) -> TrainingSession:
        if session_id not in self._sessions:
            raise KeyError(f"Session '{session_id}' not found.")
        return self._sessions[session_id]

    def list_sessions(self, model_name: Optional[str] = None) -> list[TrainingSession]:
        sessions = list(self._sessions.values())
        if model_name:
            sessions = [s for s in sessions if s.model_name == model_name]
        return sessions

    # ------------------------------------------------------------------
    # Versioning
    # ------------------------------------------------------------------

    def _create_version(
        self, session: TrainingSession, accuracy: float, loss: float
    ) -> ModelVersion:
        """Auto-create a version snapshot after a completed training session."""
        versions = self._versions.setdefault(session.model_name, [])
        version_number = len(versions) + 1
        version_id = f"v{version_number}_{uuid.uuid4().hex[:8]}"
        mv = ModelVersion(
            version_id=version_id,
            model_name=session.model_name,
            version_number=version_number,
            accuracy=accuracy,
            loss=loss,
            parameters={
                "epochs": session.epochs,
                "learning_rate": session.learning_rate,
                "model_type": session.model_type.value,
            },
            training_session_id=session.session_id,
        )
        versions.append(mv)
        return mv

    def list_versions(self, model_name: str) -> list[ModelVersion]:
        return list(self._versions.get(model_name, []))

    def get_best_version(self, model_name: str) -> Optional[ModelVersion]:
        versions = self._versions.get(model_name, [])
        if not versions:
            return None
        return max(versions, key=lambda v: v.accuracy)

    # ------------------------------------------------------------------
    # Deployment
    # ------------------------------------------------------------------

    def deploy_version(self, model_name: str, version_id: str) -> dict:
        """Deploy a specific model version to production."""
        versions = self._versions.get(model_name, [])
        target = next((v for v in versions if v.version_id == version_id), None)
        if target is None:
            raise KeyError(f"Version '{version_id}' for model '{model_name}' not found.")

        # Mark previous deployed version as rolled back
        if model_name in self._deployed:
            prev_id = self._deployed[model_name]
            prev = next((v for v in versions if v.version_id == prev_id), None)
            if prev:
                prev.deployed = False

        target.deployed = True
        self._deployed[model_name] = version_id

        return {
            "status": "deployed",
            "model_name": model_name,
            "version_id": version_id,
            "accuracy": target.accuracy,
            "message": (
                f"Version {target.version_number} of '{model_name}' is now live. "
                f"Accuracy: {target.accuracy * 100:.1f}%."
            ),
        }

    def rollback(self, model_name: str, version_id: str) -> dict:
        """Roll back a model to a previous version."""
        result = self.deploy_version(model_name, version_id)
        result["status"] = "rolled_back"
        result["message"] = result["message"].replace("is now live", "has been rolled back to")
        return result

    def get_deployed_version(self, model_name: str) -> Optional[ModelVersion]:
        version_id = self._deployed.get(model_name)
        if version_id is None:
            return None
        versions = self._versions.get(model_name, [])
        return next((v for v in versions if v.version_id == version_id), None)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        return {
            "trainer_id": self.trainer_id,
            "total_datasets": len(self._datasets),
            "total_sessions": len(self._sessions),
            "models_versioned": list(self._versions.keys()),
            "models_deployed": list(self._deployed.keys()),
        }
