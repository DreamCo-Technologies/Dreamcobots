#!/usr/bin/env python3
"""Deterministic expert + route balancer for the US weight system.

This is a control-plane simulator: capacity, load CV, overflow, and
quality-aware route mix. It does not load frontier checkpoints.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class ExpertSpec:
    expert_id: str
    capacity: float
    specialty: str


@dataclass(frozen=True)
class RouteSpec:
    route_id: str
    quality: float
    cost: float
    us_controlled: bool


def softmax(xs: list[float]) -> list[float]:
    peak = max(xs)
    exps = [math.exp(x - peak) for x in xs]
    total = sum(exps) or 1.0
    return [x / total for x in exps]


def assign_tokens(affinities: list[list[float]], top_k: int, capacity_factor: float) -> dict:
    n_tokens = len(affinities)
    n_experts = len(affinities[0]) if affinities else 0
    cap = max(1, int(math.ceil(capacity_factor * n_tokens * top_k / max(n_experts, 1))))
    load = [0] * n_experts
    overflow = 0
    chosen: list[list[int]] = []
    for row in affinities:
        ranked = sorted(range(n_experts), key=lambda i: row[i], reverse=True)
        picked = []
        for idx in ranked:
            if len(picked) >= top_k:
                break
            if load[idx] < cap:
                load[idx] += 1
                picked.append(idx)
            else:
                overflow += 1
        chosen.append(picked)
    mean = (sum(load) / n_experts) if n_experts else 0.0
    var = sum((x - mean) ** 2 for x in load) / n_experts if n_experts else 0.0
    cv = math.sqrt(var) / mean if mean else 0.0
    return {
        "tokens": n_tokens,
        "experts": n_experts,
        "top_k": top_k,
        "capacity_per_expert": cap,
        "load": load,
        "overflow": overflow,
        "load_cv": cv,
        "balanced": cv <= 0.35 and overflow <= max(1, n_tokens // 20),
        "assignments": chosen,
    }


def mix_routes(routes: list[RouteSpec], quality_floor: float) -> dict:
    eligible = [r for r in routes if r.quality >= quality_floor]
    if not eligible:
        eligible = routes[:]
    scores = [r.quality / max(r.cost, 1e-6) for r in eligible]
    weights = softmax(scores)
    return {
        "quality_floor": quality_floor,
        "mix": [
            {
                "route_id": r.route_id,
                "weight": w,
                "quality": r.quality,
                "cost": r.cost,
                "us_controlled": r.us_controlled,
            }
            for r, w in zip(eligible, weights)
        ],
        "us_share": sum(w for r, w in zip(eligible, weights) if r.us_controlled),
    }


def simulate(seed: int = 7, n_tokens: int = 256, n_experts: int = 32, top_k: int = 2) -> dict:
    rng = random.Random(seed)
    affinities = [[rng.random() + (0.15 if i % 4 == t % 4 else 0.0) for i in range(n_experts)] for t in range(n_tokens)]
    experts = [ExpertSpec(f"E{i:02d}", 1.0, ["code", "reason", "tools", "safety"][i % 4]) for i in range(n_experts)]
    balance = assign_tokens(affinities, top_k=top_k, capacity_factor=1.25)
    routes = [
        RouteSpec("xai/grok-best-available", quality=0.96, cost=1.0, us_controlled=True),
        RouteSpec("dream-work-student", quality=0.72, cost=0.12, us_controlled=True),
        RouteSpec("dream-work+rag", quality=0.78, cost=0.18, us_controlled=True),
        RouteSpec("open-weight-shortlist", quality=0.70, cost=0.20, us_controlled=False),
    ]
    mix = mix_routes(routes, quality_floor=0.7)
    return {
        "schema": "dreamco.weight_balance_sim.v1",
        "experts": [expert.expert_id for expert in experts],
        "balance": {k: v for k, v in balance.items() if k != "assignments"},
        "route_mix": mix,
        "rivalry_claim": False,
        "truth": "Balancer math only. Not a trained frontier weight dump and not a China-rivalry score.",
    }
