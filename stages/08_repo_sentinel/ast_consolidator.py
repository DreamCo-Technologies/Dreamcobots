"""Conservative AST duplicate detection and opt-in exact-duplicate shimming.

The Sentinel never selects a 'longest' implementation or silently resolves semantic
conflicts. Automatic rewriting is limited to AST-identical top-level symbols whose
canonical owner is explicitly registered. All other overlaps remain findings.
"""
from __future__ import annotations

import ast
import importlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

SYMBOL_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache", ".sentinel_backups"}


def _symbol_nodes(path: Path) -> tuple[list[tuple[ast.AST, list[str]]], str | None]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        return [], f"{type(exc).__name__}: {exc}"
    found = []
    for node in tree.body:
        if isinstance(node, SYMBOL_TYPES):
            start = node.decorator_list[0].lineno if node.decorator_list else node.lineno
            found.append((node, source.splitlines()[start - 1:node.end_lineno]))
    return found, None


def _node_digest(node: ast.AST) -> str:
    import hashlib
    normalized = ast.dump(node, annotate_fields=True, include_attributes=False)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _module_import_path(repo_root: Path, rel_path: str) -> str:
    path = Path(rel_path)
    if path.suffix != ".py" or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe canonical module path: {rel_path}")
    return ".".join(path.with_suffix("").parts)


def scan_duplicate_symbols(repo_root: Path, roots: list[str]) -> dict[str, Any]:
    locations: dict[str, list[dict[str, str]]] = {}
    parse_errors: list[dict[str, str]] = []
    for root_name in roots:
        root = repo_root / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            nodes, error = _symbol_nodes(path)
            if error:
                parse_errors.append({"path": path.relative_to(repo_root).as_posix(), "error": error})
                continue
            rel = path.relative_to(repo_root).as_posix()
            for node, _ in nodes:
                locations.setdefault(node.name, []).append({
                    "path": rel,
                    "line": str(node.lineno),
                    "digest": _node_digest(node),
                    "kind": type(node).__name__,
                })
    duplicates = [
        {"type": "duplicate_symbol", "symbol": name, "locations": rows}
        for name, rows in sorted(locations.items()) if len({x["path"] for x in rows}) > 1
    ]
    return {"duplicates": duplicates, "parse_errors": parse_errors,
            "symbols_scanned": sum(len(v) for v in locations.values())}


def _find_top_level_node(source: str, symbol: str) -> tuple[ast.AST | None, int, int]:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, SYMBOL_TYPES) and node.name == symbol:
            start = node.decorator_list[0].lineno - 1 if node.decorator_list else node.lineno - 1
            return node, start, node.end_lineno
    return None, -1, -1


def _shim(symbol: str, module_path: str) -> str:
    return (
        "import importlib as _dc_importlib\n"
        "import warnings as _dc_warnings\n"
        f"_dc_warnings.warn({symbol!r} + ' is deprecated here; import it from {module_path} instead.', "
        "DeprecationWarning, stacklevel=2)\n"
        f"_dc_owner = _dc_importlib.import_module({module_path!r})\n"
        f"globals()[{symbol!r}] = getattr(_dc_owner, {symbol!r})\n"
        "del _dc_owner\n"
    )


def _top_level_symbols(source: str, symbol: str) -> list[ast.AST]:
    tree = ast.parse(source)
    return [node for node in tree.body if isinstance(node, SYMBOL_TYPES) and node.name == symbol]


def _inside_repo(repo_root: Path, path: Path) -> bool:
    root = repo_root.resolve()
    candidate = path.resolve()
    return candidate == root or root in candidate.parents


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def consolidate_exact_duplicates(
    repo_root: Path,
    overlaps: list[dict[str, Any]],
    canonical_owners: dict[str, str],
    *,
    apply: bool = False,
    backup_dir: Path | None = None,
) -> list[dict[str, Any]]:
    if apply and backup_dir is None:
        raise ValueError("apply mode requires an explicit backup_dir")
    results: list[dict[str, Any]] = []
    for item in overlaps:
        if item.get("type") != "duplicate_symbol":
            continue
        symbol = str(item.get("symbol") or "")
        canonical_rel = canonical_owners.get(symbol)
        if not canonical_rel:
            results.append({"symbol": symbol, "status": "unregistered_owner", "changed": []})
            continue
        try:
            module_path = _module_import_path(repo_root, canonical_rel)
        except ValueError:
            results.append({"symbol": symbol, "status": "unsafe_canonical_path", "changed": []})
            continue
        canonical_path = repo_root / canonical_rel
        if canonical_path.is_symlink() or not _inside_repo(repo_root, canonical_path):
            results.append({"symbol": symbol, "status": "unsafe_canonical_path", "changed": []})
            continue
        if not canonical_path.is_file():
            results.append({"symbol": symbol, "status": "canonical_file_missing", "changed": []})
            continue
        canonical_source = canonical_path.read_text(encoding="utf-8")
        canonical_node, _, _ = _find_top_level_node(canonical_source, symbol)
        if canonical_node is None:
            results.append({"symbol": symbol, "status": "canonical_symbol_missing", "changed": []})
            continue
        canonical_digest = _node_digest(canonical_node)
        eligible: list[str] = []
        conflicts: list[str] = []
        seen_paths: set[str] = set()
        for location in item.get("locations", []):
            rel = location["path"]
            if rel == canonical_rel:
                continue
            if rel in seen_paths:
                conflicts.append(f"{rel}: multiple top-level definitions are ambiguous")
                continue
            seen_paths.add(rel)
            duplicate_path = repo_root / rel
            if duplicate_path.is_symlink() or not _inside_repo(repo_root, duplicate_path):
                conflicts.append(f"{rel}: symlink or path escapes repository")
                continue
            if not duplicate_path.is_file():
                conflicts.append(rel)
                continue
            duplicate_source = duplicate_path.read_text(encoding="utf-8")
            duplicate_nodes = _top_level_symbols(duplicate_source, symbol)
            if len(duplicate_nodes) != 1 or _node_digest(duplicate_nodes[0]) != canonical_digest:
                conflicts.append(rel)
            else:
                eligible.append(rel)
        changed: list[str] = []
        if apply:
            for rel in eligible:
                path = repo_root / rel
                source = path.read_text(encoding="utf-8")
                _, start, end = _find_top_level_node(source, symbol)
                lines = source.splitlines(keepends=True)
                replacement = _shim(symbol, module_path)
                updated = "".join(lines[:start]) + replacement + "".join(lines[end:])
                ast.parse(updated, filename=str(path))
                backup = backup_dir / rel
                backup.parent.mkdir(parents=True, exist_ok=True)
                if backup.exists():
                    raise FileExistsError(f"refusing to overwrite backup: {backup}")
                _atomic_write_text(backup, source)
                _atomic_write_text(path, updated)
                changed.append(rel)
        results.append({
            "symbol": symbol,
            "canonical": canonical_rel,
            "status": "applied" if apply and changed else ("ready" if eligible else "conflict"),
            "eligible_exact_duplicates": eligible,
            "semantic_conflicts_left_untouched": conflicts,
            "changed": changed,
        })
    return results
