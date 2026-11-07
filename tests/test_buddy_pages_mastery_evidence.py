import unittest
from tools.build_buddy_pages_mastery_evidence import build

class BuddyPagesEvidenceTests(unittest.TestCase):
    def test_no_unsupported_mastery(self):
        data = build()
        self.assertFalse(data["coding_mastery_verified"])
        self.assertFalse(data["worldwide_code_study_verified"])
        self.assertEqual(data["independent_mastery_results"], [])

    def test_counts_from_report(self):
        data = build()
        self.assertEqual(data["counts"]["benchmark_programs"], 13)
        self.assertEqual(data["counts"]["live_programs_with_evidence"], 0)

    def test_programs_not_mislabeled_mastered(self):
        self.assertGreaterEqual(len(build()["programs"]), 10)
        self.assertTrue(all(not x["mastered"] for x in build()["programs"]))

if __name__ == "__main__":
    unittest.main()
