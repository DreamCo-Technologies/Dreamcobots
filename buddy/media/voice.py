"""Voice cloning. Backends are pluggable; Chatterbox is the default (MIT, works on Apple GPU via MPS)."""
from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import List, Protocol, Tuple

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly


class VoiceBackend(Protocol):
    name: str
    model: str

    def load(self) -> None: ...
    def unload(self) -> None: ...
    def synthesize(self, text: str, reference_path: str, **kw) -> Tuple[np.ndarray, int]: ...


def pick_device() -> str:
    try:
        import torch

        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
    return "cpu"


def prepare_reference(path, out_dir=None, sr: int = 24000, max_seconds: float = 15.0) -> Path:
    """Mono, resampled, silence-trimmed, peak-normalised, capped clip of the reference voice."""
    y, in_sr = sf.read(str(path), dtype="float32", always_2d=True)
    y = y.mean(axis=1)
    if in_sr != sr:
        from math import gcd

        g = gcd(int(in_sr), sr)
        y = resample_poly(y, sr // g, int(in_sr) // g).astype(np.float32)
    peak = float(np.abs(y).max()) if len(y) else 0.0
    if peak <= 0:
        raise ValueError("Reference audio is silent.")
    loud = np.where(np.abs(y) > peak * 10 ** (-35 / 20))[0]
    y = y[loud[0] : loud[-1] + 1]
    if len(y) / sr < 3.0:
        raise ValueError("Reference needs at least 3 seconds of clean speech (10-15 s is ideal).")
    y = y[: int(sr * max_seconds)]
    y = y / float(np.abs(y).max()) * 0.95
    out_dir = Path(out_dir or tempfile.mkdtemp(prefix="buddy_ref_"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "ref_prepared.wav"
    sf.write(str(out), y, sr)
    return out


def split_text(text: str, max_chars: int = 250) -> List[str]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    chunks, cur = [], ""
    for s in sentences:
        if cur and len(cur) + len(s) + 1 > max_chars:
            chunks.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        chunks.append(cur)
    return chunks or [text.strip()]


def synthesize_long(backend: VoiceBackend, text: str, reference_path, gap_seconds: float = 0.25, **kw):
    parts, sr = [], None
    for chunk in split_text(text):
        wav, sr = backend.synthesize(chunk, str(reference_path), **kw)
        parts.append(np.asarray(wav, dtype=np.float32).reshape(-1))
        parts.append(np.zeros(int(sr * gap_seconds), dtype=np.float32))
    return np.concatenate(parts[:-1]) if parts else np.zeros(0, np.float32), sr


class ChatterboxBackend:
    name = "chatterbox"
    model = "ResembleAI/chatterbox"

    def __init__(self, device: str | None = None):
        self.device = device or pick_device()
        self._m = None

    def load(self) -> None:
        import torch
        from chatterbox.tts import ChatterboxTTS

        if self.device == "mps":
            # Chatterbox checkpoints are saved for CUDA; remap to the Apple GPU when loading.
            orig = torch.load
            torch.load = lambda *a, **k: orig(*a, **{**k, "map_location": torch.device("mps")})
            try:
                self._m = ChatterboxTTS.from_pretrained(device="mps")
            finally:
                torch.load = orig
        else:
            self._m = ChatterboxTTS.from_pretrained(device=self.device)

    def unload(self) -> None:
        self._m = None

    def synthesize(self, text, reference_path, exaggeration: float = 0.5, cfg_weight: float = 0.5, **_):
        wav = self._m.generate(
            text, audio_prompt_path=str(reference_path), exaggeration=exaggeration, cfg_weight=cfg_weight
        )
        return wav.squeeze().detach().cpu().numpy(), int(self._m.sr)
