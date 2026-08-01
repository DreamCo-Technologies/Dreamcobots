#!/usr/bin/env python3
"""Validate and publish Buddy's local-first media engine catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "buddy-local-media-engines.json"
OUTPUT = ROOT / "website" / "data" / "buddy-local-media-engines.js"


def load_catalog() -> dict:
    catalog = json.loads(SOURCE.read_text(encoding="utf-8"))
    if catalog.get("schema") != "dreamco.buddy_local_media_engines.v2":
        raise SystemExit("Unexpected local media catalog schema.")
    if catalog.get("policy", {}).get("paid_provider_required") is not False:
        raise SystemExit("The local media core cannot require a paid provider.")
    engines = catalog.get("engines", [])
    if len(engines) < 8 or len({item["id"] for item in engines}) != len(engines):
        raise SystemExit("The media catalog needs at least eight unique engine records.")
    if any(not item.get("license_status") or not item.get("commercial_status") for item in engines):
        raise SystemExit("Every media engine needs explicit license and commercial states.")
    if len(catalog.get("benchmark_suites", [])) < 8:
        raise SystemExit("The local media catalog needs the complete benchmark suite.")
    targets = catalog.get("benchmark_targets", [])
    if len(targets) < 4 or not any(item.get("kind") == "optional_external_reference" for item in targets):
        raise SystemExit("The media catalog needs owned, local-reference, and external-reference benchmark targets.")
    if any(item.get("required") for item in targets if item.get("id") != "buddy-media-core"):
        raise SystemExit("External and third-party benchmark targets cannot be required by Buddy.")
    return catalog


def render(catalog: dict) -> str:
    return "window.BUDDY_LOCAL_MEDIA_ENGINES = " + json.dumps(catalog, sort_keys=True) + ";\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(load_catalog())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit("Buddy local media browser catalog is stale. Regenerate it.")
        print(json.dumps({"ok": True, "output": str(OUTPUT.relative_to(ROOT))}, indent=2))
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(json.dumps({"generated": str(OUTPUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
