"""Generate and validate DreamCo's 55 division specialist curricula."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from buddy.learning.division_curriculum_builder import ROOT, build_division_curricula, build_manifest


def _render(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the 55 curriculum drafts and manifest")
    mode.add_argument("--check", action="store_true", help="validate all source-backed curricula and generated artifacts")
    args = parser.parse_args()
    catalog = build_division_curricula()
    manifest = build_manifest(catalog)
    output = ROOT / "data/dreamco_training/division_curricula"
    manifest_path = ROOT / "config/dreamco-division-curricula-manifest.json"

    if args.write:
        output.mkdir(parents=True, exist_ok=True)
        for course in catalog["artifacts"]:
            path = output / f"{course['division']['id']}.json"
            path.write_text(_render(course), encoding="utf-8")
        manifest_path.write_text(_render(manifest), encoding="utf-8")
        print(json.dumps({"status": "GENERATED_DRAFTS_NOT_TRAINED", **catalog["counts"]}, indent=2))
        return 0

    if not manifest_path.is_file():
        raise SystemExit("division specialist course artifact manifest is missing; run --write")
    actual_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if actual_manifest != manifest:
        raise SystemExit("division specialist course artifact manifest is stale; run --write")
    missing = []
    for course in catalog["artifacts"]:
        path = output / f"{course['division']['id']}.json"
        if not path.is_file() or path.read_text(encoding="utf-8") != _render(course):
            missing.append(path.relative_to(ROOT).as_posix())
    if missing:
        raise SystemExit(f"division specialist curriculum files stale or missing: {len(missing)}")
    print(json.dumps({"status": "VALIDATED_DRAFTS_NOT_TRAINED", **catalog["counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
