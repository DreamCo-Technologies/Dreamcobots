#!/usr/bin/env python3
from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "trusted-code-delivery-program.json"
OUT = ROOT / "config" / "generated" / "trusted-code-delivery-audit.json"
REPORT = ROOT / "reports" / "TRUSTED_CODE_DELIVERY_AUDIT.md"

EXECUTABLE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".mjs", ".cjs"}
SOURCE_ROOTS = ["server", "shared", "client", "tools", "script"]
SKIP_PARTS = {"node_modules", "dist", "build", ".git", "coverage", ".buddy-local"}


def run(command: list[str]) -> dict:
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    return {
        "command": command,
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-5000:],
        "stderr_tail": proc.stderr[-5000:],
    }


def source_inventory() -> list[Path]:
    rows: list[Path] = []
    for rel in SOURCE_ROOTS:
        base = ROOT / rel
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in EXECUTABLE_SUFFIXES:
                continue
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            rows.append(path)
    return sorted(rows)


def test_inventory() -> list[Path]:
    base = ROOT / "tests"
    return sorted(p for p in base.rglob("*") if p.is_file() and p.suffix in EXECUTABLE_SUFFIXES) if base.exists() else []


def python_syntax_check(paths: list[Path]) -> list[dict]:
    failures = []
    for path in paths:
        if path.suffix != ".py":
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            failures.append({"path": str(path.relative_to(ROOT)), "error": str(exc)})
    return failures


def js_syntax_check(paths: list[Path]) -> list[dict]:
    failures = []
    for path in paths:
        if path.suffix not in {".js", ".mjs", ".cjs"}:
            continue
        proc = subprocess.run(["node", "--check", str(path)], cwd=ROOT, capture_output=True, text=True)
        if proc.returncode:
            failures.append({"path": str(path.relative_to(ROOT)), "error": (proc.stderr or proc.stdout)[-2000:]})
    return failures


def suspicious_patterns(paths: list[Path]) -> list[dict]:
    rules = {
        "empty_catch": re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}", re.S),
        "ts_ignore": re.compile(r"@ts-ignore"),
        "eslint_disable_all": re.compile(r"eslint-disable(?!-next-line)"),
        "todo_fixme": re.compile(r"\b(?:TODO|FIXME|HACK)\b", re.I),
    }
    hits = []
    for path in paths:
        if path.suffix not in {".ts", ".tsx", ".js", ".mjs", ".cjs"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for rule, pattern in rules.items():
            count = len(pattern.findall(text))
            if count:
                hits.append({"path": str(path.relative_to(ROOT)), "rule": rule, "count": count, "release_blocker": rule == "empty_catch"})
    return hits


def main() -> int:
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    sources = source_inventory()
    tests = test_inventory()
    py_failures = python_syntax_check(sources + tests)
    js_failures = js_syntax_check(sources + tests)
    suspicious = suspicious_patterns(sources)

    commands = []
    if (ROOT / "package.json").exists() and (ROOT / "node_modules").exists():
        commands.append(run(["npm", "run", "check"]))
    else:
        commands.append({"command": ["npm", "run", "check"], "exit_code": None, "status": "not_run_dependencies_missing"})

    blockers = []
    if py_failures:
        blockers.append(f"Python syntax failures: {len(py_failures)}")
    if js_failures:
        blockers.append(f"JavaScript syntax failures: {len(js_failures)}")
    blocker_hits = [h for h in suspicious if h["release_blocker"]]
    if blocker_hits:
        blockers.append(f"Empty catch blocks detected: {len(blocker_hits)}")
    for result in commands:
        if result.get("exit_code") not in (0, None):
            blockers.append(f"Command failed: {' '.join(result['command'])}")

    payload = {
        "schema": "dreamco.trusted_code_delivery_audit.v1",
        "source_file_count": len(sources),
        "test_file_count": len(tests),
        "test_to_source_file_ratio": round(len(tests) / len(sources), 4) if sources else 0,
        "python_syntax_failures": py_failures,
        "javascript_syntax_failures": js_failures,
        "suspicious_patterns": suspicious,
        "command_checks": commands,
        "release_blockers": blockers,
        "release_candidate_from_static_audit": not blockers,
        "quality_layers_required": program["quality_layers"],
        "truth_boundary": program["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Trusted Code Delivery Audit", "",
        f"- Source files inventoried: **{len(sources)}**",
        f"- Test files inventoried: **{len(tests)}**",
        f"- Static release blockers: **{len(blockers)}**",
        f"- Python syntax failures: **{len(py_failures)}**",
        f"- JavaScript syntax failures: **{len(js_failures)}**",
        f"- Suspicious-pattern findings: **{len(suspicious)}**", "",
        "> Passing this static audit does not prove code is bug-free. Full repository, security, integration, E2E, deployment and runtime evidence remain required.",
    ]
    if blockers:
        lines += ["", "## Release blockers", ""] + [f"- {b}" for b in blockers]
    if suspicious:
        lines += ["", "## Findings to review", ""]
        for hit in suspicious[:200]:
            lines.append(f"- `{hit['path']}` — {hit['rule']} × {hit['count']}" + (" **BLOCKER**" if hit["release_blocker"] else ""))
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": not blockers, "sources": len(sources), "tests": len(tests), "blockers": blockers, "output": str(OUT.relative_to(ROOT)), "report": str(REPORT.relative_to(ROOT))}, indent=2))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
