#!/usr/bin/env python3
"""Build dependency intelligence reports for DreamCobots."""

from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "__pycache__",
        "coverage",
        "dist",
        "node_modules",
        "venv",
    }
)

NODE_IMPORT_RE = re.compile(
    r"""(?:
        import\s+(?:.+?\s+from\s+)?['"]([^'"]+)['"]|
        require\(\s*['"]([^'"]+)['"]\s*\)
    )""",
    re.VERBOSE,
)

CRITICAL_INFRA_PACKAGES = {
    "express",
    "flask",
    "fastapi",
    "httpx",
    "requests",
    "pytest",
    "dotenv",
    "openai",
    "selenium",
    "stripe",
}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def normalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def requirement_name(line: str) -> str | None:
    stripped = line.split("#", 1)[0].strip()
    if not stripped or stripped.startswith("-"):
        return None
    name = re.split(r"[<>=!~;\[]", stripped, maxsplit=1)[0].strip()
    if not name:
        return None
    return normalize_name(name)


def npm_module_to_package(module_name: str) -> str:
    if not module_name or module_name.startswith(".") or module_name.startswith("/"):
        return ""
    if module_name.startswith("@"):
        parts = module_name.split("/")
        return "/".join(parts[:2]) if len(parts) >= 2 else module_name
    return module_name.split("/", 1)[0]


def discover_package_json_dirs(root: Path) -> list[Path]:
    package_dirs: list[Path] = []
    for manifest in sorted(root.rglob("package.json")):
        if should_skip(manifest):
            continue
        package_dirs.append(manifest.parent)
    return package_dirs


def discover_requirements_files(root: Path) -> list[Path]:
    requirements_files: list[Path] = []
    for req_file in sorted(root.rglob("requirements*.txt")):
        if should_skip(req_file):
            continue
        requirements_files.append(req_file)
    return requirements_files


def discover_python_imports(search_root: Path, excluded_roots: set[Path] | None = None) -> set[str]:
    imports: set[str] = set()
    excluded_roots = excluded_roots or set()
    for py_file in sorted(search_root.rglob("*.py")):
        if should_skip(py_file):
            continue
        if any(py_file.is_relative_to(excluded) for excluded in excluded_roots):
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(normalize_name(alias.name.split(".", 1)[0]))
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(normalize_name(node.module.split(".", 1)[0]))
    return imports


def discover_node_imports(search_root: Path, excluded_roots: set[Path] | None = None) -> set[str]:
    imports: set[str] = set()
    excluded_roots = excluded_roots or set()
    for js_file in sorted(search_root.rglob("*.js")):
        if should_skip(js_file):
            continue
        if any(js_file.is_relative_to(excluded) for excluded in excluded_roots):
            continue
        try:
            text = js_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for match in NODE_IMPORT_RE.finditer(text):
            module_name = match.group(1) or match.group(2) or ""
            package_name = npm_module_to_package(module_name.strip())
            if package_name:
                imports.add(normalize_name(package_name))
    return imports


