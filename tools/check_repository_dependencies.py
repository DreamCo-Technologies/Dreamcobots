#!/usr/bin/env python3
"""Check declared Node dependencies and repository-local Python imports."""

from __future__ import annotations

import ast
import json
import sys
import sysconfig
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKIPPED_ROOTS = {".git", ".vercel", "__pycache__", "dist", "logs", "node_modules", "reports"}
DEPENDENCY_SECTIONS = ("dependencies", "devDependencies", "optionalDependencies")
PYTHON_REQUIREMENT_FILES = (
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-tools.txt",
    "requirements-buddy-learning.txt",
)


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected an object in {path.relative_to(ROOT)}")
    return value


def python_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.py")
        if not any(part in SKIPPED_ROOTS for part in path.relative_to(ROOT).parts)
    )


def local_python_roots() -> set[str]:
    roots = {path.stem for path in ROOT.glob("*.py")}
    roots.update(path.name for path in ROOT.iterdir() if path.is_dir() and not path.name.startswith("."))
    roots.update(path.stem for path in python_files())
    return roots


def scan_python_imports(files: list[Path]) -> tuple[set[str], list[str]]:
    imports: set[str] = set()
    syntax_errors: list[str] = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except SyntaxError as error:
            syntax_errors.append(f"{relative}:{error.lineno}: {error.msg}")
            continue
        optional_imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                handles_optional_import = any(
                    (
                        handler.type is None
                        or (
                            isinstance(handler.type, ast.Name)
                            and handler.type.id in {"ImportError", "ModuleNotFoundError"}
                        )
                        or (
                            isinstance(handler.type, ast.Tuple)
                            and any(
                                isinstance(element, ast.Name)
                                and element.id in {"ImportError", "ModuleNotFoundError"}
                                for element in handler.type.elts
                            )
                        )
                    )
                    for handler in node.handlers
                )
                if handles_optional_import:
                    for body_node in ast.walk(node):
                        if isinstance(body_node, ast.Import):
                            optional_imports.update(alias.name.split(".")[0] for alias in body_node.names)
                        elif isinstance(body_node, ast.ImportFrom) and body_node.level == 0 and body_node.module:
                            optional_imports.add(body_node.module.split(".")[0])
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imports.add(node.module.split(".")[0])
        imports.difference_update(optional_imports)
    return imports, syntax_errors


def standard_library_roots() -> set[str]:
    roots = set(getattr(sys, "stdlib_module_names", ()))
    roots.update(sys.builtin_module_names)
    roots.add("__future__")
    stdlib_path = Path(sysconfig.get_path("stdlib"))
    if not stdlib_path.is_dir():
        return roots
    for path in stdlib_path.iterdir():
        if path.name in {"__pycache__", "site-packages"}:
            continue
        if path.is_file() and path.suffix in {".py", ".so"}:
            roots.add(path.stem.split(".")[0])
        elif path.is_dir() and (path / "__init__.py").exists():
            roots.add(path.name)
    return roots


def declared_python_roots() -> tuple[set[str], list[str]]:
    declared: set[str] = set()
    manifests: list[str] = []
    for name in PYTHON_REQUIREMENT_FILES:
        path = ROOT / name
        if not path.is_file():
            continue
        manifests.append(name)
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line or line.startswith(("-", "http://", "https://", "git+")):
                continue
            package = line.split(";", 1)[0].split("[", 1)[0]
            for marker in ("===", "==", ">=", "<=", "~=", "!=", ">", "<"):
                package = package.split(marker, 1)[0]
            root = package.strip().replace("-", "_").lower()
            if root:
                declared.add(root)
    return declared, manifests


def audit_dependencies() -> dict[str, Any]:
    package = read_object(ROOT / "package.json")
    lock = read_object(ROOT / "package-lock.json")
    lock_root = lock.get("packages", {}).get("", {})
    errors: list[str] = []

    direct_node_dependencies = 0
    for section in DEPENDENCY_SECTIONS:
        declared = package.get(section, {})
        locked = lock_root.get(section, {})
        if declared != locked:
            missing = sorted(set(declared) - set(locked))
            extra = sorted(set(locked) - set(declared))
            mismatched = sorted(name for name in set(declared) & set(locked) if declared[name] != locked[name])
            errors.append(f"{section} differs from package-lock.json: missing={missing}, extra={extra}, versions={mismatched}")
        direct_node_dependencies += len(declared)
        for name in declared:
            if f"node_modules/{name}" not in lock.get("packages", {}):
                errors.append(f"Direct Node dependency has no lockfile package entry: {name}")

    files = python_files()
    imports, syntax_errors = scan_python_imports(files)
    errors.extend(syntax_errors)
    local_roots = local_python_roots()
    stdlib = standard_library_roots()
    declared_python, python_manifests = declared_python_roots()
    undeclared_python = sorted(
        name for name in imports - stdlib - local_roots
        if name.replace("-", "_").lower() not in declared_python
    )
    if undeclared_python:
        errors.append(
            "Python imports require a declared environment manifest or repository-local package: "
            + ", ".join(undeclared_python)
        )

    required_scripts = {"check", "build", "test:governed", "test:repository", "buddy:fleet-quality"}
    missing_scripts = sorted(required_scripts - set(package.get("scripts", {})))
    if missing_scripts:
        errors.append("Missing required package scripts: " + ", ".join(missing_scripts))

    result = {
        "ok": not errors,
        "node_lockfile_version": lock.get("lockfileVersion"),
        "direct_node_dependencies": direct_node_dependencies,
        "python_files_parsed": len(files),
        "python_import_roots": len(imports),
        "python_environment_manifests": python_manifests,
        "declared_python_dependencies": sorted(declared_python),
        "undeclared_python_imports": undeclared_python,
        "errors": errors,
        "boundary": "TypeScript resolution is verified by npm run check; optional provider credentials and external binaries are tested by their adapter suites.",
    }
    return result


def main() -> int:
    result = audit_dependencies()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
