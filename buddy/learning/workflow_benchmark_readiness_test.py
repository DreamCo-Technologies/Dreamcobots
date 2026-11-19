import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workflow_benchmark_readiness import build_events, inventory


class WorkflowBenchmarkReadinessTest(unittest.TestCase):
    def test_files_and_events_cover_the_repository_without_claiming_execution(self) -> None:
        found = inventory()
        self.assertEqual(found["missing"], [])
        self.assertGreaterEqual(len(found["workflows"]), 80)
        self.assertGreaterEqual(len(found["benchmarks"]), 10)
        events = build_events(found)
        self.assertEqual(len(events["events"]), len(found["workflows"]) + len(found["benchmarks"]))
        self.assertTrue(all(item["event_type"] in {"tool_outcome", "benchmark"} for item in events["events"]))
        self.assertTrue(all(item["event_status"] == "inventory_only" for item in events["events"]))
        self.assertTrue(all(item["success"] is False for item in events["events"]))
        self.assertTrue(all(item["verified"] is False for item in events["events"]))
        self.assertTrue(all(item["regression_passed"] is False for item in events["events"]))
        self.assertTrue(all(item["safety_passed"] is False for item in events["events"]))
        self.assertTrue(all(item["evidence_refs"] == [] for item in events["events"]))
        encoded = json.dumps(events)
        self.assertIn("benchmarks/america_gov/sandbox.py", encoded)
        self.assertIn("benchmark_inventory", encoded)
        self.assertNotIn('"promote": true', encoded)


if __name__ == "__main__":
    unittest.main()
