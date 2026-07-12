from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_json(relative_path: str):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def test_master_registry_covers_all_divisions_and_bot_profiles():
    divisions = load_json("config/divisions.json")["divisions"]
    registry = load_json("config/master_bot_registry.json")
    profile_count = len(list((ROOT / "bots").glob("*/bot_profile.json")))

    assert registry["summary"]["division_count"] == 45
    assert len(registry["divisions"]) == len(divisions) == 45
    assert len(registry["bots"]) == profile_count
    assert all(division["bot_count"] > 0 for division in registry["divisions"])


def test_every_bot_has_blueprint_and_cash_safety_gates():
    registry = load_json("config/master_bot_registry.json")
    assert registry["summary"]["autonomous_cash_enabled"] is False
    assert registry["autonomy_policy"]["human_approval_required_for_money_movement"] is True

    for bot in registry["bots"]:
        assert bot["emoji"].strip()
        assert bot["dashboard_url"] == f"docs/bots/index.html?bot={bot['slug']}"
        assert bot["prospectus_url"].endswith(f"?bot={bot['slug']}#prospectus")
        blueprint = bot["blueprint"]
        assert blueprint["schema"] == "bot_blueprint.v1"
        assert blueprint["storage"]["mode"] == "local-first"
        assert blueprint["governance"]["approval_required_for_revenue"] is True
        assert blueprint["governance"]["approval_required_for_spend"] is True
        assert blueprint["identity"]["emoji"] == bot["emoji"]
        assert bot["safety"]["autonomous_cash_enabled"] is False
        assert bot["safety"]["enterprise_ai_approval_claim"] is False


def test_control_tower_catalog_matches_master_registry():
    registry = load_json("config/master_bot_registry.json")
    catalog = load_json("dreamco-control-tower/config/generated/bots.catalog.json")

    assert catalog["summary"]["bot_count"] == registry["summary"]["bot_count"]
    assert catalog["summary"]["division_count"] == registry["summary"]["division_count"]
    assert len(catalog["bots"]) == len(registry["bots"])
    assert len(catalog["divisions"]) == len(registry["divisions"])
    assert all(bot["governance"]["autonomous_cash_enabled"] is False for bot in catalog["bots"])
    assert all(bot["emoji"].strip() for bot in catalog["bots"])
    assert all(bot["dashboardUrl"] and bot["prospectusUrl"] for bot in catalog["bots"])


def test_generated_bot_experience_covers_every_registered_bot():
    registry = load_json("config/master_bot_registry.json")
    experience = load_json("docs/bots/bots.json")

    assert experience["bot_count"] == registry["summary"]["bot_count"]
    assert len(experience["bots"]) == len(registry["bots"])
    assert {bot["slug"] for bot in experience["bots"]} == {
        bot["slug"] for bot in registry["bots"]
    }
    assert (ROOT / "docs/bots/index.html").exists()


def test_local_first_storage_policy_defines_approval_gates():
    policy = load_json("config/local_first_storage_policy.json")
    gates = set(policy["approval_gates"])

    assert policy["defaults"]["storage_mode"] == "local-first"
    assert "paid_campaigns" in gates
    assert "payouts_or_transfers" in gates
    assert "external_outreach" in gates
