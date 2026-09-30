"""Local voice for personal, business, and social use.

clone_voice() requires an adult consent record. Speech is Buddy's own
letter-to-sound network. It does not call Chatterbox or any other service,
and it does not download weights.
"""
from __future__ import annotations

import logging
from pathlib import Path

from buddy.speech.speak import speak

from .consent_gate import require_consent
from .watermark import watermark_audio

logger = logging.getLogger(__name__)
USES = {"personal", "business", "social"}


def clone_voice(
    reference_audio_path: str | Path,
    text: str,
    consent_record_path: str | Path,
    output_path: str | Path,
    language: str = "en",
    use: str = "personal",
) -> Path:
    """Speak `text` in a tone measured from the reference, then watermark the wav."""
    if use not in USES:
        raise ValueError("use must be personal, business, or social")
    if not str(text).strip():
        raise ValueError("text is required")
    reference_audio_path = Path(reference_audio_path)
    output_path = Path(output_path)
    record = require_consent(reference_audio_path, "voice_clone", consent_record_path)
    logger.info("consent verified for '%s' (%s, %s)", record.subject_name, use, language)
    samples, sample_rate = speak(text, reference_audio_path, output_path)
    samples = watermark_audio(samples, sample_rate)
    import wave

    with wave.open(str(output_path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        import numpy as np

        handle.writeframes((np.clip(samples, -1, 1) * 32767).astype(np.int16).tobytes())
    return output_path