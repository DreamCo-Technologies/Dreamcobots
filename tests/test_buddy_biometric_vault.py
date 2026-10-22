"""Unit tests for Buddy biometric vault. Requires cryptography."""
import os
import tempfile
import unittest
from pathlib import Path

from buddy.biometric_vault import delete_templates, get_template, put_template


class BiometricVaultTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.key = os.urandom(32)

    def enroll(self, modality="face"):
        put_template(self.path, self.key, "person_001", modality, b"example_embedding",
                     consent=True, adult_or_guardian_approved=True)

    def test_roundtrip(self):
        self.enroll()
        self.assertEqual(get_template(self.path, self.key, "person_001", "face", consent_active=True),
                         b"example_embedding")
        self.assertNotIn(b"example_embedding", (self.path / "person_001.face.enc").read_bytes())

    def test_wrong_key(self):
        self.enroll()
        with self.assertRaises(Exception):
            get_template(self.path, os.urandom(32), "person_001", "face", consent_active=True)

    def test_consent_required(self):
        with self.assertRaises(PermissionError):
            put_template(self.path, self.key, "person_001", "face", b"x",
                         consent=False, adult_or_guardian_approved=True)

    def test_revoked_consent_blocks_read(self):
        self.enroll()
        with self.assertRaises(PermissionError):
            get_template(self.path, self.key, "person_001", "face", consent_active=False)

    def test_no_overwrite(self):
        self.enroll()
        with self.assertRaises(FileExistsError):
            self.enroll()

    def test_delete_both_modalities(self):
        self.enroll("face")
        self.enroll("voice")
        self.assertEqual(delete_templates(self.path, "person_001"), 2)
        self.assertEqual(delete_templates(self.path, "person_001"), 0)

    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):
            delete_templates(self.path, "../someone")

    def test_modality_swap_rejected(self):
        self.enroll("face")
        (self.path / "person_001.voice.enc").write_bytes((self.path / "person_001.face.enc").read_bytes())
        with self.assertRaises(Exception):
            get_template(self.path, self.key, "person_001", "voice", consent_active=True)


if __name__ == "__main__":
    unittest.main()
