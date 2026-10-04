import unittest

from buddy.builder.strategy_analysis import analyze


class StrategyAnalysisTest(unittest.TestCase):
    def test_team_checks_sections_and_does_not_score_them(self) -> None:
        report = analyze()
        self.assertGreater(len(report["sections"]), 20)
        self.assertIsNone(report["winner"])
        self.assertTrue(all(row["score"] is None for row in report["sections"]))


if __name__ == "__main__":
    unittest.main()
