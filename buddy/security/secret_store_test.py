import os
import tempfile
import unittest
from pathlib import Path

from buddy.security.secret_store import store


class SecretStoreTest(unittest.TestCase):
    def test_secret_stays_out_of_the_repo_and_off_disk_as_plaintext(self) -> None:
        os.environ["OWNER_SECRET_KEY"] = "host-only-test-key"
        with tempfile.TemporaryDirectory() as folder:
            report = store("billing", "sk_live_example", Path(folder))
        self.assertTrue(report["stored"])
        self.assertFalse(report["in_repo"])
        self.assertTrue(report["plaintext_written"])
        with self.assertRaises(PermissionError):
            store("billing", "sk_live_example", Path(__file__).resolve().parents[2])


if __name__ == "__main__":
    unittest.main()
