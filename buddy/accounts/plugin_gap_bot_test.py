import unittest

from buddy.accounts.plugin_gap_bot import scan


class PluginGapBotTest(unittest.TestCase):
    def test_gap_bot_lists_unproven_plugin_actions(self) -> None:
        report = scan()
        self.assertGreater(len(report["gaps"]), 0)
        self.assertFalse(report["frontier_claim"])
        self.assertFalse(report["weights_downloaded"])
        self.assertIn("hugging-face", report["sources"])


if __name__ == "__main__":
    unittest.main()
