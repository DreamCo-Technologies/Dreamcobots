from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BuddySafetyOperationsTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_approval_policy_uses_least_privilege_and_reversibility(self):
        text = self.read("buddy_os/governance/approval_policy.yaml")
        for item in (
            "least_privilege: true",
            "default_to_reversible: true",
            "dry_run_before_destructive: true",
            "never_bypass_repository_protection: true",
            "log_decision_and_approval: true",
        ):
            self.assertIn(item, text)

    def test_recovery_is_bounded_and_verified(self):
        text = self.read("buddy_os/operations/recovery_contract.yaml")
        self.assertIn("bounded_retries_only: true", text)
        self.assertIn("never_retry_destructive_actions_automatically: true", text)
        self.assertIn("verify_after_recovery: true", text)
        self.assertIn("repeated_failures_escalate: true", text)

    def test_audit_schema_requires_risk_approval_and_result(self):
        payload = json.loads(self.read("buddy_os/governance/audit_event.schema.json"))
        for field in ("risk", "approval", "result"):
            self.assertIn(field, payload["required"])


if __name__ == "__main__":
    unittest.main()
