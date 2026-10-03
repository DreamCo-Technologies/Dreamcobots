"""Consent gate for media cloning: five refusal/accept cases, lazy imports, schema shape.

No model is downloaded or run. Only the consent gate and capability JSON files are exercised.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from capabilities.media_cloning.consent_gate import ConsentError, require_consent, write_consent_record

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "capabilities" / "capability_package.schema.json"
CAPABILITY_FILES = [
    ROOT / "capabilities" / "voice_clone.capability.json",
    ROOT / "capabilities" / "image_clone.capability.json",
    ROOT / "capabilities" / "media_cloning" / "voice_clone.capability.json",
    ROOT / "capabilities" / "media_cloning" / "image_clone.capability.json",
]
HEAVY_MODULES = ("torch", "torchaudio", "TTS", "diffusers", "transformers", "audioseal", "chatterbox", "librosa")


class ConsentGateCases(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self._tmp.name)
        self.reference = self.folder / "clip.wav"
        self.reference.write_bytes(b"reference-bytes")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _record(self, scope: str = "voice_clone", **kwargs) -> Path:
        return write_consent_record(
            "Ada", self.reference, "Ada", scope, self.folder / "consent.json", adult_confirmed=True, **kwargs
        )

    def test_missing_record_is_refused(self) -> None:
        with self.assertRaisesRegex(ConsentError, "no consent record"):
            require_consent(self.reference, "voice_clone", self.folder / "missing.json")

    def test_hash_mismatch_is_refused(self) -> None:
        record = self._record()
        self.reference.write_bytes(b"swapped-reference-bytes")
        with self.assertRaisesRegex(ConsentError, "does not match"):
            require_consent(self.reference, "voice_clone", record)

    def test_wrong_scope_is_refused(self) -> None:
        record = self._record(scope="voice_clone")
        with self.assertRaisesRegex(ConsentError, "does not cover"):
            require_consent(self.reference, "image_clone", record)

    def test_expired_record_is_refused(self) -> None:
        record = self._record(expires_in_seconds=60)
        body = json.loads(record.read_text(encoding="utf-8"))
        body["expires_at"] = time.time() - 1
        record.write_text(json.dumps(body), encoding="utf-8")
        with self.assertRaisesRegex(ConsentError, "expired"):
            require_consent(self.reference, "voice_clone", record)

    def test_valid_record_is_accepted(self) -> None:
        record = self._record(expires_in_seconds=3600)
        loaded = require_consent(self.reference, "voice_clone", record)
        self.assertEqual(loaded.scope, "voice_clone")
        self.assertTrue(loaded.adult_confirmed)
        self.assertEqual(len(loaded.reference_hash), 64)


class LazyImports(unittest.TestCase):
    def test_package_import_loads_no_model_libraries(self) -> None:
        code = (
            "import sys, capabilities.media_cloning, capabilities.media_cloning.consent_gate\n"
            f"print(','.join(m for m in {HEAVY_MODULES!r} if m in sys.modules))\n"
        )
        proc = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "", f"heavy modules imported eagerly: {proc.stdout.strip()}")


class CapabilityPackageSchema(unittest.TestCase):
    def test_capability_files_match_schema(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        try:
            import jsonschema
        except ImportError:
            jsonschema = None
        for path in CAPABILITY_FILES:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                doc = json.loads(path.read_text(encoding="utf-8"))
                if jsonschema is not None:
                    jsonschema.validate(doc, schema)
                    continue
                for key in schema["required"]:
                    self.assertIn(key, doc)
                if schema.get("additionalProperties") is False:
                    self.assertEqual(set(doc) - set(schema["properties"]), set())
                for key in schema["properties"]["mastery"]["required"]:
                    self.assertIn(key, doc["mastery"])
                self.assertGreaterEqual(doc["mastery"]["threshold"], 0)
                self.assertLessEqual(doc["mastery"]["threshold"], 1)


if __name__ == "__main__":
    unittest.main()
