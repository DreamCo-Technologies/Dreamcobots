from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_buddy_laptop_app.mjs"


class BuddyLaptopAppSafetyTests(unittest.TestCase):
    def test_local_test_credential_is_not_key_shaped(self):
        source = RUNNER.read_text(encoding="utf-8")
        self.assertNotIn("sk-local-test-placeholder", source)
        self.assertIn("local-test-placeholder-not-a-key", source)


if __name__ == "__main__":
    unittest.main()
