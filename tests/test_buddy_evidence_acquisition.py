"""Offline tests for opt-in Buddy evidence and capability proposals."""
import unittest

from buddy.learning.evidence_acquisition import (
    Capability, CapabilityRegistry, LearningEvent, LearningLedger, benchmark_gate,
)


def event(**overrides):
    fields = dict(tenant_id="alice", task_id="t1", domain="technical", goal="fix build",
                  workflow="test-first", outcome="success", source="user-approved-task",
                  source_revision="r1", consent=True, redacted=True, verified=True)
    fields.update(overrides)
    return LearningEvent(**fields)


class LearningEvidenceTests(unittest.TestCase):
    def test_consent_redaction_and_verification(self):
        for changes, error in [({"consent": False}, PermissionError),
                               ({"redacted": False}, PermissionError),
                               ({"verified": False}, ValueError)]:
            with self.assertRaises(error):
                LearningLedger().record(event(**changes))

    def test_tenant_isolation_idempotency_and_deletion(self):
        ledger = LearningLedger()
        self.assertEqual(ledger.record(event()), ledger.record(event()))
        ledger.record(event(tenant_id="bob"))
        self.assertEqual(len(ledger.retrieve("alice")), 1)
        self.assertEqual(len(ledger.retrieve("bob")), 1)
        self.assertEqual(ledger.forget("alice"), 1)
        self.assertEqual(ledger.retrieve("alice"), [])
        self.assertEqual(len(ledger.retrieve("bob")), 1)

    def test_conflicting_revision_rejected(self):
        ledger = LearningLedger()
        ledger.record(event())
        with self.assertRaises(ValueError):
            ledger.record(event(outcome="failure"))

    def test_holdout_not_used_for_recommendations(self):
        ledger = LearningLedger()
        ledger.record(event(split="holdout", outcome="failure"))
        self.assertEqual(ledger.recommendations("alice", "technical")["observations"], 0)
        ledger.record(event())
        result = ledger.recommendations("alice", "technical")
        self.assertEqual(result["candidates"][0]["successes"], 1)
        self.assertEqual(result["candidates"][0]["automation"], "human_review_required")

    def test_ratings_and_duration_validation(self):
        for changes in ({"rating": 6}, {"rating": True}, {"duration_seconds": -1},
                        {"duration_seconds": float("nan")}):
            with self.assertRaises(ValueError):
                event(**changes).validate()

    def test_unverified_capability_cannot_register(self):
        registry = CapabilityRegistry()
        with self.assertRaises(PermissionError):
            registry.register(Capability("editor", "local", "1", ("read",), "e1", False, True))
        self.assertEqual(registry.propose("read file", ["read"])["status"], "capability_gap")

    def test_verified_capability_and_missing_actions(self):
        registry = CapabilityRegistry()
        cap = Capability("editor", "local", "1", ("read",), "e1", True, True)
        registry.register(cap)
        registry.register(cap)
        result = registry.propose("inspect then write", ["read", "write"], risk="external_side_effect")
        self.assertEqual(result["matched"], {"read": "editor"})
        self.assertEqual(result["missing"], ["write"])
        self.assertFalse(result["executed"])
        with self.assertRaises(ValueError):
            registry.register(Capability("editor", "local", "2", ("read",), "e2", True, True))

    def test_benchmark_gate(self):
        self.assertTrue(benchmark_gate([.6] * 3, [.9] * 3, [.85] * 3)["promote"])
        self.assertFalse(benchmark_gate([.6] * 3, [.61] * 3, [.9] * 3)["promote"])
        with self.assertRaises(ValueError):
            benchmark_gate([.5], [.9] * 3, [.9] * 3)


if __name__ == "__main__":
    unittest.main()
