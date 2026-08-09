from __future__ import annotations

from tools.buddy_continuous_expansion import build_expansion_plan


def test_expansion_plan_preserves_existing_assets():
    plan = build_expansion_plan()
    assert plan["preserve_existing"] is True


def test_expansion_plan_invents_new_systems():
    plan = build_expansion_plan()
    proposals = plan["invented_system_proposals"]
    assert len(proposals) >= 10
    assert any(item["id"] == "innovation-composer-bot" for item in proposals)


def test_library_specialists_are_distinct_proposals():
    plan = build_expansion_plan()
    ids = [item["id"] for item in plan["library_specialist_proposals"]]
    assert "library-specialist:python:pandas" in ids
    assert "library-specialist:javascript:react" in ids
    assert len(ids) == len(set(ids))


def test_existing_inventory_is_detected_without_mutation():
    plan = build_expansion_plan()
    assert plan["existing_bot_count_detected"] > 0