def build_report(root: Path) -> dict[str, Any]:
    package_dirs = discover_package_json_dirs(root)
    requirements_files = discover_requirements_files(root)

    project_nodes: list[str] = []
    package_manifest_data: list[dict[str, Any]] = []
    requirements_manifest_data: list[dict[str, Any]] = []
    dependency_occurrences: dict[str, list[dict[str, str]]] = defaultdict(list)
    internal_relationships: list[dict[str, str]] = []
    likely_unused: list[dict[str, Any]] = []

    local_package_names: dict[str, str] = {}
    package_dir_set = set(package_dirs)
    for package_dir in package_dirs:
        manifest_path = package_dir / "package.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        package_name = manifest.get("name")
        if isinstance(package_name, str):
            local_package_names[normalize_name(package_name)] = str(
                package_dir.relative_to(root)
            )

    for package_dir in package_dirs:
        manifest_path = package_dir / "package.json"
        rel_manifest = str(manifest_path.relative_to(root))
        project_node = str(package_dir.relative_to(root))
        project_nodes.append(project_node)

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        dependencies = manifest.get("dependencies", {}) or {}
        dev_dependencies = manifest.get("devDependencies", {}) or {}
        all_dependencies: dict[str, str] = {}
        for dep_name, version in {**dependencies, **dev_dependencies}.items():
            dep_name_norm = normalize_name(dep_name)
            all_dependencies[dep_name_norm] = str(version)
            dependency_occurrences[dep_name_norm].append(
                {"manifest": rel_manifest, "version": str(version), "type": "node"}
            )
            if dep_name_norm in local_package_names:
                internal_relationships.append(
                    {
                        "from": project_node,
                        "to": local_package_names[dep_name_norm],
                        "dependency": dep_name_norm,
                    }
                )
        nested_package_roots = {
            candidate
            for candidate in package_dir_set
            if candidate != package_dir and candidate.is_relative_to(package_dir)
        }
        imported_modules = discover_node_imports(
            package_dir,
            excluded_roots=nested_package_roots,
        )
        unused = sorted(dep for dep in all_dependencies if dep not in imported_modules)
        if unused:
            likely_unused.append(
                {"manifest": rel_manifest, "type": "node", "dependencies": unused}
            )
        package_manifest_data.append(
            {
                "manifest": rel_manifest,
                "project": project_node,
                "dependencies": all_dependencies,
            }
        )

    for req_file in requirements_files:
        rel_manifest = str(req_file.relative_to(root))
        project_node = str(req_file.parent.relative_to(root))
        project_nodes.append(project_node)
        declared: dict[str, str] = {}
        for line in req_file.read_text(encoding="utf-8").splitlines():
            name = requirement_name(line)
            if not name:
                continue
            declared[name] = line.strip()
            dependency_occurrences[name].append(
                {"manifest": rel_manifest, "version": line.strip(), "type": "python"}
            )
        nested_requirement_roots = {
            candidate.parent
            for candidate in requirements_files
            if candidate != req_file
            and candidate.parent != req_file.parent
            and candidate.parent.is_relative_to(req_file.parent)
        }
        imports = discover_python_imports(
            req_file.parent,
            excluded_roots=nested_requirement_roots,
        )
        unused = sorted(dep for dep in declared if dep not in imports)
        if unused:
            likely_unused.append(
                {"manifest": rel_manifest, "type": "python", "dependencies": unused}
            )
        requirements_manifest_data.append(
            {
                "manifest": rel_manifest,
                "project": project_node,
                "dependencies": declared,
            }
        )

    version_conflicts: list[dict[str, Any]] = []
    duplicate_dependencies: list[dict[str, Any]] = []
    ranked_counter = Counter()
    for dep_name, occurrences in sorted(dependency_occurrences.items()):
        versions = sorted({entry["version"] for entry in occurrences})
        manifests = sorted({entry["manifest"] for entry in occurrences})
        if len(manifests) > 1:
            duplicate_dependencies.append(
                {
                    "dependency": dep_name,
                    "manifest_count": len(manifests),
                    "manifests": manifests,
                }
            )
        if len(versions) > 1:
            version_conflicts.append(
                {
                    "dependency": dep_name,
                    "versions": versions,
                    "occurrences": occurrences,
                }
            )
        score = len(manifests)
        if dep_name in CRITICAL_INFRA_PACKAGES:
            score += 5
        if any(
            rel["dependency"] == dep_name for rel in internal_relationships
        ):
            score += 2
        ranked_counter[dep_name] = score

    ranked_critical = [
        {"dependency": name, "score": score}
        for name, score in ranked_counter.most_common(25)
    ]

    return {
        "summary": {
            "project_node_count": len(set(project_nodes)),
            "package_json_count": len(package_manifest_data),
            "requirements_count": len(requirements_manifest_data),
            "duplicate_dependency_count": len(duplicate_dependencies),
            "version_conflict_count": len(version_conflicts),
            "likely_unused_entries": len(likely_unused),
            "internal_relationship_count": len(internal_relationships),
        },
        "projects": sorted(set(project_nodes)),
        "package_manifests": package_manifest_data,
        "requirements_manifests": requirements_manifest_data,
        "internal_relationships": internal_relationships,
        "duplicate_dependencies": duplicate_dependencies,
        "version_conflicts": version_conflicts,
        "likely_unused_dependencies": likely_unused,
        "ranked_critical_packages": ranked_critical,
    }


