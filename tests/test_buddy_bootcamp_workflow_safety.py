from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/buddy-bootcamp-curriculum.yml"


class BuddyBootcampWorkflowSafetyTests(unittest.TestCase):
    def test_curriculum_generation_is_read_only_and_artifact_based(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read", text)
        self.assertNotIn("pull-requests: write", text)
        self.assertNotIn("peter-evans/create-pull-request@", text)
        self.assertIn("actions/upload-artifact@v7", text)
        self.assertIn("Publish manual-review instructions", text)

    def test_workflow_does_not_claim_training_or_model_promotion(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("No dataset downloads, training, certification, or model promotion occurred.", text)
        self.assertIn("python tools/build_buddy_bootcamp_curriculum.py --check", text)


if __name__ == "__main__":
    unittest.main()
