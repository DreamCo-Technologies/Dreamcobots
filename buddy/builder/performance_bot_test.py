import unittest

from buddy.builder.performance_bot import record, summarize


class PerformanceBotTest(unittest.TestCase):
    def test_summary_uses_median_and_does_not_certify(self) -> None:
        runs = [record("bot", "task", 0, 10, True, 1), record("bot", "task", 0, 30, True, 3), record("bot", "task", 0, 50, False, 2)]
        report = summarize(runs)
        self.assertEqual(report["median_latency_ms"], 30)
        self.assertAlmostEqual(report["success_rate"], 2 / 3)
        self.assertFalse(report["production_ready"])


if __name__ == "__main__":
    unittest.main()
