#!/usr/bin/env python3
"""Audit DreamCo Python files for local-module import path drift.

This audit focuses on imports that look like they should resolve to files in
this repository. Third-party packages are left to dependency audits.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dreamco_import_paths import LEGACY_IMPORT_PATHS, configure_import_paths


configure_import_paths()

REPORT_JSON = ROOT / "reports" / "local_import_audit_report.json"
REPORT_MD = ROOT / "reports" / "LOCAL_IMPORT_AUDIT_REPORT.md"

IGNORE_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "venv",
    ".venv",
}

KNOWN_EXTERNAL_ROOTS = {
    "aiohttp",
    "asyncpg",
    "boto3",
    "bs4",
    "click",
    "cv2",
    "deepface",
    "distilabel",
    "docker",
    "dotenv",
    "fastapi",
    "flask",
    "flask_cors",
    "httpx",
    "jinja2",
    "kaggle",
    "locust",
    "numpy",
    "openai",
    "openpyxl",
    "pandas",
    "pdfminer",
    "pgvector",
    "PIL",
    "prometheus_client",
    "psutil",
    "psycopg2",
    "pydantic",
    "pytest",
    "redis",
    "reportlab",
    "requests",
    "rich",
    "selenium",
    "sklearn",
    "slowapi",
    "speech_recognition",
    "speechbrain",
    "starlette",
    "stripe",
    "tensorflow",
    "twilio",
    "uvicorn",
    "vosk",
    "webdriver_manager",
    "yaml",
}


def is_ignored(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def read_python_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.py") if not is_ignored(path.relative_to(ROOT)))


def local_module_index(files: list[Path]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for path in files:
        rel = path.relative_to(ROOT)
        if path.name == "__init__.py":
            index[path.parent.name].append(str(rel))
        else:
            index[path.stem].append(str(rel))
    return dict(index)


def top_level_packages() -> set[str]:
    packages = set()
    for init_file in ROOT.glob("*/__init__.py"):
        if not is_ignored(init_file.relative_to(ROOT)):
            packages.add(init_file.parent.name)
    for py_file in ROOT.glob("*.py"):
        packages.add(py_file.stem)
    return packages


def import_roots(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(errors="ignore"))
    except SyntaxError:
        return []

    roots: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.append(node.module.split(".")[0])
    return roots


def stdlib_roots() -> set[str]:
    roots = set(getattr(sys, "stdlib_module_names", set()))
    roots.update(
        {
            "__future__",
            "abc",
            "argparse",
            "ast",
            "asyncio",
            "base64",
            "collections",
            "contextlib",
            "copy",
            "csv",
            "dataclasses",
            "datetime",
            "email",
            "enum",
            "functools",
            "hashlib",
            "importlib",
            "io",
            "itertools",
            "json",
            "logging",
            "math",
            "mimetypes",
            "os",
            "pathlib",
            "random",
            "re",
            "sched",
            "shlex",
            "sqlite3",
            "statistics",
            "subprocess",
            "sys",
            "tempfile",
            "threading",
            "time",
            "traceback",
            "typing",
            "unicodedata",
            "urllib",
            "uuid",
        }
    )
    return roots


def is_resolvable_from_repo(module: str) -> bool:
    original_path = list(sys.path)
    try:
        configure_import_paths()
        return importlib.util.find_spec(module) is not None
    except (ImportError, AttributeError, ValueError):
        return False
    finally:
        sys.path[:] = original_path


def audit() -> dict[str, Any]:
    files = read_python_files()
    module_index = local_module_index(files)
    package_roots = top_level_packages()
    stdlib = stdlib_roots()
    issues: list[dict[str, str]] = []
    checked_imports = 0

    for path in files:
        rel = str(path.relative_to(ROOT))
        for root in import_roots(path):
            checked_imports += 1
            if root in stdlib or root in KNOWN_EXTERNAL_ROOTS:
                continue
            if root in package_roots and is_resolvable_from_repo(root):
                continue
            if root in module_index and not is_resolvable_from_repo(root):
                issues.append(
                    {
                        "file": rel,
                        "import": root,
                        "reason": "local module name exists in the repo but is not importable from the repository root",
                        "candidates": ", ".join(module_index[root][:10]),
                    }
                )

    return {
        "schema": "dreamco.local_import_audit.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "python_files": len(files),
            "checked_imports": checked_imports,
            "legacy_import_paths": len([path for path in LEGACY_IMPORT_PATHS if path.exists()]),
            "local_module_names": len(module_index),
            "issues": len(issues),
        },
        "issues": issues,
    }


def write_reports(report: dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2) + "\n")

    lines = [
        "# DreamCo Local Import Audit",
        "",
        f"Generated: {report['generated_at']}",
        "",
        f"- Python files: {report['summary']['python_files']}",
        f"- Checked imports: {report['summary']['checked_imports']}",
        f"- Legacy import paths: {report['summary']['legacy_import_paths']}",
        f"- Local module names: {report['summary']['local_module_names']}",
        f"- Issues: {report['summary']['issues']}",
        "",
        "## Issues",
        "",
    ]
    if not report["issues"]:
        lines.append("- No local import path issues detected.")
    for issue in report["issues"]:
        lines.append(
            f"- `{issue['file']}` imports `{issue['import']}`: {issue['reason']}. "
            f"Candidates: {issue['candidates']}"
        )
    REPORT_MD.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when local import issues are found.")
    args = parser.parse_args()

    report = audit()
    write_reports(report)
    print(
        "DreamCo local import audit complete: "
        f"{report['summary']['issues']} issues across {report['summary']['python_files']} files."
    )
    if args.check and report["issues"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
