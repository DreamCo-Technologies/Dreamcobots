import json
import unittest
from pathlib import Path

from buddy.datasets.database_router import (
    DatabaseRouteError,
    load_source_registry,
    route_database_request,
    validate_source_registry,
)


def source(source_id="source-a", **overrides):
    value = {
        "source_id": source_id,
        "provider": "synthetic-test-provider",
        "engine": "postgresql",
        "environment": "test",
        "owner": "test-fixture",
        "purpose": "synthetic routing policy fixture",
        "schema_version": "test-v1",
        "retention": "ephemeral test data only",
        "credential_status": "no credentials stored",
        "source_code": "tests/test_buddy_database_router.py",
        "lifecycle_state": "TESTED",
        "connector_status": "CONNECTED",
        "health": "HEALTHY",
        "permitted_operations": ["read"],
        "data_types": ["dataset_metadata"],
        "query_capabilities": ["sql_select"],
        "max_data_classification": "internal",
        "freshness_seconds": 5,
        "consistency": "strong",
        "latency_ms": 25,
        "cost_tier": "low",
        "residency_regions": ["us-central"],
        "write_enabled": False,
        "supports_idempotency": False,
        "transaction_support": False,
        "write_approval_refs": [],
        "backup_restore_status": "NOT_VERIFIED",
        "backup_restore_evidence_refs": [],
        "replication_status": "NOT_VERIFIED",
        "replication_evidence_refs": [],
        "connection_pooling_status": "NOT_VERIFIED",
        "connection_pooling_evidence_refs": [],
        "encryption_at_rest_status": "NOT_VERIFIED",
        "encryption_at_rest_evidence_refs": [],
        "encryption_in_transit_status": "NOT_VERIFIED",
        "encryption_in_transit_evidence_refs": [],
        "observability_status": "NOT_VERIFIED",
        "observability_evidence_refs": [],
        "disaster_recovery_status": "NOT_VERIFIED",
        "disaster_recovery_evidence_refs": [],
        "residency_status": "NOT_VERIFIED",
        "residency_evidence_refs": [],
    }
    value.update(overrides)
    return value


def request(**overrides):
    value = {
        "operation": "read",
        "data_type": "dataset_metadata",
        "data_classification": "internal",
        "query_capability": "sql_select",
        "max_staleness_seconds": 30,
        "consistency": "strong",
        "max_latency_ms": 100,
        "max_cost_tier": "medium",
        "region": "us-central",
        "routing_priority": ["cost", "latency", "freshness"],
    }
    value.update(overrides)
    return value


