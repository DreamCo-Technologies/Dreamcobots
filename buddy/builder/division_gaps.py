"""Per-division resource check. Market data is present only if a file says so."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def check() -> dict:
    rows = []
    for path in sorted(ROOT.iterdir()):
        if not path.is_dir() or path.name.startswith(".") or path.name == "node_modules":
            continue
        files = sum(1 for item in path.rglob("*") if item.is_file())
        market = any("market" in item.name.lower() for item in path.glob("*") if item.is_file())
        rows.append({"division": path.name, "files": files, "market_data": market, "working": False, "production_ready": False})
    return {"divisions": rows, "working": 0, "production_ready": False}


def main() -> int:
    report = check()
    (ROOT / "reports" / "DIVISION_GAPS.json").write_text(json.dumps({"count": len(report["divisions"]), "working": 0, "production_ready": False, "sample": report["divisions"][:8]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"count": len(report["divisions"]), "working": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
