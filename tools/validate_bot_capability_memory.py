"""Validate the canonical bot/capability memory contract.

This validator intentionally validates structure and migration safety rather than
pretending that catalog metadata proves a capability works.
"""

from __future__ import annotations

import json
from pathlib import Path

SCHEMA_PATH = Path("config/bot-capability-memory-schema.json")
REQUIRED_BOT_FIELDS = {
    "bot_id",
    "name",
    "original_path",
    "status",
    "capabilities",
    "tasks",
    "tools",
    "dependencies",
    "benchmarks",
    "known_limitations",
    "failure_modes",
    "migration_state",
}


def main() -> int:
    if not SCHEMA_PATH.exists():
        raise SystemExit(f"Missing schema: {SCHEMA_PATH}")

    data = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    bot = data.get("bot_record", {})
    capability = data.get("capability_record", {})

    missing_bot = sorted(REQUIRED_BOT_FIELDS - bot.keys())
    if missing_bot:
        raise SystemExit(f"Bot schema missing fields: {', '.join(missing_bot)}")

    for key in ("capabilities", "sub_capabilities", "tasks", "tools", "dependencies", "benchmarks"):
        if not isinstance(bot[key], list):
            raise SystemExit(f"Bot field must be a list: {key}")

    for key in ("origin_bot_ids", "task_examples", "benchmarks", "holdout_tests", "transfer_tests", "regression_tests"):
        if not isinstance(capability.get(key), list):
            raise SystemExit(f"Capability field must be a list: {key}")

    states = {"unmapped", "mapped", "partially_migrated", "capability_extracted", "fully_migrated"}
    if bot["migration_state"] not in states:
        raise SystemExit(f"Invalid migration state: {bot['migration_state']}")

    print("Bot capability memory schema: PASS")
    print("Lossless migration fields: PASS")
    print("Capability evidence fields: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
