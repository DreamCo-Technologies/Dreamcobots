import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workflow_benchmark_readiness import build_events, inventory


class WorkflowBenchmarkReadinessTest(unittest.TestCase):
    def test_files_and_events_cover_the_repository(self) -> None:
        found = inventory()
        self.assertEqual(found["missing"], [])
        self.assertGreaterEqual(len(found["workflows"]), 80)
        self.assertGreaterEqual(len(found["benchmarks"]), 10)
        events = build_events(found)
        self.assertEqual(len(events["events"]), len(found["workflows"]) + len(found["benchmarks"]))
        self.assertTrue(all(item["event_type"] in {"tool_outcome", "benchmark"} for item in events["events"]))
        encoded = json.dumps(events)
        self.assertIn("benchmarks/america_gov/sandbox.py", encoded)


if __name__ == "__main__":
    unittest.main()
