import unittest
from pathlib import Path

from tools.build_buddy_fleet_execution_map import CHARTERS, build


class BuddyFleetExecutionMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = build()
        cls.bots = cls.payload["bots"]

    def test_full_generated_manifest_is_covered(self):
        self.assertEqual(self.payload["counts"]["manifest_bot_profiles"], len(self.bots))
        self.assertGreaterEqual(len(self.bots), 1051)
        self.assertEqual(len({row["slug"] for row in self.bots}), len(self.bots))

    def test_every_bot_has_buddy_and_division_route(self):
        for bot in self.bots:
            self.assertEqual(bot["buddy_execution"]["orchestrator"], "Buddy")
            self.assertTrue(bot["buddy_execution"]["queue"])
            self.assertTrue(bot["buddy_execution"]["learning_route"])
            self.assertTrue(bot["buddy_execution"]["benchmark_route"])
            self.assertTrue(bot["division_route"]["primary_masterbot_id"])
            if bot["division_route"]["status"] == "proposed_shared_teammate_platform_route":
                self.assertTrue(bot["canonical_owner_division"])
                self.assertEqual(bot["shared_workforce_group"], "GrokTeammates")
            else:
                self.assertTrue(bot["canonical_owner_division"])
            if bot["division_route"]["status"] != "discovery_review_required":
                self.assertEqual(bot["division_route"]["route_scope"], "non_privileged_planning_only_until_owner_approval")
                self.assertTrue(bot["division_route"]["owner_approval_required_for_privileged_work"])
            self.assertEqual(bot["execution_plan_status"], "plan_only_not_runtime_proof")

    def test_every_revenue_candidate_has_a_complete_non_live_execution_plan(self):
        candidates = [bot for bot in self.bots if bot["commercial_plan"].get("candidate")]
        self.assertGreater(len(candidates), 0)
        required = {
            "revenue_lane", "approved_source_categories", "verified_revenue_event_types", "workflow",
            "revenue_event_required", "forecast_is_not_revenue",
            "live_status", "live_actions_allowed", "owner_live_enable_required",
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
        import json
        from tools.build_buddy_fleet_execution_map import OPPORTUNITY_SOURCES
        allowed = set(json.loads(OPPORTUNITY_SOURCES.read_text(encoding="utf-8"))["categories"])
        for bot in self.bots:
            plan = bot["commercial_plan"]
            if plan.get("candidate"):
                self.assertIn(plan["approved_source_category"], allowed)
                self.assertTrue(plan["approved_source_categories"])
                self.assertTrue(all(isinstance(source, str) and source.strip()
                                    for source in plan["approved_source_categories"]))

    def test_all_eleven_specialist_portfolios_have_distinct_bot_charters(self):
        charters = __import__("json").loads(CHARTERS.read_text(encoding="utf-8"))
        self.assertEqual(len(charters["portfolios"]), 11)
        domains = [row["unique_domain"] for row in charters["portfolios"]]
        self.assertEqual(len(domains), len(set(domains)))
        all_scopes = []
        for portfolio in charters["portfolios"]:
            self.assertTrue(portfolio["mission"])
            self.assertTrue(portfolio["collaborators"])
            self.assertEqual(len(portfolio["bots"]), 19 if portfolio["portfolio"] == "Dream3D" else 5)
            slugs = [bot[0] for bot in portfolio["bots"]]
            self.assertEqual(len(slugs), len(set(slugs)))
            for bot in portfolio["bots"]:
                self.assertGreaterEqual(len(bot[2]), 4)
                self.assertTrue(bot[1])
                self.assertTrue(bot[3])
                self.assertTrue(bot[4])
                self.assertTrue(bot[5])
                all_scopes.extend(bot[2])
        normalized = [item.casefold().strip() for item in all_scopes]
        self.assertEqual(len(normalized), len(set(normalized)))

    def test_supplemental_bots_keep_identity_but_route_to_canonical_owner(self):
        supplemental = [bot for bot in self.bots if bot["supplemental_portfolio"]]
        self.assertEqual(len(supplemental), 69)
        for bot in supplemental:
            self.assertNotEqual(bot["source_division"], bot["canonical_owner_division"])
            self.assertTrue(bot["specialist_capability_domain"])
            self.assertTrue(bot["specialist_bot_scope"])
            self.assertEqual(bot["specialist_bot_scope"]["exact_capability_overlap_with_canonical_owner"], [])

    def test_all_supplemental_specialists_have_distinct_commercial_routes(self):
        supplemental = [bot for bot in self.bots if bot["supplemental_portfolio"]]
        self.assertEqual(len(supplemental), 50)
        for bot in supplemental:
            plan = bot["commercial_plan"]
            self.assertTrue(plan.get("candidate"), bot["slug"])
            self.assertTrue(plan.get("revenue_lane"), bot["slug"])
            self.assertTrue(plan.get("verified_revenue_event_types"), bot["slug"])
            self.assertFalse(plan["live_actions_allowed"])

    def test_45_domain_masterbot_routes_are_explicitly_proposed_not_privileged(self):
        self.assertEqual(self.payload["counts"]["canonical_business_divisions"], 45)
        self.assertEqual(self.payload["counts"]["proposed_domain_masterbot_matches"], 1232)
        domain_bots = [bot for bot in self.bots if bot["division_route"]["status"] == "proposed_domain_masterbot_match_requires_owner_review"]
        self.assertEqual(len(domain_bots), 1232)
        self.assertTrue(all(bot["division_route"]["primary_domain_owner"] for bot in domain_bots))
        self.assertTrue(all(bot["division_route"]["owner_approval_required_for_privileged_work"] for bot in domain_bots))

    def test_112_grok_teammates_are_shared_workers_with_platform_masterbot_routes(self):
        teammates = [bot for bot in self.bots if bot["shared_workforce_group"] == "GrokTeammates"]
        self.assertEqual(len(teammates), 112)
        self.assertEqual(self.payload["counts"]["shared_teammate_profiles"], 112)
        for bot in teammates:
            self.assertEqual(bot["division_route"]["status"], "proposed_domain_masterbot_match_requires_owner_review")
            self.assertEqual(bot["division_route"]["route_scope"], "non_privileged_planning_only_until_owner_approval")
            self.assertIn(bot["division_route"]["primary_masterbot_id"], range(1, 46))
            self.assertIn(bot["division_route"]["shared_teammate_masterbot_id"], range(46, 66))
            self.assertTrue(bot["canonical_owner_division"])
            self.assertTrue(bot["teammate_lane_route"]["description"])
            self.assertEqual(bot["teammate_lane_route"]["shared_masterbot_id"], bot["division_route"]["shared_teammate_masterbot_id"])
            self.assertEqual(len(bot["source_paths"]), 1)
            self.assertTrue(bot["source_paths"][0].startswith("config/bots/teammate-lanes.json#"))

    def test_threejs_profiles_are_assigned_to_dream3d_not_left_unassigned(self):
        threejs = [row for row in self.bots if row["slug"].startswith("threejs-")]
        self.assertEqual(len(threejs), 19)
        self.assertTrue(all(row["source_division"] == "UNASSIGNED" for row in threejs))
        self.assertTrue(all(row["supplemental_portfolio"] == "Dream3D" for row in threejs))
        self.assertTrue(all(row["canonical_owner_division"] == "DreamCodeLab" for row in threejs))
        self.assertTrue(all(row["specialist_bot_scope"] for row in threejs))
        self.assertEqual(self.payload["counts"]["threejs_profiles_routed_to_dream3d"], 19)
        self.assertEqual(self.payload["counts"]["unresolved_owner_count"], 0)
        self.assertEqual(self.payload["division_review_queue"], [])

    def test_all_money_os_registry_entries_have_buddy_and_revenue_routes(self):
        catalog = self.payload["money_os_catalog"]
        self.assertEqual(len(catalog), 22)
        self.assertEqual(self.payload["counts"]["money_os_registry_entries"], 15)
        self.assertEqual(self.payload["counts"]["new_money_os_registry_entries"], 7)
        self.assertEqual(self.payload["counts"]["money_os_catalog_entries_with_buddy_routes"], 22)
        from tools.build_buddy_fleet_execution_map import OPPORTUNITY_SOURCES
        import json
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
            if entry["related_manifest_bot_slug"]:
                self.assertIn(entry["related_manifest_bot_slug"], {bot["slug"] for bot in self.bots})

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
