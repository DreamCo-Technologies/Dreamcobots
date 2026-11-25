import unittest

from buddy.fleet_runtime.executor import FleetExecutor
from buddy.fleet_runtime.routing import resolve_route


class CanonicalFleetRoutingTests(unittest.TestCase):
    def test_core_domain_resolves_but_remains_pending_identity_attestation(self):
        route = resolve_route({"division": "DreamFinance"})
        self.assertTrue(route["route_valid"])
        self.assertEqual(route["primary_masterbot_id"], 1)
        self.assertEqual(route["mapping_status"], "proposed_exact_name_match")
        self.assertEqual(route["route_status"], "proposed_core_route_pending_github_identity_attestation")
        self.assertTrue(route["owner_approval_required"])
        self.assertTrue(route["github_identity_attestation_required"])
        self.assertFalse(route["privileged_execution_enabled"])
        self.assertFalse(route["live_external_actions_enabled"])
        self.assertFalse(route["training_execution_enabled"])

    def test_supplemental_domain_stays_unassigned(self):
        route = resolve_route({"division": "DreamAffiliate"})
        self.assertFalse(route["route_valid"])
        self.assertIsNone(route["primary_masterbot_id"])
        self.assertEqual(route["route_status"], "supplemental_domain_unassigned_pending_owner_review")
        self.assertEqual(route["shared_platform_masterbot_ids"], list(range(46, 66)))
        self.assertFalse(route["privileged_execution_enabled"])

    def test_shared_platform_masterbot_is_collaborator_not_primary_owner(self):
        route = resolve_route({
            "division": "GrokTeammates",
            "primary_domain_owner": "DreamAIInfra",
            "primary_masterbot_id": 4,
            "shared_teammate_masterbot_id": 47,
            "shared_workforce_group": "GrokTeammates",
        })
        self.assertTrue(route["route_valid"])
        self.assertEqual(route["primary_masterbot_id"], 4)
        self.assertEqual(route["shared_teammate_masterbot_id"], 47)
        self.assertEqual(route["collaborating_masterbot_ids"], [47])
        self.assertNotEqual(route["primary_masterbot_id"], route["shared_teammate_masterbot_id"])

    def test_shared_masterbot_cannot_be_primary_domain_owner(self):
        route = resolve_route({
            "division": "DreamAIInfra",
            "primary_domain_owner": "DreamAIInfra",
            "primary_masterbot_id": 47,
        })
        self.assertFalse(route["route_valid"])
        self.assertIsNone(route["primary_masterbot_id"])
        self.assertEqual(route["route_status"], "blocked_inconsistent_primary_masterbot")

    def test_executor_attaches_route_to_output_and_evidence(self):
        executor = FleetExecutor(env={}, customizations={})
        result = executor.run("analytics-hub", {"objective": "Plan a sandbox-only KPI review"})
        self.assertIn("routing", result)
        self.assertEqual(result["evidence"]["routing"], result["routing"])
        self.assertTrue(result["routing"]["owner_approval_required"])
        self.assertFalse(result["routing"]["privileged_execution_enabled"])

    def test_unknown_domain_fails_closed_without_assigning_masterbot(self):
        route = resolve_route({"division": "UnknownDivision"})
        self.assertFalse(route["route_valid"])
        self.assertIsNone(route["primary_masterbot_id"])
        self.assertEqual(route["route_status"], "blocked_domain_not_in_canonical_crosswalk")


if __name__ == "__main__":
    unittest.main()
