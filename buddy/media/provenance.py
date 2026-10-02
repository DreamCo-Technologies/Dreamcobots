"""Provenance: keyed watermarks + sidecar manifests + an append-only ledger.

Honest limits: the watermark is a basic keyed spread-spectrum mark. It survives lossless saves and mild
edits, but re-encoding (MP3/JPEG), resampling, or cropping can destroy it. It is a provenance aid,
not tamper-proof security. The sidecar manifest + ledger carry the durable record.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Tuple

import numpy as np

from .consent import sha256_file


def key_id(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()[:8]


def _sequence(key: str, n: int) -> np.ndarray:
    seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], "big")
    return np.random.RandomState(seed).choice([-1.0, 1.0], size=n)


def _z_score(x: np.ndarray, seq: np.ndarray) -> float:
    xc = x - x.mean()
    denom = xc.std() * np.sqrt(len(xc))
    return float(np.dot(xc, seq) / denom) if denom > 0 else 0.0


# ---- audio (float mono in [-1, 1]) ----
def watermark_audio(x: np.ndarray, key: str, rel_strength: float = 0.02, floor: float = 0.002) -> np.ndarray:
    """Mark ~-34 dB below the signal RMS. Reliable detection needs roughly >= 4 s of audio."""
    x = np.asarray(x, dtype=np.float32).reshape(-1)
    rms = float(np.sqrt(np.mean(x**2))) if len(x) else 0.0
    strength = max(floor, rel_strength * rms)
    return np.clip(x + strength * _sequence(key, len(x)), -1.0, 1.0).astype(np.float32)


def detect_audio_watermark(x: np.ndarray, key: str, threshold: float = 5.0) -> Tuple[bool, float]:
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    z = _z_score(x, _sequence(key, len(x)))
    return z > threshold, z


# ---- image (uint8 HxWxC) ----
def watermark_image(arr: np.ndarray, key: str, strength: int = 2) -> np.ndarray:
    seq = _sequence(key, arr.size).reshape(arr.shape)
    return np.clip(arr.astype(np.int16) + strength * seq.astype(np.int16), 0, 255).astype(np.uint8)


def detect_image_watermark(arr: np.ndarray, key: str, threshold: float = 5.0) -> Tuple[bool, float]:
    x = arr.astype(np.float64).reshape(-1)
    z = _z_score(x, _sequence(key, x.size))
    return z > threshold, z


# ---- manifests + ledger ----
def manifest_path(output: Path) -> Path:
    return Path(str(output) + ".provenance.json")


def write_manifest(output: Path, info: dict) -> dict:
    manifest = dict(info)
    manifest["output_file"] = output.name
    manifest["output_sha256"] = sha256_file(output)
    manifest["created_at"] = manifest.get("created_at", time.time())
    manifest["ai_generated"] = True
    manifest_path(output).write_text(json.dumps(manifest, indent=2))
    return manifest


def append_ledger(ledger: Path, entry: dict) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger, "a") as f:
        f.write(json.dumps(entry) + "\n")
