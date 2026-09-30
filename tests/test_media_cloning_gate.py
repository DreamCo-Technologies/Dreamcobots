"""Consent and refusal tests. They do not download or run a model."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from capabilities.media_cloning.consent_gate import ConsentError, require_consent, write_consent_record
from capabilities.media_cloning.image_clone import _refuse_prompt
from capabilities.media_cloning.watermark import watermark_audio
import numpy as np


class MediaCloningGateTest(unittest.TestCase):
    def test_missing_consent_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            reference = Path(folder) / "clip.wav"
            reference.write_bytes(b"not-a-real-wav")
            with self.assertRaises(ConsentError):
                require_consent(reference, "voice_clone", Path(folder) / "missing.json")

    def test_hash_and_adult_check(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            reference = Path(folder) / "clip.wav"
            reference.write_bytes(b"reference-bytes")
            record = write_consent_record("Ada", reference, "Ada", "voice_clone", Path(folder) / "ok.json", adult_confirmed=True)
            loaded = require_consent(reference, "voice_clone", record)
            self.assertTrue(loaded.adult_confirmed)
            reference.write_bytes(b"different-bytes")
            with self.assertRaises(ConsentError):
                require_consent(reference, "voice_clone", record)

    def test_minor_record_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            reference = Path(folder) / "clip.wav"
            reference.write_bytes(b"reference-bytes")
            with self.assertRaises(ConsentError):
                write_consent_record("Kid", reference, "parent", "voice_clone", Path(folder) / "no.json", adult_confirmed=False)

    def test_blocked_image_prompt(self) -> None:
        with self.assertRaises(ValueError):
            _refuse_prompt("a sexual portrait")

    def test_unwatermarked_audio_is_not_returned(self) -> None:
        try:
            import audioseal  # noqa: F401
        except ImportError:
            with self.assertRaises(RuntimeError):
                watermark_audio(np.zeros(8, dtype=np.float32), 24000)
            return
        self.skipTest("audioseal is installed; the missing-watermark stop was not the case under test")

    def test_expired_record_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            reference = Path(folder) / "clip.wav"
            reference.write_bytes(b"reference-bytes")
            path = write_consent_record(
                "Ada", reference, "Ada", "image_clone", Path(folder) / "old.json",
                adult_confirmed=True, expires_in_seconds=-1,
            )
            body = json.loads(path.read_text(encoding="utf-8"))
            self.assertLess(body["expires_at"], body["signed_at"])
            with self.assertRaises(ConsentError):
                require_consent(reference, "image_clone", path)


if __name__ == "__main__":
    unittest.main()
