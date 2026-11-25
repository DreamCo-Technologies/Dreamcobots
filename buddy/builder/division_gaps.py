"""Per-division resource check. Market data is present only if a file says so."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def check() -> dict:
    rows = []
    division_root = ROOT / "config" / "divisions"
    for config_path in sorted(division_root.glob("*.json")):
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        identity = payload.get("identity") if isinstance(payload.get("identity"), dict) else {}
        division = str(identity.get("division") or config_path.stem)
        source_paths = {
            str(row.get("source_path"))
            for row in payload.get("capabilities", [])
            if isinstance(row, dict) and isinstance(row.get("source_path"), str) and row.get("source_path")
        }
        existing_sources = [ROOT / source for source in sorted(source_paths) if (ROOT / source).is_file()]
        market = any("market" in Path(source).name.lower() for source in source_paths)
        rows.append({
            "division": division,
            "files": len(existing_sources),
            "market_data": market,
            "working": False,
            "production_ready": False,
        })
    return {"divisions": rows, "working": 0, "production_ready": False}


def main() -> int:
    report = check()
    (ROOT / "reports" / "DIVISION_GAPS.json").write_text(json.dumps({"count": len(report["divisions"]), "working": 0, "production_ready": False, "sample": report["divisions"][:8]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"count": len(report["divisions"]), "working": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
