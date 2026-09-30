"""Local voice cloning.

clone_voice() requires a consent record. There is no parameter that skips it.
The local backend is Coqui XTTS-v2, which is non-commercial. A paid run is refused.
Long jobs are not sent to another company unless the caller passes their own
remote_client. Nothing is downloaded when this file is imported.
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from .consent_gate import require_consent
from .watermark import watermark_audio

logger = logging.getLogger(__name__)
_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
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


def _load_model():
    global _tts_singleton
    if _tts_singleton is None:
        from TTS.api import TTS

        logger.info("loading %s on %s", _MODEL_NAME, _device())
        _tts_singleton = TTS(_MODEL_NAME)
        _tts_singleton.to(_device())
    return _tts_singleton


def clone_voice(
    reference_audio_path: str | Path,
    text: str,
    consent_record_path: str | Path,
    output_path: str | Path,
    language: str = "en",
    paid: bool = False,
    use_remote: bool = False,
    remote_client=None,
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
    if use_remote:
        if remote_client is None:
            raise ValueError("use_remote=True requires a remote_client callable supplied by the caller")
        samples = np.asarray(remote_client(str(reference_audio_path), text, language), dtype=np.float32)
        sample_rate = 24000
    else:
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
