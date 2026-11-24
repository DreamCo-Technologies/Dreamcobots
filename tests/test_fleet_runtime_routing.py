import unittest

from buddy.fleet_runtime.contract import expand
from buddy.fleet_runtime.executor import FleetExecutor
from buddy.fleet_runtime.routing import resolve_route
from tools.generate_bot_manifests import build


class BuddyFleetRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.collection = build()
        cls.bots = cls.collection["bots"]
        cls.by_slug = {row["slug"]: row for row in cls.bots}

    def test_all_manifest_profiles_resolve_to_a_canonical_domain_masterbot(self):
        self.assertEqual(len(self.bots), 1232)
        domains = {
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
        self.assertEqual({row["division"] for row in self.bots}, domains)
        for compact in self.bots:
            self.assertIn(compact["primary_masterbot_id"], range(1, 46))
            self.assertEqual(compact["division_route_status"], "proposed_domain_masterbot_match_requires_owner_review")
            self.assertTrue(compact["owner_approval_required"])
            self.assertEqual(compact["shared_platform_masterbot_ids"], list(range(46, 66)))

    def test_all_112_grok_teammates_keep_shared_route_and_gain_primary_owner(self):
        teammates = [row for row in self.bots if row.get("shared_workforce_group") == "GrokTeammates"]
        self.assertEqual(len(teammates), 112)
        for row in teammates:
            self.assertIn(row["division"], {"DreamAIInfra", "DreamEducation", "DreamOps", "DreamCodeLab",
                "CommandCore", "DreamContent", "DreamData", "DreamBizLaunch", "DreamProtection",
                "DreamMarket", "DreamSalesPro", "DreamLegal", "DreamDecision", "GameTitan", "DreamAutomation"})
            self.assertIn(row["primary_masterbot_id"], range(1, 46))
            self.assertIn(row["shared_teammate_masterbot_id"], range(46, 66))
            self.assertTrue(row["shared_teammate_masterbot_route"])

    def test_all_69_specialist_profiles_are_owned_by_canonical_divisions(self):
        specialists = [row for row in self.bots if row.get("supplemental_portfolio")]
        self.assertEqual(len(specialists), 69)
        self.assertEqual(sum(1 for row in specialists if row["supplemental_portfolio"] == "Dream3D"), 19)
        self.assertTrue(all(row["division"] in {bot["division"] for bot in self.bots} for row in specialists))
        self.assertTrue(all(row["specialist_capability_domain"] for row in specialists))

    def test_threejs_profiles_have_specialist_capabilities_in_runtime_content(self):
        for slug in ("threejs-addons", "threejs-animation", "threejs-renderers", "threejs-tsl"):
            compact = self.by_slug[slug]
            full = expand(compact, self.collection)
            self.assertEqual(full["division"], "DreamCodeLab")
            self.assertEqual(full["supplemental_portfolio"], "Dream3D")
            self.assertGreaterEqual(len(full["capabilities"]), 5)
            self.assertTrue(any("Three.js" in cap or "threejs" in cap.lower() for cap in full["capabilities"]))

    def test_runtime_executor_exposes_buddy_route_in_result_and_evidence(self):
        executor = FleetExecutor(collection=self.collection, customizations={})
        result = executor.run("threejs-addons", {
            "objective": "Plan a sandbox-only Three.js addon compatibility check"
        })
        self.assertIn("routing", result)
        self.assertTrue(result["routing"]["route_valid"])
        self.assertEqual(result["routing"]["canonical_division"], "DreamCodeLab")
        self.assertEqual(result["routing"]["supplemental_portfolio"], "Dream3D")
        self.assertTrue(result["routing"]["owner_approval_required"])
        self.assertFalse(result["routing"]["privileged_execution_enabled"])
        self.assertEqual(result["evidence"]["routing"], result["routing"])

    def test_shared_teammate_runtime_route_has_primary_and_shared_masterbots(self):
        executor = FleetExecutor(collection=self.collection, customizations={})
        result = executor.run("grok-lane-500-model-bench-runner", {
            "objective": "Prepare a sandbox-only benchmark plan for a model evaluation"
        })
        route = result["routing"]
        self.assertTrue(route["route_valid"])
        self.assertEqual(route["canonical_division"], "DreamAIInfra")
        self.assertEqual(route["primary_masterbot_id"], 4)
        self.assertEqual(route["shared_teammate_masterbot_id"], 47)
        self.assertFalse(route["privileged_execution_enabled"])

    def test_invalid_masterbot_route_fails_closed(self):
        route = resolve_route({
            "slug": "bad-route", "division": "DreamCodeLab", "primary_masterbot_id": 65,
            "division_route_status": "proposed_domain_masterbot_match_requires_owner_review",
        })
        self.assertFalse(route["route_valid"])
        self.assertEqual(route["route_status"], "blocked_unmapped_or_inconsistent_route")
        self.assertFalse(route["privileged_execution_enabled"])


if __name__ == "__main__":
    unittest.main()
