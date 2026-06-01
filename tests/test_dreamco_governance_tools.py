from __future__ import annotations

import json

from tools.audit_capabilities import audit_capabilities, load_registered_capabilities
from tools.dreamco_council import COUNCIL, run_council
from tools.validate_bot_registry import validate_bot_registry


def test_validate_bot_registry_flags_duplicates_and_missing_fields():
    registry = {
        "bots": [
            {"id": "alpha_bot", "name": "Alpha Bot", "division": "Ops", "capabilities": []},
            {"id": "alpha_bot", "name": "Alpha Bot", "division": "", "capabilities": [{"intent": "x"}]},
        ]
    }
    issues = validate_bot_registry(registry)
    assert any("duplicate bot ID 'alpha_bot'" in issue for issue in issues)
    assert any("duplicate slug 'alpha-bot'" in issue for issue in issues)
    assert any("missing category/division" in issue for issue in issues)
    assert any("missing capabilities" in issue for issue in issues)


def test_audit_capabilities_flags_empty_duplicate_and_unregistered(tmp_path):
    bot_library = tmp_path / "bot_library.py"
    bot_library.write_text(
        """
class BotEntry:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

_DREAMCO_BOTS = [
    BotEntry(capabilities=["registered_a", "registered_b"]),
]
""".strip()
        + "\n",
        encoding="utf-8",
    )
    registered = load_registered_capabilities(bot_library)
    assert registered == {"registered_a", "registered_b"}

    registry = {
        "bots": [
            {"id": "a", "capabilities": []},
            {
                "id": "b",
                "capabilities": [
                    {"intent": "registered_a"},
                    {"intent": "registered_a"},
                    {"intent": "unknown_cap"},
                ],
            },
        ]
    }
    issues = audit_capabilities(registry, registered)
    assert "a: empty capability list" in issues
    assert "b: duplicate capability 'registered_a'" in issues
    assert "b: unregistered capability 'unknown_cap'" in issues


def test_council_uses_all_global_ai_models():
    result = run_council("Safe change with tests and audit trail.")
    assert result["models_in_global_ai_registry"] == 100
    assert result["all_models_considered"] is True
    assert len(result["votes"]) == len(COUNCIL)
    assert json.dumps(result)
