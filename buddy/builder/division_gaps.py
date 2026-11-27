"""Per-division resource check. Market data is present only if a file says so."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CROSSWALK = ROOT / "config/generated/masterbot-55-domain-crosswalk.json"


def check() -> dict:
    """Inventory canonical divisions only; repository folders are not division records."""
    if not CROSSWALK.is_file():
        raise FileNotFoundError(f"canonical division crosswalk is required: {CROSSWALK}")
    payload = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    domains = payload.get("domains")
    if not isinstance(domains, list) or not domains:
        raise ValueError("canonical division crosswalk has no domains")
    rows = []
    for domain in sorted(domains, key=lambda item: str(item.get("domain_name", ""))):
        name = str(domain.get("domain_name", "")).strip()
        if not name:
            raise ValueError("canonical division record is missing domain_name")
        manifest = ROOT / "App_bots" / f"{name}.json"
        files = 1 if manifest.is_file() else 0
        if manifest.is_file():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                files += len(data.get("files", [])) if isinstance(data.get("files"), list) else 0
            except (OSError, json.JSONDecodeError):
                pass
        rows.append({
            "division": name,
            "files": files,
            "market_data": False,
            "working": False,
            "production_ready": False,
            "manifest_present": manifest.is_file(),
            "mapping_status": domain.get("mapping_status", "unreviewed"),
            "owner_approval": domain.get("owner_approval"),
        })
    return {"divisions": rows, "working": 0, "production_ready": False}


def main() -> int:
    report = check()
    (ROOT / "reports" / "DIVISION_GAPS.json").write_text(json.dumps({"count": len(report["divisions"]), "working": 0, "production_ready": False, "sample": report["divisions"][:8]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"count": len(report["divisions"]), "working": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
