#!/usr/bin/env python3
"""Validate and publish Buddy's creative, crypto, and government hub catalogs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "creative": ROOT / "config" / "buddy-creative-academy.json",
    "crypto": ROOT / "config" / "buddy-chain-registry.json",
    "government": ROOT / "config" / "buddy-government-resources.json",
}
GENERATED = ROOT / "config" / "generated" / "buddy_specialized_hubs.json"
PUBLIC = ROOT / "website" / "data" / "buddy-specialized-hubs.js"


def load_catalogs() -> dict[str, Any]:
    payload = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in SOURCES.items()}
    if payload["creative"].get("schema") != "dreamco.buddy_creative_academy.v1":
        raise ValueError("Unsupported creative academy schema.")
    if payload["crypto"].get("schema") != "dreamco.buddy_chain_registry.v1":
        raise ValueError("Unsupported chain registry schema.")
    if payload["government"].get("schema") != "dreamco.buddy_government_resources.v1":
        raise ValueError("Unsupported government resource schema.")

    phases = payload["creative"]["film_standard"].get("phases", [])
    genres = payload["creative"]["music_standard"].get("genre_families", [])
    families = payload["crypto"].get("families", [])
    sources = payload["government"].get("sources", [])
    for label, rows in (("film phases", phases), ("music genres", genres), ("chain families", families), ("government sources", sources)):
        ids = [row.get("id") for row in rows]
        if not rows or any(not item for item in ids) or len(ids) != len(set(ids)):
            raise ValueError(f"{label} must be non-empty and have unique ids.")
    if payload["crypto"]["policy"].get("private_keys_accepted") is not False:
        raise ValueError("The public crypto policy must reject private keys.")
    for source in sources:
        parsed = urlsplit(source.get("url", ""))
        if parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.endswith(".gov"):
            raise ValueError(f"Government source is not an official HTTPS .gov host: {source.get('id')}")
    return payload


def render(payload: dict[str, Any]) -> tuple[str, str]:
    document = {
        "schema": "dreamco.buddy_specialized_hubs.v1",
        "creative": payload["creative"],
        "crypto": payload["crypto"],
        "government": payload["government"],
        "summary": {
            "film_phases": len(payload["creative"]["film_standard"]["phases"]),
            "music_genre_families": len(payload["creative"]["music_standard"]["genre_families"]),
            "chain_families": len(payload["crypto"]["families"]),
            "verified_government_sources": len(payload["government"]["sources"]),
        },
    }
    body = json.dumps(document, indent=2, sort_keys=True) + "\n"
    public = "window.BUDDY_SPECIALIZED_HUBS = " + json.dumps(document, separators=(",", ":")) + ";\n"
    return body, public


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated, public = render(load_catalogs())
    if args.check:
        if not GENERATED.exists() or GENERATED.read_text(encoding="utf-8") != generated:
            raise SystemExit("Generated specialized hub catalog is stale.")
        if not PUBLIC.exists() or PUBLIC.read_text(encoding="utf-8") != public:
            raise SystemExit("Public specialized hub catalog is stale.")
    else:
        GENERATED.parent.mkdir(parents=True, exist_ok=True)
        PUBLIC.parent.mkdir(parents=True, exist_ok=True)
        GENERATED.write_text(generated, encoding="utf-8")
        PUBLIC.write_text(public, encoding="utf-8")
    print(json.dumps({"ok": True, "generated": str(GENERATED.relative_to(ROOT)), "public": str(PUBLIC.relative_to(ROOT))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
