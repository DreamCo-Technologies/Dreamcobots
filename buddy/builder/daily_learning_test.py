import unittest

from buddy.builder.daily_learning import scan


class DailyLearningTest(unittest.TestCase):
    def test_scan_does_not_invent_learned_rows(self) -> None:
        report = scan()
        self.assertGreater(report["study_files"], 100)
        self.assertEqual(report["learned"], [])
        self.assertGreater(len(report["sources"]), 20)


if __name__ == "__main__":
    unittest.main()
