import unittest

from tools.dreamco_10pillar_extensions import (
    audit_buyer_readiness,
    build_regression_issue_draft,
    canonical_json,
    distill_verified_repair,
    propose_upgrade_101,
    sha256_json,
    sign_isolation_receipt,
    update_curriculum_state,
    evaluate_swarm_handoff,
)


class CurriculumSchedulerTests(unittest.TestCase):
    def test_high_pass_rate_scales_difficulty_and_spaced_interval(self):
        result = update_curriculum_state(
            {}, scope_type="domain_division", scope_id="dreamcodelab",
            pass_rate=0.96, difficulty=2.0, interval_days=3,
        )
        self.assertEqual(result["difficulty"], 2.2)
        self.assertEqual(result["spaced_interval_days"], 6)
        self.assertFalse(result["mastery_awarded"])

    def test_low_pass_rate_reduces_difficulty_and_resets_interval(self):
        result = update_curriculum_state(
            {}, scope_type="masterbot_lane", scope_id="DreamBenchmark",
            pass_rate=0.60, difficulty=1.0, interval_days=14,
        )
        self.assertEqual(result["difficulty"], 0.9)
        self.assertEqual(result["spaced_interval_days"], 1)

    def test_holdout_data_cannot_change_curriculum(self):
        with self.assertRaisesRegex(ValueError, "holdout"):
            update_curriculum_state(
                {}, scope_type="masterbot_lane", scope_id="DreamBenchmark",
                pass_rate=1.0, evidence_split="private_holdout",
            )


class BootcampDistillerTests(unittest.TestCase):
    def _evidence(self):
        payload = {
            "evidence_id": "repair-001",
            "lesson_id": "dreamcodelab-debugging-001",
            "division_id": "dreamcodelab",
            "status": "VERIFIED_REPAIR",
            "human_review_status": "APPROVED",
            "source_rights_approved": True,
            "training_use_approved": True,
            "privacy_review_status": "APPROVED",
            "holdout": False,
            "evidence_split": "practice",
            "failure_summary": "A deterministic validation step rejected a malformed response.",
            "root_cause_summary": "The parser accepted an absent required field.",
            "repair_summary": "The schema validator now rejects missing required fields.",
            "regression_test_summary": "A negative test confirms the missing field is rejected.",
        }
        return {**payload, "evidence_sha256": sha256_json(payload)}

    def test_emits_25_original_rubric_drills(self):
        drills = distill_verified_repair(self._evidence())
        self.assertEqual(len(drills), 25)
        self.assertEqual(len({row["drill_id"] for row in drills}), 25)
        self.assertTrue(all(row["training_eligible"] for row in drills))
        self.assertTrue(all(not row["holdout"] for row in drills))
        self.assertTrue(all(row["lesson_minhash_signature"] for row in drills))

    def test_unreviewed_or_holdout_repairs_are_blocked(self):
        evidence = self._evidence()
        evidence["holdout"] = True
        payload = {key: value for key, value in evidence.items() if key != "evidence_sha256"}
        evidence["evidence_sha256"] = sha256_json(payload)
        with self.assertRaisesRegex(ValueError, "holdout"):
            distill_verified_repair(evidence)

    def test_near_duplicate_lesson_is_rejected_by_minhash(self):
        evidence = self._evidence()
        signature = distill_verified_repair(evidence)[0]["lesson_minhash_signature"]
        with self.assertRaisesRegex(ValueError, "near-duplicate"):
            distill_verified_repair(evidence, existing_signatures=[tuple(signature)])


class SwarmEvaluationTests(unittest.TestCase):
    def test_handoff_requires_correct_route_schema_latency_and_precision(self):
        result = evaluate_swarm_handoff(
            expected_route="DreamCodeLab", actual_route="DreamCodeLab",
            router_latency_ms=3.4, schema_valid=True, tool_calls_used=5,
            optimal_tool_calls=4,
        )
        self.assertTrue(result["passed"])

    def test_wrong_route_fails(self):
        result = evaluate_swarm_handoff(
            expected_route="DreamCodeLab", actual_route="DreamFinance",
            router_latency_ms=3.4, schema_valid=True, tool_calls_used=4,
            optimal_tool_calls=4,
        )
        self.assertFalse(result["passed"])


class RegressionGuardTests(unittest.TestCase):
    def test_relative_drop_over_half_percent_creates_issue_draft_only(self):
        result = build_regression_issue_draft(
            model_id="buddy-test-model", baseline_score=0.90, current_score=0.89,
            baseline_sha256="a" * 64, current_sha256="b" * 64,
            reproduction_command="python -m unittest tests.test_example",
        )
        self.assertEqual(result["status"], "ISSUE_DRAFT_REQUIRES_REVIEW")
        self.assertFalse(result["github_issue_created"])

    def test_small_drop_does_not_create_issue_draft(self):
        result = build_regression_issue_draft(
            model_id="buddy-test-model", baseline_score=0.90, current_score=0.899,
            baseline_sha256="a" * 64, current_sha256="b" * 64,
            reproduction_command="python -m unittest tests.test_example",
        )
        self.assertEqual(result["status"], "NO_REGRESSION")


class BuyerReadinessTests(unittest.TestCase):
    def test_unverified_isolation_never_awards_certification(self):
        result = audit_buyer_readiness(
            fp16_score=0.95, q8_score=0.94, q4_score=0.93,
            isolation_receipt=None,
        )
        self.assertEqual(result["status"], "BLOCKED_PENDING_EVIDENCE")
        self.assertFalse(result["buyer_certification_awarded"])

    def test_hmac_verified_isolation_receipt_can_reach_human_review(self):
        key = "dreamco-test-hmac-key-material-32-bytes-minimum"
        receipt = {
            "network_blocked": True,
            "egress_probe_attempted": True,
            "egress_probe_blocked": True,
            "kit_sha256": "c" * 64,
            "runner_id": "github-hosted-isolated-runner",
        }
        signed = sign_isolation_receipt(receipt, key, "test-key-01")
        result = audit_buyer_readiness(
            fp16_score=0.95, q8_score=0.94, q4_score=0.93,
            isolation_receipt=signed, hmac_key=key, key_id="test-key-01",
        )
        self.assertEqual(result["status"], "READY_FOR_HUMAN_BUYER_REVIEW")
        self.assertFalse(result["buyer_certification_awarded"])


class Upgrade101Tests(unittest.TestCase):
    def test_requires_repeated_verified_telemetry_and_stays_draft(self):
        telemetry = [
            {"status": "VERIFIED", "bottleneck": "tool_latency", "evidence_sha256": "a" * 64, "holdout": False},
            {"status": "VERIFIED", "bottleneck": "tool_latency", "evidence_sha256": "b" * 64, "holdout": False},
            {"status": "VERIFIED", "bottleneck": "tool_latency", "evidence_sha256": "c" * 64, "holdout": False},
        ]
        result = propose_upgrade_101(telemetry)
        self.assertEqual(result["status"], "PROPOSAL_DRAFTED")
        self.assertEqual(result["proposal"]["status"], "DRAFT_REQUIRES_HUMAN_REVIEW")
        self.assertIsNone(result["proposal"]["claimed_improvement_percent"])
        self.assertFalse(result["proposal"]["automatic_merge"])

    def test_no_verified_telemetry_means_no_proposal(self):
        result = propose_upgrade_101([])
        self.assertEqual(result["status"], "NO_PROPOSAL_INSUFFICIENT_VERIFIED_TELEMETRY")


if __name__ == "__main__":
    unittest.main()
