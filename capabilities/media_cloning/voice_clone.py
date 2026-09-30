"""Local voice cloning for personal, business, and social use.

clone_voice() requires an adult consent record. There is no remote call.
The commercial backend is Chatterbox, which is MIT licensed. XTTS-v2 is not
used, because its license is non-commercial. Weights are used only from a
folder already on this machine.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

import numpy as np

from .consent_gate import require_consent
from .watermark import watermark_audio

logger = logging.getLogger(__name__)
USES = {"personal", "business", "social"}
_model = None


def _device() -> str:
    try:
        import torch
    except ImportError:
        return "cpu"
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _local_chatterbox() -> Path:
    folder = Path(os.environ.get("DREAMCO_CHATTERBOX_DIR", ""))
    weights = list(folder.glob("*.safetensors")) + list(folder.glob("*.pt"))
    if not weights:
        raise RuntimeError(
            "Local Chatterbox weights are not on this machine. Set DREAMCO_CHATTERBOX_DIR "
            "to a folder that already contains the MIT-licensed weight files. This package "
            "will not download weights and will not send the clip anywhere."
        )
    return folder


def _load_model():
    global _model
    folder = _local_chatterbox()
    if _model is None:
        from chatterbox.tts import ChatterboxTTS

        loader = getattr(ChatterboxTTS, "from_local", None)
        if loader is None:
            raise RuntimeError("This Chatterbox install cannot load a local folder. This package will not download weights.")
        logger.info("loading local Chatterbox on %s", _device())
        _model = loader(str(folder), _device())
    return _model


def clone_voice(
    reference_audio_path: str | Path,
    text: str,
    consent_record_path: str | Path,
    output_path: str | Path,
    language: str = "en",
    use: str = "personal",
) -> Path:
    """Clone the reference voice for personal, business, or social use."""
    if use not in USES:
        raise ValueError("use must be personal, business, or social")
    if not str(text).strip():
        raise ValueError("text is required")
    reference_audio_path = Path(reference_audio_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    record = require_consent(reference_audio_path, "voice_clone", consent_record_path)
    logger.info("consent verified for '%s' (%s)", record.subject_name, use)
    model = _load_model()
    wav = model.generate(text, audio_prompt_path=str(reference_audio_path))
    samples = np.asarray(getattr(wav, "cpu", lambda: wav)().numpy() if hasattr(wav, "cpu") else wav, dtype=np.float32).reshape(-1)
    sample_rate = int(getattr(model, "sr", 24000))
    samples = watermark_audio(samples, sample_rate)
    import soundfile as sf

    sf.write(str(output_path), samples, sample_rate)
    return output_path