import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_CFG = ROOT / "config" / "universal-human-ai-software-task-sandbox.json"
TASK_OUT = ROOT / "config" / "generated" / "universal-human-ai-task-sandbox.json"
GH_CFG = ROOT / "config" / "github-platform-parity-benchmark.json"
GH_OUT = ROOT / "config" / "generated" / "github-platform-parity-benchmark.json"
NOTES_CFG = ROOT / "config" / "notes-to-code-program.json"
NOTES_OUT = ROOT / "config" / "generated" / "notes-to-code-backlog.json"


class PlatformEvolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_universal_human_ai_task_sandbox.py")], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_github_platform_benchmark.py")], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_notes_to_code_backlog.py")], cwd=ROOT, check=True)
        cls.task_cfg = json.loads(TASK_CFG.read_text(encoding="utf-8"))
        cls.task_out = json.loads(TASK_OUT.read_text(encoding="utf-8"))
        cls.gh_cfg = json.loads(GH_CFG.read_text(encoding="utf-8"))
        cls.gh_out = json.loads(GH_OUT.read_text(encoding="utf-8"))
        cls.notes_cfg = json.loads(NOTES_CFG.read_text(encoding="utf-8"))
        cls.notes_out = json.loads(NOTES_OUT.read_text(encoding="utf-8"))

    def test_task_sandbox_is_massive_and_truthful(self):
        self.assertGreaterEqual(self.task_out["category_count"], 50000)
        self.assertFalse(any(row.get("status") == "passed" for row in self.task_out["categories"]))
        self.assertIn("runtime capability", self.task_out["truth_boundary"].lower())

    def test_github_benchmark_tracks_many_platform_capabilities(self):
        self.assertGreaterEqual(self.gh_out["capability_count"], 45)
        ids = {row["id"] for row in self.gh_out["capabilities"]}
        for required in {
            "repository_storage","issues","pull_requests","actions_runner","workflow_artifacts","pages","releases",
            "packages","rulesets","dependency_graph","code_scanning","secret_scanning","rest_api","webhooks",
            "custom_agents","coding_agent","failure_observability","self_repair","open_source_discovery"
        }:
            self.assertIn(required, ids)
        self.assertFalse(self.gh_out["parity_complete"])

    def test_every_github_gap_has_builder_plan(self):
        for row in self.gh_out["capabilities"]:
            self.assertIn("gap_builder_plan", row)
            self.assertGreaterEqual(len(row["gap_builder_plan"]["acceptance"]), 6)
            self.assertTrue(row["runtime_evidence_required"])

    def test_notes_to_code_requires_search_dedupe_and_tests(self):
        pipeline = " ".join(self.notes_cfg["pipeline"]).lower()
        self.assertIn("search repository", pipeline)
        self.assertIn("deduplicate", pipeline)
        self.assertIn("acceptance criteria", pipeline)
        self.assertIn("sandbox/test requirements", pipeline)
        for item in self.notes_out["items"][:200]:
            self.assertTrue(item["repository_search_required"])
            self.assertTrue(item["dedupe_required"])
            self.assertTrue(item["acceptance_tests_required"])
            self.assertNotEqual(item["code_candidate_status"], "implemented")

    def test_notes_to_code_does_not_turn_documentation_into_random_code(self):
        rules = " ".join(self.notes_cfg["rules"]).lower()
        self.assertIn("do not convert explanatory documentation into pointless code", rules)
        self.assertIn("search before building", rules)


if __name__ == "__main__":
    unittest.main()
