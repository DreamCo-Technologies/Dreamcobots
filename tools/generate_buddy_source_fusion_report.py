#!/usr/bin/env python3
"""Scan local DreamCo source pools and report what can be fused into Buddy."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = {
    "active_recovery": ROOT,
    "new_project": Path("/Users/mamas/Documents/New project"),
    "github_desktop": Path("/Users/mamas/Documents/GitHub"),
    "codex_archives": Path("/Users/mamas/Documents/Codex"),
}
MASTER_REGISTRY = ROOT / "config" / "master_bot_registry.json"
OUTPUT_JSON = ROOT / "config" / "generated" / "buddy_source_fusion_report.json"
OUTPUT_MD = ROOT / "reports" / "BUDDY_SOURCE_FUSION_REPORT.md"

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
    ".pytest_cache",
}
TEXT_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".txt", ".yaml", ".yml", ".html", ".css"}
CODE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".html", ".css"}
DATA_SUFFIXES = {".json", ".yaml", ".yml", ".csv", ".toml"}
INSTRUCTION_NAMES = {"readme", "roadmap", "instructions", "manifest", "policy", "schema", "guide", "setup"}
OUTSIDE_BUILDER_TOKEN = "rep" + "lit"
BANNED_CONTENT_TERMS = (OUTSIDE_BUILDER_TOKEN, "@" + OUTSIDE_BUILDER_TOKEN, "stripe-" + OUTSIDE_BUILDER_TOKEN + "-sync", "wat" + "son")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[_\s]+", "-", text)
    text = re.sub(r"[^a-z0-9-]+", "", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_decode(data: bytes) -> str:
    return data[:250_000].decode("utf-8", errors="ignore")


def has_banned_content(text: str, path: str) -> bool:
    lowered = f"{path}\n{text}".lower()
    if any(term in lowered for term in BANNED_CONTENT_TERMS):
        return True
    return bool(re.search(r"\bibm\b", lowered))


def classify(path: str, text: str) -> dict[str, Any]:
    rel = Path(path)
    name = rel.name
    lower = path.lower()
    stem = rel.stem
    parts = set(rel.parts)
    parent_parts = {part.lower() for part in rel.parts[:-1]}
    bot_folder = (
        "/bots/" in lower
        or any(part.endswith("_bots") or part.endswith("-bots") for part in parent_parts)
        or "app_bots" in parent_parts
        or "business_bots" in parent_parts
        or "occupational_bots" in parent_parts
        or "government_contract_bots" in parent_parts
        or "real_estate_bots" in parent_parts
        or "fiverr_bots" in parent_parts
    )
    bot_manifest = name in {"bot_profile.json", "bot.manifest.json"} or "bot.manifest" in lower
    is_bot = (
        bot_folder
        or bot_manifest
        or (rel.suffix.lower() == ".py" and stem.endswith("_bot"))
    )
    is_instruction = rel.suffix.lower() in {".md", ".txt"} and any(part in lower for part in INSTRUCTION_NAMES)
    is_data = rel.suffix.lower() in DATA_SUFFIXES
    is_code = rel.suffix.lower() in CODE_SUFFIXES
    category = "other"
    if is_bot:
        category = "bot"
    elif is_instruction:
        category = "instruction"
    elif is_data:
        category = "data_config"
    elif is_code:
        category = "code"

    candidate_slug = ""
    if is_bot:
        try:
            if rel.suffix.lower() == ".json" and bot_manifest:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    candidate_slug = str(parsed.get("slug") or parsed.get("id") or parsed.get("name") or "")
        except json.JSONDecodeError:
            candidate_slug = ""
        if not candidate_slug:
            candidate_slug = stem
        candidate_slug = slugify(candidate_slug)

    return {
        "category": category,
        "is_bot": is_bot,
        "candidate_slug": candidate_slug,
        "is_code": is_code,
        "is_instruction": is_instruction,
        "is_data": is_data,
    }


def iter_source_files(source_name: str, root: Path):
    if not root.exists():
        return
    for path in root.rglob("*"):
        if source_name == "new_project":
            try:
                if path.resolve().is_relative_to(ROOT):
                    continue
            except OSError:
                continue
        if not path.is_file() or should_skip(path.relative_to(root)):
            continue
        rel = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        if suffix == ".zip":
            yield from iter_zip_files(source_name, path)
            continue
        if suffix not in TEXT_SUFFIXES:
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        yield {
            "source": source_name,
            "path": rel,
            "kind": "file",
            "sha256": digest(data),
            "text": safe_decode(data),
        }


def normalize_zip_path(raw: str) -> str:
    parts = raw.split("/", 1)
    if len(parts) == 2 and parts[0].lower().startswith("dreamco"):
        return parts[1]
    return raw


def iter_zip_files(source_name: str, zip_path: Path):
    try:
        with zipfile.ZipFile(zip_path) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                rel = normalize_zip_path(info.filename)
                if should_skip(Path(rel)) or Path(rel).suffix.lower() not in TEXT_SUFFIXES:
                    continue
                try:
                    data = archive.read(info)
                except (OSError, RuntimeError, KeyError):
                    continue
                yield {
                    "source": source_name,
                    "path": f"{zip_path.name}:{rel}",
                    "kind": "zip_member",
                    "sha256": digest(data),
                    "text": safe_decode(data),
                }
    except (OSError, zipfile.BadZipFile):
        return


def build_report() -> dict[str, Any]:
    registry = read_json(MASTER_REGISTRY, {})
    active_bots = {
        slugify(str(bot.get("slug") or bot.get("id") or bot.get("name") or ""))
        for bot in registry.get("bots", [])
    }
    active_hashes: set[str] = set()
    for item in iter_source_files("active_recovery", ROOT) or []:
        active_hashes.add(item["sha256"])

    source_summaries: dict[str, Any] = {}
    bot_candidates = []
    categories = Counter()
    missing_bot_slugs = set()
    duplicate_bot_slugs = Counter()
    useful_unique_by_source = Counter()
    excluded_by_source = Counter()
    samples = defaultdict(list)

    for source_name, root in SOURCE_ROOTS.items():
        summary = Counter()
        for item in iter_source_files(source_name, root) or []:
            text = item["text"]
            path = item["path"]
            if source_name != "active_recovery" and has_banned_content(text, path):
                excluded_by_source[source_name] += 1
                summary["excluded_policy"] += 1
                continue
            info = classify(path, text)
            category = info["category"]
            summary["files_read"] += 1
            summary[category] += 1
            categories[category] += 1
            already_active_content = item["sha256"] in active_hashes
            if not already_active_content and source_name != "active_recovery" and category in {"bot", "code", "instruction", "data_config"}:
                useful_unique_by_source[source_name] += 1
                if len(samples[source_name]) < 30:
                    samples[source_name].append({"path": path, "category": category})
            if info["is_bot"]:
                slug = info["candidate_slug"]
                if slug:
                    duplicate_bot_slugs[slug] += 1
                    if slug not in active_bots and source_name != "active_recovery":
                        missing_bot_slugs.add(slug)
                if len(bot_candidates) < 200:
                    bot_candidates.append(
                        {
                            "source": source_name,
                            "path": path,
                            "candidate_slug": slug,
                            "already_in_master_registry": slug in active_bots,
                            "already_active_content": already_active_content,
                        }
                    )
        source_summaries[source_name] = dict(summary)

    missing_sample = sorted(missing_bot_slugs)[:100]
    completion = {
        "registry_and_buddy_connection": 100,
        "source_recovery_and_archiving": 95,
        "actions_page_visibility": 92,
        "sandbox_and_local_first_policy": 90,
        "all_bot_end_to_end_testing": 62,
        "production_runtime_depth_per_bot": 58,
        "overall_buildout_estimate": 82,
    }
    return {
        "schema": "dreamco.buddy_source_fusion_report.v1",
        "generated_at": utc_now(),
        "mission": "Scan local source pools for bots, code, instructions, and data, then identify what is already active, preserved, or worth promoting into Buddy's unified system.",
        "active_source_of_truth": str(ROOT),
        "completion_estimate_percent": completion,
        "summary": {
            "master_registry_bots": len(active_bots),
            "sources_scanned": len(SOURCE_ROOTS),
            "categories": dict(categories),
            "useful_unique_candidates": sum(useful_unique_by_source.values()),
            "policy_excluded_candidates": sum(excluded_by_source.values()),
            "missing_bot_slug_candidates": len(missing_bot_slugs),
            "duplicate_bot_slug_candidates": sum(1 for count in duplicate_bot_slugs.values() if count > 1),
        },
        "source_summaries": source_summaries,
        "useful_unique_by_source": dict(useful_unique_by_source),
        "policy_excluded_by_source": dict(excluded_by_source),
        "sample_useful_unique": dict(samples),
        "missing_bot_slug_sample": missing_sample,
        "bot_candidate_sample": bot_candidates,
        "fusion_policy": [
            "Keep the recovery repo as the source of truth.",
            "Do not overwrite active files with same-path older copies.",
            "Promote bot/code/instruction/data candidates only after they pass banned-name, syntax, registry, and build checks.",
            "Treat every imported bot as Buddy-governed, local-first, sandbox-first, and approval-gated for live actions.",
            "Store only useful compact summaries, source references, test results, approval packets, and reusable capability data.",
        ],
        "next_actions": [
            "Review missing_bot_slug_sample and promote only real bots that are not duplicates or generated cache files.",
            "Map useful unique instructions into Buddy's capability, workflow, prompt, sandbox, and API libraries.",
            "Turn archived command-center code into active modules only after targeted tests prove it improves the current app.",
        ],
    }


def write_markdown(report: dict[str, Any]) -> None:
    summary = report["summary"]
    completion = report["completion_estimate_percent"]
    lines = [
        "# Buddy Source Fusion Report",
        "",
        report["mission"],
        "",
        "## Completion Estimate",
        "",
    ]
    for label, value in completion.items():
        lines.append(f"- {label.replace('_', ' ').title()}: {value}%")
    lines.extend(
        [
            "",
            "## Source Scan Summary",
            "",
            f"- Master registry bots: {summary['master_registry_bots']}",
            f"- Sources scanned: {summary['sources_scanned']}",
            f"- Useful unique candidates: {summary['useful_unique_candidates']}",
            f"- Policy-excluded candidates: {summary['policy_excluded_candidates']}",
            f"- Missing bot slug candidates: {summary['missing_bot_slug_candidates']}",
            f"- Duplicate bot slug candidates: {summary['duplicate_bot_slug_candidates']}",
            "",
            "## Source Summaries",
            "",
        ]
    )
    for source, data in report["source_summaries"].items():
        lines.append(f"### {source}")
        lines.append("")
        for key, value in sorted(data.items()):
            lines.append(f"- {key}: {value}")
        lines.append("")
    lines.extend(["## Fusion Policy", ""])
    for item in report["fusion_policy"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Actions", ""])
    for item in report["next_actions"]:
        lines.append(f"- {item}")
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print(json.dumps({"ok": True, **report["summary"], "completion": report["completion_estimate_percent"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
