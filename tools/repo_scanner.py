#!/usr/bin/env python3
"""
DreamCo Repo Scanner
====================

A beginner-friendly automated scanner that inspects the repository for common
issues and produces a single unified report.  Run it locally or via GitHub
Actions on every push.

Checks performed
----------------
1. Missing Python dependencies / broken imports
2. Referenced files (.json, .txt, .csv, .py) that do not exist on disk
3. Empty or suspiciously small (< 10 bytes) files
4. GitHub Actions workflow inspection — bad ``run:`` paths / script references
5. Attempt to execute every Python file and capture failures
6. Full repository file-tree overview
7. Unified report (all findings in one place)

Usage
-----
    python tools/repo_scanner.py [--path ROOT] [--no-exec]

Options
-------
--path ROOT   Root directory to scan (default: repository root).
--no-exec     Skip the "try to run every Python file" step (faster).
--output FILE Write the unified report to FILE instead of stdout.

Exit codes
----------
0 — Scan complete (issues may have been found — check the report).
The scanner intentionally exits 0 so it never blocks CI on its own.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants / helpers
# ---------------------------------------------------------------------------

_SEP = "=" * 70

# Files/directories to skip entirely during scanning
_SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        ".mypy_cache",
        ".pytest_cache",
        "dist",
        "build",
        ".tox",
    }
)

_SKIP_FILES: frozenset[str] = frozenset(
    {
        "repo_scanner.py",  # don't analyse ourselves
    }
)

# Patterns inside Python source that reference external files
_FILE_REF_PATTERN = re.compile(
    r"""(?:open|pd\.read_csv|pd\.read_json|pd\.read_excel|json\.load|
         json\.loads|yaml\.safe_load|yaml\.load|
         with\s+open)\s*\(\s*[\"']([^\"']+\.(?:json|txt|csv|py|yaml|yml))[\"']""",
    re.VERBOSE,
)

# Built-in stdlib module names (a representative subset used for fast exclusion)
_STDLIB_TOP_LEVEL: frozenset[str] = frozenset(sys.stdlib_module_names)  # type: ignore[attr-defined]


def _iter_python_files(root: Path) -> list[Path]:
    """Return a list of all .py files under *root*, skipping ignored directories."""
    result: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored directories in-place
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fname in filenames:
            if fname.endswith(".py") and fname not in _SKIP_FILES:
                result.append(Path(dirpath) / fname)
    return sorted(result)


def _iter_all_files(root: Path) -> list[Path]:
    """Return a list of every non-ignored file under *root*."""
    result: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fname in filenames:
            result.append(Path(dirpath) / fname)
    return sorted(result)


def _short(path: Path, root: Path) -> str:
    """Return a path string relative to *root* for cleaner output."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# 1. Missing Python dependencies / broken imports
# ---------------------------------------------------------------------------

def scan_missing_imports(root: Path) -> dict[str, Any]:
    """
    Walk every Python file and collect ``import`` / ``from ... import``
    statements whose top-level module cannot be found in the current
    Python environment.

    Returns a dict with keys:
        issues   — list of {"file", "line", "module", "statement"} dicts
        scanned  — number of files examined
    """
    issues: list[dict] = []
    scanned = 0

    for py_file in _iter_python_files(root):
        scanned += 1
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            module_name: str | None = None
            stmt_text = ""

            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split(".")[0]
                    stmt_text = f"import {alias.name}"
                    _check_module(module_name, stmt_text, node.lineno, py_file, root, issues)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split(".")[0]
                    stmt_text = f"from {node.module} import ..."
                    _check_module(module_name, stmt_text, node.lineno, py_file, root, issues)

    return {"issues": issues, "scanned": scanned}


def _check_module(
    module: str,
    stmt: str,
    lineno: int,
    py_file: Path,
    root: Path,
    issues: list[dict],
) -> None:
    """Append to *issues* if *module* cannot be resolved."""
    if not module:
        return
    # Skip stdlib modules — they are always available
    if module in _STDLIB_TOP_LEVEL:
        return
    # Try importlib first (handles installed packages)
    if importlib.util.find_spec(module) is not None:
        return
    # Check if it's a local package inside the repo (sibling directory)
    if (root / module).is_dir() or (root / f"{module}.py").is_file():
        return
    issues.append(
        {
            "file": _short(py_file, root),
            "line": lineno,
            "module": module,
            "statement": stmt,
        }
    )


# ---------------------------------------------------------------------------
# 2. Referenced files that don't exist
# ---------------------------------------------------------------------------

def scan_missing_file_references(root: Path) -> dict[str, Any]:
    """
    Scan Python source files for string literals that look like file paths
    (ending in .json, .txt, .csv, .py, .yaml, .yml) and verify they exist
    on disk relative to the repository root.

    Dynamically generated paths (containing format placeholders or variable
    characters) are skipped to avoid false positives.

    Returns {"issues": [...], "scanned": int}
    """
    issues: list[dict] = []
    scanned = 0

    for py_file in _iter_python_files(root):
        scanned += 1
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for match in _FILE_REF_PATTERN.finditer(source):
            ref = match.group(1)
            # Skip anything that looks dynamic (curly braces, %, $, etc.)
            if any(c in ref for c in ("{", "}", "%", "$", "*", "?")):
                continue
            candidate = root / ref
            if not candidate.exists():
                lineno = source[: match.start()].count("\n") + 1
                issues.append(
                    {
                        "file": _short(py_file, root),
                        "line": lineno,
                        "referenced_path": ref,
                    }
                )

    return {"issues": issues, "scanned": scanned}


# ---------------------------------------------------------------------------
# 3. Empty / suspect files
# ---------------------------------------------------------------------------

_EMPTY_THRESHOLD_BYTES = 10  # files smaller than this are flagged


def scan_empty_files(root: Path) -> dict[str, Any]:
    """
    Find files that are completely empty or suspiciously small
    (< _EMPTY_THRESHOLD_BYTES bytes).

    Returns {"issues": [...], "scanned": int}
    """
    issues: list[dict] = []
    scanned = 0

    for f in _iter_all_files(root):
        scanned += 1
        try:
            size = f.stat().st_size
        except OSError:
            continue
        if size < _EMPTY_THRESHOLD_BYTES:
            issues.append(
                {
                    "file": _short(f, root),
                    "size_bytes": size,
                    "note": "empty" if size == 0 else f"only {size} bytes",
                }
            )

    return {"issues": issues, "scanned": scanned}


# ---------------------------------------------------------------------------
# 4. GitHub Actions workflow inspection
# ---------------------------------------------------------------------------

def scan_workflows(root: Path) -> dict[str, Any]:
    """
    Parse every ``*.yml`` file under ``.github/workflows/`` and look for
    ``run:`` blocks that reference Python scripts or shell commands whose
    target file does not exist in the repository.

    Returns {"issues": [...], "scanned": int}
    """
    issues: list[dict] = []
    scanned = 0

    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return {"issues": issues, "scanned": scanned, "note": "No .github/workflows directory found"}

    # Regex patterns for common problematic references
    _python_script = re.compile(r"python(?:3)?\s+([\w./-]+\.py)")
    _node_script = re.compile(r"node\s+([\w./-]+\.js)")

    for yml_file in sorted(workflows_dir.glob("*.yml")):
        scanned += 1
        try:
            content = yml_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for lineno, raw_line in enumerate(content.splitlines(), start=1):
            line = raw_line.strip()

            # Check Python script references
            for match in _python_script.finditer(line):
                script_path = match.group(1)
                if not (root / script_path).exists():
                    issues.append(
                        {
                            "workflow": _short(yml_file, root),
                            "line": lineno,
                            "command": line.strip(),
                            "missing_file": script_path,
                            "type": "python_script",
                        }
                    )

            # Check Node script references
            for match in _node_script.finditer(line):
                script_path = match.group(1)
                if not (root / script_path).exists():
                    issues.append(
                        {
                            "workflow": _short(yml_file, root),
                            "line": lineno,
                            "command": line.strip(),
                            "missing_file": script_path,
                            "type": "node_script",
                        }
                    )

    return {"issues": issues, "scanned": scanned}


# ---------------------------------------------------------------------------
# 5. Manual execution checks
# ---------------------------------------------------------------------------

_EXEC_TIMEOUT_SECONDS = 10  # per-file timeout


def scan_exec_checks(root: Path) -> dict[str, Any]:
    """
    Attempt to import-check (``python -m py_compile``) every Python file.
    Full execution is intentionally avoided to prevent side-effects; syntax
    and top-level import errors are still caught.

    Returns {"issues": [...], "scanned": int}
    """
    issues: list[dict] = []
    scanned = 0

    for py_file in _iter_python_files(root):
        scanned += 1
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)],
                capture_output=True,
                text=True,
                timeout=_EXEC_TIMEOUT_SECONDS,
                cwd=str(root),
            )
            if result.returncode != 0:
                issues.append(
                    {
                        "file": _short(py_file, root),
                        "error": (result.stderr or result.stdout).strip(),
                        "type": "syntax_error",
                    }
                )
        except subprocess.TimeoutExpired:
            issues.append(
                {
                    "file": _short(py_file, root),
                    "error": f"Timed out after {_EXEC_TIMEOUT_SECONDS}s",
                    "type": "timeout",
                }
            )
        except OSError as exc:
            issues.append(
                {
                    "file": _short(py_file, root),
                    "error": str(exc),
                    "type": "os_error",
                }
            )

    return {"issues": issues, "scanned": scanned}


# ---------------------------------------------------------------------------
# 6. Repository file-tree overview
# ---------------------------------------------------------------------------

def build_file_tree(root: Path, max_depth: int = 4) -> str:
    """
    Return a human-readable tree of the repository (up to *max_depth* levels).
    Skipped directories (node_modules, .git, etc.) are omitted.
    """
    lines: list[str] = [str(root)]

    def _walk(current: Path, prefix: str, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            entries = sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            return
        entries = [e for e in entries if e.name not in _SKIP_DIRS]
        for i, entry in enumerate(entries):
            connector = "└── " if i == len(entries) - 1 else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                extension = "    " if i == len(entries) - 1 else "│   "
                _walk(entry, prefix + extension, depth + 1)

    _walk(root, "", 1)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 7. Report builder
# ---------------------------------------------------------------------------

def _section(title: str, emoji: str = "🔍") -> str:
    return f"\n{_SEP}\n{emoji}  {title}\n{_SEP}"


def build_report(
    root: Path,
    imports_result: dict,
    refs_result: dict,
    empty_result: dict,
    workflow_result: dict,
    exec_result: dict,
    tree: str,
) -> str:
    """Compile all scan results into a single, beginner-friendly report."""
    lines: list[str] = []

    lines.append(_SEP)
    lines.append("🤖  DreamCo Repo Scanner — Unified Report")
    lines.append(f"    Repository root : {root}")
    lines.append(_SEP)

    # ------------------------------------------------------------------
    # 1. Missing imports
    # ------------------------------------------------------------------
    lines.append(_section("1. Missing Python Dependencies / Broken Imports", "📦"))
    issues = imports_result["issues"]
    lines.append(f"Files scanned : {imports_result['scanned']}")
    if issues:
        lines.append(f"Issues found  : {len(issues)}")
        lines.append("")
        lines.append("  💡 Tip — install missing packages with:  pip install <package-name>")
        lines.append("")
        for item in issues:
            lines.append(
                f"  ❌  {item['file']}  (line {item['line']})  →  "
                f"'{item['module']}' not found   [{item['statement']}]"
            )
    else:
        lines.append("  ✅  No missing imports detected.")

    # ------------------------------------------------------------------
    # 2. Missing file references
    # ------------------------------------------------------------------
    lines.append(_section("2. Missing Referenced Files", "📂"))
    issues = refs_result["issues"]
    lines.append(f"Files scanned : {refs_result['scanned']}")
    if issues:
        lines.append(f"Issues found  : {len(issues)}")
        lines.append("")
        lines.append("  💡 Tip — make sure every file referenced in code is committed to the repo.")
        lines.append("")
        for item in issues:
            lines.append(
                f"  ❌  {item['file']}  (line {item['line']})  →  "
                f"references missing file: '{item['referenced_path']}'"
            )
    else:
        lines.append("  ✅  No missing file references detected.")

    # ------------------------------------------------------------------
    # 3. Empty / suspect files
    # ------------------------------------------------------------------
    lines.append(_section("3. Empty or Suspect Files", "🗑️"))
    issues = empty_result["issues"]
    lines.append(f"Files scanned : {empty_result['scanned']}")
    if issues:
        lines.append(f"Issues found  : {len(issues)}")
        lines.append("")
        lines.append("  💡 Tip — empty files may be placeholder stubs or incomplete commits.")
        lines.append("")
        for item in issues:
            lines.append(f"  ⚠️   {item['file']}  ({item['note']})")
    else:
        lines.append("  ✅  No empty or suspect files detected.")

    # ------------------------------------------------------------------
    # 4. Workflow inspection
    # ------------------------------------------------------------------
    lines.append(_section("4. GitHub Actions Workflow Inspection", "⚙️"))
    issues = workflow_result["issues"]
    lines.append(f"Workflows scanned : {workflow_result.get('scanned', 0)}")
    if workflow_result.get("note"):
        lines.append(f"  ℹ️   {workflow_result['note']}")
    if issues:
        lines.append(f"Issues found      : {len(issues)}")
        lines.append("")
        lines.append("  💡 Tip — ensure all scripts referenced in workflow files exist in the repo.")
        lines.append("")
        for item in issues:
            lines.append(
                f"  ❌  {item['workflow']}  (line {item['line']})  →  "
                f"missing {item['type'].replace('_', ' ')}: '{item['missing_file']}'"
            )
            lines.append(f"       command: {item['command'][:120]}")
    else:
        lines.append("  ✅  No workflow issues detected.")

    # ------------------------------------------------------------------
    # 5. Execution / syntax checks
    # ------------------------------------------------------------------
    lines.append(_section("5. Python File Syntax & Compile Checks", "🧪"))
    issues = exec_result["issues"]
    lines.append(f"Files checked : {exec_result['scanned']}")
    if issues:
        lines.append(f"Issues found  : {len(issues)}")
        lines.append("")
        lines.append("  💡 Tip — fix syntax errors so your bots can actually be loaded by Python.")
        lines.append("")
        for item in issues:
            lines.append(f"  ❌  {item['file']}  [{item['type']}]")
            for error_line in item["error"].splitlines():
                lines.append(f"       {error_line}")
    else:
        lines.append("  ✅  All Python files pass syntax / compile check.")

    # ------------------------------------------------------------------
    # 6. File tree
    # ------------------------------------------------------------------
    lines.append(_section("6. Repository File Overview", "🌲"))
    lines.append(tree)

    # ------------------------------------------------------------------
    # 7. Summary
    # ------------------------------------------------------------------
    lines.append(_section("7. Scan Summary", "📋"))
    total_issues = (
        len(imports_result["issues"])
        + len(refs_result["issues"])
        + len(empty_result["issues"])
        + len(workflow_result["issues"])
        + len(exec_result["issues"])
    )
    if total_issues == 0:
        lines.append("  🎉  No issues found — repo looks healthy!")
    else:
        lines.append(f"  🚨  Total issues detected: {total_issues}")
        lines.append("")
        lines.append(f"      Missing imports         : {len(imports_result['issues'])}")
        lines.append(f"      Missing file references : {len(refs_result['issues'])}")
        lines.append(f"      Empty / suspect files   : {len(empty_result['issues'])}")
        lines.append(f"      Workflow issues         : {len(workflow_result['issues'])}")
        lines.append(f"      Syntax / compile errors : {len(exec_result['issues'])}")
        lines.append("")
        lines.append("  ℹ️   Review the sections above for details and fix suggestions.")

    lines.append(_SEP)
    lines.append("Scan complete.")
    lines.append(_SEP)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DreamCo Repo Scanner — find missing files, broken imports, and workflow issues.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--path",
        default=None,
        help="Repository root directory (default: auto-detected from this file's location).",
    )
    parser.add_argument(
        "--no-exec",
        action="store_true",
        default=False,
        help="Skip the Python file execution / compile check (faster).",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Write the unified report to FILE instead of printing to stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.path:
        root = Path(args.path).resolve()
    else:
        # Default: two levels up from this file (tools/ → repo root)
        root = Path(__file__).resolve().parent.parent

    print(f"🤖  DreamCo Repo Scanner starting …  root={root}", flush=True)

    print("  → [1/6] Scanning for missing imports …", flush=True)
    imports_result = scan_missing_imports(root)

    print("  → [2/6] Scanning for missing file references …", flush=True)
    refs_result = scan_missing_file_references(root)

    print("  → [3/6] Scanning for empty / suspect files …", flush=True)
    empty_result = scan_empty_files(root)

    print("  → [4/6] Inspecting GitHub Actions workflows …", flush=True)
    workflow_result = scan_workflows(root)

    if args.no_exec:
        print("  → [5/6] Skipping execution checks (--no-exec).", flush=True)
        exec_result: dict[str, Any] = {"issues": [], "scanned": 0}
    else:
        print("  → [5/6] Running Python compile checks …", flush=True)
        exec_result = scan_exec_checks(root)

    print("  → [6/6] Building file tree …", flush=True)
    tree = build_file_tree(root)

    report = build_report(
        root,
        imports_result,
        refs_result,
        empty_result,
        workflow_result,
        exec_result,
        tree,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\n📄  Report written to: {output_path}")
    else:
        print(report)

    # Always exit 0 — the scanner is informational and must not block CI
    return 0


if __name__ == "__main__":
    sys.exit(main())
