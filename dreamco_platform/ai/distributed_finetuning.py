"""Distributed model fine-tuning coordinator."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence
import statistics
import uuid


@dataclass
class FineTuningJob:
    base_model: str
    dataset: Sequence[float]
    hyperparams: Dict[str, float]
    workers: int


@dataclass
class JobHandle:
    job_id: str
    status: str
    worker_losses: Dict[int, List[float]] = field(default_factory=dict)
    aggregated_gradient: float = 0.0
    best_loss: float = float("inf")
    stopped_early: bool = False
    history: List[float] = field(default_factory=list)


class DistributedFinetuner:
    def _split_dataset(self, dataset: Sequence[float], workers: int) -> List[List[float]]:
        shards = [[] for _ in range(max(1, workers))]
        for index, item in enumerate(dataset):
            shards[index % len(shards)].append(float(item))
        return shards

    def _worker_step(self, shard: Sequence[float], epoch: int, lr: float) -> tuple[float, float]:
        mean_value = statistics.fmean(shard) if shard else 0.0
        gradient = (mean_value / (epoch + 1)) * lr
        loss = abs(mean_value - gradient) / (epoch + 1 or 1)
        return gradient, loss

    def _aggregate_gradients(self, gradients: Sequence[float]) -> float:
        return sum(gradients) / max(1, len(gradients))

    def submit(self, job: FineTuningJob) -> JobHandle:
        lr = float(job.hyperparams.get("learning_rate", 0.01))
        epochs = int(job.hyperparams.get("epochs", 5))
        patience = int(job.hyperparams.get("early_stopping_patience", 2))
        shards = self._split_dataset(job.dataset, job.workers)
        handle = JobHandle(job_id=str(uuid.uuid4()), status="running")
        no_improve = 0
        for epoch in range(epochs):
            gradients: List[float] = []
            losses: List[float] = []
            for worker_id, shard in enumerate(shards):
                gradient, loss = self._worker_step(shard, epoch, lr)
                handle.worker_losses.setdefault(worker_id, []).append(loss)
                gradients.append(gradient)
                losses.append(loss)
            handle.aggregated_gradient = self._aggregate_gradients(gradients)
            mean_loss = sum(losses) / max(1, len(losses))
            handle.history.append(mean_loss)
            if mean_loss < handle.best_loss:
                handle.best_loss = mean_loss
                no_improve = 0
            else:
                no_improve += 1
            if no_improve >= patience:
                handle.stopped_early = True
                handle.status = "completed"
                break
        if handle.status != "completed":
            handle.status = "completed"
        return handle
