#!/usr/bin/env python3
"""
Data Integrity Checker for DreamCo-Technologies/Dreamcobots
============================================================
Scans the repository for:
  1. Duplicate files (identical content / same SHA)
  2. Duplicate code symbols (functions, classes) across Python and JS files
  3. Data loss — files deleted in the current change-set that appear critical
  4. Merge-conflict markers left in tracked files

Outputs a structured JSON report and exits with:
  0  — no blocking issues found
  1  — one or more blocking issues found (prevents merge)
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]  # repo root


def _run(cmd: list[str], cwd: Path = ROOT) -> tuple[int, str]:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _list_tracked_files(cwd: Path = ROOT) -> list[Path]:
    """Return all files currently tracked by git."""
    rc, out = _run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=cwd)
    if rc != 0:
        return []
    return [cwd / p.strip() for p in out.splitlines() if p.strip()]


def _changed_files_in_pr(base: str, head: str, cwd: Path = ROOT) -> dict[str, list[str]]:
    """
    Return files categorised by status (added, modified, deleted, renamed).
    Falls back to comparing HEAD with HEAD~1 when base/head are not available.
    """
    rc, out = _run(["git", "diff", "--name-status", f"{base}...{head}"], cwd=cwd)
    if rc != 0:
        rc, out = _run(["git", "diff", "--name-status", "HEAD~1", "HEAD"], cwd=cwd)
    categories: dict[str, list[str]] = defaultdict(list)
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0][0].upper()  # A / M / D / R / C
        fname = parts[-1]
        if status == "A":
            categories["added"].append(fname)
        elif status == "M":
            categories["modified"].append(fname)
        elif status == "D":
            categories["deleted"].append(fname)
        elif status == "R":
            categories["renamed"].append(fname)
        else:
            categories["other"].append(fname)
    return dict(categories)


# ---------------------------------------------------------------------------
# Check 1 — Duplicate files (same content)
# ---------------------------------------------------------------------------

_MIN_DUPLICATE_SIZE = 10  # bytes — skip trivially-small files (e.g. empty __init__.py)


def check_duplicate_files(files: list[Path]) -> list[dict[str, Any]]:
    """Find groups of files with identical content (minimum size threshold applied)."""
    sha_map: dict[str, list[str]] = defaultdict(list)
    for f in files:
        if not f.is_file():
            continue
        try:
            if f.stat().st_size < _MIN_DUPLICATE_SIZE:
                continue  # skip empty / near-empty files (e.g. blank __init__.py)
            sha_map[_sha256(f)].append(str(f.relative_to(ROOT)))
        except (OSError, ValueError):
            continue
    duplicates = []
    for sha, paths in sha_map.items():
        if len(paths) > 1:
            duplicates.append({"sha256": sha[:12], "files": sorted(paths)})
    return duplicates


# ---------------------------------------------------------------------------
# Check 2 — Duplicate symbols (Python functions / classes, JS exports)
# ---------------------------------------------------------------------------

def _python_symbols(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]


_JS_SYM_RE = re.compile(
    r"""(?:^|\s)(?:"""
    r"""function\s+(\w+)"""                           # function foo()
    r"""|class\s+(\w+)"""                             # class Foo
    r"""|(?:const|let|var)\s+(\w+)\s*=\s*(?:function|\(|async\s*\()"""  # const foo = function / () =>
    r"""|(?:const|let|var)\s+(\w+)\s*=\s*async\s+function"""            # const foo = async function
    r""")""",
    re.MULTILINE,
)


def _js_symbols(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    symbols = []
    for m in _JS_SYM_RE.finditer(text):
        name = m.group(1) or m.group(2) or m.group(3) or m.group(4)
        if name:
            symbols.append(name)
    return symbols


def check_duplicate_symbols(files: list[Path]) -> list[dict[str, Any]]:
    """Find function/class names defined in more than one file."""
    symbol_map: dict[str, list[str]] = defaultdict(list)
    for f in files:
        if not f.is_file():
            continue
        rel = str(f.relative_to(ROOT))
        if f.suffix == ".py":
            syms = _python_symbols(f)
        elif f.suffix in (".js", ".mjs", ".cjs", ".ts"):
            syms = _js_symbols(f)
        else:
            continue
        for sym in syms:
            symbol_map[sym].append(rel)

    duplicates = []
    for sym, paths in symbol_map.items():
        unique_paths = sorted(set(paths))
        if len(unique_paths) > 1:
            duplicates.append({"symbol": sym, "defined_in": unique_paths})
    return duplicates


# ---------------------------------------------------------------------------
# Check 3 — Data loss (deleted critical files)
# ---------------------------------------------------------------------------

_MAX_SYMBOLS_DISPLAY = 20   # max duplicate-symbol entries shown in PR comment
_MAX_CHANGELOG_DISPLAY = 50  # max change-log entries shown in PR comment

_CRITICAL_PATTERNS = [
    re.compile(r"^requirements\.txt$"),
    re.compile(r"^package\.json$"),
    re.compile(r"^README(\.md)?$", re.IGNORECASE),
    re.compile(r"^framework/"),
    re.compile(r"^bots/[^/]+/[^/]+\.py$"),       # any Python module inside a bot folder
    re.compile(r"^tests/test_.*\.py$"),
    re.compile(r"^tools/"),
    re.compile(r"^\.github/workflows/"),
]


def check_data_loss(deleted: list[str]) -> list[dict[str, str]]:
    """Flag deleted files that match known-critical patterns."""
    flagged = []
    for path in deleted:
        for pat in _CRITICAL_PATTERNS:
            if pat.search(path):
                flagged.append({"file": path, "reason": f"Matches critical pattern: {pat.pattern}"})
                break
    return flagged


# ---------------------------------------------------------------------------
# Check 4 — Merge-conflict markers
# ---------------------------------------------------------------------------

_CONFLICT_RE = re.compile(r"^(<{7}|={7}|>{7})\s", re.MULTILINE)

_TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".mjs", ".cjs", ".json", ".md",
    ".txt", ".yml", ".yaml", ".html", ".css", ".sh",
}


def check_conflict_markers(changed_files: list[str], cwd: Path = ROOT) -> list[dict[str, Any]]:
    """Return files that still contain git merge-conflict markers."""
    conflicts = []
    for rel in changed_files:
        path = cwd / rel
        if not path.is_file() or path.suffix not in _TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if _CONFLICT_RE.search(text):
            # Collect line numbers
            lines = [
                i + 1
                for i, line in enumerate(text.splitlines())
                if _CONFLICT_RE.match(line)
            ]
            conflicts.append({"file": rel, "conflict_lines": lines})
    return conflicts


# ---------------------------------------------------------------------------
# Change audit log
# ---------------------------------------------------------------------------

def build_change_log(categories: dict[str, list[str]], cwd: Path = ROOT) -> list[dict[str, Any]]:
    log = []
    for status, files in categories.items():
        for f in files:
            entry: dict[str, Any] = {"file": f, "status": status}
            path = cwd / f
            if path.is_file():
                entry["size_bytes"] = path.stat().st_size
            log.append(entry)
    return log


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def build_report(
    dup_files: list[dict],
    dup_symbols: list[dict],
    data_loss: list[dict],
    conflicts: list[dict],
    change_log: list[dict],
    preexisting_dup_files: list[dict] | None = None,
) -> dict[str, Any]:
    blocking = bool(dup_files or data_loss or conflicts)
    warnings = bool(dup_symbols or preexisting_dup_files)
    return {
        "status": "BLOCKED" if blocking else ("WARNING" if warnings else "OK"),
        "blocking": blocking,
        "summary": {
            "duplicate_files_new": len(dup_files),
            "duplicate_files_preexisting": len(preexisting_dup_files or []),
            "duplicate_symbols": len(dup_symbols),
            "data_loss_risk": len(data_loss),
            "conflict_markers": len(conflicts),
            "total_changed_files": len(change_log),
        },
        "duplicate_files": dup_files,
        "duplicate_files_preexisting": preexisting_dup_files or [],
        "duplicate_symbols": dup_symbols,
        "data_loss_risk": data_loss,
        "conflict_markers": conflicts,
        "change_log": change_log,
    }


def format_markdown(report: dict[str, Any]) -> str:
    status = report["status"]
    summary = report["summary"]
    icon = {"OK": "✅", "WARNING": "⚠️", "BLOCKED": "🚫"}.get(status, "❓")

    lines = [
        "## 🔍 DreamCobots Data Integrity Report",
        "",
        f"**Overall Status: {icon} {status}**",
        "",
        "### Summary",
        "| Check | Count | Result |",
        "|-------|-------|--------|",
    ]

    def row(label: str, count: int, blocking: bool) -> str:
        if count == 0:
            return f"| {label} | {count} | ✅ None detected |"
        marker = "🚫 BLOCKED" if blocking else "⚠️ Warning"
        return f"| {label} | {count} | {marker} |"

    lines += [
        row("Duplicate files introduced by this change", summary["duplicate_files_new"], True),
        row("Pre-existing duplicate files (repo-wide)", summary["duplicate_files_preexisting"], False),
        row("Duplicate code symbols (this change)", summary["duplicate_symbols"], False),
        row("Data loss risk (deleted critical files)", summary["data_loss_risk"], True),
        row("Merge conflict markers", summary["conflict_markers"], True),
        f"| Files changed in this update | {summary['total_changed_files']} | ℹ️ |",
        "",
    ]

    if report["duplicate_files"]:
        lines += ["### 🚫 Duplicate Files Introduced by This Change", ""]
        lines += [
            "These files added/modified in this PR have identical content to other files in the repository.",
            "Consolidate them before merging.",
            "",
        ]
        for entry in report["duplicate_files"]:
            lines.append(f"- **SHA:** `{entry['sha256']}` — files: `{'`, `'.join(entry['files'])}`")
        lines += [
            "",
            "**Recommended action:** Keep one canonical copy and update all imports/references.",
            "",
        ]

    if report.get("duplicate_files_preexisting"):
        lines += ["### ⚠️ Pre-existing Duplicate Files (Repository-wide)", ""]
        lines += [
            "These files already had identical content before this change.",
            "They are not blocking this merge but should be cleaned up.",
            "",
        ]
        for entry in report["duplicate_files_preexisting"]:
            lines.append(f"- **SHA:** `{entry['sha256']}` — files: `{'`, `'.join(entry['files'])}`")
        lines.append("")

    if report["data_loss_risk"]:
        lines += ["### 🚫 Data Loss Risk — Deleted Critical Files", ""]
        for entry in report["data_loss_risk"]:
            lines.append(f"- `{entry['file']}` — {entry['reason']}")
        lines += [
            "",
            "**Recommended action:** Restore these files or confirm intentional removal before merging.",
            "",
        ]

    if report["conflict_markers"]:
        lines += ["### 🚫 Unresolved Merge Conflict Markers", ""]
        for entry in report["conflict_markers"]:
            linenos = ", ".join(str(n) for n in entry["conflict_lines"][:10])
            lines.append(f"- `{entry['file']}` — conflict markers at line(s): {linenos}")
        lines += [
            "",
            "**Recommended action:** Resolve all conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) before merging.",
            "",
        ]

    if report["duplicate_symbols"]:
        lines += ["### ⚠️ Duplicate Code Symbols", ""]
        lines += [
            "The following function/class names appear in multiple files.",
            "This is a warning — it may be intentional (e.g., base classes) but should be reviewed.",
            "",
        ]
        for entry in report["duplicate_symbols"][:_MAX_SYMBOLS_DISPLAY]:  # cap to keep comment readable
            files = ", ".join(f"`{p}`" for p in entry["defined_in"])
            lines.append(f"- `{entry['symbol']}` — defined in: {files}")
        if len(report["duplicate_symbols"]) > _MAX_SYMBOLS_DISPLAY:
            lines.append(f"- … and {len(report['duplicate_symbols']) - _MAX_SYMBOLS_DISPLAY} more (see JSON report artifact)")
        lines.append("")

    if report["change_log"]:
        lines += ["### 📋 Change Audit Log", ""]
        lines += ["| File | Status | Size |", "|------|--------|------|"]
        for entry in report["change_log"][:_MAX_CHANGELOG_DISPLAY]:
            size = f"{entry.get('size_bytes', '—')} bytes" if "size_bytes" in entry else "deleted"
            lines.append(f"| `{entry['file']}` | {entry['status']} | {size} |")
        if len(report["change_log"]) > _MAX_CHANGELOG_DISPLAY:
            lines.append(f"| … | +{len(report['change_log']) - _MAX_CHANGELOG_DISPLAY} more | |")
        lines.append("")

    if report["blocking"]:
        lines += [
            "---",
            "🚫 **Merge is blocked** until the issues above are resolved.",
            "Please fix all blocking issues and push a new commit to re-trigger this check.",
        ]
    elif report["status"] == "WARNING":
        lines += [
            "---",
            "⚠️ **Merge is allowed** but please review the warnings above.",
        ]
    else:
        lines += [
            "---",
            "✅ **All integrity checks passed.** This branch is safe to merge.",
        ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="DreamCobots data-integrity checker")
    parser.add_argument("--base", default="origin/main", help="Base ref for diff (default: origin/main)")
    parser.add_argument("--head", default="HEAD", help="Head ref for diff (default: HEAD)")
    parser.add_argument("--output-json", default="/tmp/integrity-report.json", help="Path to write JSON report")
    parser.add_argument("--output-md", default="/tmp/integrity-report.md", help="Path to write Markdown report")
    parser.add_argument(
        "--skip-symbol-scan",
        action="store_true",
        help="Skip the (slower) duplicate-symbol scan across all tracked files",
    )
    args = parser.parse_args()

    print(f"[data-integrity] Base: {args.base}  Head: {args.head}")

    # 1. Get changed files
    categories = _changed_files_in_pr(args.base, args.head)
    all_changed = [f for files in categories.values() for f in files]
    print(f"[data-integrity] Changed files: {len(all_changed)}")

    # 2. Get all tracked files for file-level duplicate scan
    tracked = _list_tracked_files()
    print(f"[data-integrity] Total tracked files: {len(tracked)}")

    # 3. Run checks
    # Compute set of files touched by this PR/push for scoping duplicate results
    pr_touched = set(all_changed)

    all_dup_files = check_duplicate_files(tracked)
    # Split into: blocking (duplicate introduced by this change) vs. pre-existing warning
    dup_files_new: list[dict] = []
    dup_files_existing: list[dict] = []
    for entry in all_dup_files:
        if any(f in pr_touched for f in entry["files"]):
            dup_files_new.append(entry)
        else:
            dup_files_existing.append(entry)

    dup_symbols: list[dict] = []
    if not args.skip_symbol_scan:
        all_dup_symbols = check_duplicate_symbols(tracked)
        # Only flag as a new duplicate if a changed file introduces a duplicate symbol
        for entry in all_dup_symbols:
            if any(f in pr_touched for f in entry["defined_in"]):
                dup_symbols.append(entry)
    data_loss = check_data_loss(categories.get("deleted", []))
    conflicts = check_conflict_markers(all_changed)
    change_log = build_change_log(categories)

    # 4. Build report (pass pre-existing duplicates separately for informational display)
    report = build_report(dup_files_new, dup_symbols, data_loss, conflicts, change_log,
                          preexisting_dup_files=dup_files_existing)
    md = format_markdown(report)

    # 5. Write outputs
    Path(args.output_json).write_text(json.dumps(report, indent=2))
    Path(args.output_md).write_text(md)
    print(md)

    if report["blocking"]:
        print("\n[data-integrity] ❌ BLOCKING issues detected. Merge prevented.")
        return 1

    if report["status"] == "WARNING":
        print("\n[data-integrity] ⚠️  Warnings detected. Review before merging.")
        return 0

    print("\n[data-integrity] ✅ All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
