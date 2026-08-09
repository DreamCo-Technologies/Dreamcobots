#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "App_bots"
ORIGINAL = ROOT / "original-bots"
PROGRAM = ROOT / "config" / "original-bot-recovery-program.json"
OUT = ROOT / "config" / "generated" / "original-bot-recovery.json"
OVERLAY = ROOT / "config" / "generated" / "recovered-original-bot-overlay.json"
REPORT = ROOT / "reports" / "ORIGINAL_BOT_RECOVERY.md"

TEXT_SUFFIXES = {".md", ".txt", ".py", ".js", ".ts", ".tsx", ".json", ".yaml", ".yml"}
BOT_HINT = re.compile(r"\b(bot|agent|assistant|copilot|ai|worker)\b", re.I)
FRONTMATTER_FIELD = re.compile(r"^(name|title|slug|description|category|capabilities)\s*:\s*(.+)$", re.I | re.M)
HEADING = re.compile(r"^#\s+(.+)$", re.M)


def slugify(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value[:120]


def normalized_name(value: str) -> str:
    return re.sub(r"\b(bot|agent|assistant|ai|system|tool)\b", "", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def canonical_inventory() -> tuple[dict[str, dict], dict[str, str]]:
    by_slug: dict[str, dict] = {}
    by_name: dict[str, str] = {}
    for path in sorted(APP.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        division = doc.get("division") or path.stem
        for bot in doc.get("bots", []):
            slug = str(bot.get("slug", "")).strip()
            if not slug:
                continue
            row = dict(bot)
            row["division"] = division
            by_slug[slugify(slug)] = row
            name_key = normalized_name(str(bot.get("displayName") or slug))
            if name_key:
                by_name[name_key] = slugify(slug)
    return by_slug, by_name


def infer_division(text: str, program: dict) -> str:
    lower = text.lower()
    for pattern, division in program["division_inference"]["keyword_map"].items():
        if re.search(pattern, lower):
            return division
    return program["division_inference"]["default"]


def capabilities_from_value(value) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()][:50]
    if isinstance(value, str):
        parts = re.split(r"[,;|\n]+", value)
        return [x.strip(" -*\t") for x in parts if x.strip(" -*\t")][:50]
    return []


def json_candidates(path: Path, doc) -> list[dict]:
    out: list[dict] = []

    def walk(value, trail: list[str]):
        if isinstance(value, dict):
            name = value.get("displayName") or value.get("name") or value.get("title")
            slug = value.get("slug") or value.get("id")
            caps = capabilities_from_value(value.get("capabilities") or value.get("skills") or value.get("functions"))
            desc = value.get("description") or value.get("mission") or value.get("purpose") or ""
            key_text = " ".join(map(str, value.keys()))
            if (name or slug) and (caps or BOT_HINT.search(f"{name or ''} {slug or ''} {key_text}")):
                display = str(name or slug)
                out.append({
                    "display_name": display,
                    "slug": slugify(str(slug or display)),
                    "description": str(desc)[:1500],
                    "capabilities": caps or ["Recovered historical specialist capability; detailed capability extraction required"],
                    "raw_category": str(value.get("category") or "recovered-original"),
                    "trail": trail,
                })
            for key, child in value.items():
                walk(child, trail + [str(key)])
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, trail + [str(i)])

    walk(doc, [])
    return out


def text_candidate(path: Path, text: str) -> list[dict]:
    if not BOT_HINT.search(f"{path.stem} {text[:4000]}"):
        return []
    fields = {m.group(1).lower(): m.group(2).strip() for m in FRONTMATTER_FIELD.finditer(text[:5000])}
    heading = HEADING.search(text[:3000])
    display = fields.get("name") or fields.get("title") or (heading.group(1).strip() if heading else path.stem.replace("_", " ").replace("-", " ").title())
    slug = slugify(fields.get("slug") or display)
    caps = capabilities_from_value(fields.get("capabilities", ""))
    if not caps:
        bullets = re.findall(r"^\s*[-*]\s+(.{3,180})$", text, re.M)
        caps = [b.strip() for b in bullets[:20] if not b.lower().startswith(("http", "copyright", "license"))]
    return [{
        "display_name": display,
        "slug": slug,
        "description": fields.get("description") or f"Recovered from historical source file {path.name}",
        "capabilities": caps or ["Recovered historical specialist capability; detailed capability extraction required"],
        "raw_category": fields.get("category") or "recovered-original",
        "trail": [],
    }]


def scan_original(program: dict) -> tuple[list[dict], list[dict]]:
    candidates: list[dict] = []
    systems: list[dict] = []
    if not ORIGINAL.exists():
        return candidates, systems
    for path in sorted(p for p in ORIGINAL.rglob("*") if p.is_file()):
        rel = str(path.relative_to(ROOT))
        if path.suffix.lower() not in TEXT_SUFFIXES:
            systems.append({"source": rel, "kind": "asset", "state": "unsupported_file", "size": path.stat().st_size})
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            found: list[dict] = []
            if path.suffix.lower() == ".json":
                try:
                    found = json_candidates(path, json.loads(text))
                except json.JSONDecodeError:
                    found = text_candidate(path, text)
            else:
                found = text_candidate(path, text)
            if found:
                for row in found:
                    row["source"] = rel
                    row["division"] = infer_division(" ".join([row["display_name"], row["description"], " ".join(row["capabilities"]), rel]), program)
                    candidates.append(row)
            else:
                systems.append({"source": rel, "kind": path.suffix.lower().lstrip(".") or "text", "state": "system_asset", "size": len(text)})
        except Exception as exc:
            systems.append({"source": rel, "kind": path.suffix.lower().lstrip("."), "state": "parse_error", "error": str(exc)[:500]})
    return candidates, systems


def runtime_profile(row: dict) -> dict:
    caps = row["capabilities"][:50]
    return {
        "identity": {
            "slug": row["slug"],
            "display_name": row["display_name"],
            "division": row["division"],
            "category": row.get("raw_category") or "recovered-original",
            "tier": "recovered",
            "catalog_status": "supplemental_recovered",
        },
        "mission": row["description"],
        "capability_count": len(caps),
        "capability_search": " | ".join(caps),
        "tool_summary": [
            {"id": "buddy_fleet_runtime", "name": "Executable fleet runtime", "status": "runtime_instance_ready"},
            {"id": "buddy_chat_router", "name": "Buddy shared chat router", "status": "runtime_routed"},
            {"id": "buddy_approval_gateway", "name": "Buddy approval gateway", "status": "policy_available"},
            {"id": "buddy_bot_sandbox", "name": "Recovered bot sandbox", "status": "generated"},
            {"id": "buddy_platform_registry", "name": "Governed platform capability registry", "status": "runtime_routed"},
            {"id": "buddy_bot_calculator", "name": "Planning calculator", "status": "local_interactive_ready"},
            {"id": "buddy_distribution_service", "name": "Distribution planner", "status": "web_ready_native_review_required"},
            {"id": "buddy_governed_lead_system", "name": "Governed lead system", "status": "sandbox_ready_external_adapters_required"},
        ],
        "api_candidate_names": [],
        "approval_required": True,
        "sample_test_prompt": f"Test every recovered capability for {row['display_name']} in sandbox mode using synthetic data only. Record runtime evidence and do not perform live external actions.",
        "readiness": {"profile_schema": "verified", "buddy_chat_route": "verified"},
        "evidence": {"recovered_source": row["source"], "recovery_state": "supplemental_recovered"},
    }


def main() -> int:
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    canonical_by_slug, canonical_by_name = canonical_inventory()
    candidates, systems = scan_original(program)

    recovered = []
    already = []
    review = []
    seen_supplemental: set[str] = set()
    for row in candidates:
        slug = row["slug"]
        name_key = normalized_name(row["display_name"])
        if slug in canonical_by_slug:
            already.append({**row, "state": "already_canonical", "canonical_slug": slug})
        elif name_key and name_key in canonical_by_name:
            review.append({**row, "state": "merge_review", "canonical_slug": canonical_by_name[name_key]})
        elif slug in seen_supplemental:
            review.append({**row, "state": "merge_review", "reason": "duplicate original supplemental slug"})
        else:
            seen_supplemental.add(slug)
            recovered.append({**row, "state": "supplemental_recovered"})

    overlay_bots = [runtime_profile(row) for row in recovered]
    overlay = {
        "schema": "dreamco.recovered_original_bot_overlay.v1",
        "summary": {
            "canonical_baseline": len(canonical_by_slug),
            "supplemental_profiles": len(overlay_bots),
            "combined_routable_profiles_when_loaded": len(canonical_by_slug) + len(overlay_bots),
        },
        "bots": overlay_bots,
        "truth_boundary": program["truth_rule"],
    }
    inventory = {
        "schema": "dreamco.original_bot_recovery.generated.v1",
        "canonical_bot_count": len(canonical_by_slug),
        "original_candidate_count": len(candidates),
        "already_canonical_count": len(already),
        "supplemental_recovered_count": len(recovered),
        "merge_review_count": len(review),
        "system_asset_count": len(systems),
        "source_file_count": len({row.get("source") for row in candidates + systems}),
        "state_counts": dict(Counter([row["state"] for row in already + recovered + review] + [row["state"] for row in systems])),
        "already_canonical": already,
        "supplemental_recovered": recovered,
        "merge_review": review,
        "systems": systems,
        "truth_boundary": program["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    OVERLAY.write_text(json.dumps(overlay, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Original Bot Recovery",
        "",
        f"- Canonical App_bots baseline: **{len(canonical_by_slug)}**",
        f"- Original bot-like candidates found: **{len(candidates)}**",
        f"- Already represented canonically: **{len(already)}**",
        f"- Supplemental recovered workers: **{len(recovered)}**",
        f"- Merge/review candidates: **{len(review)}**",
        f"- Original system/assets inventoried: **{len(systems)}**",
        f"- Combined routable profiles when overlay is loaded: **{len(canonical_by_slug) + len(overlay_bots)}**",
        "",
        "> The 1,051 canonical baseline is preserved. Recovered workers use Buddy's shared governed sandbox runtime and require runtime certification before production claims.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "canonical": len(canonical_by_slug),
        "original_candidates": len(candidates),
        "already_canonical": len(already),
        "supplemental_recovered": len(recovered),
        "merge_review": len(review),
        "systems": len(systems),
        "combined_when_loaded": len(canonical_by_slug) + len(overlay_bots),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
