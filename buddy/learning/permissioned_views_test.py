import unittest

from buddy.learning.permissioned_views import PermissionError, call, grant, learn


class PermissionedViewsTest(unittest.TestCase):
    def test_final_view_needs_permission_and_several_sources(self) -> None:
        grants = [grant("train", "buddy-a", True), grant("download_weights", "buddy-a", True)]
        views = [
            {"source": "docs", "claim": "cite it", "stance": "agree"},
            {"source": "benchmark", "claim": "cite it", "stance": "agree"},
            {"source": "counterexample", "claim": "skip it", "stance": "conflict"},
        ]
        with self.assertRaises(PermissionError):
            learn("buddy-a", views[:2], grants)
        report = learn("buddy-a", views, grants, download_weights=True)
        self.assertTrue(report["final"])
        self.assertFalse(report["weights_downloaded"])
        self.assertTrue(report["conflicts"])

    def test_calls_need_both_sides_and_consent_for_voice(self) -> None:
        with self.assertRaises(PermissionError):
            grant("voice_call", "buddy-a", True)
        grants = [
            grant("voice_call", "buddy-a", True, "a" * 16),
            grant("voice_call", "buddy-b", True, "b" * 16),
            grant("peer_message", "buddy-a", True),
        ]
        answered = call("voice", "buddy-a", "buddy-b", grants, "hello")
        self.assertEqual(answered["answered_with"], "voice")
        self.assertFalse(answered["delivered"])


if __name__ == "__main__":
    unittest.main()
