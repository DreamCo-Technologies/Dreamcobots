#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "legacy-unification-program.json"
RECOVERY = ROOT / "config" / "generated" / "original-bot-recovery.json"
OVERLAY = ROOT / "config" / "generated" / "recovered-original-bot-overlay.json"
OUT = ROOT / "config" / "generated" / "unified-legacy-system.json"
REPORT = ROOT / "reports" / "UNIFIED_LEGACY_SYSTEM.md"

OWNER_RULES = [
    (("route", "runtime", "buddy", "bot"), "Buddy routing/runtime"),
    (("ontology", "entity", "relationship", "knowledge graph"), "DreamCo operational ontology"),
    (("sandbox", "test", "benchmark", "certif"), "sandbox and certification"),
    (("code", "debug", "quality", "lint", "ci", "github"), "trusted code delivery"),
    (("gap", "builder", "repair", "engineering"), "engineering gap closure"),
    (("data", "database", "storage", "memory", "vault"), "data/storage"),
    (("api", "connect", "integration", "webhook"), "connections/integrations"),
    (("model", "training", "dataset", "data package", "lora", "weight"), "models/training/data packages"),
    (("stripe", "payment", "revenue", "sales", "business", "money"), "business/revenue"),
    (("trade", "supplier", "manufacturer", "import", "export"), "trade/manufacturing"),
    (("music", "media", "video", "film", "creative", "actor"), "creative/media"),
    (("user", "readiness", "beta", "live testing"), "live user readiness"),
    (("offline", "local", "desktop"), "offline/local runtime"),
]


def owner_for(value: str) -> str:
    lower = value.lower()
    for words, owner in OWNER_RULES:
        if any(word in lower for word in words):
            return owner
    return "Buddy routing/runtime"


def ensure_recovery() -> None:
    subprocess.run([sys.executable, "tools/recover_original_bots.py"], cwd=ROOT, check=True)


def main() -> int:
    ensure_recovery()
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    recovery = json.loads(RECOVERY.read_text(encoding="utf-8"))
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

    hash_groups: dict[str, list[dict]] = defaultdict(list)
    unique_assets = []
    no_hash_assets = []
    for asset in recovery.get("systems", []):
        digest = asset.get("sha256")
        if digest:
            hash_groups[digest].append(asset)
        else:
            no_hash_assets.append(asset)

    duplicate_groups = []
    for digest, rows in sorted(hash_groups.items()):
        sources = sorted({row.get("source") for row in rows if row.get("source")})
        canonical = sources[0] if sources else None
        combined_text = " ".join(str(row.get("source", "")) for row in rows)
        record = {
            "sha256": digest,
            "canonical_source": canonical,
            "all_sources": sources,
            "source_count": len(sources),
            "duplicate": len(sources) > 1,
            "canonical_owner": owner_for(combined_text),
            "state": "deduplicated_reference" if len(sources) > 1 else "unique_asset",
        }
        unique_assets.append(record)
        if record["duplicate"]:
            duplicate_groups.append(record)

    worker_records = []
    for state_key in ["already_canonical", "supplemental_recovered", "merge_review"]:
        for row in recovery.get(state_key, []):
            worker_records.append({
                "slug": row.get("slug"),
                "display_name": row.get("display_name"),
                "division": row.get("division"),
                "source": row.get("source"),
                "source_root": row.get("source_root"),
                "state": row.get("state", state_key),
                "canonical_slug": row.get("canonical_slug"),
                "canonical_owner": "Buddy routing/runtime",
                "capability_count": len(row.get("capabilities", [])),
            })

    owner_counts = Counter(record["canonical_owner"] for record in unique_assets)
    worker_state_counts = Counter(record["state"] for record in worker_records)
    blockers = []
    if recovery.get("canonical_bot_count") != 1051:
        blockers.append(f"canonical baseline changed: {recovery.get('canonical_bot_count')}")
    parse_errors = [row for row in recovery.get("systems", []) if row.get("state") == "parse_error"]
    if parse_errors:
        blockers.append(f"legacy parse/source errors requiring review: {len(parse_errors)}")

    payload = {
        "schema": "dreamco.unified_legacy_system.v1",
        "source_roots": program["source_roots"],
        "canonical_bot_baseline": recovery.get("canonical_bot_count"),
        "supplemental_recovered_workers": overlay.get("summary", {}).get("supplemental_profiles", 0),
        "combined_routable_workers_when_overlay_loaded": overlay.get("summary", {}).get("combined_routable_profiles_when_loaded", 1051),
        "worker_state_counts": dict(worker_state_counts),
        "workers": worker_records,
        "legacy_asset_source_records": len(recovery.get("systems", [])),
        "unique_content_assets": len(unique_assets) + len(no_hash_assets),
        "duplicate_content_groups": len(duplicate_groups),
        "duplicate_assets": duplicate_groups,
        "assets": unique_assets,
        "unhashed_assets": no_hash_assets,
        "canonical_owner_counts": dict(owner_counts),
        "merge_review_count": recovery.get("merge_review_count", 0),
        "release_blockers": blockers,
        "unification_ready": not blockers,
        "promotion_requirements": program["promotion_requirements"],
        "truth_boundary": program["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Unified Legacy System",
        "",
        f"- Canonical bot baseline: **{payload['canonical_bot_baseline']}**",
        f"- Supplemental recovered workers: **{payload['supplemental_recovered_workers']}**",
        f"- Combined routable workers when overlay loaded: **{payload['combined_routable_workers_when_overlay_loaded']}**",
        f"- Legacy asset source records: **{payload['legacy_asset_source_records']}**",
        f"- Unique content assets: **{payload['unique_content_assets']}**",
        f"- Duplicate content groups collapsed by reference: **{payload['duplicate_content_groups']}**",
        f"- Merge-review workers: **{payload['merge_review_count']}**",
        f"- Unification blockers: **{len(blockers)}**",
        "",
        "## Canonical owners",
        "",
    ]
    for owner, count in sorted(owner_counts.items()):
        lines.append(f"- {owner}: {count}")
    if blockers:
        lines += ["", "## Blockers", ""] + [f"- {item}" for item in blockers]
    lines += ["", "> Historical files remain preserved. One-system unification is expressed through the canonical registry, ownership map, deduplication references, shared runtime, and shared sandbox/certification stack."]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "ok": not blockers,
        "canonical": payload["canonical_bot_baseline"],
        "supplemental": payload["supplemental_recovered_workers"],
        "combined": payload["combined_routable_workers_when_overlay_loaded"],
        "assets": payload["legacy_asset_source_records"],
        "duplicate_groups": payload["duplicate_content_groups"],
        "merge_review": payload["merge_review_count"],
        "blockers": blockers,
    }, indent=2))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
