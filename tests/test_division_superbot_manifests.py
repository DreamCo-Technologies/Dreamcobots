"""Source-backed Division Superbot manifest generation tests."""
import unittest

from tools.build_division_superbot_manifests import build_division_manifest, load_domain_profiles, ROOT


class DivisionSuperbotManifestTests(unittest.TestCase):
    def setUp(self):
        self.division = {"id": "dreamfinance", "division": "DreamFinance", "cluster": "money"}
        self.canonical = [{
            "slug": "algo-trading",
            "source_path": "App_bots/DreamFinance.json",
            "capabilities": ["Backtesting", "Risk sizing"],
            "toolsNeeded": ["Sandbox harness", "Approval gate"],
            "api": ["Broker API"],
            "benchmarks": [{"label": "Sandbox pass rate", "target": "100%", "current": "unmeasured"}],
            "tasks": [{"id": "test", "title": "Run sandbox checks", "status": "todo"}],
            "targetUsers": "Institutional traders",
            "revenueModel": "SaaS subscription",
            "route": {"primary_domain_owner": "DreamFinance"},
        }]
        self.proposed = [{
            "slug": "supplemental-trader",
            "source_path": "App_bots/Dream3D.json",
            "capabilities": ["Portfolio visualization"],
            "route": {"proposed_domain_owner": "DreamFinance"},
        }]
        self.domain = {
            "purpose": "Support finance workflows with governed evidence.",
            "serves": ["traders", "finance teams"],
            "outcome": "Better risk-adjusted decisions.",
            "boundary": "No trades or transfers without approval.",
            "focusAreas": ["portfolio risk", "backtesting"],
        }
        self.model = {
            "model_id": "dreamco.division.dreamfinance",
            "model_version": "0.0.0",
            "lifecycle_state": "planned",
            "training": {"checkpoint": None, "checkpoint_sha256": None},
            "evaluation": {"last_result": None},
            "serving": {"endpoint": None},
            "release_evidence": {"model_card": None},
        }
        self.policy = {
            "status": "PLAN_DEFINED_NOT_EXECUTED",
            "student_size": {"initial_parameter_target": 25000000},
            "tokenizer": {"default_mode": "shared_per_base_model"},
            "training": {"strategy": "SFT plus LoRA/QLoRA by default"},
        }

    def test_declared_capabilities_are_source_linked_and_not_marked_tested(self):
        result = build_division_manifest(self.division, self.canonical, self.proposed, [], self.domain, self.model, self.policy)
        self.assertEqual([row["name"] for row in result["capabilities"]], ["Backtesting", "Risk sizing"])
        self.assertTrue(all(row["source_path"] == "App_bots/DreamFinance.json" for row in result["capabilities"]))
        self.assertTrue(all(row["evidence_status"] == "declared_in_source_profile_not_runtime_verified" for row in result["capabilities"]))

    def test_proposed_owner_capabilities_never_enter_canonical_inventory(self):
        result = build_division_manifest(self.division, self.canonical, self.proposed, [], self.domain, self.model, self.policy)
        self.assertEqual([row["name"] for row in result["proposedCapabilities"]], ["Portfolio visualization"])
        self.assertEqual(result["migration"]["proposedProfilesPendingOwnerReview"], ["supplemental-trader"])
        self.assertEqual(result["status"], "source_mapped_needs_validation")

    def test_tools_connectors_and_benchmarks_are_truthfully_unverified(self):
        result = build_division_manifest(self.division, self.canonical, self.proposed, [], self.domain, self.model, self.policy)
        self.assertTrue(all(row["status"] == "required_not_configured_or_verified" for row in result["tools"]))
        self.assertTrue(all(row["status"] == "candidate_not_connected" for row in result["connectors"]))
        self.assertTrue(all(row["status"] == "declared_target_not_measured" for row in result["benchmarks"]))
        self.assertEqual(result["commercial"]["status"], "source_declared_not_financially_verified")

    def test_missing_operational_contracts_and_connector_gaps_are_explicit(self):
        result = build_division_manifest(self.division, [], [], [], self.domain, None, self.policy)
        areas = {row["area"] for row in result["gaps"]}
        self.assertIn("user_jobs", areas)
        self.assertIn("workflows", areas)
        self.assertIn("ownership", areas)
        self.assertIn("connectors", areas)
        self.assertIn("benchmarks", areas)
        self.assertIn("model_training", areas)
        self.assertEqual(result["status"], "inventory_only_needs_owner_review")
        self.assertEqual(result["capabilities"], [])

    def test_domain_contract_and_model_training_plan_are_attached(self):
        result = build_division_manifest(self.division, self.canonical, [], [], self.domain, self.model, self.policy)
        self.assertEqual(result["mission"], self.domain["purpose"])
        self.assertEqual(result["domainProfile"]["serves"], ["traders", "finance teams"])
        self.assertEqual(result["candidateUserJobAreas"][0]["status"], "hypothesis_not_validated")
        self.assertEqual(result["modelTraining"]["status"], "planned")
        self.assertEqual(result["modelTraining"]["parameterTarget"], 25000000)
        self.assertEqual(result["modelTraining"]["tokenizerMode"], "shared_per_base_model")

    def test_domain_contract_parser_covers_all_canonical_division_profiles(self):
        profiles = load_domain_profiles(ROOT / "shared" / "division-production-contract.ts")
        self.assertGreaterEqual(len(profiles), 45)
        self.assertIn("DreamFinance", profiles)
        self.assertTrue(profiles["DreamFinance"]["purpose"])
        self.assertTrue(profiles["DreamFinance"]["focusAreas"])

    def test_duplicate_tool_names_preserve_each_bot_source(self):
        second = dict(self.canonical[0], slug="portfolio-risk", source_path="App_bots/DreamFinance.json")
        second["toolsNeeded"] = ["Sandbox harness"]
        result = build_division_manifest(self.division, self.canonical + [second], [], [], self.domain, self.model, self.policy)
        matching = [row for row in result["tools"] if row["name"] == "Sandbox harness"]
        self.assertEqual({row["source_bot_slug"] for row in matching}, {"algo-trading", "portfolio-risk"})

    def test_explicit_user_jobs_and_workflows_are_preserved_with_provenance(self):
        profile = dict(self.canonical[0], userJobs=[{"job": "Reduce manual reconciliation"}], workflows=[{"id": "weekly-review"}])
        result = build_division_manifest(self.division, [profile], [], [], self.domain, self.model, self.policy)
        self.assertEqual(result["userJobs"][0]["source_bot_slug"], "algo-trading")
        self.assertEqual(result["workflows"][0]["source_path"], "App_bots/DreamFinance.json")


if __name__ == "__main__":
    unittest.main()
