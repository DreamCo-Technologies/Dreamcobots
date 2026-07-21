# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""Modular evolution engine for tracking AI model lifecycle stages."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid


class EvolutionStage(Enum):
    INIT = "init"
    TRAINING = "training"
    TESTING = "testing"
    OPTIMIZING = "optimizing"
    DEPLOYED = "deployed"
    RETIRED = "retired"


_STAGE_ORDER = [
    EvolutionStage.INIT,
    EvolutionStage.TRAINING,
    EvolutionStage.TESTING,
    EvolutionStage.OPTIMIZING,
    EvolutionStage.DEPLOYED,
    EvolutionStage.RETIRED,
]


@dataclass
class ModelEvolution:
    model_id: str
    name: str
    stage: EvolutionStage = EvolutionStage.INIT
    version: str = "0.1.0"
    performance_score: float = 0.0
    iterations: int = 0


class EvolutionEngine:
    """Manages the full lifecycle of AI models from init to retirement."""

    def __init__(self):
        self._models: dict[str, ModelEvolution] = {}

    def register_model(self, model_id: str, name: str) -> ModelEvolution:
        if model_id in self._models:
            raise ValueError(f"Model '{model_id}' is already registered.")
        model = ModelEvolution(model_id=model_id, name=name)
        self._models[model_id] = model
        return model

    def advance_stage(self, model_id: str) -> ModelEvolution:
        model = self.get_model(model_id)
        current_index = _STAGE_ORDER.index(model.stage)
        if current_index >= len(_STAGE_ORDER) - 1:
            raise ValueError(f"Model '{model_id}' is already at final stage '{model.stage.value}'.")
        model.stage = _STAGE_ORDER[current_index + 1]
        model.iterations += 1
        # Bump minor version on each advance
        parts = model.version.split(".")
        parts[1] = str(int(parts[1]) + 1)
        model.version = ".".join(parts)
        return model

    def update_performance(self, model_id: str, score: float) -> None:
        if not (0.0 <= score <= 100.0):
            raise ValueError("Performance score must be between 0 and 100.")
        model = self.get_model(model_id)
        model.performance_score = score

    def get_model(self, model_id: str) -> ModelEvolution:
        if model_id not in self._models:
            raise KeyError(f"Model '{model_id}' not found.")
        return self._models[model_id]

    def list_models(self, stage: Optional[EvolutionStage] = None) -> list[ModelEvolution]:
        models = list(self._models.values())
        if stage is not None:
            models = [m for m in models if m.stage == stage]
        return models

    def get_evolution_report(self) -> dict:
        models = list(self._models.values())
        stage_counts: dict[str, int] = {s.value: 0 for s in EvolutionStage}
        for m in models:
            stage_counts[m.stage.value] += 1

        avg_perf = (
            sum(m.performance_score for m in models) / len(models) if models else 0.0
        )
        top_model = max(models, key=lambda m: m.performance_score) if models else None

        return {
            "total_models": len(models),
            "stage_distribution": stage_counts,
            "avg_performance_score": round(avg_perf, 2),
            "top_model": {
                "model_id": top_model.model_id,
                "name": top_model.name,
                "performance_score": top_model.performance_score,
                "stage": top_model.stage.value,
            } if top_model else None,
        }
