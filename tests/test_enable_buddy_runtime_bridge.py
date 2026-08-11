import unittest

from tools.enable_buddy_runtime_bridge import ANCHOR, SCRIPT_TAG, enable_bridge


class BuddyRuntimeBridgeInjectionTests(unittest.TestCase):
    def test_injects_bridge_after_existing_buddy_script(self):
        html = f"<html><body>\n{ANCHOR}</body></html>"
        updated = enable_bridge(html)
        self.assertIn(ANCHOR + SCRIPT_TAG, updated)

    def test_injection_is_idempotent(self):
        html = f"<html><body>\n{ANCHOR}</body></html>"
        once = enable_bridge(html)
        twice = enable_bridge(once)
        self.assertEqual(once, twice)
        self.assertEqual(twice.count("buddy-runtime-bridge.js?v=1"), 1)

    def test_missing_anchor_fails_instead_of_silently_skipping(self):
        with self.assertRaises(ValueError):
            enable_bridge("<html><body>No Buddy script</body></html>")


if __name__ == "__main__":
    unittest.main()
