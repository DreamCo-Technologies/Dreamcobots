"""The fleet refresh proposal must remain read-only and artifact-based."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "fleet-catalog-refresh-proposal.yml"


class FleetCatalogRefreshProposalWorkflowTests(unittest.TestCase):
    def test_proposal_does_not_request_pull_request_write_permission(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        permissions = workflow.split("permissions:", 1)[1].split("concurrency:", 1)[0]
        self.assertIn("contents: read", permissions)
        self.assertNotIn("pull-requests: write", permissions)

    def test_generated_changes_are_uploaded_as_review_artifact(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("actions/upload-artifact@v4", workflow)
        self.assertIn("fleet-catalog-refresh-proposal-", workflow)
        self.assertIn("git diff --binary > fleet-catalog-refresh.patch", workflow)
        self.assertNotIn("peter-evans/create-pull-request", workflow)

    def test_proposal_workflow_never_auto_merges_or_deploys(self):
        workflow = WORKFLOW.read_text(encoding="utf-8").lower()
        self.assertNotIn("gh pr merge", workflow)
        self.assertNotIn("auto-merge", workflow)
        self.assertNotIn("deploy-buddy", workflow)


if __name__ == "__main__":
    unittest.main()