class BuddyDatabaseRouterTests(unittest.TestCase):
    def test_selects_lowest_cost_eligible_source_deterministically(self):
        expensive = source("pg-fast", latency_ms=5, cost_tier="high")
        cheap = source("sqlite-local", engine="sqlite", latency_ms=50, cost_tier="free")
        first = route_database_request(request(), [expensive, cheap])
        second = route_database_request(request(), [cheap, expensive])
        self.assertEqual(first["status"], "ROUTED")
        self.assertEqual(first["selected_source_id"], "sqlite-local")
        self.assertEqual(first["selected_source_id"], second["selected_source_id"])

    def test_rejects_stale_sensitive_wrong_region_and_unsupported_sources(self):
        stale = source(
            "stale",
            freshness_seconds=600,
            max_data_classification="public",
            residency_regions=["eu-west"],
            query_capabilities=["vector_search"],
        )
        result = route_database_request(request(), [stale])
        self.assertEqual(result["status"], "BLOCKED")
        reasons = set(result["rejected_sources"][0]["reasons"])
        self.assertIn("freshness_exceeds_limit", reasons)
        self.assertIn("insufficient_data_classification", reasons)
        self.assertIn("residency_region_not_allowed", reasons)
        self.assertIn("query_capability_not_supported", reasons)

    def test_unconnected_or_unhealthy_source_never_routes(self):
        configured = source("configured", lifecycle_state="CONFIGURED", connector_status="NOT_VERIFIED")
        result = route_database_request(request(), [configured])
        self.assertEqual(result["status"], "BLOCKED")
        reasons = set(result["rejected_sources"][0]["reasons"])
        self.assertIn("lifecycle_state_not_routable", reasons)
        self.assertIn("connector_not_connected", reasons)

    def test_write_requires_approval_and_idempotency_key(self):
        writable = source(
            "approved-db",
            permitted_operations=["read", "write"],
            write_enabled=True,
            supports_idempotency=True,
            transaction_support=True,
            write_approval_refs=["APPROVAL-1"],
        )
        missing_approval = route_database_request(
            request(operation="write", query_capability="sql_select", idempotency_key="idem-1"),
            [writable],
        )
        self.assertEqual(missing_approval["reason"], "write_approval_id_required")
        missing_idempotency = route_database_request(
            request(operation="write", query_capability="sql_select", write_approval_id="APPROVAL-1"),
            [writable],
        )
        self.assertEqual(missing_idempotency["reason"], "idempotency_key_required")

    def test_approved_write_is_source_allowlisted_and_never_auto_fails_over(self):
        writable = source(
            "approved-db",
            permitted_operations=["read", "write"],
            query_capabilities=["sql_select", "transactional_write"],
            write_enabled=True,
            supports_idempotency=True,
            transaction_support=True,
            write_approval_refs=["APPROVAL-1"],
        )
        result = route_database_request(
            request(
                operation="write",
                query_capability="transactional_write",
                write_approval_id="APPROVAL-1",
                idempotency_key="idem-1",
                allow_failover=True,
                idempotent=True,
            ),
            [writable],
        )
        self.assertEqual(result["status"], "ROUTED")
        self.assertFalse(result["failover_allowed"])
        self.assertEqual(result["alternatives"], [])

    def test_read_failover_requires_explicit_permission_and_idempotency(self):
        sources = [source("a"), source("b", latency_ms=40)]
        blocked = route_database_request(request(allow_failover=True), sources)
        allowed = route_database_request(request(allow_failover=True, idempotent=True), sources)
        self.assertFalse(blocked["failover_allowed"])
        self.assertTrue(allowed["failover_allowed"])
        self.assertEqual(allowed["alternatives"], ["b"])

    def test_default_registry_is_cataloged_but_not_routable(self):
        registry = load_source_registry()
        result = route_database_request(request(), registry["sources"], registry["policy"])
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIsNone(result["selected_source_id"])

    def test_registry_rejects_duplicate_ids_and_credential_values(self):
        with self.assertRaises(DatabaseRouteError):
            validate_source_registry([source("duplicate"), source("duplicate")])
        unsafe = source("unsafe")
        unsafe["connection_string"] = "postgres://not-a-real-secret"
        with self.assertRaises(DatabaseRouteError):
            validate_source_registry([unsafe])

    def test_verified_operational_status_requires_evidence_reference(self):
        unproven = source("unproven", encryption_at_rest_status="VERIFIED")
        with self.assertRaisesRegex(DatabaseRouteError, "requires at least one evidence reference"):
            validate_source_registry([unproven])

    def test_production_source_requires_all_operational_controls_and_evidence(self):
        production = source("production", lifecycle_state="PRODUCTION")
        with self.assertRaisesRegex(DatabaseRouteError, "production source requires verified controls"):
            validate_source_registry([production])

        verified = source(
            "verified-production",
            lifecycle_state="PRODUCTION",
            backup_restore_status="VERIFIED",
            backup_restore_evidence_refs=["evidence:backup-restore"],
            replication_status="VERIFIED",
            replication_evidence_refs=["evidence:replication"],
            connection_pooling_status="VERIFIED",
            connection_pooling_evidence_refs=["evidence:pooling"],
            encryption_at_rest_status="VERIFIED",
            encryption_at_rest_evidence_refs=["evidence:encryption-at-rest"],
            encryption_in_transit_status="VERIFIED",
            encryption_in_transit_evidence_refs=["evidence:encryption-in-transit"],
            observability_status="VERIFIED",
            observability_evidence_refs=["evidence:observability"],
            disaster_recovery_status="VERIFIED",
            disaster_recovery_evidence_refs=["evidence:disaster-recovery"],
            residency_status="VERIFIED",
            residency_evidence_refs=["evidence:residency"],
        )
        validate_source_registry([verified])

    def test_registry_file_is_valid_json_and_documents_lifecycle(self):
        path = Path(__file__).resolve().parents[1] / "config" / "buddy-database-source-registry.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "dreamco.database_source_registry.v1")
        self.assertEqual(data["policy"]["routable_lifecycle_states"], ["CONNECTED", "TESTED", "PRODUCTION"])
        self.assertTrue(all(item["lifecycle_state"] in {
            "DISCOVERED", "DOCUMENTED", "CONFIGURED", "AUTHENTICATED",
            "CONNECTED", "TESTED", "PRODUCTION", "BLOCKED"
        } for item in data["sources"]))


if __name__ == "__main__":
    unittest.main()
