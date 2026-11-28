#!/usr/bin/env python3
"""Fail-closed static AST guard for proposed Python repair patches.

This guard parses candidate source only. It never imports, executes, applies, or
runs model-generated code. A PASS is a static preflight, not a sandbox result.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any

BLOCKED_MODULES = {
    "subprocess", "socket", "urllib", "http", "httpx", "requests",
    "ftplib", "telnetlib", "ctypes", "multiprocessing", "pickle",
    "marshal", "shelve", "importlib",
}
BLOCKED_CALLS = {"eval", "exec", "compile", "__import__", "breakpoint"}
BLOCKED_ATTRIBUTES = {"system", "popen", "spawn", "fork", "connect", "urlopen", "run"}


class GuardVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.findings: list[dict[str, Any]] = []

    def _add(self, node: ast.AST, rule: str, detail: str) -> None:
        self.findings.append({
            "rule": rule,
            "line": getattr(node, "lineno", None),
            "detail": detail,
        })

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".", 1)[0]
            if root in BLOCKED_MODULES:
                self._add(node, "blocked_import", alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        root = (node.module or "").split(".", 1)[0]
        if root in BLOCKED_MODULES or node.level:
            self._add(node, "blocked_import_from", node.module or "relative_import")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
            self._add(node, "blocked_dynamic_execution", node.func.id)
        if isinstance(node.func, ast.Attribute) and node.func.attr in BLOCKED_ATTRIBUTES:
            self._add(node, "blocked_system_or_network_call", node.func.attr)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr.startswith("__") and node.attr.endswith("__"):
            self._add(node, "blocked_dunder_access", node.attr)
        self.generic_visit(node)


def inspect_source(source: str, *, filename: str = "<candidate>") -> dict[str, Any]:
    if not isinstance(source, str) or not source.strip():
        raise ValueError("candidate source must be non-empty text")
    if len(source.encode("utf-8")) > 250_000:
        raise ValueError("candidate source exceeds 250 KB")
    try:
        tree = ast.parse(source, filename=filename, mode="exec")
    except SyntaxError as exc:
        return {
            "schema": "dreamco.patch_ast_guard.v1",
            "status": "BLOCKED_SYNTAX_ERROR",
            "passed": False,
            "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "findings": [{"rule": "syntax_error", "line": exc.lineno, "detail": exc.msg}],
            "execution_performed": False,
        }
    visitor = GuardVisitor()
    visitor.visit(tree)
    return {
        "schema": "dreamco.patch_ast_guard.v1",
        "status": "PASS_STATIC_PREFLIGHT" if not visitor.findings else "BLOCKED_STATIC_FINDINGS",
        "passed": not visitor.findings,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "findings": visitor.findings,
        "execution_performed": False,
        "truth_boundary": "Static AST inspection is not a security sandbox or runtime proof.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = inspect_source(args.source.read_text(encoding="utf-8"), filename=str(args.source))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "passed", "source_sha256")}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
