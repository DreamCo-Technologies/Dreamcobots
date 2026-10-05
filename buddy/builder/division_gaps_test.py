import unittest

from buddy.builder.division_gaps import check


class DivisionGapTest(unittest.TestCase):
    def test_every_division_stays_not_working(self) -> None:
        report = check()
        self.assertEqual(len(report["divisions"]), 40)
        self.assertTrue(all(row["working"] is False for row in report["divisions"]))
        self.assertFalse(report["production_ready"])


if __name__ == "__main__":
    unittest.main()
