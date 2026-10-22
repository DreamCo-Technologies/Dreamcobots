"""Tests for Buddy account-scoped inbox and workflow policy."""
import unittest
from datetime import datetime, timedelta, timezone

from buddy.inbox_workflow_policy import Authorization, authorize, workflow_plan


class InboxWorkflowPolicyTests(unittest.TestCase):
    def setUp(self):
        self.auth = Authorization("user_1", "buddy_inbox", frozenset({
            "inbox.read", "inbox.draft", "inbox.send", "workflow.inspect",
            "workflow.plan", "workflow.dispatch"
        }), datetime.now(timezone.utc) + timedelta(days=1))
        self.args = {"user_id": "user_1", "connected_account_id": "buddy_inbox"}

    def test_read_allowed(self):
        self.assertTrue(authorize("inbox.read", self.auth, **self.args)["allowed"])

    def test_send_needs_confirmation(self):
        self.assertFalse(authorize("inbox.send", self.auth, **self.args)["allowed"])
        self.assertTrue(authorize("inbox.send", self.auth, confirmed=True, **self.args)["allowed"])

    def test_cross_account_denied(self):
        self.assertFalse(authorize("inbox.read", self.auth, user_id="user_2",
                                   connected_account_id="buddy_inbox")["allowed"])

    def test_revoked_denied(self):
        auth = Authorization(self.auth.user_id, self.auth.connected_account_id,
                             self.auth.allowed_actions, self.auth.expires_at, revoked=True)
        self.assertFalse(authorize("inbox.read", auth, **self.args)["allowed"])

    def test_expired_denied(self):
        auth = Authorization(self.auth.user_id, self.auth.connected_account_id,
                             self.auth.allowed_actions, datetime.now(timezone.utc) - timedelta(seconds=1))
        self.assertFalse(authorize("inbox.read", auth, **self.args)["allowed"])

    def test_deployment_always_blocked(self):
        self.assertFalse(authorize("workflow.deploy_production", self.auth,
                                   confirmed=True, **self.args)["allowed"])

    def test_unknown_action_denied(self):
        self.assertFalse(authorize("account.export_passwords", self.auth, **self.args)["allowed"])

    def test_dry_run_only(self):
        result = workflow_plan([{"action": "inbox.read"}, {"action": "inbox.send"}],
                               self.auth, **self.args)
        self.assertEqual(result["status"], "dry_run_only")
        self.assertFalse(result["ready_for_automatic_execution"])


if __name__ == "__main__":
    unittest.main()
