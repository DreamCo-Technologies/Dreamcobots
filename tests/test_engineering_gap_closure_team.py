import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEAM = ROOT / "config" / "engineering-gap-closure-team.json"
PLAN = ROOT / "config" / "generated" / "engineering-gap-closure-plan.json"


class EngineeringGapClosureTeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_github_platform_benchmark.py")], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_engineering_gap_closure_plan.py")], cwd=ROOT, check=True)
        cls.team = json.loads(TEAM.read_text(encoding="utf-8"))
        cls.plan = json.loads(PLAN.read_text(encoding="utf-8"))

    def test_team_has_broad_specialist_coverage(self):
        ids = {row["id"] for row in self.team["team"]}
        required = {
            "chief_architect","ci_reliability_builder","platform_builder","developer_experience_builder",
            "security_builder","sandbox_qa_builder","performance_builder","data_model_builder",
            "agent_runtime_builder","deployment_builder","business_system_builder","open_source_builder",
            "observability_builder","migration_compatibility_builder","red_team_reviewer","release_reviewer"
        }
        self.assertTrue(required.issubset(ids))

    def test_parallel_policy_is_fast_but_owner_safe(self):
        policy = self.team["parallel_policy"]
        self.assertGreaterEqual(policy["maximum_parallel_lanes"], 20)
        self.assertGreaterEqual(policy["maximum_parallel_candidates_per_gap"], 3)
        self.assertTrue(policy["same_canonical_owner_serialized"])
        self.assertTrue(policy["independent_owners_parallel"])
        self.assertTrue(policy["shared_infrastructure_first"])

    def test_completion_gate_cannot_skip_quality_or_safety(self):
        gate = " ".join(self.team["completion_gate"]).lower()
        for phrase in ["acceptance tests", "sandbox/negative tests", "security/privacy/permission", "focused tests pass", "regression suite passes", "rollback", "before/after benchmark", "runtime evidence"]:
            self.assertIn(phrase, gate)

    def test_every_current_github_gap_has_owner_and_reviewers(self):
        for gap in self.plan["gaps"]:
            self.assertTrue(gap["primary_owner"])
            self.assertGreaterEqual(len(gap["required_reviewers"]), 3)
            self.assertIn("security_builder", gap["required_reviewers"])
            self.assertIn("sandbox_qa_builder", gap["required_reviewers"])
            self.assertIn("release_reviewer", gap["required_reviewers"])
            self.assertGreaterEqual(gap["parallel_slot"], 1)
            self.assertLessEqual(gap["parallel_slot"], self.team["parallel_policy"]["maximum_parallel_lanes"])

    def test_no_gap_is_claimed_closed_by_generation(self):
        self.assertIn("not closed until executable evidence passes", self.team["truth_rule"].lower())


if __name__ == "__main__":
    unittest.main()
