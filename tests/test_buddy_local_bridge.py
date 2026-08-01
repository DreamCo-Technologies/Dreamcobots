from __future__ import annotations

import unittest

from tools.buddy_local_bridge import LocalBridgeError, require_approval, safe_url, search_url, workspace_targets


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


if __name__ == "__main__":
    unittest.main()
