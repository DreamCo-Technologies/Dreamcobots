"""Every division works: manifest, division smoke through the shared runtime, auditor state, prospectus + Run job."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from buddy.fleet_runtime import FleetExecutor  # noqa: E402
from buddy.fleet_runtime.__main__ import run_divisions  # noqa: E402
from buddy.fleet_runtime.contract import load_manifests  # noqa: E402
from buddy.fleet_runtime.customize import PatchError, effective_customization, validate_division_patch  # noqa: E402
from buddy.fleet_runtime.divisions import build_division_manifests, division_smoke  # noqa: E402

DIVISIONS = {d["name"]: d for d in json.loads((ROOT / "config/bots/division-manifests.generated.json").read_text())["divisions"]}
APP_DIVISIONS = sorted({json.loads(p.read_text())["division"] for p in (ROOT / "App_bots").glob("*.json")
                        if json.loads(p.read_text()).get("bots")})


def test_every_app_bots_division_has_a_manifest():
    assert len(APP_DIVISIONS) == 55
    assert set(APP_DIVISIONS) <= set(DIVISIONS)
    for name in APP_DIVISIONS:
        d = DIVISIONS[name]
        assert d["bots"] > 0 and d["smoke_bots"] and f"App_bots/{name}.json" in d["sources"], name
        assert d["triggerable"] is True, name


def test_division_manifests_are_generated_not_hand_edited():
    import generate_bot_manifests as gen

    text = gen.render_divisions(load_manifests())
    assert (ROOT / "config/bots/division-manifests.generated.json").read_text() == text


@pytest.mark.parametrize("name", APP_DIVISIONS)
def test_division_smoke_runs_its_own_bots_end_to_end_offline(name):
    executor = FleetExecutor(env={}, customizations={})
    result = division_smoke(executor, DIVISIONS[name])
    assert result["ran"] >= 1 and result["passed"], result
    for r in result["results"]:
        assert executor.bots[r["bot"]]["division"] == name


def test_smoke_bot_selection_is_one_per_engine_preferring_runnable():
    collection = load_manifests()
    by_slug = {b["slug"]: b for b in collection["bots"]}
    for d in build_division_manifests(collection)["divisions"]:
        engines = [by_slug[s]["engine"] for s in d["smoke_bots"]]
        assert len(engines) == len(set(engines))
        for slug in d["smoke_bots"]:
            same = [b for b in collection["bots"] if b["division"] == d["name"] and b["engine"] == by_slug[slug]["engine"]]
            if any(b["run"] == "allowed" for b in same):
                assert by_slug[slug]["run"] == "allowed"


def test_division_smoke_fails_when_a_smoke_bot_is_miswired():
    executor = FleetExecutor(env={}, customizations={})
    d = DIVISIONS["DreamContent"]
    slug = d["smoke_bots"][0]
    broken = dict(executor.manifest(slug))
    broken["capabilities"] = ["Zebra quilting", "Lunar pottery"]
    executor._expanded[slug] = broken
    assert division_smoke(executor, d)["passed"] is False


def test_auditor_reports_a_state_for_every_division():
    status = json.loads((ROOT / "website/data/fleet-runtime-status.json").read_text())
    states = {d["name"]: d for d in status["divisions"]}
    assert set(states) == set(DIVISIONS)
    for name in APP_DIVISIONS:
        assert states[name]["state"] == "TESTED" and states[name]["smoke_passed"], name
    assert states["UNASSIGNED"]["state"] == "SPEC_ONLY"
    assert sum(status["summary"]["divisions_by_state"].values()) == len(DIVISIONS)


def test_every_division_has_a_complete_prospectus_card_and_run_job():
    import build_actions_prospectus as bap

    cards = json.loads((ROOT / "website/data/run-prospectus.json").read_text())
    by_id = {c["id"]: c for c in cards["divisions"]}
    for name in DIVISIONS:
        assert bap.card_problems(by_id["division:" + name]) == [], name
    for name in APP_DIVISIONS:
        assert by_id["division:" + name]["trigger"]["command"] == f"/buddy run fleet_division_run division={name}"
    assert by_id["division:UNASSIGNED"]["trigger"]["triggerable"] is False
    registry = json.loads((ROOT / "config/buddy/run-with-buddy.generated.json").read_text())
    job = next(j for j in registry["jobs"] if j["id"] == "fleet_division_run")
    assert job["workflow"] == "fleet-bot-run.yml" and job["risk_tier"] == "read_only"
    bots = json.loads((ROOT / "website/data/run-prospectus-bots.json").read_text())
    broken = json.loads(json.dumps(cards))
    dropped = broken["divisions"].pop(0)["id"].split(":", 1)[1]
    assert f"division {dropped}: no prospectus card" in bap.check_buttons(broken, registry, bots)


def test_division_customization_validation_and_precedence():
    assert validate_division_patch("DreamContent", {"model": "dreamco/fast", "enabled": False})
    for bad, msg in [({"run_policy": "allowed"}, "protected"),
                     ({"display_name": "Renamed"}, "not an editable division field"),
                     ({"secret_token": "x"}, "protected"),
                     ({"model": "gpt-4"}, "allowlist")]:
        with pytest.raises(PatchError) as info:
            validate_division_patch("DreamContent", bad)
        assert msg in str(info.value), (bad, str(info.value))
    with pytest.raises(PatchError):
        validate_division_patch("UNASSIGNED", {"enabled": False})
    merged = effective_customization({"division:DreamContent": {"enabled": False, "model": "dreamco/fast"},
                                      "x-bot": {"enabled": True}}, "x-bot", "DreamContent")
    assert merged == {"enabled": True, "model": "dreamco/fast"}


def test_division_disable_reaches_runtime_but_never_money_bots():
    collection = load_manifests()
    slug = DIVISIONS["DreamContent"]["smoke_bots"][0]
    ex = FleetExecutor(env={}, customizations={"division:DreamContent": {"enabled": False}})
    assert ex.manifest(slug).get("enabled") is False
    money = next(b for b in collection["bots"] if b["run"] == "blocked_money")
    ex2 = FleetExecutor(env={}, customizations={"division:" + money["division"]: {"enabled": False}})
    assert ex2.manifest(money["slug"]).get("enabled") is not False


def test_division_job_refuses_unassigned_and_disabled_and_runs_otherwise(tmp_path, capsys):
    ns = lambda name, out=None: argparse.Namespace(cmd="division-job", name=name, out=out)  # noqa: E731
    assert run_divisions(FleetExecutor(env={}, customizations={}), ns("UNASSIGNED")) == 3
    assert run_divisions(FleetExecutor(env={}, customizations={"division:DreamContent": {"enabled": False}}), ns("DreamContent")) == 3
    assert run_divisions(FleetExecutor(env={}, customizations={}), ns("NoSuchDivision")) == 2
    out = tmp_path / "d.json"
    assert run_divisions(FleetExecutor(env={}, customizations={}), ns("DreamData", str(out))) == 0
    record = json.loads(out.read_text())
    assert record["status"] == "passed" and record["live_external_action_taken"] is False
    assert record["smoke"]["ran"] >= 1
