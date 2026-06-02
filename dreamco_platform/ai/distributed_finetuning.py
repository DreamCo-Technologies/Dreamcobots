"""Utilities for planning distributed fine-tuning workloads."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List
import math


@dataclass
class TrainingShard:
    node_id: str
    samples: int
    compute_score: float
    network_cost: float
    assigned_batches: int = 0


@dataclass
class FinetuningPlan:
    learning_rate: float
    global_batch_size: int
    accumulation_steps: int
    shards: List[TrainingShard] = field(default_factory=list)

    @property
    def total_batches(self) -> int:
        return sum(shard.assigned_batches for shard in self.shards)


class DistributedFinetuner:
    def choose_learning_rate(self, parameter_count: int, dataset_size: int) -> float:
        scale = min(4.0, math.log10(max(parameter_count, 10)) / 2)
        data_factor = max(0.3, min(2.0, dataset_size / 100_000))
        rate = 2e-5 / scale * math.sqrt(data_factor)
        return round(max(1e-6, min(5e-4, rate)), 7)

    def build_plan(self, nodes: Iterable[Dict[str, float]], dataset_size: int, micro_batch: int = 8) -> FinetuningPlan:
        shards = [
            TrainingShard(
                node_id=str(node["node_id"]),
                samples=int(node["samples"]),
                compute_score=float(node.get("compute_score", 1.0)),
                network_cost=float(node.get("network_cost", 0.1)),
            )
            for node in nodes
        ]
        if not shards:
            return FinetuningPlan(learning_rate=0.0, global_batch_size=0, accumulation_steps=0, shards=[])
        total_compute = sum(max(0.1, s.compute_score - s.network_cost) for s in shards)
        total_batches = max(1, math.ceil(dataset_size / max(1, micro_batch)))
        for shard in shards:
            weight = max(0.1, shard.compute_score - shard.network_cost) / total_compute
            shard.assigned_batches = max(1, round(total_batches * weight))
        global_batch_size = micro_batch * len(shards)
        accumulation_steps = max(1, math.ceil(dataset_size / max(global_batch_size * 100, 1)))
        lr = self.choose_learning_rate(parameter_count=7_000_000_000, dataset_size=dataset_size)
        return FinetuningPlan(lr, global_batch_size, accumulation_steps, shards)

    def rebalance(self, plan: FinetuningPlan, failed_nodes: Iterable[str]) -> FinetuningPlan:
        failed = set(failed_nodes)
        survivors = [shard for shard in plan.shards if shard.node_id not in failed]
        failed_batches = sum(shard.assigned_batches for shard in plan.shards if shard.node_id in failed)
        if not survivors:
            return FinetuningPlan(plan.learning_rate, plan.global_batch_size, plan.accumulation_steps, [])
        total_capacity = sum(max(0.1, s.compute_score - s.network_cost) for s in survivors)
        for shard in survivors:
            extra = failed_batches * max(0.1, shard.compute_score - shard.network_cost) / total_capacity
            shard.assigned_batches += round(extra)
        return FinetuningPlan(plan.learning_rate, plan.global_batch_size, plan.accumulation_steps, survivors)

    def estimate_epoch_time(self, plan: FinetuningPlan, seconds_per_batch: float = 0.8) -> float:
        if not plan.shards:
            return 0.0
        node_times = [
            shard.assigned_batches * seconds_per_batch / max(shard.compute_score, 0.1) * (1 + shard.network_cost)
            for shard in plan.shards
        ]
        return round(max(node_times), 2)


def summarize_plan(plan: FinetuningPlan) -> Dict[str, object]:
    return {
        "learning_rate": plan.learning_rate,
        "global_batch_size": plan.global_batch_size,
        "accumulation_steps": plan.accumulation_steps,
        "total_batches": plan.total_batches,
        "nodes": [
            {
                "node_id": shard.node_id,
                "assigned_batches": shard.assigned_batches,
                "samples": shard.samples,
            }
            for shard in plan.shards
        ],
    }
