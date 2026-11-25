import json
import unittest

from tools.build_buddy_fleet_execution_map import CHARTERS, build
from tools.generate_bot_manifests import main as generate_manifests


class BuddyFleetExecutionMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if generate_manifests([]) != 0:
            raise RuntimeError("could not generate current bot manifests")
        cls.payload = build()
        cls.bots = cls.payload["bots"]
        cls.by_slug = {row["slug"]: row for row in cls.bots}

    def test_full_generated_manifest_is_covered(self):
        self.assertEqual(self.payload["counts"]["manifest_bot_profiles"], len(self.bots))
        self.assertEqual(len(self.bots), 1232)
        self.assertEqual(len({row["slug"] for row in self.bots}), len(self.bots))

    def test_every_bot_has_a_buddy_plan_and_fail_closed_route_metadata(self):
        for bot in self.bots:
            self.assertEqual(bot["buddy_execution"]["orchestrator"], "Buddy")
            self.assertTrue(bot["buddy_execution"]["queue"])
            self.assertTrue(bot["buddy_execution"]["learning_route"])
            self.assertTrue(bot["buddy_execution"]["benchmark_route"])
            route = bot["division_route"]
            self.assertTrue(route["owner_approval_required_for_remap"])
            self.assertTrue(route["owner_approval_required_for_privileged_work"])
            self.assertFalse(route["privileged_execution_enabled"])
            self.assertEqual(route["shared_platform_masterbot_ids"], list(range(46, 66)))
            if route["status"] == "supplemental_domain_unassigned_pending_owner_review":
                self.assertIsNone(route["primary_masterbot_id"])
                self.assertTrue(route["proposed_domain_owner"])
                self.assertTrue(route["proposed_primary_masterbot_id"])
                self.assertEqual(route["route_scope"], "discovery_only")
            else:
                self.assertTrue(route["primary_masterbot_id"])
            self.assertEqual(bot["execution_plan_status"], "plan_only_not_runtime_proof")

    def test_ten_supplemental_domains_remain_unassigned_with_proposals_only(self):
        supplemental = [bot for bot in self.bots if bot["division_route"]["status"] == "supplemental_domain_unassigned_pending_owner_review"]
        self.assertEqual(len(supplemental), 50)
        self.assertEqual(len({bot["execution_division"] for bot in supplemental}), 10)
        self.assertEqual(self.payload["counts"]["unassigned_supplemental_domain_profiles"], 10)
        self.assertEqual(self.payload["counts"]["unassigned_supplemental_bot_profiles"], 50)
        self.assertEqual(self.payload["counts"]["unresolved_owner_count"], 50)
        for bot in supplemental:
            self.assertIsNone(bot["canonical_owner_division"])
            self.assertEqual(bot["proposed_owner_division"], bot["division_route"]["proposed_domain_owner"])
            self.assertIn(bot["proposed_owner_division"], {
                "DreamSalesPro", "DreamProServices", "DreamAIInfra", "DreamBizLaunch",
                "DreamCodeLab", "DreamLegal", "DreamAutomation", "DreamContent", "DreamTransport",
            })
            self.assertIsNone(bot["division_route"]["primary_masterbot_id"])
            self.assertIn(bot["division_route"]["proposed_primary_masterbot_id"], range(1, 46))

    def test_45_core_and_112_teammate_routes_are_proposals_not_privilege(self):
        self.assertEqual(self.payload["counts"]["canonical_business_divisions"], 45)
        core_routes = [bot for bot in self.bots if bot["division_route"]["status"] == "proposed_domain_masterbot_match_requires_owner_review"]
        self.assertEqual(self.payload["counts"]["proposed_domain_masterbot_matches"], len(core_routes))
        self.assertTrue(all(bot["division_route"]["primary_masterbot_id"] in range(1, 46) for bot in core_routes))
        self.assertTrue(all(bot["division_route"]["owner_approval_required_for_privileged_work"] for bot in core_routes))
        teammates = [bot for bot in self.bots if bot["shared_workforce_group"] == "GrokTeammates"]
        self.assertEqual(len(teammates), 112)
        self.assertEqual(self.payload["counts"]["shared_teammate_profiles"], 112)
        for bot in teammates:
            self.assertIn(bot["division_route"]["primary_masterbot_id"], range(1, 46))
            self.assertIn(bot["division_route"]["shared_teammate_masterbot_id"], range(46, 66))
            self.assertTrue(bot["canonical_owner_division"])
            self.assertTrue(bot["teammate_lane_route"]["description"])
            self.assertEqual(bot["teammate_lane_route"]["shared_masterbot_id"], bot["division_route"]["shared_teammate_masterbot_id"])

    def test_ten_supplemental_domains_and_dream3d_subportfolio_are_distinct(self):
        charters = json.loads(CHARTERS.read_text(encoding="utf-8"))
        supplemental = [row for row in charters["portfolios"] if row["classification"] == "supplemental_domain_profile"]
        dream3d = [row for row in charters["portfolios"] if row["portfolio"] == "Dream3D"]
        self.assertEqual(len(supplemental), 10)
        self.assertEqual(len(dream3d), 1)
        self.assertEqual(dream3d[0]["classification"], "supplemental_portfolio")
        for portfolio in supplemental + dream3d:
            self.assertTrue(portfolio["owner_approval_required"])
            self.assertTrue(portfolio["owner"])
        self.assertEqual(self.payload["counts"]["supplemental_domain_profiles"], 10)
        self.assertEqual(self.payload["counts"]["specialist_subportfolios"], 1)

    def test_all_69_specialist_profiles_have_distinct_capability_charters(self):
        specialists = [bot for bot in self.bots if bot["supplemental_portfolio"]]
        self.assertEqual(len(specialists), 69)
        self.assertEqual(sum(1 for bot in specialists if bot["supplemental_portfolio"] == "Dream3D"), 19)
        for bot in specialists:
            self.assertTrue(bot["specialist_capability_domain"])
            self.assertTrue(bot["specialist_bot_scope"])
            self.assertEqual(bot["specialist_bot_scope"]["exact_capability_overlap_with_canonical_owner"], [])

    def test_all_supplemental_specialists_have_distinct_non_live_commercial_routes(self):
        supplemental = [bot for bot in self.bots if bot["supplemental_portfolio"]]
        self.assertEqual(len(supplemental), 69)
        for bot in supplemental:
            plan = bot["commercial_plan"]
            self.assertTrue(plan.get("candidate"), bot["slug"])
            self.assertTrue(plan.get("revenue_lane"), bot["slug"])
            self.assertTrue(plan.get("verified_revenue_event_types"), bot["slug"])
            self.assertFalse(plan["live_actions_allowed"])

    def test_dream3d_profiles_are_proposed_under_dreamcodelab(self):
        threejs = [row for row in self.bots if row["slug"].startswith("threejs-")]
        self.assertEqual(len(threejs), 19)
        self.assertEqual(self.payload["counts"]["threejs_profiles_proposed_for_dream3d"], 19)
        for bot in threejs:
            self.assertEqual(bot["execution_division"], "Dream3D")
            self.assertEqual(bot["canonical_owner_division"], "DreamCodeLab")
            self.assertEqual(bot["division_route"]["status"], "proposed_specialist_subportfolio_route_pending_owner_review")
            self.assertTrue(bot["division_route"]["owner_approval_required_for_privileged_work"])
            self.assertFalse(bot["division_route"]["privileged_execution_enabled"])

    def test_owner_review_queue_groups_divisions_not_individual_bots(self):
        queue = self.payload["division_review_queue"]
        self.assertEqual(len(queue), 11)
        self.assertEqual(len({row["division_or_portfolio"] for row in queue}), 11)
        self.assertEqual(self.payload["counts"]["owner_review_queue_entries"], 11)
        self.assertEqual(sum(row["bot_count"] for row in queue), 50 + 19)

    def test_every_revenue_candidate_has_a_complete_non_live_execution_plan(self):
        candidates = [bot for bot in self.bots if bot["commercial_plan"].get("candidate")]
        self.assertGreater(len(candidates), 0)
        required = {
            "revenue_lane", "approved_source_categories", "verified_revenue_event_types", "workflow",
            "revenue_event_required", "forecast_is_not_revenue", "live_status", "live_actions_allowed",
            "owner_live_enable_required",
        }
        for bot in candidates:
            plan = bot["commercial_plan"]
            self.assertTrue(required.issubset(plan))
            self.assertTrue(plan["approved_source_categories"])
            self.assertGreaterEqual(len(plan["workflow"]), 8)
            self.assertTrue(plan["revenue_event_required"])
            self.assertTrue(plan["verified_revenue_event_types"])
            self.assertFalse(plan["live_actions_allowed"])
            self.assertTrue(plan["owner_live_enable_required"])

    def test_revenue_candidates_use_declared_authorized_source_categories(self):
        from tools.build_buddy_fleet_execution_map import OPPORTUNITY_SOURCES
        allowed = set(json.loads(OPPORTUNITY_SOURCES.read_text(encoding="utf-8"))["categories"])
        for bot in self.bots:
            plan = bot["commercial_plan"]
            if plan.get("candidate"):
                self.assertIn(plan["approved_source_category"], allowed)
                self.assertTrue(plan["approved_source_categories"])

    def test_all_money_os_registry_entries_have_buddy_and_revenue_routes(self):
        catalog = self.payload["money_os_catalog"]
        self.assertEqual(len(catalog), 22)
        self.assertEqual(self.payload["counts"]["money_os_registry_entries"], 15)
        self.assertEqual(self.payload["counts"]["new_money_os_registry_entries"], 7)
        self.assertEqual(self.payload["counts"]["money_os_catalog_entries_with_buddy_routes"], 22)
        from tools.build_buddy_fleet_execution_map import OPPORTUNITY_SOURCES
        allowed = set(json.loads(OPPORTUNITY_SOURCES.read_text(encoding="utf-8"))["categories"])
        for entry in catalog:
            self.assertTrue(entry["canonical_owner_division"])
            self.assertTrue(entry["primary_masterbot_id"])
            self.assertEqual(entry["buddy_orchestrator"], "Buddy")
            self.assertTrue(entry["buddy_queue"])
            self.assertTrue(entry["learning_route"])
            self.assertTrue(entry["benchmark_route"])
            plan = entry["revenue_plan"]
            self.assertIn(plan["approved_source_category"], allowed)
            self.assertTrue(plan["approved_source_types"])
            self.assertGreaterEqual(len(plan["workflow"]), 8)
            self.assertTrue(plan["verified_revenue_event_types"])
            self.assertTrue(plan["forecast_is_not_revenue"])
            self.assertFalse(plan["live_actions_allowed"])

    def test_all_bots_can_access_shared_platform_masterbots(self):
        expected = list(range(46, 66))
        for bot in self.bots:
            self.assertEqual(bot["division_route"]["shared_platform_masterbot_ids"], expected)

    def test_no_generated_plan_claims_live_revenue_or_training(self):
        self.assertEqual(self.payload["counts"]["live_enabled_bots"], 0)
        for bot in self.bots:
            self.assertFalse(bot["commercial_plan"]["live_actions_allowed"])
            self.assertEqual(bot["learning_status"], "curriculum_and_evidence_required_not_trained_by_generation")

    def test_duplicate_capability_groups_are_explicitly_review_only(self):
        for group in self.payload["duplicate_capability_groups"]:
            self.assertTrue(group["requires_review"])
            self.assertGreater(len(group["bot_slugs"]), 1)


if __name__ == "__main__":
    unittest.main()
