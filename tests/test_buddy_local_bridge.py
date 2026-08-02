from __future__ import annotations

import unittest
from unittest.mock import patch

from tools.buddy_local_bridge import (
    LocalBridgeError,
    require_approval,
    safe_url,
    search_url,
    store_macos_keychain_secret,
    validate_secret_locator,
    validate_secret_value,
    workspace_targets,
)


class BuddyLocalBridgePolicyTests(unittest.TestCase):
    def test_search_urls_are_encoded_and_engine_allowlisted(self):
        self.assertEqual(
            search_url("Buddy local coding", "duckduckgo"),
            "https://duckduckgo.com/?q=Buddy+local+coding",
        )
        with self.assertRaisesRegex(LocalBridgeError, "supported search engine"):
            search_url("Buddy local coding", "unknown")

    def test_only_https_and_loopback_http_urls_are_openable(self):
        self.assertEqual(safe_url("https://example.com/path"), "https://example.com/path")
        self.assertEqual(safe_url("http://127.0.0.1:8765/buddy.html"), "http://127.0.0.1:8765/buddy.html")
        with self.assertRaisesRegex(LocalBridgeError, "Only HTTPS"):
            safe_url("http://example.com")
        with self.assertRaisesRegex(LocalBridgeError, "embedded credentials"):
            safe_url("https://user:secret@example.com")

    def test_every_side_effect_requires_one_action_approval(self):
        with self.assertRaisesRegex(LocalBridgeError, "Approve this one"):
            require_approval({"approved": False})
        require_approval({"approved": True})

    def test_workspace_targets_are_bounded_allowlisted_and_credential_free(self):
        apps, urls = workspace_targets(
            ["finder", "notes", "finder"],
            ["https://github.com/DreamCo-Technologies/Dreamcobots", "http://127.0.0.1:8765/buddy.html"],
        )
        self.assertEqual(apps, ["finder", "notes"])
        self.assertEqual(len(urls), 2)
        with self.assertRaisesRegex(LocalBridgeError, "at most six"):
            workspace_targets(["finder", "notes", "calendar", "mail"], ["https://example.com/1", "https://example.com/2", "https://example.com/3"])
        with self.assertRaisesRegex(LocalBridgeError, "approved local app"):
            workspace_targets(["terminal"], [])
        with self.assertRaisesRegex(LocalBridgeError, "embedded credentials"):
            workspace_targets([], ["https://user:secret@example.com"])

    def test_secret_intake_validates_locator_and_secret_without_logging_values(self):
        self.assertEqual(validate_secret_locator("gemini", "GEMINI_API_KEY"), ("gemini", "GEMINI_API_KEY"))
        self.assertEqual(validate_secret_value("test-secret-value"), "test-secret-value")
        with self.assertRaisesRegex(LocalBridgeError, "provider id"):
            validate_secret_locator("Gemini API", "GEMINI_API_KEY")
        with self.assertRaisesRegex(LocalBridgeError, "line breaks"):
            validate_secret_value("secret\nvalue")

    @patch("tools.buddy_local_bridge.subprocess.run")
    @patch("tools.buddy_local_bridge.sys.platform", "darwin")
    def test_macos_keychain_intake_uses_stdin_and_returns_only_a_locator(self, run):
        run.return_value.returncode = 0
        reference = store_macos_keychain_secret("gemini", "GEMINI_API_KEY", "test-secret-value")
        self.assertEqual(reference, "os_keychain:dreamco.buddy.gemini/GEMINI_API_KEY")
        command = run.call_args.args[0]
        self.assertNotIn("test-secret-value", command)
        self.assertEqual(command[-1], "-w")
        self.assertEqual(run.call_args.kwargs["input"], "test-secret-value\n")
        self.assertTrue(run.call_args.kwargs["capture_output"])


if __name__ == "__main__":
    unittest.main()
