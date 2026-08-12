import json
import unittest

from tools.generate_buddy_benchmark_index import build_index


class BuddyBenchmarkIndexTests(unittest.TestCase):
    def test_all_programs_and_repository_suites_are_publicly_tracked(self):
        index = build_index()
        summary = index["summary"]
        self.assertGreaterEqual(summary["benchmarkPrograms"], 12)
        self.assertGreaterEqual(summary["repositorySuites"], 25)
        self.assertEqual(summary["publicTrackingPrograms"], summary["benchmarkPrograms"])
        self.assertEqual(summary["liveBenchmarkPrograms"], 0)
        self.assertTrue(index["truthContract"]["liveResultsRequireEvidenceArtifacts"])
        serialized = json.dumps(index).lower()
        self.assertNotIn("github_pat_", serialized)
        self.assertNotIn("sk_live_", serialized)


if __name__ == "__main__":
    unittest.main()
