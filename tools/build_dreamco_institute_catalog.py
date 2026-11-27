"""Synchronize the canonical academic catalog into the static Pages data tree."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "dreamco-institute-academic-catalog.json"
OUTPUT = ROOT / "website" / "data" / "dreamco-institute-academic-catalog.json"


def build() -> str:
    catalog = json.loads(SOURCE.read_text(encoding="utf-8"))
    if catalog.get("schema") != "dreamco.institute.academic_catalog.v1":
        raise ValueError("Unsupported DreamCo Institute catalog schema.")
    colleges = catalog.get("colleges", [])
    assignments = catalog.get("division_crosswalk", {}).get("academic_assignments", [])
    if len(colleges) != 5 or len(assignments) != 55:
        raise ValueError("Expected five colleges and 55 domain academic assignments.")
    ids = [row.get("domain_id") for row in assignments]
    if len(set(ids)) != 55 or any(not value for value in ids):
        raise ValueError("Domain academic assignments must be 55 unique non-empty IDs.")
    return json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = build()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"stale generated catalog: {OUTPUT.relative_to(ROOT)}")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
