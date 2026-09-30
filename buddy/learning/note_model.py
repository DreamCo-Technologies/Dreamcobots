#!/usr/bin/env python3
"""Train a small character model on the own-version notes. It is not a frontier model."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NOTES = ROOT / "buddy/learning/own_versions.jsonl"
WEIGHTS = ROOT / "buddy/learning/note_model.npz"
REPORT = ROOT / "website/data/note-model.json"
CONTEXT = 12
WIDTH = 16


def notes() -> list[str]:
    rows = [json.loads(line) for line in NOTES.open(encoding="utf-8")]
    return [row["own_version"] for row in rows if row.get("copied_a_view") is False and row.get("own_version")]


def train(steps: int = 40, seed: int = 1) -> dict:
    lines = notes()
    text = "\n".join(lines)
    chars = sorted(set(text))
    index = {char: pos for pos, char in enumerate(chars)}
    data = np.array([index[char] for char in text], dtype=np.int32)
    vocab = len(chars)
    rng = np.random.default_rng(seed)
    embed = rng.normal(0, 0.02, (vocab, WIDTH))
    weight = rng.normal(0, 0.02, (CONTEXT * WIDTH, vocab))
    bias = np.zeros(vocab)
    losses = []
    for _ in range(steps):
        batch = 96
        starts = rng.integers(0, len(data) - CONTEXT - 1, size=batch)
        window = np.stack([data[start:start + CONTEXT] for start in starts])
        target = data[starts + CONTEXT]
        flat = embed[window].reshape(batch, -1)
        logits = flat @ weight + bias
        logits = logits - logits.max(axis=1, keepdims=True)
        probs = np.exp(logits)
        probs /= probs.sum(axis=1, keepdims=True)
        losses.append(float(-np.log(probs[np.arange(batch), target] + 1e-9).mean()))
        delta = probs.copy()
        delta[np.arange(batch), target] -= 1
        delta /= batch
        back = delta @ weight.T
        weight = weight - 0.5 * (flat.T @ delta)
        bias = bias - 0.5 * delta.sum(axis=0)
        grad = np.zeros_like(embed)
        np.add.at(grad, window, back.reshape(batch, CONTEXT, WIDTH))
        embed = embed - 0.5 * grad
    return {
        "notes": len(lines),
        "characters": len(text),
        "steps": steps,
        "start_loss": round(losses[0], 4),
        "end_loss": round(losses[-1], 4),
        "loss_dropped": losses[-1] < losses[0],
        "weights_trained": True,
        "frontier_model": False,
        "source": "buddy/learning/own_versions.jsonl",
        "rule": "Trained on the own-version lines only. The source pages were not in the training text. This is not a frontier model.",
        "_arrays": {"embed": embed, "weight": weight, "bias": bias, "chars": np.array(chars)},
    }


def save(report: dict | None = None) -> dict:
    made = report or train(steps=80)
    arrays = made.pop("_arrays")
    np.savez_compressed(WEIGHTS, **arrays)
    public = {key: value for key, value in made.items() if not key.startswith("_")}
    REPORT.write_text(json.dumps(public, indent=2) + "\n", encoding="utf-8")
    return public


def generate(prompt: str, count: int = 40, seed: int = 1) -> str:
    """Continue a prompt with the saved weights. This is a small character model."""
    if not WEIGHTS.is_file():
        raise RuntimeError("buddy/learning/note_model.npz is missing")
    loaded = np.load(WEIGHTS, allow_pickle=False)
    chars = [str(char) for char in loaded["chars"].tolist()]
    index = {char: pos for pos, char in enumerate(chars)}
    embed = loaded["embed"]
    weight = loaded["weight"]
    bias = loaded["bias"]
    rng = np.random.default_rng(seed)
    text = prompt[-CONTEXT:] if prompt else chars[0]
    while len(text) < CONTEXT:
        text = chars[0] + text
    for _ in range(count):
        window = np.array([index.get(char, 0) for char in text[-CONTEXT:]], dtype=np.int32)
        flat = embed[window].reshape(1, -1)
        logits = flat @ weight + bias
        logits = logits - logits.max()
        probs = np.exp(logits[0])
        probs /= probs.sum()
        choice = int(rng.choice(len(chars), p=probs))
        text += chars[choice]
    return text[-count:]


if __name__ == "__main__":
    made = train(steps=30)
    assert made["notes"] == 600
    assert made["loss_dropped"] is True
    assert made["frontier_model"] is False
    assert made["end_loss"] < made["start_loss"]
    public = save(train(steps=80))
    sample = generate("Buddy ", count=12)
    assert sample and public["loss_dropped"] is True
    print(json.dumps({"notes": public["notes"], "start_loss": public["start_loss"], "end_loss": public["end_loss"], "sample_characters": len(sample), "frontier_model": False}))
