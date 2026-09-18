#!/usr/bin/env python3
"""Customer chooses open-source, open-weights, or frontier-hosted. Buddy returns a build plan."""
from __future__ import annotations

TRACKS = {
    "open_source": {
        "publishes_code": True,
        "publishes_weights": False,
        "base": "foundry code + RAG + LoRA recipes",
        "next": ["fork runtime", "attach private RAG", "optional later weights"],
    },
    "open_weights": {
        "publishes_code": False,
        "publishes_weights": True,
        "base": "pinned student checkpoint + model card + hashes",
        "next": ["license review", "QLoRA on owned pack", "signed card"],
    },
    "frontier": {
        "publishes_code": False,
        "publishes_weights": False,
        "base": "xai/grok-best-available + private RAG",
        "next": ["keep Grok as brain", "store only customer index", "student later if eval wins"],
    },
}


def build_plan(track: str, specialty: str = "coding") -> dict:
    if track not in TRACKS:
        raise ValueError(f"track must be one of {sorted(TRACKS)}")
    spec = TRACKS[track]
    return {
        "schema": "dreamco.customer_model_plan.v1",
        "track": track,
        "specialty": specialty,
        "teacher": "xai/grok-best-available",
        "studied_labs": ["deepseek-r1", "olmo", "llama", "gemma", "gpt-oss", "qwen", "mistral", "grok-xai"],
        "publishes_code": spec["publishes_code"],
        "publishes_weights": spec["publishes_weights"],
        "base": spec["base"],
        "next": spec["next"],
        "trained_weights_exist": False,
        "truth": "Plan for a customer model. Buddy studied public methods only. No ultimate-frontier checkpoint is included.",
    }
