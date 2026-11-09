#!/usr/bin/env python3
"""Audit Git-tracked Markdown plans against repository implementation references."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config/buddy/markdown-implementation-gap-policy.json"
JSON_OUTPUT = ROOT / "config/generated/markdown-implementation-gap-audit.json"
WEB_OUTPUT = ROOT / "website/data/markdown-implementation-gap-audit.json"
REPORT_OUTPUT = ROOT / "reports/MARKDOWN_IMPLEMENTATION_GAP_AUDIT.md"
PATH_SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".json", ".yml", ".yaml", ".html", ".css", ".sh", ".toml", ".sql"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def tracked_markdown(root: Path = ROOT) -> list[Path]:
    result = subprocess.run(["git", "ls-files", "--", "*.md"], cwd=root, check=True, capture_output=True, text=True)
    excluded = set(json.loads((root / "config/buddy/markdown-implementation-gap-policy.json").read_text(encoding="utf-8"))["excluded_path_segments"])
    return sorted(root / line for line in result.stdout.splitlines() if line and not excluded.intersection(Path(line).parts))


def candidate_paths(text: str) -> set[str]:
    candidates = set(re.findall(r"`([^`]+)`", text))
    candidates.update(re.findall(r"\\]\\(([^)]+)\\)", text))
    output = set()
    for value in candidates:
        token = value.strip().split()[0].strip(".,;:()[]{}<>")
        if token.startswith("./"):
            token = token[2:]
        if token.startswith(("https://", "http://", "mailto:", "#")):
            continue
        suffix = Path(token).suffix.lower()
        if suffix not in PATH_SUFFIXES:
            continue
        if "/" not in token and not token.startswith(".github/"):
            continue
        output.add(token)
    return output


def classify_reference(path: str, policy: dict[str, Any]) -> str:
    for kind, roots in policy["path_roots"].items():
        if any(path.startswith(root) for root in roots):
            return kind
    if path.startswith(".github/workflows/"):
        return "workflows"
    return "other"


def analyze_document(relative: str, text: str, policy: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    refs = sorted(candidate_paths(text))
    existing = [path for path in refs if (root / path).is_file()]
    missing = [path for path in refs if not (root / path).is_file()]
    buckets: dict[str, list[str]] = {key: [] for key in policy["path_roots"]}
    for path in existing:
        kind = classify_reference(path, policy)
        if kind in buckets:
            buckets[kind].append(path)
    actionable_lines = [
        line.strip() for line in text.splitlines()
        if re.search(r"\b(must|should|shall|required|needs to|implement|build|create|support|enable|provide|automate|verify|test|deploy)\b", line, re.I)
        and line.strip()
    ]
    if missing:
        status = "broken_path_references"
        next_action = "Repair or explicitly supersede the missing repository path references."
    elif not buckets["implementation"]:
        status = "implementation_reference_missing" if actionable_lines else "reference_only"
        next_action = "Find or build the implementation, or record why the requirement is intentionally documentation-only."
    elif not buckets["tests"]:
        status = "test_reference_missing"
        next_action = "Add focused tests and acceptance evidence for the referenced implementation."
    else:
        status = "implementation_and_test_paths_referenced_not_verified"
        next_action = "Run the linked tests and attach CI, benchmark, regression, and runtime evidence before promotion."
    return {
        "path": relative,
        "title": next((line.lstrip("# ").strip() for line in text.splitlines() if line.startswith("#")), Path(relative).stem),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "actionable_claim_lines": len(actionable_lines),
        "referenced_paths": existing,
        "missing_paths": missing,
        "implementation_paths": sorted(buckets["implementation"]),
        "test_paths": sorted(buckets["tests"]),
        "workflow_paths": sorted(buckets["workflows"]),
        "configuration_paths": sorted(buckets["configuration"]),
        "documentation_paths": sorted(buckets["documentation"]),
        "gap_status": status,
        "next_action": next_action,
        "execution_verified": False,
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    policy = json.loads((root / "config/buddy/markdown-implementation-gap-policy.json").read_text(encoding="utf-8"))
    documents = []
    for path in tracked_markdown(root):
        relative = path.relative_to(root).as_posix()
        documents.append(analyze_document(relative, path.read_text(encoding="utf-8", errors="replace"), policy, root))
    counts = Counter(row["gap_status"] for row in documents)
    return {
        "schema": "dreamco.buddy.markdown_implementation_gap_audit.v1",
        "generated_at": now_iso(),
        "inventory_mode": policy["inventory_mode"],
        "document_count": len(documents),
        "actionable_claim_lines": sum(row["actionable_claim_lines"] for row in documents),
        "gap_status_counts": dict(sorted(counts.items())),
        "documents_with_missing_paths": sum(bool(row["missing_paths"]) for row in documents),
        "documents_without_implementation_references": sum(not row["implementation_paths"] for row in documents),
        "documents_without_test_references": sum(bool(row["implementation_paths"]) and not row["test_paths"] for row in documents),
        "documents": documents,
        "truth_boundary": "This report maps documentation references to repository paths. It does not prove that code implements the full requirement, that tests pass, or that a feature is production-ready.",
    }


def render_report(data: dict[str, Any]) -> str:
    lines = [
        "# Markdown-to-Implementation Gap Audit",
        "",
        f"Generated: {data['generated_at']}",
        "",
        "This is a live inventory of Git-tracked Markdown requirements and their linked repository paths. Counts are computed from the current Git tree; no document, claim, or reference count is a fixed ceiling.",
        "",
        "## Current derived summary",
        "",
        f"- Markdown documents scanned: {data['document_count']}",
        f"- Actionable claim lines detected: {data['actionable_claim_lines']}",
        f"- Documents with missing path references: {data['documents_with_missing_paths']}",
        f"- Documents without implementation references: {data['documents_without_implementation_references']}",
        f"- Documents with implementation references but no test references: {data['documents_without_test_references']}",
        "",
        "## Gap inventory",
        "",
    ]
    for row in data["documents"]:
        lines.extend([
            f"### {row['path']}",
            "",
            f"- **Status:** `{row['gap_status']}`",
            f"- **Actionable claim lines:** {row['actionable_claim_lines']}",
            f"- **Implementation paths:** {', '.join(f'`{x}`' for x in row['implementation_paths']) or 'None detected'}",
            f"- **Test paths:** {', '.join(f'`{x}`' for x in row['test_paths']) or 'None detected'}",
            f"- **Missing paths:** {', '.join(f'`{x}`' for x in row['missing_paths']) or 'None detected'}",
            f"- **Next action:** {row['next_action']}",
            "- **Execution verified:** No; run-specific evidence is required.",
            "",
        ])
    lines.extend(["## Truth boundary", "", data["truth_boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="regenerate JSON, Pages mirror, and Markdown report")
    mode.add_argument("--check", action="store_true", help="fail when generated outputs are stale")
    args = parser.parse_args()
    data = build()
    if args.check and JSON_OUTPUT.exists():
        try:
            previous = json.loads(JSON_OUTPUT.read_text(encoding="utf-8"))
            data["generated_at"] = previous.get("generated_at")
        except (json.JSONDecodeError, OSError):
            pass
    outputs = {
        JSON_OUTPUT: json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        WEB_OUTPUT: json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        REPORT_OUTPUT: render_report(data),
    }
    drift = [path for path, value in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != value]
    if args.check:
        if drift:
            print(json.dumps({"ok": False, "drift": [path.relative_to(ROOT).as_posix() for path in drift]}, indent=2))
            return 1
    else:
        for path, value in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")
    print(json.dumps({"ok": True, "documents": data["document_count"], "gaps": data["gap_status_counts"], "output": REPORT_OUTPUT.relative_to(ROOT).as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
