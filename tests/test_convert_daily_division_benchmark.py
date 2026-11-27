import unittest

from tools.convert_daily_division_benchmark import convert


class DailyDivisionBenchmarkConversionTests(unittest.TestCase):
    def setUp(self):
        self.crosswalk = {
            "domains": [
                {"domain_id": "alpha", "domain_name": "Alpha", "mapping_status": "proposed"},
                {"domain_id": "beta", "domain_name": "Beta", "mapping_status": "unresolved"},
            ]
        }

    def test_missing_domain_rows_remain_unmeasured_not_failed(self):
        result = convert({
            "divisions": 1,
            "divisionResults": [
                {"division": "Alpha", "score": 100, "passed": 5, "status": "pass"}
            ],
        }, self.crosswalk)
        self.assertEqual(result["domain_division_count"], 2)
        self.assertEqual(result["measured_domain_division_count"], 1)
        self.assertEqual(result["unmeasured_domain_divisions"], ["Beta"])
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["status"], "pass")
        self.assertIsNone(result["results"][0]["masterbot_id"])

    def test_unknown_and_duplicate_domain_rows_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate domain benchmark result"):
            convert({
                "divisionResults": [
                    {"division": "Alpha", "score": 100, "passed": 5, "status": "pass"},
                    {"division": "Alpha", "score": 90, "passed": 4, "status": "needs_remediation"},
                ]
            }, self.crosswalk)
        with self.assertRaisesRegex(ValueError, "unknown domain divisions"):
            convert({
                "divisionResults": [
                    {"division": "NotACanonicalDomain", "score": 100, "passed": 5, "status": "pass"}
                ]
            }, self.crosswalk)

    def test_source_count_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "division count does not match"):
            convert({"divisions": 2, "divisionResults": [
                {"division": "Alpha", "score": 100, "passed": 5, "status": "pass"}
            ]}, self.crosswalk)


if __name__ == "__main__":
    unittest.main()
