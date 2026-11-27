import json
import subprocess
import sys
from datetime import date


def test_planner_blocks_missing_provenance(tmp_path):
    src = tmp_path / "in.json"
    out = tmp_path / "out.json"
    src.write_text(json.dumps({"units": [
        {"capability_id": "c1", "objective": "learn", "benchmark": "b1"},
        {"capability_id": "c2", "objective": "learn", "benchmark": "b2", "provenance": "licensed"},
    ]}))
    subprocess.run(
        [sys.executable, "tools/bootcamp_lesson_planner.py", str(src), "--output", str(out)],
        check=True,
    )
    data = json.loads(out.read_text())
    assert data["units"][0]["status"] == "blocked"
    assert data["units"][1]["status"] == "ready"


def test_gpt_track_gets_fourteen_day_evidence_plan():
    from tools.bootcamp_lesson_planner import build_plan

    track = {
        "track_id": "ai_ml.gpt_style_model_engineering",
        "training_policy": {
            "weight_updates_authorized": False,
            "paid_compute_authorized": False,
        },
        "units": [{
            "capability_id": "GPTS-01",
            "objective": "tiny GPT baseline",
            "benchmark": "causal mask and tiny-batch overfit",
            "provenance": ["FCC-25M"],
        }],
    }
    result = build_plan(track, days=14, start=date(2026, 11, 20))
    assert result["target_date"] == "2026-12-03"
    assert result["units"][0]["scheduled_date"] == "2026-11-20"
    assert result["units"][0]["execution_status"] == "PLANNED_NOT_EXECUTED"
    assert result["units"][0]["weights_trained"] is False
    assert result["training_policy"]["weight_updates_authorized"] is False
    assert len(result["daily_growth_loop"]) >= 6
    assert result["milestones"][-1]["name"] == "graduation_review"


def test_planner_rejects_zero_day_schedule():
    from tools.bootcamp_lesson_planner import build_plan

    try:
        build_plan({"units": []}, days=0)
    except ValueError as exc:
        assert "at least 1" in str(exc)
    else:
        raise AssertionError("zero-day schedule must be rejected")
