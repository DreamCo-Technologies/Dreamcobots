#!/usr/bin/env python3
"""See if this machine can train a voice or image clone. Do not download a model."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "buddy" / "content" / "samples"
AUDIO = {".wav", ".mp3", ".flac", ".m4a"}
IMAGES = {".png", ".jpg", ".jpeg", ".webp"}


def ready() -> dict:
    files = [path for path in SAMPLES.rglob("*") if path.is_file()] if SAMPLES.exists() else []
    audio = [path.name for path in files if path.suffix.lower() in AUDIO]
    images = [path.name for path in files if path.suffix.lower() in IMAGES]
    consent = SAMPLES / "consent.txt"
    words = consent.read_text(encoding="utf-8") if consent.exists() else ""
    allowed = "allow" in words.lower() and "child" not in words.lower() and "minor" not in words.lower()
    gpu = shutil.which("nvidia-smi") is not None
    reasons = []
    if not audio:
        reasons.append("Put recordings you are allowed to use in buddy/content/samples.")
    if not images:
        reasons.append("Put photos you are allowed to use in buddy/content/samples.")
    if not allowed:
        reasons.append("Add buddy/content/samples/consent.txt with the owner's name and the word allow. Do not include a child.")
    if not gpu:
        reasons.append("This machine has no NVIDIA GPU. A clone is not trained on these 2 CPUs.")
    reasons.append("No cloning model is downloaded.")
    return {
        "trained": False,
        "downloaded_model": False,
        "gpu": gpu,
        "audio": len(audio),
        "images": len(images),
        "consent": allowed,
        "reasons": reasons,
    }


if __name__ == "__main__":
    made = ready()
    assert made["trained"] is False and made["downloaded_model"] is False
    print(json.dumps({"trained": False, "audio": made["audio"], "images": made["images"], "gpu": made["gpu"]}))
