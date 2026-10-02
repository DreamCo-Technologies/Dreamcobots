import json
import unittest
from pathlib import Path

from benchmarks.america_gov.sandbox import GovernmentSandbox, load_catalog


class AmericaGovSandboxTest(unittest.TestCase):
    def test_benchmark_and_catalog(self) -> None:
        report = GovernmentSandbox().benchmark()
        self.assertEqual(report["failed"], 0)
        catalog = load_catalog()
        self.assertGreaterEqual(len(catalog["resources"]), 15)
        self.assertGreaterEqual(len(catalog["services"]), 18)
        self.assertTrue(all(row["sandbox"] for row in catalog["services"]))
        self.assertTrue(all(not row["live_actions"] for row in catalog["resources"]))

    def test_report_shape(self) -> None:
        report = GovernmentSandbox().benchmark()
        encoded = json.dumps(report)
        self.assertIn("America.gov", encoded)
        self.assertNotIn("123-45-6789", encoded)


if __name__ == "__main__":
    unittest.main()
