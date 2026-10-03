import unittest

from tools.daily_bot_study_scan import scan


class DailyBotStudyScanTest(unittest.TestCase):
    def test_scan_covers_bots_without_claiming_production_mastery(self) -> None:
        report = scan()
        self.assertGreaterEqual(report["bot_count"], 1100)
        self.assertGreater(report["original_bot_studies"], 100)
        self.assertFalse(report["production_mastered"])
        self.assertTrue(report["speed"])


if __name__ == "__main__":
    unittest.main()
