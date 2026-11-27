from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/buddy-technology-radar.yml"


class BuddyTechnologyRadarWorkflowSafetyTests(unittest.TestCase):
    def test_refresh_never_pushes_directly_to_main(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: write\n  pull-requests: write", text)
        self.assertIn("peter-evans/create-pull-request@v7", text)
        self.assertIn("base: main", text)
        self.assertIn("branch: automation/buddy-technology-radar", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("persist-credentials: true", text)
        self.assertIn("persist-credentials: false", text)

    def test_refresh_preserves_bounded_public_projection_and_artifact_fallback(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("python3 tools/refresh_buddy_technology_radar.py --check", text)
        self.assertIn("website/data/buddy-technology-radar.json", text)
        self.assertIn("actions/upload-artifact@v7", text)
        self.assertIn("if: success()", text)
        self.assertIn("requires human review", text)


if __name__ == "__main__":
    unittest.main()
