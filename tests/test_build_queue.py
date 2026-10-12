import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = json.loads((ROOT / "config/bots/build-queue.json").read_text())


def test_queue_items_are_well_formed_and_inside_the_week():
    ids = [i["id"] for i in QUEUE["items"]]
    assert len(ids) == len(set(ids))
    start, end = (date.fromisoformat(QUEUE["week"][k]) for k in ("start", "end"))
    for item in QUEUE["items"]:
        assert start <= date.fromisoformat(item["day"]) <= end, item["id"]
        assert item["kind"] in {"automation", "owner_decision"}
        assert item["status"] in {"queued", "in_progress", "done", "blocked"}
        assert item["acceptance"] and item["title"]
        assert set(item["depends_on"]) <= set(ids)
        if item["kind"] == "automation":
            assert item["risk_tier"] not in {"money", "destructive"}
            assert item["owner"] != "ireanjordan24"


def test_dependencies_are_scheduled_no_later_than_dependents():
    by_id = {i["id"]: i for i in QUEUE["items"]}
    for item in QUEUE["items"]:
        for dep in item["depends_on"]:
            assert by_id[dep]["day"] <= item["day"], (dep, item["id"])


def test_acceptance_tools_exist():
    for item in QUEUE["items"]:
        for token in item["acceptance"].split():
            if token.startswith("tools/") or token.startswith("tests/"):
                assert (ROOT / token).exists(), (item["id"], token)


def test_plan_doc_lists_every_item():
    doc = (ROOT / "docs/FLEET_ONE_WEEK_BUILD_PLAN.md").read_text()
    for item in QUEUE["items"]:
        assert item["title"] in doc
