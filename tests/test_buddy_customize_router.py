#!/usr/bin/env python3
"""Offline tests: generated-job merge, /buddy customize routing, and the apply planner."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import tools.buddy_control_plane as bcp  # noqa: E402
import tools.buddy_customize_apply as apply_mod  # noqa: E402
from test_buddy_control_plane import OWNER, REGISTRY, FakeAPI, comment_event, issue_event  # noqa: E402

PATCH = "/buddy customize ad-copy\n\n```yaml\nmodel: dreamco/fast\nenabled: false\n```\n"


def gen_job(**over):
    job = {"id": "wf_example", "family": "workflow", "title": "Example", "workflow": "example.yml",
           "risk_tier": "read_only", "requires_owner_approval": False, "triggerable": True, "inputs": {},
           "generated": True, "notes": "generated"}
    job.update(over)
    return job


class MergeGeneratedTest(unittest.TestCase):
    def test_curated_wins_and_bad_jobs_fail_closed_individually(self):
        curated_job = REGISTRY["jobs"][0]
        generated = {"jobs": [
            gen_job(),
            gen_job(id=curated_job["id"], title="shadow"),                       # same id: curated wins
            gen_job(id="wf_shadow", workflow=curated_job["workflow"]),          # same workflow: curated wins
            gen_job(id="wf_money", risk_tier="money", requires_owner_approval=True),  # triggerable money: rejected
            gen_job(id="wf_blocked", triggerable=False),                          # no blocked_reason: rejected
            gen_job(id="fleet_bot_run", workflow="fleet-bot-run.yml",
                    inputs={"bot": {"type": "string", "pattern": "^[a-z0-9-]{1,80}$", "max_length": 80}}),
            gen_job(id="fleet_division_run", workflow="fleet-bot-run.yml",
                    inputs={"division": {"type": "string", "pattern": "^[A-Za-z0-9]{2,41}$", "max_length": 41}}),
        ]}
        merged, skipped = bcp.merge_generated(REGISTRY, generated)
        ids = [j["id"] for j in merged["jobs"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("wf_example", ids)
        self.assertIn("fleet_bot_run", ids)
        self.assertIn("fleet_division_run", ids)
        self.assertNotIn("wf_shadow", ids)
        self.assertNotIn("wf_money", ids)
        self.assertNotIn("wf_blocked", ids)
        self.assertEqual(bcp.jobs_by_id(merged)[curated_job["id"]]["title"], curated_job["title"])
        self.assertEqual({s.split(":")[0] for s in skipped}, {"wf_money", "wf_blocked"})
        self.assertEqual(bcp.check_registry(merged, workflows_dir=None), [])

    def test_unreadable_generated_file_falls_back_to_curated(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "gen.json"
            bad.write_text("{not json")
            merged, skipped = bcp.load_merged(bcp.REGISTRY_PATH, bad)
        self.assertEqual(len(merged["jobs"]), len(REGISTRY["jobs"]))
        self.assertTrue(skipped)

    def test_generated_run_dispatches_through_router(self):
        merged, _ = bcp.merge_generated(REGISTRY, {"jobs": [gen_job(id="fleet_division_run", workflow="fleet-bot-run.yml",
                                                                    inputs={"division": {"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9]{1,40}$", "max_length": 41}})]})
        api = FakeAPI()
        code, _ = bcp.route(comment_event("/buddy run fleet_division_run division=DreamData"), merged, api)
        self.assertEqual(code, 0)
        self.assertEqual(api.dispatched, [("fleet-bot-run.yml", "main", {"division": "DreamData"})])
        api = FakeAPI()
        bcp.route(comment_event("/buddy run fleet_division_run division=../etc"), merged, api)
        self.assertEqual(api.dispatched, [])


class CustomizeParseTest(unittest.TestCase):
    def test_targets(self):
        for target in ["ad-copy", "division:DreamContent", "file:website/index.html"]:
            cmd = bcp.parse_command_line("/buddy customize " + target)
            self.assertEqual((cmd.verb, cmd.target), ("customize", target))
        for bad in ["/buddy customize", "/buddy customize a b", "/buddy customize Ad_Copy", "/buddy customize file:../x",
                    "/buddy customize file:a/../../etc", "/buddy customize division:Dream-Content", "/buddy customize $(id)"]:
            with self.assertRaises(bcp.CommandError, msg=bad):
                bcp.parse_command_line(bad)

    def test_body_needs_exactly_one_bounded_yaml_fence(self):
        bcp.check_customize_body(PATCH)
        for bad in ["/buddy customize x\nmodel: dreamco/fast", PATCH + "\n```yaml\na: b\n```\n",
                    "```yaml\n\n```", "```yaml\n" + "a: b\n" * 1000 + "```", "```yaml\na: \x07\n```"]:
            with self.assertRaises(bcp.CommandError):
                bcp.check_customize_body(bad)


class CustomizeRouteTest(unittest.TestCase):
    def test_operator_comment_dispatches_apply_job(self):
        api = FakeAPI()
        event = comment_event(PATCH)
        event["comment_id"] = "123456"
        code, body = bcp.route(event, REGISTRY, api)
        self.assertEqual(code, 0)
        self.assertEqual(api.dispatched, [("buddy-customize-apply.yml", "main", {"issue": "7", "comment": "123456"})])
        self.assertIn("opens a PR", body)

    def test_issue_form_dispatches_with_comment_zero(self):
        api = FakeAPI()
        code, _ = bcp.route(issue_event("/buddy customize ad-copy", PATCH), REGISTRY, api)
        self.assertEqual(code, 0)
        self.assertEqual(api.dispatched, [("buddy-customize-apply.yml", "main", {"issue": "9", "comment": "0"})])

    def test_non_operator_and_bad_patch_are_rejected_without_dispatch(self):
        for event, api in [(comment_event(PATCH, actor="mallory"), FakeAPI(permissions={"mallory": "admin"})),
                           (comment_event("/buddy customize ad-copy\nno fence here"), FakeAPI()),
                           (issue_event("/buddy customize ad-copy", PATCH, author="mallory"), FakeAPI())]:
            code, body = bcp.route(event, REGISTRY, api)
            self.assertEqual(api.dispatched, [])
            self.assertIn("rejected", body)

    def test_customize_disabled_without_registry_job(self):
        reg = copy.deepcopy(REGISTRY)
        reg["jobs"] = [j for j in reg["jobs"] if j["id"] != bcp.CUSTOMIZE_JOB_ID]
        api = FakeAPI()
        _, body = bcp.route(comment_event(PATCH), reg, api)
        self.assertEqual(api.dispatched, [])
        self.assertIn("not enabled", body)

    def test_apply_job_cannot_be_run_directly(self):
        api = FakeAPI()
        _, body = bcp.route(comment_event("/buddy run buddy_customize_apply issue=7"), REGISTRY, api)
        self.assertEqual(api.dispatched, [])
        self.assertIn("not triggerable", body)


class ApplyPlanTest(unittest.TestCase):
    def test_plan_picks_validator_and_rechecks_author(self):
        target, argv = apply_mod.plan(REGISTRY, OWNER, PATCH)
        self.assertEqual(target, "ad-copy")
        self.assertIn("buddy.fleet_runtime", argv)
        target, argv = apply_mod.plan(REGISTRY, OWNER, "/buddy customize file:website/index.html\n\n```yaml\npurpose: \"Home page\"\n```\n")
        self.assertEqual(target, "file:website/index.html")
        self.assertIn("tools/build_file_prospectus.py", argv)
        with self.assertRaises(bcp.CommandError):
            apply_mod.plan(REGISTRY, "mallory", PATCH)
        with self.assertRaises(bcp.CommandError):
            apply_mod.plan(REGISTRY, OWNER, PATCH + "\n/buddy customize other-bot\n")

    def test_apply_workflow_is_pr_only(self):
        text = (ROOT / ".github/workflows/buddy-customize-apply.yml").read_text()
        self.assertIsNone(bcp.PUSH_TO_MAIN_RE.search(text))
        self.assertIn('git push origin "HEAD:refs/heads/${branch}"', text)
        self.assertNotIn("${{ github.event.comment.body }}", text)
        self.assertNotIn("gh pr merge", text)


if __name__ == "__main__":
    unittest.main()
