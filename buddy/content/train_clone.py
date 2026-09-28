#!/usr/bin/env python3
"""See if this machine can train a voice or image clone. Do not download a model."""
from __future__ import annotations

import json
import platform
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
    system = platform.system()
    on_mac = system == "Darwin"
    nvidia = shutil.which("nvidia-smi") is not None
    reasons = []
    if not audio:
        reasons.append("Put recordings you are allowed to use in buddy/content/samples.")
    if not images:
        reasons.append("Put photos you are allowed to use in buddy/content/samples.")
    if not allowed:
        reasons.append("Add buddy/content/samples/consent.txt with the owner's name and the word allow. Do not include a child.")
    if not on_mac:
        reasons.append("This command is running on Linux, not on the MacBook Neo. An NVIDIA card is the wrong test for that laptop.")
    else:
        reasons.append("A Mac GPU uses Metal, not NVIDIA. An A18 with 8GB of memory is not enough to train a voice or image clone.")
    reasons.append("No cloning model is downloaded.")
    return {
        "trained": False,
        "downloaded_model": False,
        "running_on": system,
        "is_macbook_neo": False,
        "nvidia": nvidia,
        "gpu": nvidia or on_mac,
        "audio": len(audio),
        "images": len(images),
        "consent": allowed,
        "reasons": reasons,
    }


if __name__ == "__main__":
    made = ready()
    assert made["trained"] is False and made["downloaded_model"] is False and made["is_macbook_neo"] is False
    print(json.dumps({"trained": False, "running_on": made["running_on"], "is_macbook_neo": False, "audio": made["audio"]}))
