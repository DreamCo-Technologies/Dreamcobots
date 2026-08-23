from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BuddyGovernanceContractTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_observability_contract_has_trace_and_privacy_controls(self):
        text = self.read("buddy_os/observability/observability_contract.yaml")
        for item in ("trace_id", "task_id", "project_id", "never_log_secrets: true", "alert_on_anomaly: true"):
            self.assertIn(item, text)

    def test_release_readiness_cannot_skip_evidence(self):
        text = self.read("buddy_os/governance/release_readiness.yaml")
        self.assertIn("no_status_jump: true", text)
        self.assertIn("missing_evidence_is_blocked: true", text)
        self.assertIn("rollback_plan_required_for_live_change: true", text)

    def test_agent_modes_reassess_risk_when_switching(self):
        text = self.read("buddy_os/agents/agent_mode_contract.yaml")
        self.assertIn("explicit_user_switch: true", text)
        self.assertIn("risk_change_requires_reassessment: true", text)
        self.assertIn("preserve_trace_id: true", text)

    def test_dashboard_health_needs_real_verification(self):
        text = self.read("buddy_os/dashboards/dashboard_health_contract.yaml")
        self.assertIn("registered_does_not_equal_healthy: true", text)
        self.assertIn("browser_load: required", text)
        self.assertIn("missing_health_evidence_is_not_healthy: true", text)

    def test_benchmark_requires_evidence_and_regression_suite(self):
        text = self.read("buddy_os/learning/benchmark_contract.yaml")
        self.assertIn("no_benchmark_pass_without_evidence: true", text)
        self.assertIn("no_training_promotion_without_regression_suite: true", text)
        self.assertIn("detect_capability_gaps: true", text)

    def test_incident_schema_is_parseable(self):
        payload = json.loads(self.read("buddy_os/debugging/incident_record.schema.json"))
        self.assertEqual(payload["title"], "BuddyIncidentRecord")
        self.assertIn("root_cause", payload["required"])
        self.assertIn("prevention", payload["required"])


if __name__ == "__main__":
    unittest.main()
