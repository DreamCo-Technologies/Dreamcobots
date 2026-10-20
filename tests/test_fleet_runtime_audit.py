"""Tests for tools/fleet_runtime_audit.py (bot states, regression gate, folder verdicts)."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import fleet_runtime_audit as audit  # noqa: E402
from buddy.fleet_runtime.contract import PIECE_IDS, load_fixtures, load_manifests  # noqa: E402

FULL_EVIDENCE = {
    "connections": [{"id": "model_router", "status": "ok", "checked_at": "2026-10-06T00:00:00Z"}],
    "benchmark_results": [{"suite_id": "synthetic-fleet-test", "status": "measured", "passed": True, "evidence_hash": "a" * 64}],
    "test_reference": "t", "security_result": "s", "build_result": "b", "runtime_result": "r",
    "approval_reference": "a", "deployment_reference": "d", "health_result": "h", "observability_reference": "o",
}


class BenchmarkEvidenceTruthTests(unittest.TestCase):
    def test_only_identified_passing_measured_receipts_qualify(self):
        valid = FULL_EVIDENCE["benchmark_results"][0]
        self.assertTrue(audit.benchmarks_measured({"benchmark_results": [valid]}))
        self.assertFalse(audit.benchmarks_measured(None))
        for bad in (
            {"benchmark_results": [{"label": "x", "value": 1}]},
            {"benchmark_results": [{"suite_id": "x", "status": "planned", "passed": True, "evidence_hash": "a" * 64}]},
            {"benchmark_results": [{"suite_id": "x", "status": "measured", "passed": False, "evidence_hash": "a" * 64}]},
            {"benchmark_results": [{"suite_id": "x", "status": "measured", "passed": True, "evidence_hash": "bad"}]},
            {"benchmark_results": [valid, {"label": "bad"}]},
            {"benchmark_results": {"suite_id": "x"}},
            {"benchmark_results": []},
        ):
            with self.subTest(record=bad):
                self.assertFalse(audit.benchmarks_measured(bad))

    def test_unverified_truthy_benchmark_cannot_promote(self):
        slug = "ad-copy"
        record = {**FULL_EVIDENCE, "benchmark_results": [{"label": "x", "value": 1}]}
        with mock.patch.object(audit, "load_evidence", lambda s: record if s == slug else None):
            rows = audit.audit_bots(unit_ok=True)["rows"]
        state = next(r["state"] for r in rows if r["slug"] == slug)
        self.assertEqual(state, "CONNECTED")


class ConnectionEvidenceTests(unittest.TestCase):
    def test_no_required_api_needs_passing_checked_connection(self):
        manifest = {"engine": "analysis"}
        for connections in (
            [{"id": "db", "status": "failed", "checked_at": "2026-10-20T12:00:00Z"}],
            [{"id": "db", "status": "ok"}],
            [{"status": "ok", "checked_at": "2026-10-20T12:00:00Z"}],
        ):
            with self.subTest(connections=connections):
                self.assertFalse(audit.connections_ok(manifest, {"connections": connections}))
        self.assertTrue(audit.connections_ok(manifest, {"connections": [
            {"id": "db", "status": "ok", "checked_at": "2026-10-20T12:00:00Z"}]}))

    def test_drafting_still_requires_model_router(self):
        manifest = {"engine": "drafting"}
        self.assertFalse(audit.connections_ok(manifest, {"connections": [
            {"id": "db", "status": "ok", "checked_at": "2026-10-20T12:00:00Z"}]}))
        self.assertTrue(audit.connections_ok(manifest, {"connections": [
            {"id": "model_router", "status": "ok", "checked_at": "2026-10-20T12:00:00Z"}]}))


class BotStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = audit.audit_bots(unit_ok=True)["rows"]
        cls.by_slug = {r["slug"]: r for r in cls.rows}

    def test_every_bot_classified_with_all_pieces(self):
        self.assertEqual(len(self.rows), len(load_manifests()["bots"]))
        for r in self.rows:
            self.assertEqual(list(r["pieces"]), list(PIECE_IDS))
            self.assertIn(r["state"], audit.STATES_ALL)

    def test_no_production_without_evidence(self):
        counts = audit.summarise_bots(self.rows)["by_state"]
        self.assertEqual(counts["PRODUCTION"], 0)
        self.assertEqual(counts["VERIFIED"], 0)
        self.assertEqual(counts["CONNECTED"], 0)

    def test_tested_requires_fixture(self):
        fixtures = set(load_fixtures()["fixtures"])
        tested = {r["slug"] for r in self.rows if r["state"] == "TESTED"}
        self.assertEqual(tested, fixtures)

    def test_unmapped_is_spec_only(self):
        for r in self.rows:
            if r["engine"] == "unmapped":
                self.assertEqual(r["state"], "SPEC_ONLY", r["slug"])

    def test_unit_test_failure_caps_at_implemented(self):
        rows = audit.audit_bots(unit_ok=False)["rows"]
        self.assertFalse(any(r["state"] == "TESTED" for r in rows))

    def test_evidence_ladder(self):
        slug = "ad-copy"  # drafting bot with a passing fixture
        cases = [
            ({}, "TESTED"),
            ({"connections": FULL_EVIDENCE["connections"]}, "CONNECTED"),
            ({k: v for k, v in FULL_EVIDENCE.items() if k not in {"approval_reference"}}, "VERIFIED"),
            (FULL_EVIDENCE, "PRODUCTION"),
            ({**FULL_EVIDENCE, "benchmark_results": []}, "CONNECTED"),
            ({**FULL_EVIDENCE, "connections": [{"id": "model_router", "status": "failed", "checked_at": "x"}]}, "TESTED"),
            ({"_invalid": True}, "BLOCKED"),
        ]
        for record, expected in cases:
            with mock.patch.object(audit, "load_evidence", lambda s, r=record: (r or None) if s == slug else None):
                rows = audit.audit_bots(unit_ok=True)["rows"]
            state = next(r["state"] for r in rows if r["slug"] == slug)
            self.assertEqual(state, expected, record.keys())

    def test_committed_baseline_has_no_regressions(self):
        baseline = json.loads(audit.BASELINE.read_text())
        links = {"broken": []}
        result = audit.compare_baseline(baseline, self.rows, links, drift=False)
        self.assertEqual(result["state_drops"], [])


class RegressionGateTests(unittest.TestCase):
    rows = [{"slug": "a", "state": "TESTED", "blocked_reasons": []}, {"slug": "b", "state": "BLOCKED", "blocked_reasons": ["x"]}]

    def test_detects_drop_new_link_and_drift(self):
        base = {"bots": {"a": "TESTED", "b": "IMPLEMENTED", "gone": "SPEC_ONLY"}, "links_broken": ["old.html -> x"]}
        links = {"broken": [{"source": "old.html", "href": "x"}, {"source": "new.html", "href": "y"}]}
        result = audit.compare_baseline(base, self.rows, links, drift=True)
        self.assertEqual([d["slug"] for d in result["state_drops"]], ["b"])
        self.assertEqual(result["new_broken_links"], ["new.html -> y"])
        self.assertEqual(result["removed_bots"], ["gone"])
        self.assertFalse(result["ok"])

    def test_pre_existing_debt_passes(self):
        base = {"bots": {"a": "TESTED", "b": "BLOCKED"}, "links_broken": ["old.html -> x"]}
        links = {"broken": [{"source": "old.html", "href": "x"}]}
        self.assertTrue(audit.compare_baseline(base, self.rows, links, drift=False)["ok"])


class FolderVerdictTests(unittest.TestCase):
    def test_verdicts(self):
        v = audit.verdict
        self.assertEqual(v({"code_files": 0}), "placeholder")
        self.assertEqual(v({"code_files": 4}), "untested")
        self.assertEqual(v({"code_files": 4, "tests": {"ran": True, "passed": 5, "failed": 0}}), "working")
        self.assertEqual(v({"code_files": 4, "tests": {"ran": True, "passed": 5, "failed": 1}}), "partial")
        self.assertEqual(v({"code_files": 4, "tests": {"ran": True, "passed": 1, "failed": 4}}), "broken")
        self.assertEqual(v({"code_files": 2, "import_probe": {"modules": 2, "failed": 2}}), "broken")
        self.assertEqual(v({"code_files": 4, "tests": {"ran": True, "passed": 5}, "type_errors": 3}), "partial")
        self.assertEqual(v({"code_files": 4, "tests": {"ran": False, "reason": "no tests collected"}}), "untested")

    def test_parse_pytest(self):
        res = {"code": 1, "out": "== 1 failed, 107 passed in 2.65s ==", "err": "", "timeout": False}
        self.assertEqual(audit.parse_pytest(res)["failed"], 1)
        self.assertFalse(audit.parse_pytest({"code": 5, "out": "no tests ran in 0.00s", "err": "", "timeout": False})["ran"])
        self.assertTrue(audit.parse_pytest({"code": None, "out": "", "err": "timeout", "timeout": True})["timeout"])


class StatusFileTests(unittest.TestCase):
    def test_committed_status_is_consistent(self):
        status = json.loads(audit.STATUS.read_text())
        self.assertEqual(status["schema"], "dreamco.fleet_runtime_status.v1")
        self.assertEqual(len(status["bots"]), status["summary"]["bots"])
        self.assertEqual(sum(status["summary"]["by_state"].values()), status["summary"]["bots"])
        self.assertEqual(status["summary"]["by_state"]["PRODUCTION"], 0)
        self.assertEqual(status["bot_columns"], audit.BOT_COLUMNS)
        self.assertEqual(status["contract_pieces"], list(PIECE_IDS))
        self.assertNotIn("generated_at", status)

    def test_dashboard_page_wired(self):
        html = (ROOT / "website" / "fleet-runtime.html").read_text()
        js = (ROOT / "website" / "fleet-runtime.js").read_text()
        nav = (ROOT / "website" / "nav.js").read_text()
        self.assertIn('src="nav.js"', html)
        self.assertIn("fleet-runtime.js", html)
        self.assertIn("data/fleet-runtime-status.json", js)
        self.assertIn("'bot-' + slug", js)
        self.assertIn("fleet-runtime.html", nav)
        for control in ("fr-search", "fr-state-filter", "fr-division-filter", "fr-engine-filter", "fr-bot-table", "fr-division-table"):
            self.assertIn(f'id="{control}"', html)


if __name__ == "__main__":
    unittest.main()
