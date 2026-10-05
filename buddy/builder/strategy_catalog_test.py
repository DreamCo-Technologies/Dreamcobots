import unittest

from buddy.builder.strategy_catalog import catalog


class StrategyCatalogTest(unittest.TestCase):
    def test_every_strategy_has_a_prospectus_and_no_frontier_claim(self) -> None:
        report = catalog()
        self.assertGreater(report["count"], 25)
        self.assertTrue(all(row["prospectus"] and row["button"] for row in report["strategies"]))
        self.assertFalse(any(row["frontier_claim"] for row in report["strategies"]))


if __name__ == "__main__":
    unittest.main()
