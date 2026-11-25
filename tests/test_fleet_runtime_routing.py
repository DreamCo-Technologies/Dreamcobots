import json
import unittest
from pathlib import Path

from buddy.fleet_runtime.executor import FleetExecutor
from buddy.fleet_runtime.routing import resolve_route

ROOT = Path(__file__).resolve().parents[1]


class GovernedFleetRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / "config/masterbot-65-registry.json").read_text(encoding="utf-8"))
        cls.crosswalk = json.loads((ROOT / "config/generated/masterbot-55-domain-crosswalk.json").read_text(encoding="utf-8"))
        cls.approval = json.loads((ROOT / "config/review/division-owner-conversation-approval.json").read_text(encoding="utf-8"))

    def test_all_45_core_domains_get_only_proposed_routes(self):
        core = [row for row in self.crosswalk["domains"] if row["mapping_status"] == "proposed_exact_name_match"]
        self.assertEqual(len(core), 45)
        for row in core:
            with self.subTest(domain=row["domain_name"]):
                route = resolve_route({"division": row["domain_name"]})
                self.assertTrue(route["route_valid"])
                self.assertEqual(route["primary_masterbot_id"], row["masterbot_id"])
                self.assertEqual(route["route_status"], "proposed_exact_name_match_pending_owner_review")
                self.assertTrue(route["owner_approval_required"])
                self.assertFalse(route["dispatch_allowed"])
                self.assertFalse(route["privileged_execution_enabled"])
                self.assertFalse(route["model_training_enabled"])

    def test_all_10_supplemental_domains_remain_proposed_collaborators(self):
        supplemental = [row for row in self.crosswalk["domains"] if row["mapping_status"] == "unresolved"]
        self.assertEqual(len(supplemental), 10)
        proposals = {row["domain_id"]: row for row in self.approval["supplemental_collaborators"]}
        self.assertEqual(set(proposals), {row["domain_id"] for row in supplemental})
        for row in supplemental:
            with self.subTest(domain=row["domain_name"]):
                route = resolve_route({"division": row["domain_name"]})
                proposal = proposals[row["domain_id"]]
                self.assertTrue(route["route_valid"])
                self.assertEqual(route["proposed_collaborator_masterbot_id"], proposal["proposed_collaborator_masterbot_id"])
                self.assertEqual(route["related_domain"], proposal["related_domain"])
                self.assertEqual(route["route_status"], "proposed_collaborator_pending_owner_review")
                self.assertFalse(route["dispatch_allowed"])

    def test_all_20_shared_platform_masterbots_have_no_primary_domain(self):
        shared_ids = self.approval["shared_platform_services"]["masterbot_ids"]
        self.assertEqual(shared_ids, list(range(46, 66)))
        registry = {int(row["id"]): row["name"] for row in self.registry["divisions"]}
        for ident in shared_ids:
            with self.subTest(masterbot_id=ident):
                route = resolve_route({"division": registry[ident]})
                self.assertTrue(route["route_valid"])
                self.assertEqual(route["primary_masterbot_id"], ident)
                self.assertIsNone(route["primary_domain_owner"])
                self.assertEqual(route["route_status"], "shared_platform_service_pending_owner_confirmation")
                self.assertTrue(route["available_to_all_domain_divisions"])
                self.assertFalse(route["dispatch_allowed"])

    def test_unknown_and_unmapped_divisions_fail_closed(self):
        for division in ("GrokTeammates", "UnknownDivision", ""):
            with self.subTest(division=division):
                route = resolve_route({"division": division})
                self.assertFalse(route["route_valid"])
                self.assertEqual(route["route_status"], "blocked_unmapped_division")
                self.assertFalse(route["dispatch_allowed"])
                self.assertFalse(route["privileged_execution_enabled"])

    def test_fleet_executor_includes_route_in_result_and_evidence(self):
        executor = FleetExecutor(customizations={})
        bot = next(row for row in executor.bots.values()
                   if row["division"] == "DreamFinance" and row["engine"] != "unmapped")
        result = executor.run(bot["slug"], {"objective": "Prepare a sandbox-only planning task"})
        self.assertIn("routing", result)
        self.assertEqual(result["routing"]["primary_masterbot_id"], 1)
        self.assertEqual(result["evidence"]["routing"], result["routing"])
        self.assertFalse(result["routing"]["dispatch_allowed"])
        self.assertFalse(result["live_external_action_taken"])


if __name__ == "__main__":
    unittest.main()
