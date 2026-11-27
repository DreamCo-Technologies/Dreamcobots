from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from buddy.security.secret_store import load, store


class SecretStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self.old_key = os.environ.get("OWNER_SECRET_KEY")
        os.environ["OWNER_SECRET_KEY"] = "test-only-random-master-secret-32-chars-minimum"

    def tearDown(self) -> None:
        if self.old_key is None:
            os.environ.pop("OWNER_SECRET_KEY", None)
        else:
            os.environ["OWNER_SECRET_KEY"] = self.old_key

    def test_secret_round_trips_as_authenticated_ciphertext_outside_repo(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            report = store("billing", "sk_live_example", Path(folder))
            path = Path(folder) / "billing"
            payload = path.read_bytes()
            self.assertTrue(report["stored"])
            self.assertFalse(report["in_repo"])
            self.assertTrue(report["plaintext_written"])
            self.assertTrue(payload.startswith(b"DCOG2"))
            self.assertNotIn(b"sk_live_example", payload)
            self.assertEqual(load("billing", Path(folder)), "sk_live_example")
            if os.name == "posix":
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_each_write_uses_fresh_salt_and_nonce_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            store("first", "same-secret", Path(folder))
            store("second", "same-secret", Path(folder))
            self.assertNotEqual((Path(folder) / "first").read_bytes(), (Path(folder) / "second").read_bytes())
            with self.assertRaises(FileExistsError):
                store("first", "replacement", Path(folder))

    def test_ciphertext_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            store("billing", "secret-value", Path(folder))
            path = Path(folder) / "billing"
            payload = bytearray(path.read_bytes())
            payload[-1] ^= 0x01
            path.write_bytes(payload)
            with self.assertRaises(Exception):
                load("billing", Path(folder))

    def test_secret_names_cannot_escape_directory(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            for name in ("../escape", "/tmp/escape", ".hidden", ""):
                with self.subTest(name=name), self.assertRaises(PermissionError):
                    store(name, "secret-value", Path(folder))

    def test_secret_directory_cannot_be_inside_repository(self) -> None:
        with self.assertRaises(PermissionError):
            store("billing", "secret-value", Path(__file__).resolve().parents[2])

    def test_weak_or_missing_master_secret_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            os.environ["OWNER_SECRET_KEY"] = "short"
            with self.assertRaisesRegex(PermissionError, "32 characters"):
                store("billing", "secret-value", Path(folder))

    def test_wrong_master_secret_cannot_decrypt(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            store("billing", "secret-value", Path(folder))
            os.environ["OWNER_SECRET_KEY"] = "different-random-master-secret-32-chars-minimum"
            with self.assertRaises(Exception):
                load("billing", Path(folder))


if __name__ == "__main__":
    unittest.main()
