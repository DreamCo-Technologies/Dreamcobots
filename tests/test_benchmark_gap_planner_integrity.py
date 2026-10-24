"""Fail-closed benchmark planner tests; no paid/network services."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools/benchmark_gap_planner.py"
spec = importlib.util.spec_from_file_location("benchmark_gap_planner", SCRIPT)
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)

REGISTRY = {"divisions": [{"name": f"Division{i}", "id": i} for i in range(1, 66)]}


def measure(score, **kw):
    return {"division": "Division1", "benchmark": "contract", "score": score, "target": 100, "status": "failed", **kw}


class PlannerIntegrityTests(unittest.TestCase):
    def test_valid_gap_is_queued_for_repair(self):
        output = planner.build_queue({"results": [measure(70)]}, REGISTRY)
        self.assertFalse(output["complete"])
        self.assertEqual(output["measured_divisions"], 1)
        self.assertEqual(len(output["unmeasured_division_ids"]), 64)
        self.assertEqual(output["queue"][0]["action"], "RUN_BENCHMARKS")
        self.assertEqual(next(row for row in output["queue"] if row["division"] == 1)["action"], "CLOSE_GAPS")

    def test_zero_score_remains_real_gap(self):
        output = planner.build_queue({"results": [measure(0)]}, REGISTRY)
        self.assertEqual(next(row for row in output["queue"] if row["division"] == 1)["action"], "CLOSE_GAPS")

    def test_nan_rejected_not_treated_as_at_target(self):
        output = planner.build_queue({"results": [measure(float("nan"))]}, REGISTRY)
        self.assertFalse(output["complete"])
        self.assertEqual(next(row for row in output["queue"] if row["division"] == 1)["action"], "RUN_BENCHMARKS")

    def test_infinity_rejected(self):
        output = planner.build_queue({"results": [measure(float("inf"))]}, REGISTRY)
        self.assertEqual(len(output["rejected"]), 1)

    def test_boolean_score_rejected(self):
        output = planner.build_queue({"results": [measure(True)]}, REGISTRY)
        self.assertFalse(output["complete"])

    def test_nonnumeric_score_rejected(self):
        output = planner.build_queue({"results": [measure("100")]}, REGISTRY)
        self.assertFalse(output["complete"])

    def test_malformed_results_list_rejected(self):
        with self.assertRaises(ValueError):
            planner.build_queue({"results": {"division": "Division1"}}, REGISTRY)

    def test_duplicate_measurements_not_silently_accepted(self):
        output = planner.build_queue({"results": [measure(80), measure(100)]}, REGISTRY)
        self.assertFalse(output["complete"])
        self.assertIn("duplicate", output["rejected"][0]["reason"])

    def test_invalid_duplicate_does_not_hide_valid_measurement(self):
        output = planner.build_queue({"results": [measure(float("nan")), measure(70)]}, REGISTRY)
        self.assertFalse(output["complete"])
        self.assertEqual(len(output["rejected"]), 1)
        self.assertEqual(next(row for row in output["queue"] if row["division"] == 1)["action"], "CLOSE_GAPS")

    def test_missing_measurement_remains_unmeasured(self):
        output = planner.build_queue({"results": [{"division": "Division1", "benchmark": "contract"}]}, REGISTRY)
        self.assertEqual(next(row for row in output["queue"] if row["division"] == 1)["action"], "RUN_BENCHMARKS")

    def test_missing_scorecard_cannot_report_complete(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as temp:
            result = planner.load_queue_from_scores(Path(temp) / "absent.json", REGISTRY)
        self.assertFalse(result["complete"])
        self.assertEqual(result["score_source_status"], "missing")
        self.assertEqual(len(result["queue"]), 65)
        self.assertTrue(all(row["action"] == "RUN_BENCHMARKS" for row in result["queue"]))

    def test_empty_scorecard_cannot_report_complete(self):
        import json
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as temp:
            path = Path(temp) / "empty.json"
            path.write_text(json.dumps({"results": []}))
            result = planner.load_queue_from_scores(path, REGISTRY)
        self.assertFalse(result["complete"])
        self.assertEqual(result["score_source_status"], "empty")

    def test_measured_scorecard_remains_complete(self):
        import json
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as temp:
            path = Path(temp) / "measured.json"
            path.write_text(json.dumps({"results": [measure(70)]}))
            result = planner.load_queue_from_scores(path, REGISTRY)
        self.assertFalse(result["complete"])
        self.assertEqual(result["measured_divisions"], 1)
        self.assertEqual(result["score_source_status"], "present")

    def test_all_65_divisions_with_valid_measurements_complete_coverage(self):
        records = [{"division": f"Division{i}", "benchmark": "contract",
                    "score": 100, "target": 100, "status": "passed"} for i in range(1, 66)]
        output = planner.build_queue({"results": records}, REGISTRY)
        self.assertTrue(output["complete"])
        self.assertEqual(output["measured_divisions"], 65)
        self.assertEqual(output["unmeasured_division_ids"], [])
        self.assertIn("not suite coverage or mastery", output["coverage_scope"])

    def test_incomplete_score_with_other_divisions_measured_stays_incomplete(self):
        records = [{"division": f"Division{i}", "benchmark": "contract",
                    "score": 100, "target": 100, "status": "passed"} for i in range(1, 66)]
        records[41].pop("score")
        output = planner.build_queue({"results": records}, REGISTRY)
        self.assertFalse(output["complete"])
        self.assertEqual(output["measured_divisions"], 64)
        self.assertEqual(output["unmeasured_division_ids"], [42])
        self.assertTrue(any(row["division"] == 42 and row["action"] == "RUN_BENCHMARKS"
                            for row in output["queue"]))

    def test_bad_registry_rejected(self):
        with self.assertRaises(ValueError):
            planner.build_queue({"results": []}, {"divisions": [{"name": "OnlyOne", "id": 1}]})

    def test_unknown_division_not_discarded_silently(self):
        output = planner.build_queue({"results": [{"division": "Unknown", "benchmark": "contract", "score": 100, "target": 100}]}, REGISTRY)
        self.assertFalse(output["complete"])
        self.assertEqual(len(output["rejected"]), 1)


if __name__ == "__main__":
    unittest.main()
