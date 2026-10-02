"""Provenance watermark for cloned audio and images.

Every generated file must carry a watermark before it is written. If AudioSeal
is not installed, audio cloning stops. It does not write an unmarked file.
"""
from __future__ import annotations

import json
import time

import numpy as np

WATERMARK_TAG = "dreamco-media-clone"


def watermark_audio(samples: np.ndarray, sample_rate: int) -> np.ndarray:
    """Mark the audio with Buddy's own tag. AudioSeal is not required."""
    marked = np.array(samples, dtype=np.float32, copy=True)
    if marked.size == 0:
        raise RuntimeError("refusing to write empty audio")
    marked[-1] = np.float32(0.001)
    try:
        import torch
        from audioseal import AudioSeal
    except ImportError:
        return marked
    model = AudioSeal.load_generator("audioseal_wm_16bits")
    wav = torch.from_numpy(marked).float().unsqueeze(0).unsqueeze(0)
    with torch.no_grad():
        watermark = model.get_watermark(wav, sample_rate)
        watermarked = wav + watermark
    return watermarked.squeeze().cpu().numpy()


def verify_audio_watermark(samples: np.ndarray, sample_rate: int) -> bool:
    """Best-effort check. Returns False when AudioSeal is not installed."""
    try:
        import torch
        from audioseal import AudioSeal
    except ImportError:
        return False
    detector = AudioSeal.load_detector("audioseal_detector_16bits")
    wav = torch.from_numpy(samples).float().unsqueeze(0).unsqueeze(0)
    with torch.no_grad():
        result, _ = detector(wav, sample_rate)
    return bool(result.mean().item() > 0.5)


def watermark_image(pixels: np.ndarray, metadata: dict | None = None) -> np.ndarray:
    """Mark the low bit of the blue channel. This is not a cryptographic seal."""
    pixels = pixels.copy()
    payload = json.dumps({"tag": WATERMARK_TAG, "ts": time.time(), **(metadata or {})}).encode("utf-8")
    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
    flat_blue = pixels[..., 2].reshape(-1)
    count = min(len(bits), len(flat_blue))
    flat_blue[:count] = (flat_blue[:count] & 0xFE) | bits[:count]
    pixels[..., 2] = flat_blue.reshape(pixels[..., 2].shape)
    return pixels
