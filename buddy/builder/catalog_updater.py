"""Catalog updater. It refreshes counts and does not mark a bot ready.

Production ready requires the contract blockers to be clear and the profile
evidence to include adapter, sandbox, auth, and telemetry.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLOCKERS = ["critical_security", "missing_build", "missing_required_tests", "missing_runtime_health", "missing_observability", "unreproducible_benchmark_claim", "missing_rollback_plan"]


def update() -> dict:
    bots = sorted(path.stem for path in (ROOT / "bots").glob("*.md"))
    legacy = json.loads((ROOT / "command-center" / "data" / "legacy-bots.json").read_text())
    return {
        "new_bots": len(bots),
        "legacy_bots": len(legacy.get("bots", [])),
        "production_ready": 0,
        "blockers": BLOCKERS,
        "performance": "no runtime latency or success rate is stored for these bots",
        "updated_catalog": False,
    }


def main() -> int:
    report = update()
    path = ROOT / "reports" / "BOT_CATALOG_UPDATE.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
