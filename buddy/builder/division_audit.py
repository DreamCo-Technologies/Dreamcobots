"""Division audit. A folder is listed. Missing health evidence stays missing."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ["code", "config", "tests", "docs", "health"]


def audit() -> dict:
    rows = []
    for path in sorted(ROOT.iterdir()):
        if path.is_dir() and not path.name.startswith(".") and path.name != "node_modules":
            rows.append({"division": path.name, "present": True, "health": "not measured", "production_ready": False})
    return {"divisions": rows, "required": REQUIRED, "production_ready": False}


def main() -> int:
    report = audit()
    (ROOT / "reports" / "DIVISION_AUDIT.json").write_text(json.dumps({"count": len(report["divisions"]), "production_ready": False}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"divisions": len(report["divisions"]), "production_ready": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
