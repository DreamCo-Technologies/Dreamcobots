import json
import tempfile
import unittest
from pathlib import Path

from tools.build_division_owner_review_queue import (
    OwnerReviewQueueError,
    build_owner_review_queue,
    validate_owner_review_queue,
)

ROOT = Path(__file__).resolve().parents[1]


class DivisionOwnerReviewQueueTests(unittest.TestCase):
    def test_current_source_classifies_shared_platform_roles_without_domain_assignment(self):
        queue = build_owner_review_queue(
            ROOT / "config/generated/division-resource-readiness-map.json",
            ROOT / "config/generated/division-reconciliation.json",
            ROOT / "config/review/division-owner-conversation-approval.json",
        )
        validate_owner_review_queue(queue)
        self.assertEqual(queue["counts"]["pending_masterbot_mappings"], 45)
        self.assertEqual([row["masterbot_id"] for row in queue["masterbot_domain_decisions"]], list(range(1, 46)))
        self.assertTrue(all(row["decision"] == "PENDING_OWNER_REVIEW" for row in queue["masterbot_domain_decisions"]))
        self.assertTrue(all(row["owner_approval"] is None for row in queue["masterbot_domain_decisions"]))
        self.assertTrue(all(row["user_approval_status"] == "APPROVED_BY_USER_IN_CHAT_PENDING_GITHUB_IDENTITY_ATTESTATION" for row in queue["masterbot_domain_decisions"]))
        self.assertTrue(all(row["github_identity_attestation_required"] is True for row in queue["masterbot_domain_decisions"]))
        self.assertEqual(queue["counts"]["shared_platform_role_confirmations"], 20)
        self.assertEqual(queue["counts"]["unassigned_domain_profiles"], 10)
        self.assertEqual(queue["counts"]["proposed_supplemental_collaborator_links"], 10)
        self.assertEqual(
            [row["masterbot_id"] for row in queue["shared_platform_masterbots"]],
            list(range(46, 66)),
        )
        self.assertTrue(all(row["primary_domain_owner"] is None for row in queue["shared_platform_masterbots"]))
        self.assertTrue(all(row["no_domain_owner_inferred"] for row in queue["shared_platform_masterbots"]))
        self.assertTrue(all(row["owner_approval"] is None for row in queue["shared_platform_masterbots"]))
        self.assertTrue(all(row["user_approval_status"] == "ACCEPTED_AS_SHARED_PLATFORM_SERVICES_NO_PRIMARY_DOMAIN_OWNER" for row in queue["shared_platform_masterbots"]))
        self.assertTrue(all(row["github_identity_attestation_required"] is True for row in queue["shared_platform_masterbots"]))
        self.assertTrue(all(len(row["candidate_masterbot_ids"]) == 1 for row in queue["unassigned_domain_profiles"]))
        self.assertTrue(all(row["no_mapping_inferred"] for row in queue["unassigned_domain_profiles"]))
        self.assertTrue(all(row["user_approval_status"] == "APPROVED_BY_USER_IN_CHAT_PENDING_GITHUB_IDENTITY_ATTESTATION" for row in queue["unassigned_domain_profiles"]))
        self.assertTrue(all(row["github_identity_attestation_required"] is True for row in queue["unassigned_domain_profiles"]))

    def test_rejects_proposed_core_mapping_without_resource_route(self):
        source = {
            "routes": [],
            "owner_review": {
                "proposed_exact_name_matches": [{
                    "masterbot_id": 1, "masterbot_name": "Alpha",
                    "primary_domain_id": "alpha",
                    "mapping_status": "proposed_exact_name_match",
                    "owner_approval": None,
                    "evidence": ["config/generated/masterbot-55-domain-crosswalk.json"],
                }],
                "masterbot_domain_decisions": [],
                "shared_platform_services": [],
                "unassigned_domain_profiles": [],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / "map.json"
            reconciliation_path = Path(tmp) / "reconciliation.json"
            source_path.write_text(json.dumps(source))
            reconciliation_path.write_text(json.dumps({"shared_platform_masterbots": [], "promoted_supplemental_divisions": []}))
            with self.assertRaisesRegex(OwnerReviewQueueError, "missing_resource_route"):
                build_owner_review_queue(source_path, reconciliation_path)
    def test_builds_pending_domain_and_supplemental_queues_without_guessing(self):
        source = {
            "routes": [{"masterbot_id": 1, "masterbot_name": "Alpha", "resource_bundle_id": "division-resource-001"}],
            "owner_review": {
                "masterbot_domain_decisions": [{
                    "masterbot_id": 1, "masterbot_name": "Alpha", "primary_domain_id": None,
                    "candidate_domain_ids": [], "resource_bundle_id": "division-resource-001",
                    "decision": "PENDING_OWNER_REVIEW", "owner_approval": None, "evidence": [],
                }],
                "unassigned_domain_profiles": [{
                    "domain_id": "alpha-domain", "domain_name": "Alpha Domain",
                    "candidate_masterbot_ids": [], "standalone_resource_bundle_id": "domain-resource-alpha",
                    "decision": "PENDING_OWNER_REVIEW", "owner_approval": None, "evidence": [],
                }],
            },
        }
        reconciliation = {"shared_platform_masterbots": [], "promoted_supplemental_divisions": []}
        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / "map.json"
            reconciliation_path = Path(tmp) / "reconciliation.json"
            source_path.write_text(json.dumps(source))
            reconciliation_path.write_text(json.dumps(reconciliation))
            queue = build_owner_review_queue(source_path, reconciliation_path)
        validate_owner_review_queue(queue)
        self.assertEqual(queue["counts"]["pending_masterbot_mappings"], 1)
        self.assertEqual(queue["counts"]["shared_platform_role_confirmations"], 0)
        self.assertIsNone(queue["masterbot_domain_decisions"][0]["proposed_primary_domain_id"])
        self.assertEqual(queue["unassigned_domain_profiles"][0]["candidate_masterbot_ids"], [])

    def test_rejects_shared_platform_identity_without_resource_lineage(self):
        platform_rows = [{
            "id": ident, "name": f"Platform{ident}", "purpose": "Documented shared capability",
            "kind": "shared_platform_service",
            "ownership_status": "shared_platform_not_a_domain_division",
            "primary_domain_owner": None, "available_to_all_domain_divisions": True,
        } for ident in range(46, 66)]
        source = {
            "routes": [{
                "masterbot_id": ident, "masterbot_name": f"Platform{ident}",
                "resource_bundle_id": f"division-resource-{ident:03d}",
            } for ident in range(47, 66)],
            "owner_review": {
                "masterbot_domain_decisions": [{
                    "masterbot_id": ident, "masterbot_name": f"Platform{ident}",
                    "primary_domain_id": None, "candidate_domain_ids": [],
                    "resource_bundle_id": f"division-resource-{ident:03d}",
                    "decision": "PENDING_OWNER_REVIEW", "owner_approval": None, "evidence": [],
                } for ident in range(46, 66)],
                "unassigned_domain_profiles": [],
            },
        }
        reconciliation = {
            "shared_platform_masterbots": platform_rows,
            "promoted_supplemental_divisions": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / "map.json"
            reconciliation_path = Path(tmp) / "reconciliation.json"
            source_path.write_text(json.dumps(source))
            reconciliation_path.write_text(json.dumps(reconciliation))
            with self.assertRaisesRegex(OwnerReviewQueueError, "missing_resource_or_crosswalk"):
                build_owner_review_queue(source_path, reconciliation_path)

    def test_rejects_owner_approval_in_pending_queue(self):
        queue = {
            "schema": "dreamco.division_owner_review_queue.v1",
            "counts": {
                "pending_masterbot_mappings": 1,
                "shared_platform_role_confirmations": 0,
                "unassigned_domain_profiles": 0,
                "proposed_supplemental_collaborator_links": 0,
            },
            "masterbot_domain_decisions": [{
                "decision": "PENDING_OWNER_REVIEW", "no_mapping_inferred": True,
                "owner_approval": {"approval_id": "fake"},
            }],
            "shared_platform_masterbots": [],
            "unassigned_domain_profiles": [],
        }
        with self.assertRaisesRegex(OwnerReviewQueueError, "separate_signed_decision"):
            validate_owner_review_queue(queue)

    def test_rejects_inferred_mapping(self):
        queue = {
            "schema": "dreamco.division_owner_review_queue.v1",
            "counts": {
                "pending_masterbot_mappings": 1,
                "shared_platform_role_confirmations": 0,
                "unassigned_domain_profiles": 0,
                "proposed_supplemental_collaborator_links": 0,
            },
            "masterbot_domain_decisions": [{"decision": "APPROVED", "no_mapping_inferred": False}],
            "shared_platform_masterbots": [],
            "unassigned_domain_profiles": [],
        }
        with self.assertRaisesRegex(OwnerReviewQueueError, "inferred_assignment"):
            validate_owner_review_queue(queue)

    def test_rejects_primary_domain_assignment_for_shared_platform_role(self):
        queue = {
            "schema": "dreamco.division_owner_review_queue.v1",
            "counts": {
                "pending_masterbot_mappings": 0,
                "shared_platform_role_confirmations": 1,
                "unassigned_domain_profiles": 0,
                "proposed_supplemental_collaborator_links": 0,
            },
            "masterbot_domain_decisions": [],
            "shared_platform_masterbots": [{
                "masterbot_id": 46,
                "decision": "SHARED_PLATFORM_ROLE_REQUIRES_OWNER_CONFIRMATION",
                "no_domain_owner_inferred": True,
                "primary_domain_owner": "DreamFinance",
                "owner_approval": None,
                "kind": "shared_platform_service",
                "ownership_status": "shared_platform_not_a_domain_division",
                "available_to_all_domain_divisions": True,
                "purpose": "Research",
                "evidence": ["config/generated/division-reconciliation.json"],
                "resource_bundle_id": "division-resource-046",
            }],
            "unassigned_domain_profiles": [],
        }
        with self.assertRaisesRegex(OwnerReviewQueueError, "invalid_or_unapproved_shared_platform"):
            validate_owner_review_queue(queue)


if __name__ == "__main__":
    unittest.main()
