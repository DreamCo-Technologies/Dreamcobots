#!/usr/bin/env python3
"""Buddy's own letter-to-sound network. It is not Chatterbox and it is not a frontier model."""
from __future__ import annotations

from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
WEIGHTS = Path(__file__).with_name("voice_net.npz")
LETTERS = " abcdefghijklmnopqrstuvwxyz"
# Hand-written targets. These are not copied from a speech product.
TARGETS = {
    "a": (800, 1200, 0.12), "e": (400, 2200, 0.10), "i": (300, 2700, 0.10),
    "o": (500, 900, 0.12), "u": (350, 800, 0.11), " ": (0, 0, 0.06),
}


def _target(char: str) -> np.ndarray:
    f1, f2, dur = TARGETS.get(char, (600, 1500, 0.08))
    return np.array([f1 / 3000, f2 / 3000, dur / 0.2], dtype=np.float32)


def train(steps: int = 60, seed: int = 1) -> dict:
    rng = np.random.default_rng(seed)
    width = 8
    weight = rng.normal(0, 0.1, (len(LETTERS), width))
    out = rng.normal(0, 0.1, (width, 3))
    losses = []
    pairs = [(index, _target(char)) for index, char in enumerate(LETTERS)]
    for _ in range(steps):
        total = 0.0
        grad_weight = np.zeros_like(weight)
        grad_out = np.zeros_like(out)
        for index, target in pairs:
            hidden = np.tanh(weight[index])
            pred = hidden @ out
            delta = pred - target
            total += float((delta ** 2).mean())
            grad_out += np.outer(hidden, delta) / 3
            grad_weight[index] += (1 - hidden ** 2) * (out @ delta) / 3
        losses.append(total / len(pairs))
        weight -= 0.2 * grad_weight
        out -= 0.2 * grad_out
    np.savez_compressed(WEIGHTS, weight=weight, out=out, letters=np.array(list(LETTERS)))
    return {
        "letters": len(LETTERS),
        "steps": steps,
        "start_loss": round(losses[0], 4),
        "end_loss": round(losses[-1], 4),
        "loss_dropped": losses[-1] < losses[0],
        "third_party_model": False,
        "weights": str(WEIGHTS.relative_to(ROOT)),
    }


def predict(char: str) -> tuple[float, float, float]:
    if not WEIGHTS.is_file():
        train()
    loaded = np.load(WEIGHTS, allow_pickle=False)
    letters = "".join(str(item) for item in loaded["letters"].tolist())
    index = letters.find(char.lower()) if char.lower() in letters else 0
    hidden = np.tanh(loaded["weight"][index])
    f1, f2, dur = hidden @ loaded["out"]
    return float(max(f1, 0) * 3000), float(max(f2, 0) * 3000), float(max(dur, 0.02) * 0.2)


if __name__ == "__main__":
    made = train()
    assert made["loss_dropped"] is True and made["third_party_model"] is False
    print(made["start_loss"], made["end_loss"])
