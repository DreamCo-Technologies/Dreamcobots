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
            self.assertEqual(reports[0]["status"], "unknown")
            self.assertTrue(any("SHA" in item for item in reports[0]["evidence_errors"]))
            failed = lambda *args: False
            reports = build_area_reports(
                contract, manifest, sha, "DreamCo-Technologies/Dreamcobots", "token",
                root=root, verify_check=failed,
            )
            self.assertEqual(reports[0]["status"], "unknown")
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

    def test_repeated_check_run_ids_are_verified_only_once(self):
        from tools.production_readiness_gate import build_area_reports, AREA_EVIDENCE_SCHEMA
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "a.txt").write_text("a", encoding="utf-8")
            (root / "b.txt").write_text("b", encoding="utf-8")
            manifest = {
                "schema": AREA_EVIDENCE_SCHEMA,
                "areas": {
                    "buddy_orchestration": {
                        "status": "VERIFIED",
                        "evidence": [
                            {"path": "a.txt", "sha": "a" * 40, "check_id": "123"},
                            {"path": "b.txt", "sha": "a" * 40, "check_id": "123"},
                        ],
                    }
                },
            }
            calls = []
            def verify(*args):
                calls.append(args[1])
                return True
            reports = build_area_reports(
                {"areas": [{"id": "buddy_orchestration", "label": "Buddy", "required": ["router"]}]},
                manifest, "a" * 40, "DreamCo-Technologies/Dreamcobots", "token",
                root=root, verify_check=verify,
            )
            self.assertEqual(reports[0]["status"], "verified")
            self.assertEqual(calls, ["123"])

    def test_live_environment_requires_non_secret_api_base_url(self):
        from tools.production_readiness_gate import probe_live_environment
        result = probe_live_environment(None)
        self.assertEqual(result["status"], "external_config_required")
        self.assertIn("DREAMCO_PRODUCTION_API_BASE_URL", result["missing_required"])

    def test_live_environment_passes_only_when_health_reports_all_configuration_flags(self):
        from tools.production_readiness_gate import probe_live_environment
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps({
                    "ok": True,
                    "databaseConfigured": True,
                    "stripeConfigured": True,
                    "stripeWebhookConfigured": True,
                    "openaiConfigured": True,
                    "configurationReady": True,
                }).encode("utf-8")
        result = probe_live_environment("https://api.example.test", opener=lambda request, timeout: Response())
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["evidence"], ["https://api.example.test/api/health"])

    def test_live_environment_reports_missing_host_configuration_without_reading_secrets(self):
        from tools.production_readiness_gate import probe_live_environment
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps({"ok": True, "databaseConfigured": True}).encode("utf-8")
        result = probe_live_environment("https://api.example.test", opener=lambda request, timeout: Response())
        self.assertEqual(result["status"], "external_config_required")
        self.assertIn("stripeConfigured", result["missing_required"])
        self.assertIn("openaiConfigured", result["missing_required"])

    def test_live_environment_fails_closed_when_health_endpoint_is_unreachable(self):
        from tools.production_readiness_gate import probe_live_environment
        def unreachable(request, timeout):
            raise OSError("unreachable")
        result = probe_live_environment("https://api.example.test", opener=unreachable)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(result["release_blocker"])

    def test_api_health_route_exposes_boolean_configuration_state_only(self):
        source = (Path(__file__).resolve().parents[1] / "server/index.ts").read_text(encoding="utf-8")
        for flag in (
            "databaseConfigured",
            "stripeConfigured",
            "stripeWebhookConfigured",
            "openaiConfigured",
            "configurationReady",
        ):
            self.assertIn(flag, source)

    def test_live_environment_rejects_http_and_embedded_credentials(self):
        from tools.production_readiness_gate import probe_live_environment
        http_result = probe_live_environment("http://api.example.test")
        credential_result = probe_live_environment("https://user:password@api.example.test")
        self.assertEqual(http_result["status"], "fail")
        self.assertEqual(credential_result["status"], "fail")
        self.assertEqual(credential_result["evidence"], [])

if __name__ == "__main__":
    unittest.main()
