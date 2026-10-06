"""Division resource check. Market data is not invented."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def resources() -> dict:
    divisions = sorted(path.name for path in ROOT.iterdir() if path.is_dir() and not path.name.startswith(".") and path.name != "node_modules")
    return {"divisions": len(divisions), "code_folder": len(divisions), "market_data": "not measured", "top_competitor": False, "production_ready": False}


def main() -> int:
    report = resources()
    (ROOT / "reports" / "DIVISION_RESOURCES.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
