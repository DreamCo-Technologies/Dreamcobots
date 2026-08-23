from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BuddyOSContractTests(unittest.TestCase):
    def test_task_envelope_is_valid_json_schema_shape(self):
        path = ROOT / "buddy_os/tasks/task_envelope.schema.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["title"], "BuddyTaskEnvelope")
        self.assertEqual(payload["required"], ["task", "purpose", "output_format"])
        self.assertIn("autonomous", payload["properties"]["mode"]["enum"])
        self.assertIn("critical", payload["properties"]["risk_level"]["enum"])

    def test_runtime_map_points_at_real_existing_components(self):
        manifest = (ROOT / "buddy_os/integration/runtime_map.yaml").read_text(encoding="utf-8")
        for path in (
            "server/fleet-runtime.ts",
            "dreamco_platform/automation/task_runner.py",
            "server/buddy-model-policy.ts",
            "tools/buddy_local_bridge.py",
            "tools/buddy_cli.py",
            "website/buddy-command-center.html",
            "website/buddy-command-center.js",
            "config/buddy-connector-registry.json",
            ".github/workflows/dreamco-control-center.yml",
            ".github/workflows/buddy-actions-test-lab.yml",
        ):
            self.assertTrue((ROOT / path).exists(), path)
            self.assertIn(path, manifest)

    def test_bot_and_dashboard_registries_have_governance_boundaries(self):
        bots = (ROOT / "buddy_os/registry/bot_registry.yaml").read_text(encoding="utf-8")
        dashboards = (ROOT / "buddy_os/dashboards/dashboard_registry.yaml").read_text(encoding="utf-8")
        self.assertIn("require_health_check_before_start: true", bots)
        self.assertIn("require_permission_for_deploy: true", bots)
        self.assertIn("require_confirmation_for_destructive_actions: true", bots)
        self.assertIn("health_indicator: required", dashboards)
        self.assertIn("backend_status: required", dashboards)

    def test_debate_protocol_blocks_unresolved_high_risk_execution(self):
        debate = (ROOT / "buddy_os/debate/debate_protocol.yaml").read_text(encoding="utf-8")
        self.assertIn("independent_first_pass: true", debate)
        self.assertIn("evidence_over_assertion: true", debate)
        self.assertIn("unresolved_high_risk_issue_blocks_autonomous_execution: true", debate)
        self.assertIn("final_decision_must_include_execution_plan: true", debate)

    def test_execution_policy_is_approval_gated(self):
        policy = (ROOT / "buddy_os/execution/policy.yaml").read_text(encoding="utf-8")
        self.assertIn("default_mode: supervised", policy)
        self.assertIn("- deploy", policy)
        self.assertIn("- destructive_command", policy)
        self.assertIn("never_bypass_repository_governance: true", policy)

    def test_memory_policy_never_persists_secrets(self):
        memory = (ROOT / "buddy_os/memory/memory_contract.yaml").read_text(encoding="utf-8")
        self.assertIn("secrets: never_persist", memory)
        self.assertIn("credentials: never_persist", memory)
        self.assertIn("provenance_required: true", memory)

    def test_mcp_registry_never_stores_secrets(self):
        registry = (ROOT / "buddy_os/registry/mcp_registry.yaml").read_text(encoding="utf-8")
        self.assertIn("audit_tool_calls: true", registry)
        self.assertIn("never_store_secrets: true", registry)


if __name__ == "__main__":
    unittest.main()
