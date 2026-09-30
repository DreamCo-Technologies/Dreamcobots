#!/usr/bin/env python3
"""Speak with Buddy's own network. No Chatterbox, no download, no remote call."""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

from buddy.speech.voice_net import predict


def reference_pitch(path: Path) -> float:
    """Measure a rough pitch from a local wav. Any other file keeps the default."""
    try:
        with wave.open(str(path), "rb") as handle:
            rate = handle.getframerate()
            frames = np.frombuffer(handle.readframes(handle.getnframes()), dtype=np.int16).astype(np.float32)
    except (wave.Error, EOFError, OSError):
        return 140.0
    if frames.size < rate // 20:
        return 140.0
    frame = frames[: rate // 20]
    frame = frame - frame.mean()
    corr = np.correlate(frame, frame, mode="full")[frame.size - 1:]
    low, high = int(rate / 350), int(rate / 70)
    if high >= corr.size:
        return 140.0
    lag = low + int(np.argmax(corr[low:high]))
    return float(rate / lag) if lag else 140.0


def speak(text: str, reference: Path, output: Path) -> tuple[np.ndarray, int]:
    rate = 16000
    pitch = reference_pitch(reference)
    pieces = []
    for char in text.lower():
        if char not in " abcdefghijklmnopqrstuvwxyz":
            continue
        first, second, duration = predict(char)
        count = max(int(rate * duration), 1)
        time = np.arange(count) / rate
        tone = 0.25 * np.sin(2 * np.pi * pitch * time)
        if first > 0:
            tone += 0.12 * np.sin(2 * np.pi * first * time)
        if second > 0:
            tone += 0.08 * np.sin(2 * np.pi * second * time)
        tone *= np.hanning(count)
        pieces.append(tone.astype(np.float32))
    samples = np.concatenate(pieces) if pieces else np.zeros(rate // 5, dtype=np.float32)
    output.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(samples, -1, 1)
    with wave.open(str(output), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes((pcm * 32767).astype(np.int16).tobytes())
    return samples, rate
