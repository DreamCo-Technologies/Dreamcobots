from __future__ import annotations

import unittest

from tools.production_readiness_gate import should_fail_gate, summarize_readiness


def area(area_id: str, status: str = "verified") -> dict:
    return {"id": area_id, "status": status}


def runtime(check_id: str, status: str = "pass", blocker: bool = True) -> dict:
    return {"id": check_id, "status": status, "release_blocker": blocker}


class ProductionCertificationTruthTests(unittest.TestCase):
    def test_partial_areas_never_count_as_production_ready(self):
        report = summarize_readiness(
            [area("buddy_orchestration", "partial"), area("distillation", "unknown")],
            [runtime("health", "pass"), runtime("live_environment", "external_config_required", False)],
        )
        self.assertFalse(report["production_ready"])
        self.assertEqual(report["release_status"], "evidence_incomplete")
        self.assertEqual(report["incomplete_areas"], ["buddy_orchestration", "distillation"])
        self.assertTrue(should_fail_gate(report, strict=False, certification=True))

    def test_complete_evidence_still_requires_external_configuration(self):
        report = summarize_readiness(
            [area("buddy_orchestration"), area("distillation")],
            [runtime("health"), runtime("live_environment", "external_config_required", False)],
        )
        self.assertFalse(report["production_ready"])
        self.assertEqual(report["release_status"], "external_config_required")
        self.assertTrue(should_fail_gate(report, strict=False, certification=True))

    def test_all_verified_and_runtime_green_is_the_only_ready_state(self):
        report = summarize_readiness(
            [area("buddy_orchestration"), area("distillation")],
            [runtime("health"), runtime("live_environment")],
        )
        self.assertTrue(report["production_ready"])
        self.assertEqual(report["release_status"], "production_ready")
        self.assertFalse(report["certification_blockers"])
        self.assertFalse(should_fail_gate(report, strict=True, certification=True))

    def test_release_blocking_runtime_failure_blocks_strict_and_certification(self):
        report = summarize_readiness(
            [area("buddy_orchestration")],
            [runtime("health", "fail")],
        )
        self.assertEqual(report["release_status"], "blocked")
        self.assertTrue(should_fail_gate(report, strict=True, certification=False))
        self.assertTrue(should_fail_gate(report, strict=False, certification=True))

    def test_critical_unknown_blocks_even_the_strict_code_gate(self):
        report = summarize_readiness(
            [area("security", "unknown")],
            [runtime("health")],
        )
        self.assertIn("security", report["blocking_unknowns"])
        self.assertTrue(should_fail_gate(report, strict=True, certification=False))


if __name__ == "__main__":
    unittest.main()
