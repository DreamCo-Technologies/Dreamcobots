import unittest
from buddy.certification.daily_lab import compare_and_plan, fingerprint
from buddy.certification.engine import run_suite

class DailyLabTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {"capabilities":[{"id":"alpha","domain":"coding",
             "description":"Edit repository", "owner":"Buddy","target":"verified","test_module":""}]}
        self.report = run_suite(self.manifest, repo_root=".", execute=False, revision="abc")

    def test_unknown_frontier_not_claimed(self):
        row = compare_and_plan(self.manifest,self.report)["plans"][0]
        self.assertIsNone(row["frontier_score"])
        self.assertEqual(row["frontier_comparison_status"],"not_run")
        self.assertEqual(row["training_status"],"not_started")

    def test_dedup_candidate_preserves_both(self):
        second = dict(self.manifest["capabilities"][0], id="beta")
        self.manifest["capabilities"].append(second)
        report = run_suite(self.manifest, repo_root=".", execute=False)
        result = compare_and_plan(self.manifest, report)
        self.assertEqual(result["duplicate_candidate_groups"],[["alpha","beta"]])
        self.assertEqual(len(result["plans"]),2)

    def test_distinct_domain_not_duplicate(self):
        x = dict(self.manifest["capabilities"][0],domain="research")
        self.assertNotEqual(fingerprint(x), fingerprint(self.manifest["capabilities"][0]))

    def test_plan_requires_review_and_holdout(self):
        row = compare_and_plan(self.manifest,self.report)["plans"][0]
        self.assertTrue(row["requires_owner_approval"])
        self.assertTrue(any("held-out" in gap for gap in row["gaps"]))

if __name__ == "__main__":
    unittest.main()
