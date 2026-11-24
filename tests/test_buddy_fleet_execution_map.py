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
            self.assertTrue(bot["canonical_owner_division"])
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
                self.assertTrue(plan["approved_source_categories"])
                self.assertTrue(set(plan["approved_source_categories"]).issubset(allowed))

    def test_all_ten_specialist_portfolios_have_five_distinct_bot_charters(self):
        charters = __import__("json").loads(CHARTERS.read_text(encoding="utf-8"))
        self.assertEqual(len(charters["portfolios"]), 10)
        domains = [row["unique_domain"] for row in charters["portfolios"]]
        self.assertEqual(len(domains), len(set(domains)))
        all_scopes = []
        for portfolio in charters["portfolios"]:
            self.assertTrue(portfolio["mission"])
            self.assertTrue(portfolio["collaborators"])
            self.assertEqual(len(portfolio["bots"]), 5)
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
        self.assertEqual(len(supplemental), 50)
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
