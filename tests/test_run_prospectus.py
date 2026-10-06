"""Run with Buddy prospectus: one card format for workflows and bots, and the button gate."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

import build_actions_prospectus as bap  # noqa: E402

CARDS = json.loads((ROOT / "website/data/run-prospectus.json").read_text())
BOTS = json.loads((ROOT / "website/data/run-prospectus-bots.json").read_text())
REGISTRY = json.loads((ROOT / "config/buddy/run-with-buddy.generated.json").read_text())


def test_outputs_current_and_every_button_has_a_prospectus():
    assert bap.main(["--check", "--check-buttons"]) == 0


def test_workflow_count_matches_live_directory():
    live = len(list((ROOT / ".github/workflows").glob("*.y*ml")))
    health = json.loads((ROOT / "website/data/actions-health-report.json").read_text())
    public = json.loads((ROOT / "website/data/actions-prospectus.json").read_text())
    assert health["workflow_count"] == public["workflow_count"] == len(CARDS["workflows"]) == live


def test_every_bot_has_a_card_and_cards_resolve_complete():
    status = json.loads((ROOT / "website/data/fleet-runtime-status.json").read_text())
    assert {r[0] for r in status["bots"]} == {r[0] for r in BOTS["rows"]}
    for row in BOTS["rows"]:
        card = bap.resolve(row, CARDS["templates"], CARDS["operators"])
        assert bap.card_problems(card) == [], row[0]


def test_money_and_destructive_never_triggerable():
    for row in BOTS["rows"]:
        card = bap.resolve(row, CARDS["templates"], CARDS["operators"])
        if card["risk_tier"] in {"money", "destructive"}:
            assert not card["trigger"]["triggerable"] and card["trigger"]["command"] is None
    for card in CARDS["workflows"]:
        if card["risk_tier"] in {"money", "destructive"}:
            assert not card["trigger"]["triggerable"]
    for job in REGISTRY["jobs"]:
        if job["risk_tier"] == "money":
            assert job["triggerable"] is False


def test_button_gate_fails_when_a_card_is_missing_or_incomplete():
    cards = json.loads(json.dumps(CARDS))
    dropped = cards["workflows"].pop(3)
    problems = bap.check_buttons(cards, REGISTRY, BOTS)
    assert any(dropped["id"] in p and "no prospectus card" in p for p in problems)
    cards = json.loads(json.dumps(CARDS))
    cards["workflows"][0]["secrets"] = []
    cards["workflows"][1]["links"]["evidence"] = ""
    problems = bap.check_buttons(cards, REGISTRY, BOTS)
    assert any("missing secrets" in p for p in problems) and any("links.evidence" in p for p in problems)
    bots = json.loads(json.dumps(BOTS))
    bots["rows"] = bots["rows"][1:]
    assert any("no prospectus card" in p for p in bap.check_buttons(CARDS, REGISTRY, bots))


def _classify(name: str, text: str) -> dict:
    return bap.classify_workflow(name, text, bap._load_yaml(text))


def test_classify_workflow_tiers():
    ro = "name: X\non:\n  workflow_dispatch:\npermissions:\n  contents: read\njobs:\n  a:\n    runs-on: ubuntu-latest\n    timeout-minutes: 7\n    steps:\n      - run: echo ${{ secrets.MY_KEY }}\n"
    info = _classify("x.yml", ro)
    assert (info["risk_tier"], info["triggerable"], info["secrets"], info["timeout_minutes"]) == ("read_only", True, ["MY_KEY"], 7)
    push = ro.replace("contents: read", "contents: write").replace("echo ${{ secrets.MY_KEY }}", "git push origin main")
    info = _classify("x.yml", push)
    assert info["risk_tier"] == "writes_code" and not info["triggerable"] and "PR-only" in info["blocked_reason"]
    pr = push.replace("git push origin main", "gh pr create --fill")
    info = _classify("x.yml", pr)
    assert info["risk_tier"] == "writes_code" and info["triggerable"] and info["requires_owner_approval"]
    destructive = ro.replace("echo ${{ secrets.MY_KEY }}", "git push origin --delete old-branch")
    assert _classify("x.yml", destructive)["risk_tier"] == "destructive"
    assert _classify("stripe-sync.yml", ro)["risk_tier"] == "money"
    no_dispatch = ro.replace("workflow_dispatch:", "push:")
    assert "workflow_dispatch" in _classify("x.yml", no_dispatch)["blocked_reason"]
    no_perms = ro.replace("permissions:\n  contents: read\n", "")
    assert _classify("x.yml", no_perms)["risk_tier"] == "unknown_permissions"
    req = ro.replace("  workflow_dispatch:\n", "  workflow_dispatch:\n    inputs:\n      target:\n        required: true\n        type: string\n")
    assert "anchored pattern" in _classify("x.yml", req)["blocked_reason"]
    choice = ro.replace("  workflow_dispatch:\n", "  workflow_dispatch:\n    inputs:\n      mode:\n        type: choice\n        options: [quick, full]\n")
    assert _classify("x.yml", choice)["inputs"] == {"mode": {"type": "choice", "options": ["quick", "full"], "default": "quick"}}


def test_fleet_bot_job_registered_with_anchored_input():
    job = next(j for j in REGISTRY["jobs"] if j["id"] == bap.BOT_JOB_ID)
    assert job["workflow"] == "fleet-bot-run.yml" and job["risk_tier"] == "read_only"
    assert job["inputs"]["bot"]["pattern"].startswith("^") and job["inputs"]["bot"]["pattern"].endswith("$")
    wf = (ROOT / ".github/workflows/fleet-bot-run.yml").read_text()
    assert "contents: read" in wf and "secrets." not in wf


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_pages_patch_builder_output_is_accepted_by_validator():
    from buddy.fleet_runtime.customize import extract_from_issue, validate_bot_patch

    script = (
        "require('./website/buddy-run.js');"
        "const B=globalThis.BuddyRun;"
        "const p=B.buildPatch({enabled:false,prompt:'Say \"hi\" & keep it short',model:'dreamco/fast',schedule:'17 9 * * 1',capabilities:{'SEO':false}});"
        "process.stdout.write(B.customizeBody('ad-copy',p));"
    )
    body = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    target, patch = extract_from_issue(body)
    assert target == "ad-copy"
    assert patch["prompt"] == 'Say "hi" & keep it short' and patch["capabilities"] == {"SEO": False}
    patch.pop("capabilities")
    assert validate_bot_patch(target, patch)


def test_generated_registry_jobs_satisfy_control_plane_rules():
    """Shape rules enforced by tools/buddy_control_plane.py check_registry (#13197), so the router can merge these jobs."""
    import re

    registry = json.loads((ROOT / "config/buddy/run-with-buddy.generated.json").read_text())
    ids = set()
    for job in registry["jobs"]:
        assert re.fullmatch(r"[a-z][a-z0-9_]{1,63}", job["id"]) and job["id"] not in ids
        ids.add(job["id"])
        assert job["risk_tier"] in {"read_only", "writes_reports", "writes_code", "money"}
        assert isinstance(job["triggerable"], bool) and isinstance(job["requires_owner_approval"], bool)
        if not job["triggerable"]:
            assert job.get("blocked_reason"), job["id"]
        if job["risk_tier"] in {"writes_code", "money"}:
            assert job["requires_owner_approval"] is True, job["id"]
        if job["risk_tier"] == "money" or job.get("destructive"):
            assert job["triggerable"] is False, job["id"]
        assert len(job["inputs"]) <= 10
