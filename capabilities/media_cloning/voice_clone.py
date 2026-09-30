"""Local voice cloning.

clone_voice() requires a consent record. There is no parameter that skips it,
and there is no remote call. The local backend is Coqui XTTS-v2, which is
non-commercial. A paid run is refused. Weights are used only from a folder
already on this machine. Nothing is downloaded when this file is imported
or when the weights are missing.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

import numpy as np

from .consent_gate import require_consent
from .watermark import watermark_audio

logger = logging.getLogger(__name__)
_tts_singleton = None


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


def _local_xtts() -> tuple[Path, Path]:
    folder = Path(os.environ.get("DREAMCO_XTTS_DIR", ""))
    model = folder / "model.pth"
    config = folder / "config.json"
    if not model.is_file() or not config.is_file():
        raise RuntimeError(
            "Local XTTS weights are not on this machine. Set DREAMCO_XTTS_DIR to a folder "
            "that already contains model.pth and config.json. This package will not download "
            "weights and will not send the clip anywhere."
        )
    return model, config


def _load_model():
    global _tts_singleton
    model, config = _local_xtts()
    if _tts_singleton is None:
        from TTS.api import TTS

        logger.info("loading local XTTS on %s", _device())
        _tts_singleton = TTS(model_path=str(model), config_path=str(config))
        _tts_singleton.to(_device())
    return _tts_singleton


def clone_voice(
    reference_audio_path: str | Path,
    text: str,
    consent_record_path: str | Path,
    output_path: str | Path,
    language: str = "en",
    paid: bool = False,
) -> Path:
    """Clone the reference voice saying `text`, then watermark the wav."""
    if paid:
        raise RuntimeError("XTTS-v2 is non-commercial. This package will not run a paid clone.")
    if not str(text).strip():
        raise ValueError("text is required")
    reference_audio_path = Path(reference_audio_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    record = require_consent(reference_audio_path, "voice_clone", consent_record_path)
    logger.info("consent verified for '%s'", record.subject_name)
    _local_xtts()
    tts = _load_model()
    samples = np.asarray(
        tts.tts(text=text, speaker_wav=str(reference_audio_path), language=language),
        dtype=np.float32,
    )
    sample_rate = getattr(tts.synthesizer, "output_sample_rate", 24000)
    samples = watermark_audio(samples, sample_rate)
    import soundfile as sf

    sf.write(str(output_path), samples, sample_rate)
    return output_path