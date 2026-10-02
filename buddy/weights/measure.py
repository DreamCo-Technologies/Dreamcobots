#!/usr/bin/env python3
"""Measure statistics of weight files already on disk. Do not download a model."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def measure(path: Path) -> dict:
    loaded = np.load(path, allow_pickle=False)
    tensors = []
    for name in loaded.files:
        values = np.asarray(loaded[name])
        if values.dtype.kind not in "fiu":
            continue
        flat = values.astype(np.float64).reshape(-1)
        if flat.size == 0:
            continue
        tensors.append({
            "name": name,
            "count": int(flat.size),
            "mean": round(float(flat.mean()), 6),
            "std": round(float(flat.std()), 6),
            "min": round(float(flat.min()), 6),
            "max": round(float(flat.max()), 6),
        })
    if not tensors:
        raise RuntimeError(f"No numeric tensors in {path}")
    return {"file": str(path.relative_to(ROOT)), "tensors": len(tensors), "downloaded": False, "rows": tensors}


def study_local() -> dict:
    files = [ROOT / "buddy/learning/note_model.npz"]
    voice = ROOT / "buddy/speech/voice_net.npz"
    if voice.is_file():
        files.append(voice)
    report = {"studied": [measure(path) for path in files], "third_party_download": False}
    out = ROOT / "website/data/weight-stats.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    made = study_local()
    assert made["studied"] and made["third_party_download"] is False
    assert made["studied"][0]["rows"][0]["count"] > 0
    print(json.dumps({"files": len(made["studied"]), "downloaded": False}))
