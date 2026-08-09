#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "dreamco-generator-factory.json"
OUT = ROOT / "config" / "generated" / "dreamco-generator-registry.json"
APP_BOTS = ROOT / "App_bots"


def slug(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def load_bots() -> list[dict]:
    rows = []
    for path in sorted(APP_BOTS.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        division = payload.get("division") or path.stem
        for bot in payload.get("bots", []):
            if bot.get("slug"):
                rows.append({"slug": bot["slug"], "division": division, "category": bot.get("category")})
    return rows


def build_registry() -> dict:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    generators = cfg["generator_types"]
    bots = load_bots()
    return {
        "schema": "dreamco.generator_registry.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator_count": len(generators),
        "bot_count": len(bots),
        "generator_ids": [g["id"] for g in generators],
        "generators": generators,
        "fleet_access": [{"bot_slug": b["slug"], "division": b["division"], "allowed_generators": [g["id"] for g in generators]} for b in bots],
        "truth_boundary": "Registry access does not prove every generator has a domain-specific executable implementation. Outputs must be validated before use.",
    }


def generate_manifest(generator_id: str, objective: str, bot_slug: str | None, output_dir: Path) -> Path:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    generator = next((g for g in cfg["generator_types"] if g["id"] == generator_id), None)
    if not generator:
        raise SystemExit(f"Unknown generator: {generator_id}")
    artifact_id = slug(f"{generator_id}-{bot_slug or 'buddy'}-{objective}")[:100] or generator_id
    payload = {
        "schema": "dreamco.generated_artifact_request.v1",
        "generator_id": generator_id,
        "generator_category": generator["category"],
        "requested_by_bot": bot_slug,
        "objective": objective,
        "expected_outputs": generator["produces"],
        "status": "draft_requires_generation_and_validation",
        "validation_required": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{artifact_id}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="DreamCo shared generator factory")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("registry")
    list_parser = sub.add_parser("list")
    list_parser.add_argument("--category")
    gen = sub.add_parser("request")
    gen.add_argument("generator_id")
    gen.add_argument("objective")
    gen.add_argument("--bot")
    gen.add_argument("--output-dir", default=".buddy-local/artifacts/generator-requests")
    args = parser.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    if args.command == "registry":
        payload = build_registry()
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, "generators": payload["generator_count"], "bots": payload["bot_count"], "output": str(OUT.relative_to(ROOT))}, indent=2))
        return 0
    if args.command == "list":
        rows = [g for g in cfg["generator_types"] if not args.category or g["category"] == args.category]
        print(json.dumps(rows, indent=2))
        return 0
    path = generate_manifest(args.generator_id, args.objective, args.bot, ROOT / args.output_dir)
    print(json.dumps({"ok": True, "request": str(path.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
