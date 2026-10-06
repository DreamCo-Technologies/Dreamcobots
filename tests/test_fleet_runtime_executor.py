"""Unit and smoke tests for the shared fleet runtime (buddy/fleet_runtime)."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from buddy.fleet_runtime import CONTRACT_PIECES, FleetExecutor, engines, permissions, router  # noqa: E402
from buddy.fleet_runtime.contract import (  # noqa: E402
    load_fixtures, load_manifests, load_schema, expand, validate, validate_bot_manifest,
)
from buddy.fleet_runtime.smoke import check_expectations, fixture_smoke, generic_smoke  # noqa: E402
from buddy.safety.guardrails import review  # noqa: E402

MANIFEST = {
    "slug": "unit-bot", "name": "Unit Bot", "division": "CommandCore", "description": "Test bot.",
    "capabilities": ["Cost analysis", "KPI tracking", "Send weekly report email"],
    "engine": "analysis",
}
OFFLINE = {"mode": "offline_only", "offline_fallback": "deterministic", "live_alias": "none", "live_requires": []}


class EngineTests(unittest.TestCase):
    def test_analysis_refuses_to_invent_data(self):
        out = engines.analysis(MANIFEST, {"objective": "analyse"}, OFFLINE)
        self.assertEqual(out["status"], "needs_input")
        self.assertNotIn("numeric_fields", out)

    def test_analysis_stats_groups_filters(self):
        task = {"objective": "cost analysis", "input": {
            "records": [{"g": "a", "v": 1}, {"g": "a", "v": 3}, {"g": "b", "v": 10}, {"g": "b", "v": True}],
            "metric": "v", "group_by": "g", "filters": {}, "top_n": 2}}
        out = engines.analysis(MANIFEST, task, OFFLINE)
        self.assertEqual(out["numeric_fields"]["v"], {"count": 3, "sum": 14.0, "mean": 4.666667, "min": 1.0, "max": 10.0})
        self.assertEqual(out["groups"]["a"], {"count": 2, "sum": 4.0, "mean": 2.0})
        self.assertEqual([r["v"] for r in out["top"]], [10, 3])
        self.assertIn("Cost analysis", out["capabilities_considered"])
        filtered = engines.analysis(MANIFEST, {"objective": "x", "input": {**task["input"], "filters": {"g": "b"}}}, OFFLINE)
        self.assertEqual(filtered["row_count"], 2)

    def test_analysis_values_shortcut(self):
        out = engines.analysis(MANIFEST, {"objective": "x", "input": {"values": [2, 4]}}, OFFLINE)
        self.assertEqual(out["numeric_fields"]["value"]["mean"], 3.0)

    def test_classification_ranks_and_escalates(self):
        out = engines.classification(MANIFEST, {"objective": "x", "input": {"text": "urgent: track the KPI dashboard"}}, OFFLINE)
        self.assertEqual(out["top_label"], "KPI tracking")
        self.assertTrue(out["escalate_to_human"])
        none = engines.classification(MANIFEST, {"objective": "x", "input": {"text": "zebra"}}, OFFLINE)
        self.assertIsNone(none["top_label"])
        self.assertTrue(none["uncertain"])

    def test_workflow_gates_live_steps(self):
        out = engines.workflow(MANIFEST, {"objective": "plan", "input": {"completed_steps": ["Prepare: Cost analysis"]}}, OFFLINE)
        self.assertEqual(out["progress"], {"done": 1, "total": 3})
        self.assertEqual(out["next_actions"], ["Prepare: KPI tracking"])
        self.assertEqual(out["awaiting_owner_approval"], ["Prepare: Send weekly report email"])

    def test_drafting_offline_is_labelled(self):
        out = engines.drafting(MANIFEST, {"objective": "KPI tracking memo"}, {**OFFLINE, "mode": "offline_first"}, env={})
        self.assertEqual(out["generated_by"], "offline_deterministic")
        self.assertIn("No model was called", out["draft_markdown"])
        self.assertEqual(out["sections"], ["KPI tracking"])


class RouterTests(unittest.TestCase):
    def test_live_requires_flag_and_key(self):
        self.assertFalse(router.live_enabled({}))
        self.assertFalse(router.live_enabled({"OPENROUTER_API_KEY": "x"}))
        self.assertFalse(router.live_enabled({router.LIVE_FLAG: "1"}))
        self.assertTrue(router.live_enabled({router.LIVE_FLAG: "1", "OPENROUTER_API_KEY": "x"}))

    def test_offline_only_never_goes_live(self):
        env = {router.LIVE_FLAG: "1", "OPENROUTER_API_KEY": "x"}
        with mock.patch("buddy.openrouter.gateway.BuddyGateway.chat", side_effect=AssertionError("network")):
            out = router.complete("hi", OFFLINE, lambda: "offline text", env=env)
        self.assertEqual(out["mode"], "offline_deterministic")

    def test_live_path_reuses_buddy_gateway(self):
        env = {router.LIVE_FLAG: "1", "OPENROUTER_API_KEY": "test-key"}
        fake = {"model": "m", "choices": [{"message": {"content": "live text"}}]}
        with mock.patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}), \
                mock.patch("buddy.openrouter.gateway.BuddyGateway.chat", return_value=fake) as chat:
            out = router.complete("hi", {"mode": "offline_first", "live_alias": "dreamco/auto"}, lambda: "x", env=env)
        chat.assert_called_once()
        self.assertEqual((out["mode"], out["text"]), ("live_model", "live text"))


class PermissionTests(unittest.TestCase):
    def test_fallback_matches_policy_file(self):
        self.assertEqual(permissions.load_levels(), permissions.FALLBACK_LEVELS)

    def test_decisions(self):
        self.assertTrue(permissions.decide("sandbox", "sandbox")["allowed"])
        self.assertTrue(permissions.decide("plan_only", "read_only")["allowed"])
        for level in ("external_side_effect", "destructive", "production_deploy", "repository_write"):
            self.assertFalse(permissions.decide("sandbox", level)["allowed"], level)
        self.assertEqual(permissions.decide("sandbox", "nope")["decision"], "unknown_level")
        self.assertFalse(permissions.decide("read_only", "sandbox")["allowed"])


class ContractTests(unittest.TestCase):
    def test_sixteen_pieces(self):
        self.assertEqual(len(CONTRACT_PIECES), 16)
        self.assertEqual(len({p["id"] for p in CONTRACT_PIECES}), 16)

    def test_validator_catches_errors(self):
        schema = load_schema()
        errors = validate({"slug": "Bad Slug"}, schema["$defs"]["botManifest"], schema)
        self.assertTrue(any("missing required 'division'" in e for e in errors))
        self.assertTrue(any("does not match" in e for e in errors))

    def test_every_expanded_manifest_validates(self):
        collection = load_manifests()
        schema = load_schema()
        for compact in collection["bots"]:
            self.assertEqual(validate_bot_manifest(expand(compact, collection), schema), [], compact["slug"])

    def test_guardrail_key_prefix_regression(self):
        self.assertTrue(review("risk-assessor task-runner desk-chrome")["allowed"])
        self.assertFalse(review("token sk-live123")["allowed"])


class ExecutorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ex = FleetExecutor(env={})

    def test_unknown_bot_is_structured_error(self):
        out = self.ex.run("no-such-bot", {"objective": "x"})
        self.assertEqual((out["status"], out["error"]["type"]), ("error", "unknown_bot"))
        self.assertTrue(out["evidence"]["run_id"])

    def test_invalid_input(self):
        out = self.ex.run("analytics-hub", {"input": {}})
        self.assertEqual(out["status"], "invalid_input")

    def test_unmapped_bot_is_not_faked(self):
        slug = next(s for s, b in self.ex.bots.items() if b["engine"] == "unmapped")
        out = self.ex.run(slug, {"objective": "x"})
        self.assertEqual(out["status"], "unmapped")
        self.assertIsNone(out["result"])

    def test_permission_gate(self):
        out = self.ex.run("analytics-hub", {"objective": "x", "action_level": "external_side_effect"})
        self.assertEqual(out["status"], "approval_required")
        self.assertFalse(out["live_external_action_taken"])

    def test_guardrail_blocks_key_shaped_input(self):
        out = self.ex.run("analytics-hub", {"objective": "use key ghp_abcdef123456", "input": {}})
        self.assertEqual(out["status"], "guardrail_blocked")

    def test_engine_exception_is_contained(self):
        with mock.patch.dict(engines.ENGINE_FUNCS, {"analysis": mock.Mock(side_effect=RuntimeError("boom"))}):
            out = self.ex.run("analytics-hub", {"objective": "x"})
        self.assertEqual((out["status"], out["error"]["type"], out["error"]["class"]), ("error", "exception", "RuntimeError"))

    def test_invalid_output_is_caught(self):
        with mock.patch.dict(engines.ENGINE_FUNCS, {"analysis": mock.Mock(return_value={"status": "weird"})}):
            out = self.ex.run("analytics-hub", {"objective": "x"})
        self.assertEqual(out["error"]["type"], "invalid_output")

    def test_evidence_is_deterministic(self):
        task = {"objective": "Summarise", "input": {"values": [1, 2]}}
        a, b = self.ex.run("analytics-hub", task), self.ex.run("analytics-hub", task)
        self.assertEqual(a["evidence"]["run_id"], b["evidence"]["run_id"])
        self.assertNotIn("recorded_at", a["evidence"])

    def test_generic_smoke_runs_every_mapped_bot_offline(self):
        results = [generic_smoke(self.ex, slug) for slug in sorted(self.ex.bots)]
        mapped = [r for r in results if r["status"] != "unmapped"]
        failed = [r["slug"] for r in mapped if not r["passed"]]
        self.assertEqual(failed, [])
        self.assertGreater(len(mapped), 0)

    def test_bot_fixtures_pass_and_match_engine(self):
        fixtures = load_fixtures()["fixtures"]
        self.assertGreaterEqual(len(fixtures), 8)
        for slug, fixture in fixtures.items():
            self.assertEqual(self.ex.manifest(slug)["engine"], fixture["engine"], slug)
            result = fixture_smoke(self.ex, slug, fixture)
            self.assertTrue(result["passed"], (slug, result["failures"]))

    def test_expectation_language(self):
        out = {"a": {"b": [1, 2]}, "s": "hello"}
        self.assertEqual(check_expectations(out, [{"path": "a.b.1", "equals": 2}, {"path": "s", "contains": "ell"}]), [])
        self.assertEqual(len(check_expectations(out, [{"path": "a.b.0", "gte": 5}, {"path": "missing", "truthy": True}])), 2)

    def test_cli_run(self):
        from buddy.fleet_runtime.__main__ import main
        with mock.patch("sys.stdout"):
            self.assertEqual(main(["run", "analytics-hub", "--objective", "x", "--input", json.dumps({"values": [1]})]), 0)


if __name__ == "__main__":
    unittest.main()


# --- generated fixtures and the Run with Buddy job --------------------------------

def test_every_mapped_bot_has_a_generated_fixture_that_passes():
    from buddy.fleet_runtime.contract import load_fixtures
    from buddy.fleet_runtime.smoke import fixture_smoke

    executor = FleetExecutor(customizations={})
    fixtures = load_fixtures()["fixtures"]
    mapped = [s for s, b in executor.bots.items() if b["engine"] != "unmapped"]
    assert set(mapped) <= set(fixtures)
    failed = [s for s in mapped if not fixture_smoke(executor, s, fixtures[s])["passed"]]
    assert failed == []


def test_generated_fixture_fails_when_bot_wiring_is_wrong():
    """A fixture must catch a bot whose capabilities do not match its manifest."""
    import copy

    from buddy.fleet_runtime.fixtures import derive_fixture
    from buddy.fleet_runtime.smoke import fixture_smoke

    executor = FleetExecutor(customizations={})
    slug = next(s for s, b in executor.bots.items() if b["engine"] == "classification")
    manifest = executor.manifest(slug)
    fixture = derive_fixture("classification", manifest["capabilities"])
    broken = copy.deepcopy(manifest)
    broken["capabilities"] = ["Completely unrelated label", "Another unrelated label"]
    executor._expanded[slug] = broken
    assert fixture_smoke(executor, slug, fixture)["passed"] is False


def test_job_refuses_money_destructive_and_disabled(tmp_path):
    from buddy.fleet_runtime.__main__ import run_job

    executor = FleetExecutor(customizations={"ad-copy": {"enabled": False}})
    assert run_job(executor, "stripe-billing", None) == 3
    destructive = next(s for s, b in executor.bots.items() if b["run"] == "blocked_destructive")
    assert run_job(executor, destructive, None) == 3
    assert run_job(executor, "ad-copy", None) == 3
    out = tmp_path / "e.json"
    assert run_job(FleetExecutor(customizations={}), "blog-writer", str(out)) == 0
    record = json.loads(out.read_text())
    assert record["status"] == "passed" and record["live_external_action_taken"] is False
