from __future__ import annotations

from tools.build_master_bot_consolidation import build_plan, load_bots, overlap


def test_consolidation_scans_existing_fleet_without_deleting_profiles():
    plan = build_plan()
    assert plan["fleet_profiles_scanned"] == len(load_bots())
    assert plan["fleet_profiles_scanned"] > 0
    assert all(item["original_profile_preserved"] is True for item in plan["proposals"])


def test_one_master_is_selected_per_detected_division():
    plan = build_plan()
    assert plan["divisions"] == len(plan["division_masters"])
    assert plan["divisions"] > 0
    assert len(set(plan["division_masters"].values())) == plan["divisions"]


def test_missing_usage_telemetry_is_not_treated_as_zero_usage():
    plan = build_plan()
    if not plan["usage_telemetry_available"]:
        assert plan["low_use_rule_active"] is False
        assert all(item["executions"] is None for item in plan["proposals"])
        assert all(not any("usage <=" in reason for reason in item["reason"]) for item in plan["proposals"])


def test_overlap_is_bounded():
    bots = load_bots()
    if len(bots) >= 2:
        value = overlap(bots[0], bots[1])
        assert 0.0 <= value <= 1.0


def test_merge_proposals_are_reversible_aliases():
    plan = build_plan()
    for item in plan["proposals"]:
        assert item["alias_slug"] != item["master_slug"]
        assert item["activation_mode"] == "reversible_alias"
        assert item["status"] in {"ready_for_regression_testing", "master_capability_union_required"}
