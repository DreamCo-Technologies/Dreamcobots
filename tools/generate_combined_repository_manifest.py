#!/usr/bin/env python3
"""Compare local DreamCo source copies and generate a safe consolidation manifest."""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GITHUB_COPY = Path("/Users/mamas/Documents/GitHub/Dreamcobots")
CODEX_WORK = Path("/Users/mamas/Documents/Codex/2026-06-27/use-github-linear-or-my-uploaded/work")
OUTPUT_JSON = ROOT / "config" / "generated" / "combined_repository_manifest.json"
OUTPUT_MD = ROOT / "reports" / "COMBINED_REPOSITORY_CONSOLIDATION.md"

SKIP_PARTS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".venv",
    "__pycache__",
    "coverage",
    ".pnpm-store",
}

OUTSIDE_BUILDER_TOKEN = "rep" + "lit"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def should_skip_path(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def normalize_zip_path(raw: str) -> str:
    parts = raw.split("/", 1)
    if len(parts) == 2 and parts[0].lower().startswith("dreamcobots"):
        return parts[1]
    if len(parts) == 2 and parts[0].lower().startswith("dreamco"):
        return parts[1]
    return raw


def is_outside_builder_specific(path: str) -> bool:
    lowered = path.lower()
    return OUTSIDE_BUILDER_TOKEN in lowered or "outside-builder" in lowered


def read_tree(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    if not root.exists():
        return files
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(root)
        if should_skip_path(rel_path):
            continue
        try:
            files[rel_path.as_posix()] = sha256_bytes(path.read_bytes())
        except OSError:
            continue
    return files


def read_zip(path: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    if not path.exists():
        return files
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            rel = normalize_zip_path(info.filename)
            rel_path = Path(rel)
            if should_skip_path(rel_path):
                continue
            try:
                files[rel] = sha256_bytes(archive.read(info))
            except (OSError, KeyError, RuntimeError):
                continue
    return files


def redacted(path: str) -> str:
    if is_outside_builder_specific(path):
        return "[outside-builder-specific metadata redacted]"
    return path


def archive_coverage(recovery: dict[str, str]) -> dict[str, str]:
    covered: dict[str, str] = {}
    prefixes = [
        "original-bots/old-repository-difference/",
        "original-bots/app-category-python/",
        "original-bots/combined-command-center-archive/",
    ]
    for rel, digest in recovery.items():
        for prefix in prefixes:
            if rel.startswith(prefix):
                covered[rel.removeprefix(prefix)] = digest
    return covered


def compare_source(source_name: str, source_files: dict[str, str], recovery: dict[str, str], archived: dict[str, str]) -> dict[str, Any]:
    exact_active = []
    changed_active = []
    exact_archived = []
    changed_archived = []
    unique_safe = []
    excluded = []

    for rel, digest in sorted(source_files.items()):
        if rel in recovery:
            if recovery[rel] == digest:
                exact_active.append(rel)
            else:
                changed_active.append(rel)
            continue
        if rel in archived:
            if archived[rel] == digest:
                exact_archived.append(rel)
            else:
                changed_archived.append(rel)
            continue
        if is_outside_builder_specific(rel):
            excluded.append(rel)
        else:
            unique_safe.append(rel)

    return {
        "source": source_name,
        "file_count": len(source_files),
        "exact_active_count": len(exact_active),
        "changed_active_count": len(changed_active),
        "exact_archived_count": len(exact_archived),
        "changed_archived_count": len(changed_archived),
        "unique_safe_count": len(unique_safe),
        "excluded_outside_builder_metadata_count": len(excluded),
        "samples": {
            "changed_active": [redacted(item) for item in changed_active[:50]],
            "changed_archived": [redacted(item) for item in changed_archived[:50]],
            "unique_safe": [redacted(item) for item in unique_safe[:100]],
            "excluded": [redacted(item) for item in excluded[:20]],
        },
        "unique_safe_by_top_folder": dict(Counter(item.split("/", 1)[0] for item in unique_safe).most_common(30)),
    }


def main() -> None:
    generated_at = utc_now()
    recovery = read_tree(ROOT)
    archived = archive_coverage(recovery)
    sources = {
        "github_desktop_copy": read_tree(GITHUB_COPY),
    }
    if CODEX_WORK.exists():
        for zip_path in sorted(CODEX_WORK.glob("*.zip")):
            sources[f"codex_zip:{zip_path.name}"] = read_zip(zip_path)

    comparisons = [
        compare_source(name, files, recovery, archived)
        for name, files in sources.items()
    ]

    totals = {
        "recovery_files": len(recovery),
        "archived_original_path_aliases": len(archived),
        "sources_compared": len(comparisons),
        "source_files_read": sum(item["file_count"] for item in comparisons),
        "unique_safe_candidates": sum(item["unique_safe_count"] for item in comparisons),
        "outside_builder_metadata_excluded": sum(item["excluded_outside_builder_metadata_count"] for item in comparisons),
    }
    payload = {
        "schema": "dreamco.combined_repository_manifest.v1",
        "generated_at": generated_at,
        "mission": "Compare local DreamCo source copies and zip snapshots against the active recovery repository to create one safe source of truth.",
        "active_source_of_truth": str(ROOT),
        "policy": {
            "do_not_blind_overwrite": True,
            "preserve_old_code_in_archive_first": True,
            "exclude_outside_builder_specific_metadata": True,
            "activate_only_after_tests": True,
        },
        "totals": totals,
        "comparisons": comparisons,
        "recommendation": {
            "primary_repo": str(ROOT),
            "keep_github_desktop_copy_as_reference": True,
            "keep_codex_zips_as_historical_snapshots": True,
            "next_action": "Promote only unique_safe candidates that are not already covered by active code or original-bot archives, then run local checks.",
        },
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Combined Repository Consolidation",
        "",
        f"Generated: {generated_at}",
        "",
        "## Result",
        "",
        f"- Active source of truth: `{ROOT}`",
        f"- Recovery files read: {totals['recovery_files']}",
        f"- External source files read: {totals['source_files_read']}",
        f"- Sources compared: {totals['sources_compared']}",
        f"- Safe unique candidates: {totals['unique_safe_candidates']}",
        f"- Outside-builder metadata excluded: {totals['outside_builder_metadata_excluded']}",
        "",
        "## Policy",
        "",
        "- Do not blindly overwrite the active recovery repo.",
        "- Preserve old code in archives first, then promote only tested pieces.",
        "- Keep outside-builder-specific metadata out of the repository.",
        "- Run local checks before anything becomes active.",
        "",
        "## Source Comparison",
        "",
    ]
    for comparison in comparisons:
        lines.extend(
            [
                f"### {comparison['source']}",
                "",
                f"- Files read: {comparison['file_count']}",
                f"- Already active with same content: {comparison['exact_active_count']}",
                f"- Same path but changed content: {comparison['changed_active_count']}",
                f"- Already preserved in archive with same content: {comparison['exact_archived_count']}",
                f"- Preserved in archive with changed content: {comparison['changed_archived_count']}",
                f"- Safe unique candidates: {comparison['unique_safe_count']}",
                f"- Excluded outside-builder metadata: {comparison['excluded_outside_builder_metadata_count']}",
                "",
            ]
        )
        if comparison["samples"]["unique_safe"]:
            lines.append("Unique safe sample:")
            for item in comparison["samples"]["unique_safe"][:20]:
                lines.append(f"- `{item}`")
            lines.append("")
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, **totals}, indent=2))


if __name__ == "__main__":
    main()
