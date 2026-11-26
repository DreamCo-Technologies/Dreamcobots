from __future__ import annotations

import unittest
import json
import tempfile
from pathlib import Path

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


    def test_area_status_requires_existing_artifact_and_successful_same_sha_check(self):
        from tools.production_readiness_gate import build_area_reports, AREA_EVIDENCE_SCHEMA
        contract = {"areas": [
            {"id": "buddy_orchestration", "label": "Buddy", "required": ["router tests"]},
            {"id": "security", "label": "Security", "required": ["secret scan"]},
        ]}
        sha = "a" * 40
        empty = {"schema": AREA_EVIDENCE_SCHEMA, "areas": {}}
        reports = build_area_reports(contract, empty, sha, "DreamCo-Technologies/Dreamcobots", "token")
        self.assertEqual([row["status"] for row in reports], ["unknown", "unknown"])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / "tests/test_router.py"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("test", encoding="utf-8")
            manifest = {
                "schema": AREA_EVIDENCE_SCHEMA,
                "areas": {
                    "buddy_orchestration": {
                        "status": "VERIFIED",
                        "evidence": [{"path": "tests/test_router.py", "sha": sha, "check_id": "12345"}],
                    }
                },
            }
            verifier = lambda repository, check_id, revision, token: (
                repository == "DreamCo-Technologies/Dreamcobots"
                and check_id == "12345" and revision == sha and token == "token"
            )
            reports = build_area_reports(
                contract, manifest, sha, "DreamCo-Technologies/Dreamcobots", "token",
                root=root, verify_check=verifier,
            )
            self.assertEqual(reports[0]["status"], "verified")
            self.assertEqual(reports[1]["status"], "unknown")
            stale = json.loads(json.dumps(manifest))
            stale["areas"]["buddy_orchestration"]["evidence"][0]["sha"] = "b" * 40
            reports = build_area_reports(
                contract, stale, sha, "DreamCo-Technologies/Dreamcobots", "token",
                root=root, verify_check=verifier,
            )
            self.assertEqual(reports[0]["status"], "partial")
            self.assertTrue(any("SHA" in item for item in reports[0]["evidence_errors"]))
            failed = lambda *args: False
            reports = build_area_reports(
                contract, manifest, sha, "DreamCo-Technologies/Dreamcobots", "token",
                root=root, verify_check=failed,
            )
            self.assertEqual(reports[0]["status"], "partial")
            self.assertTrue(any("successful" in item for item in reports[0]["evidence_errors"]))

    def test_file_discovery_alone_never_marks_an_area_verified(self):
        from tools.production_readiness_gate import build_area_reports, AREA_EVIDENCE_SCHEMA
        contract = {"areas": [{"id": "deployment", "label": "Deployment", "required": ["build", "rollback"]}]}
        reports = build_area_reports(
            contract, {"schema": AREA_EVIDENCE_SCHEMA, "areas": {}},
            "a" * 40, "DreamCo-Technologies/Dreamcobots", None,
        )
        self.assertEqual(reports[0]["status"], "unknown")
        self.assertEqual(reports[0]["evidence"], [])


    def test_partial_area_keeps_verified_refs_and_surfaces_resolution_errors(self):
        from tools.production_readiness_gate import build_area_reports, AREA_EVIDENCE_SCHEMA
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / "tests/test_router.py"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("test", encoding="utf-8")
            manifest = {
                "schema": AREA_EVIDENCE_SCHEMA,
                "areas": {
                    "buddy_orchestration": {
                        "status": "PARTIAL",
                        "evidence": [{"path": "tests/test_router.py", "sha": "a" * 40, "check_id": "123"}],
                        "resolution_errors": ["missing routing runtime evidence"],
                    }
                },
            }
            reports = build_area_reports(
                {"areas": [{"id": "buddy_orchestration", "label": "Buddy", "required": ["router", "routing runtime"]}]},
                manifest, "a" * 40, "DreamCo-Technologies/Dreamcobots", "token",
                root=root, verify_check=lambda *args: True,
            )
            self.assertEqual(reports[0]["status"], "partial")
            self.assertEqual(reports[0]["evidence"][0]["path"], "tests/test_router.py")
            self.assertIn("missing routing runtime evidence", reports[0]["evidence_errors"])

if __name__ == "__main__":
    unittest.main()
