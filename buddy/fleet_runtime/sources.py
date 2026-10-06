"""Read bot profile content from the canonical repository sources.

Manifests stay compact: profile text (name, description, capabilities) is read
from App_bots/*.json and bots/*.md at run time instead of being copied into
the generated manifest file, so the profile sources remain the single source
of truth.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from .contract import ROOT

APP_BOTS = ROOT / "App_bots"
BOTS_MD = ROOT / "bots"
SEED = ROOT / "server" / "seed-bots.ts"

MD_META_RE = re.compile(r"Division:\*\*\s*([^|]+)\|\s*\*\*Tier:\*\*\s*([^|]+)\|", re.I)
SEED_RE = re.compile(r'\bbot\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]*)"')


def parse_md(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    name = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), path.stem)
    division = tier = ""
    for line in text.splitlines()[:20]:
        meta = MD_META_RE.search(line)
        if meta:
            division, tier = meta.group(1).strip(), meta.group(2).strip().lower()
            break
    sections: dict[str, list[str]] = {"intro": []}
    current = "intro"
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.+)$", line)
        if heading:
            current = heading.group(1).strip().lower()
            sections[current] = []
            continue
        sections[current].append(line)
    caps = [l.strip().lstrip("-* ").strip() for l in sections.get("capabilities", []) if l.strip().startswith(("-", "*"))]
    tools = [l.strip().lstrip("-* ").strip() for l in sections.get("tools needed", []) if l.strip().startswith(("-", "*"))]
    desc_lines = [l.strip() for l in sections.get("description", []) if l.strip() and not l.startswith(">")]
    if not desc_lines:
        desc_lines = [l.strip() for l in sections["intro"] if l.strip() and not l.startswith(("#", ">")) and ":" not in l[:25]]
    return {"name": name, "division": division, "tier": tier, "capabilities": caps, "tools": tools,
            "description": desc_lines[0] if desc_lines else "", "category": "",
            "claims_production_ready": bool(re.search(r"production[ _]ready:?\**\s*true", text, re.I))}


def load_sources(root: Path = ROOT) -> tuple[dict[str, dict[str, Any]], list[Path], dict[str, Any]]:
    bots: dict[str, dict[str, Any]] = {}
    inputs: list[Path] = []
    folder_notes: dict[str, Any] = {}
    for path in sorted((root / "App_bots").glob("*.json")):
        inputs.append(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        division = data.get("division", path.stem)
        rel = path.relative_to(root).as_posix()
        if not data.get("bots"):
            folder_notes[rel] = "no bots in file (metadata / pointer file)"
            continue
        for raw in data["bots"]:
            slug = raw["slug"]
            entry = bots.setdefault(slug, {"sources": [], "flags": set()})
            if "app" in entry:
                entry["flags"].add("duplicate_slug")
            entry["sources"].append(rel)
            entry["app"] = {
                "name": raw.get("displayName", slug), "division": division, "tier": raw.get("tier", ""),
                "category": raw.get("category", ""), "description": raw.get("description", ""),
                "capabilities": raw.get("capabilities", []), "tools": raw.get("toolsNeeded", []),
                "benchmarks": raw.get("benchmarks", []), "target_users": raw.get("targetUsers", ""),
                "claims_production_ready": bool((raw.get("production") or {}).get("production_ready")),
            }
    for path in sorted((root / "bots").glob("*.md")):
        inputs.append(path)
        slug = path.stem.lower()
        entry = bots.setdefault(slug, {"sources": [], "flags": set()})
        entry["sources"].append(path.relative_to(root).as_posix())
        entry["md"] = parse_md(path)
    seed = root / "server" / "seed-bots.ts"
    if seed.exists():
        inputs.append(seed)
        for slug, _name, division, _cat in SEED_RE.findall(seed.read_text(encoding="utf-8")):
            if slug in bots:
                bots[slug]["seed_division"] = division
    return bots, inputs, folder_notes




@lru_cache(maxsize=1)
def _all_sources() -> dict[str, dict[str, Any]]:
    return load_sources()[0]


def profile_content(slug: str) -> dict[str, Any]:
    """Return {name, description, capabilities, target_users?} for a bot."""
    entry = _all_sources().get(slug) or {}
    base = entry.get("app") or entry.get("md") or {}
    caps = list(dict.fromkeys(base.get("capabilities") or (entry.get("md") or {}).get("capabilities") or []))
    return {"description": (base.get("description") or "")[:600], "capabilities_raw": caps,
            "target_users": base.get("target_users", "")}
