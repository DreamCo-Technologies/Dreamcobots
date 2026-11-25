import json
import unittest
from pathlib import Path

from buddy.fleet_runtime.contract import expand
from buddy.fleet_runtime.executor import FleetExecutor
from buddy.fleet_runtime.routing import resolve_route
from tools.generate_bot_manifests import build

ROOT = Path(__file__).resolve().parents[1]


class BuddyFleetRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.collection = build()
        cls.bots = cls.collection["bots"]
        cls.by_slug = {row["slug"]: row for row in cls.bots}
        cls.domains = {
            "CommandCore", "DreamAIInfra", "DreamAdmin", "DreamAgents", "DreamAgriculture",
            "DreamArts", "DreamAutomation", "DreamBizLaunch", "DreamCodeLab", "DreamConstruction",
            "DreamContent", "DreamCrypto", "DreamCustIntel", "DreamCyber", "DreamData", "DreamDecision",
            "DreamEducation", "DreamEmpire", "DreamEntFinance", "DreamFinance", "DreamFlow", "DreamFood",
            "DreamGlobal", "DreamHealth", "DreamInfluence", "DreamLegal", "DreamLoans", "DreamMaintenance",
            "DreamMarket", "DreamMilitary", "DreamOps", "DreamPayments", "DreamPersonalCare",
            "DreamPlanetary", "DreamProServices", "DreamProduction", "DreamProtection", "DreamRealEstate",
            "DreamRetail", "DreamSalesPro", "DreamScience", "DreamSocial", "DreamTrade", "DreamTransport",
            "GameTitan",
        }

    def test_all_profiles_keep_45_plus_10_plus_dream3d_and_shared_workforce_inventory(self):
        self.assertEqual(len(self.bots), 1232)
        charters = json.loads((ROOT / "config/supplemental-portfolio-capability-charters.json").read_text())
        portfolios = {row["portfolio"] for row in charters["portfolios"]}
        self.assertEqual(sum(1 for row in charters["portfolios"] if row["classification"] == "supplemental_domain_profile"), 10)
        self.assertEqual({row["division"] for row in self.bots}, self.domains | portfolios | {"GrokTeammates"})
        self.assertTrue(all(row["owner_approval_required"] for row in self.bots))
        self.assertTrue(all(row["shared_platform_masterbot_ids"] == list(range(46, 66)) for row in self.bots))

    def test_45_core_domain_routes_are_structural_proposals_not_authorization(self):
        core = [row for row in self.bots if row["division"] in self.domains]
        self.assertGreater(len(core), 0)
        for row in core:
            self.assertIn(row["primary_domain_owner"], self.domains)
            self.assertIn(row["primary_masterbot_id"], range(1, 46))
            self.assertEqual(row["division_route_status"], "proposed_domain_masterbot_match_requires_owner_review")
            route = resolve_route(row)
            self.assertTrue(route["route_valid"])
            self.assertEqual(route["route_status"], "proposed_core_route_pending_github_identity_attestation")
            self.assertTrue(route["github_identity_attestation_required"])
            self.assertFalse(route["privileged_execution_enabled"])
            self.assertFalse(route["live_external_actions_enabled"])
            self.assertFalse(route["training_execution_enabled"])

    def test_ten_supplemental_domain_profiles_remain_unassigned(self):
        supplemental = [row for row in self.bots if row.get("flags") and "supplemental_domain_unassigned_pending_owner_review" in row["flags"]]
        self.assertEqual(len({row["division"] for row in supplemental}), 10)
        self.assertEqual(len(supplemental), 50)
        for row in supplemental:
            self.assertIsNone(row["primary_domain_owner"])
            self.assertIsNone(row["primary_masterbot_id"])
            self.assertIn(row["proposed_domain_owner"], self.domains)
            self.assertIn(row["proposed_primary_masterbot_id"], range(1, 46))
            route = resolve_route(row)
            self.assertFalse(route["route_valid"])
            self.assertIsNone(route["primary_masterbot_id"])
            self.assertEqual(route["route_status"], "supplemental_domain_unassigned_pending_owner_review")
            self.assertEqual(route["proposed_domain_owner"], row["proposed_domain_owner"])
            self.assertFalse(route["privileged_execution_enabled"])

    def test_dream3d_is_a_specialist_subportfolio_under_dreamcodelab(self):
        threejs = [row for row in self.bots if row["slug"].startswith("threejs-")]
        self.assertEqual(len(threejs), 19)
        for compact in threejs:
            self.assertEqual(compact["division"], "Dream3D")
            self.assertEqual(compact["source_division"], "Dream3D")
            self.assertEqual(compact["primary_domain_owner"], "DreamCodeLab")
            self.assertEqual(compact["supplemental_portfolio"], "Dream3D")
            full = expand(compact, self.collection)
            self.assertGreaterEqual(len(full["capabilities"]), 5)
            self.assertTrue(any("Three.js" in cap or "threejs" in cap.lower() for cap in full["capabilities"]))
            route = resolve_route(full)
            self.assertTrue(route["route_valid"])
            self.assertEqual(route["canonical_domain_owner"], "DreamCodeLab")
            self.assertEqual(route["route_status"], "proposed_specialist_subportfolio_route_pending_owner_review")
            self.assertFalse(route["privileged_execution_enabled"])

    def test_all_112_grok_teammates_have_core_owner_and_shared_platform_route(self):
        teammates = [row for row in self.bots if row.get("shared_workforce_group") == "GrokTeammates"]
        self.assertEqual(len(teammates), 112)
        for row in teammates:
            self.assertEqual(row["division"], "GrokTeammates")
            self.assertEqual(row["source_division"], "GrokTeammates")
            self.assertIn(row["primary_domain_owner"], self.domains)
            self.assertIn(row["primary_masterbot_id"], range(1, 46))
            self.assertIn(row["shared_teammate_masterbot_id"], range(46, 66))
            self.assertTrue(row["shared_teammate_masterbot_route"])
            route = resolve_route(row)
            self.assertTrue(route["route_valid"])
            self.assertEqual(route["shared_teammate_masterbot_id"], row["shared_teammate_masterbot_id"])
            self.assertTrue(route["shared_route_valid"])
            self.assertNotEqual(route["primary_masterbot_id"], route["shared_teammate_masterbot_id"])

    def test_executor_attaches_route_to_output_and_evidence(self):
        executor = FleetExecutor(collection=self.collection, customizations={})
        result = executor.run("threejs-addons", {"objective": "Plan a sandbox-only Three.js addon compatibility check"})
        self.assertIn("routing", result)
        self.assertEqual(result["evidence"]["routing"], result["routing"])
        self.assertEqual(result["routing"]["canonical_domain_owner"], "DreamCodeLab")
        self.assertTrue(result["routing"]["owner_approval_required"])
        self.assertFalse(result["routing"]["privileged_execution_enabled"])

    def test_supplemental_executor_result_does_not_promote_proposed_owner(self):
        executor = FleetExecutor(collection=self.collection, customizations={})
        result = executor.run("offer-researcher", {"objective": "Plan an offline affiliate-link audit"})
        route = result["routing"]
        self.assertFalse(route["route_valid"])
        self.assertIsNone(route["primary_masterbot_id"])
        self.assertEqual(route["route_status"], "supplemental_domain_unassigned_pending_owner_review")
        self.assertFalse(route["privileged_execution_enabled"])

    def test_shared_masterbot_cannot_be_primary_domain_owner(self):
        route = resolve_route({"division": "DreamAIInfra", "primary_domain_owner": "DreamAIInfra", "primary_masterbot_id": 47})
        self.assertFalse(route["route_valid"])
        self.assertIsNone(route["primary_masterbot_id"])
        self.assertEqual(route["route_status"], "blocked_inconsistent_primary_masterbot")

    def test_malformed_primary_id_fails_closed(self):
        for value in (True, "not-an-id"):
            route = resolve_route({"division": "DreamAIInfra", "primary_domain_owner": "DreamAIInfra", "primary_masterbot_id": value})
            self.assertFalse(route["route_valid"])
            self.assertIsNone(route["primary_masterbot_id"])
            self.assertEqual(route["route_status"], "blocked_invalid_primary_masterbot_id")

    def test_invalid_shared_collaborator_does_not_corrupt_valid_primary_route(self):
        route = resolve_route({"division": "DreamAIInfra", "primary_domain_owner": "DreamAIInfra", "primary_masterbot_id": 4, "shared_teammate_masterbot_id": 4})
        self.assertTrue(route["route_valid"])
        self.assertFalse(route["shared_route_valid"])
        self.assertEqual(route["shared_route_status"], "blocked_invalid_shared_masterbot_route")

    def test_unknown_domain_fails_closed(self):
        route = resolve_route({"division": "UnknownDivision"})
        self.assertFalse(route["route_valid"])
        self.assertIsNone(route["primary_masterbot_id"])
        self.assertEqual(route["route_status"], "blocked_domain_not_in_canonical_crosswalk")


if __name__ == "__main__":
    unittest.main()
