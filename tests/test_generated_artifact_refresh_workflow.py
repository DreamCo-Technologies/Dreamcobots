"""Generated-artifact proposal workflow covers canonical Buddy source inputs."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/fleet-catalog-refresh-proposal.yml"


class GeneratedArtifactRefreshWorkflowTests(unittest.TestCase):
    def test_refresh_triggers_cover_buddy_and_canonical_division_sources(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for path in ("buddy/**", "buddy_os/**", "config/divisions/**", "config/bots/**"):
            self.assertIn(path, text)

    def test_refresh_proposes_learning_graph_and_file_prospectus_outputs(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("tools/build_buddy_learning_os_connection_graph.py", text)
        self.assertIn("tools/build_file_prospectus.py", text)
        self.assertIn("config/generated/buddy-learning-os-connections.json", text)
        self.assertIn("website/data/buddy-learning-os-connections.json", text)

    def test_refresh_triggers_cover_generated_evidence_builders_and_their_contract_test(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for path in (
            "tools/build_buddy_learning_os_connection_graph.py",
            "tools/build_file_prospectus.py",
            "tests/test_generated_artifact_refresh_workflow.py",
        ):
            self.assertIn(path, text)


if __name__ == "__main__":
    unittest.main()
