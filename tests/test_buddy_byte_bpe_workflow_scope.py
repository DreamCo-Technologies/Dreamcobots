from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "buddy-byte-bpe-trainer.yml"


class BuddyByteBpeWorkflowScopeTests(unittest.TestCase):
    def test_authorized_corpus_changes_trigger_trainer_regressions(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        pull_request_paths = workflow.split("  pull_request:", 1)[1].split(
            "  workflow_dispatch:", 1
        )[0]
        self.assertIn('"data/buddy-authorized-corpora/**"', pull_request_paths)

    def test_workflow_runs_trainer_and_its_scope_regressions(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python -m unittest tests.test_buddy_byte_bpe_trainer "
            "tests.test_buddy_byte_bpe_workflow_scope",
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
