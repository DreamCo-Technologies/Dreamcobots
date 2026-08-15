#!/usr/bin/env python3
"""Compile a loss-minimizing migration ledger from repository inventory and legacy recovery evidence.

This is deliberately a compiler, not a deleter. Its output tells engineers what
can be merged, what needs review, and what must remain preserved. No source file
is modified or removed by this program.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/superbot-consolidation-v1.json"
INVENTORY = ROOT / "config/generated/superbot-repository-inventory.json"
RECOVERY = ROOT / "config/generated/legacy-bot-recovery-manifest.json"
OUT = ROOT / "config/generated/superbot-migration-ledger.json"
REPORT = ROOT / "reports/SUPERBOT_MIGRATION_LEDGER.md"


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"required input missing: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def main() -> int:
    config = load(CONFIG)
    inventory = load(INVENTORY)
    recovery = load(RECOVERY)
    divisions = {d["division"]: d for d in config.get("division_superbots", [])}
    clusters = {c["id"]: c for c in config.get("cluster_superbots", [])}

    ledger = []
    by_owner = defaultdict(list)
    state_counts = Counter()
    review = []

    for row in inventory.get("records", []):
        owner = row.get("proposed_superbot", "command")
        record = {
            "path": row["path"],
            "sha256": row["sha256"],
            "owner_cluster": owner,
            "division": row.get("division"),
            "review_required": bool(row.get("review_required")),
            "migration_state": "preserve_and_classify",
            "allowed_actions": ["merge_as_capability", "merge_as_workflow", "preserve_as_evidence", "alias_legacy_identity", "needs_owner_review"],
        }
        if record["review_required"]:
            review.append(record["path"])
        ledger.append(record)
        by_owner[owner].append(record)
        state_counts[record["migration_state"]] += 1

    recovery_by_path = {r.get("path"): r for r in recovery.get("items", []) if r.get("path")}
    for row in ledger:
        rr = recovery_by_path.get(row["path"])
        if rr:
            row["legacy_state"] = rr.get("state")
            row["legacy_reason"] = rr.get("reason")
            row["candidate_slugs"] = rr.get("candidate_slugs", [])
            if rr.get("state") in {"legacy_duplicate", "recoverable_new_bot"}:
                row["recommended_action"] = "normalize_into_division_superbot"
            elif rr.get("state") == "supporting_asset":
                row["recommended_action"] = "preserve_as_supporting_evidence"
            else:
                row["recommended_action"] = "review"
        else:
            row["recommended_action"] = "assign_by_inventory"

    payload = {
        "schema": "dreamco.superbot_migration_ledger.v1",
        "repository": "DreamCo-Technologies/Dreamcobots",
        "policy": "No source deletion. Preserve provenance until parity gates pass.",
        "cluster_count": len(clusters),
        "division_count": len(divisions),
        "inventory_file_count": len(ledger),
        "legacy_recovery_file_count": recovery.get("file_count", 0),
        "review_required_count": len(review),
        "state_counts": dict(state_counts),
        "owner_counts": {k: len(v) for k, v in sorted(by_owner.items())},
        "legacy_recovery_state_counts": recovery.get("state_counts", {}),
        "review_paths": sorted(review),
        "records": ledger,
        "gates": config["migration_gates"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Superbot Migration Ledger", "",
        f"- Repository files inventoried: **{len(ledger):,}**",
        f"- Legacy recovery records: **{recovery.get('file_count', 0):,}**",
        f"- Division Superbots: **{len(divisions)}**",
        f"- Cluster Superbots: **{len(clusters)}**",
        f"- Files requiring ownership review: **{len(review):,}**", "",
        "## Rules", "",
        "1. No source deletion is performed by the compiler.",
        "2. Legacy identities are normalized into capabilities or aliases only after parity is proven.",
        "3. Supporting assets remain evidence/provenance until their consumers are mapped.",
        "4. Review-required paths are never silently reassigned during cleanup.", "",
        "## Owner counts", "",
    ]
    for owner, count in sorted(by_owner.items()):
        lines.append(f"- `{owner}`: {count:,} files")
    lines += ["", "## Required release gates", ""] + [f"- [ ] {gate}" for gate in config["migration_gates"]]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "inventory_files": len(ledger), "review_required": len(review), "divisions": len(divisions), "clusters": len(clusters), "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