def write_markdown(report: dict[str, Any], destination: Path) -> None:
    summary = report["summary"]
    lines = [
        "# Dependency Intelligence Report",
        "",
        "## Summary",
        "",
        f"- Project nodes: {summary['project_node_count']}",
        f"- package.json manifests: {summary['package_json_count']}",
        f"- requirements manifests: {summary['requirements_count']}",
        f"- Duplicate dependencies: {summary['duplicate_dependency_count']}",
        f"- Version conflicts: {summary['version_conflict_count']}",
        f"- Likely unused entries: {summary['likely_unused_entries']}",
        "",
        "## Top Critical Infrastructure Packages",
        "",
    ]
    for entry in report["ranked_critical_packages"][:10]:
        lines.append(f"- `{entry['dependency']}` (score: {entry['score']})")
    lines.extend(["", "## Version Conflicts", ""])
    if report["version_conflicts"]:
        for conflict in report["version_conflicts"][:25]:
            versions = ", ".join(conflict["versions"])
            lines.append(f"- `{conflict['dependency']}` → {versions}")
    else:
        lines.append("- None detected.")
    lines.extend(["", "## Likely Unused Dependencies", ""])
    if report["likely_unused_dependencies"]:
        for item in report["likely_unused_dependencies"][:25]:
            deps = ", ".join(item["dependencies"][:8])
            lines.append(f"- `{item['manifest']}`: {deps}")
    else:
        lines.append("- None detected.")
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_dot_graph(report: dict[str, Any], destination: Path) -> None:
    lines = [
        "digraph dreamco_dependency_map {",
        '  rankdir="LR";',
        '  node [shape="box"];',
    ]
    for project in report["projects"]:
        lines.append(f'  "{project}" [shape="box"];')
    for relation in report["internal_relationships"]:
        lines.append(
            f'  "{relation["from"]}" -> "{relation["to"]}" [label="{relation["dependency"]}"];'
        )
    lines.append("}")
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate dependency intelligence JSON/Markdown/graph outputs."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root (defaults to project root).",
    )
    parser.add_argument(
        "--json-out",
        default="artifacts/dependency/dependency_graph.json",
        help="JSON output path.",
    )
    parser.add_argument(
        "--markdown-out",
        default="artifacts/dependency/dependency_graph.md",
        help="Markdown output path.",
    )
    parser.add_argument(
        "--graph-out",
        default="artifacts/dependency/dependency_graph.dot",
        help="Graphviz DOT output path.",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    root = Path(args.root).resolve() if args.root else script_dir.parent
    json_out = Path(args.json_out)
    markdown_out = Path(args.markdown_out)
    graph_out = Path(args.graph_out)
    if not json_out.is_absolute():
        json_out = root / json_out
    if not markdown_out.is_absolute():
        markdown_out = root / markdown_out
    if not graph_out.is_absolute():
        graph_out = root / graph_out

    report = build_report(root)
    for output_path in (json_out, markdown_out, graph_out):
        output_path.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, markdown_out)
    write_dot_graph(report, graph_out)
    print(f"Dependency intelligence report written to {json_out}")
    print(f"Markdown summary written to {markdown_out}")
    print(f"Graph artifact written to {graph_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
