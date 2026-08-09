from __future__ import annotations

from tools.generate_revolutionary_updates import build_updates


def test_batch_contains_exactly_100_unique_updates():
    registry = build_updates()
    assert registry["count"] == 100
    ids = [item["id"] for item in registry["updates"]]
    assert len(ids) == 100
    assert len(ids) == len(set(ids))


def test_every_update_has_primary_research_and_acceptance_tests():
    registry = build_updates()
    for item in registry["updates"]:
        assert item["official_research"]
        assert all(source.startswith("https://") for source in item["official_research"])
        assert len(item["acceptance_tests"]) >= 5
        assert item["review"]["decision"] == "needed"
        assert item["review"]["not_a_certification"] is True


def test_every_update_preserves_existing_inventory_and_deduplicates():
    registry = build_updates()
    for item in registry["updates"]:
        contract = " ".join(item["implementation_contract"]).lower()
        tests = " ".join(item["acceptance_tests"]).lower()
        assert "deduplicate" in contract
        assert "preserved" in tests


def test_batch_has_ten_deep_research_themes():
    registry = build_updates()
    themes = {item["theme_id"] for item in registry["updates"]}
    assert len(themes) == 10
