#!/usr/bin/env python3
"""Install repository Node and Python dependencies with profiles and diagnostics."""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

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

PROFILE_CONFIG_PATH = Path("tools/dependency_profiles.json")
DEFAULT_PARALLELISM = 4

NODE_IMPORT_RE = re.compile(
    r"""(?:
        import\s+(?:.+?\s+from\s+)?['"]([^'"]+)['"]|
        require\(\s*['"]([^'"]+)['"]\s*\)
    )""",
    re.VERBOSE,
)


@dataclass
class InstallTask:
    """A single install operation."""

    kind: str
    label: str
    cmd: list[str]
    cwd: Path
    manifest_path: Path


@dataclass
class InstallResult:
    """Result of an install task."""

    task: InstallTask
    returncode: int
    duration_seconds: float
    stdout: str
    stderr: str
    retries: int
    classification: str | None = None


def should_skip(path: Path) -> bool:
    """Return True when *path* belongs to an excluded directory tree."""
    return any(part in SKIP_DIRS for part in path.parts)


def find_package_json_dirs(root: Path) -> list[Path]:
    """Return package directories that contain package.json."""
    dirs: list[Path] = []
    for manifest in sorted(root.rglob("package.json")):
        if should_skip(manifest):
            continue
        dirs.append(manifest.parent)
    return dirs


def find_requirements_files(root: Path) -> list[Path]:
    """Return all requirements*.txt files in the repository."""
    files: list[Path] = []
    for file_path in sorted(root.rglob("requirements*.txt")):
        if should_skip(file_path):
            continue
        files.append(file_path)
    return files


def normalize_name(name: str) -> str:
    """Normalize package/import names for comparison."""
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def requirement_name(line: str) -> str | None:
    """Extract a requirement package name from one requirements line."""
    stripped = line.split("#", 1)[0].strip()
    if not stripped or stripped.startswith("-"):
        return None
    name = re.split(r"[<>=!~;\[]", stripped, maxsplit=1)[0].strip()
    if not name:
        return None
    return normalize_name(name)


def npm_module_to_package(module_name: str) -> str:
    """Convert JS import module string to package name."""
    if not module_name or module_name.startswith(".") or module_name.startswith("/"):
        return ""
    if module_name.startswith("@"):
        parts = module_name.split("/")
        return "/".join(parts[:2]) if len(parts) >= 2 else module_name
    return module_name.split("/", 1)[0]


def discover_local_python_names(search_root: Path) -> set[str]:
    """Collect probable local module/package names from file and directory names."""
    local_names: set[str] = set()
    for py_file in sorted(search_root.rglob("*.py")):
        if should_skip(py_file):
            continue
        local_names.add(normalize_name(py_file.stem))
    for init_file in sorted(search_root.rglob("__init__.py")):
        if should_skip(init_file):
            continue
        local_names.add(normalize_name(init_file.parent.name))
    return local_names


def discover_python_imports(search_root: Path, excluded_roots: set[Path] | None = None) -> set[str]:
    """Collect likely import names from Python files under search_root."""
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
    """Collect npm package names imported by JS files under search_root."""
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


def classify_failure(stderr: str, stdout: str) -> str:
    """Classify common install failures for diagnostics."""
    text = f"{stderr}\n{stdout}".lower()
    if "no matching distribution found" in text or "could not find a version that satisfies" in text:
        return "version_resolution_failure"
    if "temporary failure in name resolution" in text or "eai_again" in text or "timeout" in text:
        return "network_instability"
    if "permission denied" in text:
        return "permission_error"
    if "not found" in text:
        return "missing_module_or_binary"
    return "unknown_failure"


def run_cmd(
    cmd: list[str],
    cwd: Path,
    dry_run: bool,
    retries: int,
    backoff_seconds: float,
) -> tuple[int, str, str, int]:
    """Run command in cwd with retries and return exit data."""
    command_text = " ".join(cmd)
    print(f"\n▶ {command_text}  (cwd={cwd})")
    if dry_run:
        return 0, "", "", 0
    attempt = 0
    while True:
        completed = subprocess.run(
            cmd,
            cwd=str(cwd),
            check=False,
            text=True,
            capture_output=True,
        )
        if completed.returncode == 0:
            return 0, completed.stdout, completed.stderr, attempt
        if attempt >= retries:
            return completed.returncode, completed.stdout, completed.stderr, attempt
        sleep_seconds = backoff_seconds * (2**attempt)
        print(
            f"  ↻ retrying in {sleep_seconds:.1f}s (attempt {attempt + 1}/{retries})"
        )
        time.sleep(sleep_seconds)
        attempt += 1


def load_profiles(root: Path) -> dict[str, Any]:
    """Load bootstrap profiles from config."""
    config_path = root / PROFILE_CONFIG_PATH
    if not config_path.exists():
        return {}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {config_path}: {exc}") from exc
    profiles = data.get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError(
            f"Profile config {config_path} must include top-level 'profiles' object."
        )
    return profiles


def resolve_profile_manifests(
    root: Path,
    profile_name: str | None,
    discovered_packages: list[Path],
    discovered_requirements: list[Path],
) -> tuple[list[Path], list[Path]]:
    """Resolve manifests for a selected profile."""
    if not profile_name:
        return discovered_packages, discovered_requirements
    profiles = load_profiles(root)
    if profile_name not in profiles:
        raise ValueError(
            f"Unknown profile '{profile_name}'. Available profiles: {', '.join(sorted(profiles))}"
        )
    profile = profiles[profile_name]
    package_patterns: Iterable[str] = profile.get("package_json", [])
    requirement_patterns: Iterable[str] = profile.get("requirements", [])
    package_paths: set[Path] = set()
    requirement_paths: set[Path] = set()
    for pattern in package_patterns:
        for matched in root.glob(pattern):
            if matched.is_file() and matched.name == "package.json" and not should_skip(matched):
                package_paths.add(matched.parent)
    for pattern in requirement_patterns:
        for matched in root.glob(pattern):
            if matched.is_file() and matched.name.startswith("requirements") and not should_skip(matched):
                requirement_paths.add(matched)
    # Keep deterministic order and avoid referencing manifests outside known discovery.
    discovered_pkg_dirs = set(discovered_packages)
    discovered_req_files = set(discovered_requirements)
    return (
        sorted(path for path in package_paths if path in discovered_pkg_dirs),
        sorted(path for path in requirement_paths if path in discovered_req_files),
    )


def manifest_checksum(path: Path) -> str:
    """Compute SHA256 for manifest file."""
    return sha256(path.read_bytes()).hexdigest()


def diagnose_missing_modules(
    root: Path,
    package_dirs: list[Path],
    requirements_files: list[Path],
) -> dict[str, Any]:
    """Report likely missing module declarations."""
    diagnostics: dict[str, Any] = {
        "python": [],
        "node": [],
    }
    stdlib_names = {normalize_name(name) for name in sys.stdlib_module_names}
    local_python_names = discover_local_python_names(root)
    package_dir_set = set(package_dirs)

    for requirements_file in requirements_files:
        declared: set[str] = set()
        for line in requirements_file.read_text(encoding="utf-8").splitlines():
            name = requirement_name(line)
            if name:
                declared.add(name)
        nested_requirement_roots = {
            candidate.parent
            for candidate in requirements_files
            if candidate != requirements_file
            and candidate.parent != requirements_file.parent
            and candidate.parent.is_relative_to(requirements_file.parent)
        }
        imports = discover_python_imports(
            requirements_file.parent,
            excluded_roots=nested_requirement_roots,
        )
        missing = sorted(
            name
            for name in imports
            if name
            and name not in declared
            and name not in stdlib_names
            and name not in local_python_names
        )
        if missing:
            diagnostics["python"].append(
                {
                    "requirements_file": str(requirements_file.relative_to(root)),
                    "missing_module_candidates": missing,
                }
            )
    for package_dir in package_dirs:
        manifest_path = package_dir / "package.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        declared = {
            normalize_name(name)
            for name in {
                *manifest.get("dependencies", {}).keys(),
                *manifest.get("devDependencies", {}).keys(),
            }
        }
        nested_package_roots = {
            candidate
            for candidate in package_dir_set
            if candidate != package_dir and candidate.is_relative_to(package_dir)
        }
        imports = discover_node_imports(package_dir, excluded_roots=nested_package_roots)
        missing = sorted(name for name in imports if name and name not in declared)
        if missing:
            diagnostics["node"].append(
                {
                    "package_json": str(manifest_path.relative_to(root)),
                    "missing_module_candidates": missing,
                }
            )
    return diagnostics


def build_install_tasks(
    root: Path,
    package_dirs: list[Path],
    requirements_files: list[Path],
    install_node: bool,
    install_python: bool,
) -> list[InstallTask]:
    """Build deterministic install task list."""
    tasks: list[InstallTask] = []
    if install_node:
        for package_dir in package_dirs:
            tasks.append(
                InstallTask(
                    kind="node",
                    label=str((package_dir / "package.json").relative_to(root)),
                    cmd=["npm", "install", "--registry", "https://registry.npmjs.org/"],
                    cwd=package_dir,
                    manifest_path=package_dir / "package.json",
                )
            )
    if install_python:
        for requirements_file in requirements_files:
            tasks.append(
                InstallTask(
                    kind="python",
                    label=str(requirements_file.relative_to(root)),
                    cmd=[
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        str(requirements_file),
                        "-i",
                        "https://pypi.org/simple",
                    ],
                    cwd=root,
                    manifest_path=requirements_file,
                )
            )
    return tasks


def run_install_task(
    task: InstallTask,
    dry_run: bool,
    retries: int,
    backoff_seconds: float,
) -> InstallResult:
    """Execute one task with timing and classification."""
    started = time.perf_counter()
    returncode, stdout, stderr, used_retries = run_cmd(
        cmd=task.cmd,
        cwd=task.cwd,
        dry_run=dry_run,
        retries=retries,
        backoff_seconds=backoff_seconds,
    )
    duration = time.perf_counter() - started
    classification = None
    if returncode != 0:
        classification = classify_failure(stderr=stderr, stdout=stdout)
    return InstallResult(
        task=task,
        returncode=returncode,
        duration_seconds=duration,
        stdout=stdout,
        stderr=stderr,
        retries=used_retries,
        classification=classification,
    )


def maybe_heal_missing_python_modules(
    root: Path,
    diagnostics: dict[str, Any],
    dry_run: bool,
    retries: int,
    backoff_seconds: float,
) -> None:
    """Attempt explicit-heal pip installs for missing Python module candidates."""
    heal_candidates: set[str] = set()
    for item in diagnostics.get("python", []):
        for module_name in item.get("missing_module_candidates", []):
            if module_name and module_name.isidentifier():
                heal_candidates.add(module_name)
    if not heal_candidates:
        print("No heal candidates found.")
        return
    print(f"\n🩹 Heal mode enabled; attempting {len(heal_candidates)} module installs.")
    for module_name in sorted(heal_candidates):
        code, _, stderr, used_retries = run_cmd(
            cmd=[
                sys.executable,
                "-m",
                "pip",
                "install",
                module_name,
                "-i",
                "https://pypi.org/simple",
            ],
            cwd=root,
            dry_run=dry_run,
            retries=retries,
            backoff_seconds=backoff_seconds,
        )
        if code != 0:
            print(
                f"  ⚠ heal failed for '{module_name}'"
                f" ({classify_failure(stderr=stderr, stdout='')}, retries={used_retries})"
            )


def print_profile_listing(root: Path) -> int:
    """Print available profile names and descriptions."""
    profiles = load_profiles(root)
    if not profiles:
        print(f"No profile config found at {root / PROFILE_CONFIG_PATH}.")
        return 0
    print("Available bootstrap profiles:")
    for profile_name in sorted(profiles):
        description = profiles[profile_name].get("description", "")
        print(f"  - {profile_name}: {description}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install all Node and Python dependencies across the repository.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root (defaults to project root).",
    )
    parser.add_argument(
        "--python-only",
        action="store_true",
        help="Install only Python dependencies.",
    )
    parser.add_argument(
        "--node-only",
        action="store_true",
        help="Install only Node dependencies.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them.",
    )
    parser.add_argument(
        "--profile",
        default=None,
        help=f"Bootstrap profile name from {PROFILE_CONFIG_PATH}.",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available bootstrap profiles and exit.",
    )
    parser.add_argument(
        "--parallelism",
        type=int,
        default=DEFAULT_PARALLELISM,
        help=f"Max concurrent install tasks (default: {DEFAULT_PARALLELISM}).",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop scheduling new work after first failure.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="Retries per failed install command (default: 2).",
    )
    parser.add_argument(
        "--backoff-seconds",
        type=float,
        default=1.5,
        help="Exponential backoff base in seconds for retries (default: 1.5).",
    )
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="Run missing module diagnostics and print suggestions.",
    )
    parser.add_argument(
        "--heal",
        action="store_true",
        help="Attempt explicit dependency healing actions (requires --diagnose).",
    )
    parser.add_argument(
        "--validate-checksums",
        action="store_true",
        help="Record deterministic manifest checksums in telemetry output.",
    )
    parser.add_argument(
        "--telemetry-path",
        default=None,
        help="Optional path to write telemetry JSON report.",
    )
    args = parser.parse_args()

    if args.python_only and args.node_only:
        print("ERROR: --python-only and --node-only cannot be combined.", file=sys.stderr)
        return 2
    if args.heal and not args.diagnose:
        print("ERROR: --heal requires --diagnose.", file=sys.stderr)
        return 2
    if args.parallelism < 1:
        print("ERROR: --parallelism must be >= 1.", file=sys.stderr)
        return 2

    script_dir = Path(__file__).resolve().parent
    root = Path(args.root).resolve() if args.root else script_dir.parent
    install_node = not args.python_only
    install_python = not args.node_only

    if args.list_profiles:
        return print_profile_listing(root)

    print(f"Repository root: {root}")

    package_dirs = find_package_json_dirs(root)
    requirements_files = find_requirements_files(root)
    try:
        package_dirs, requirements_files = resolve_profile_manifests(
            root=root,
            profile_name=args.profile,
            discovered_packages=package_dirs,
            discovered_requirements=requirements_files,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Discovered {len(package_dirs)} package.json locations.")
    print(f"Discovered {len(requirements_files)} requirements files.")
    if args.profile:
        print(f"Using profile: {args.profile}")

    diagnostics: dict[str, Any] | None = None
    if args.diagnose:
        diagnostics = diagnose_missing_modules(
            root=root,
            package_dirs=package_dirs,
            requirements_files=requirements_files,
        )
        print("\n🔎 Diagnostics:")
        print(json.dumps(diagnostics, indent=2))
        if args.heal:
            maybe_heal_missing_python_modules(
                root=root,
                diagnostics=diagnostics,
                dry_run=args.dry_run,
                retries=args.retries,
                backoff_seconds=args.backoff_seconds,
            )

    tasks = build_install_tasks(
        root=root,
        package_dirs=package_dirs,
        requirements_files=requirements_files,
        install_node=install_node,
        install_python=install_python,
    )
    results: list[InstallResult] = []
    started_all = time.perf_counter()
    if args.parallelism == 1 or len(tasks) <= 1:
        for task in tasks:
            result = run_install_task(
                task=task,
                dry_run=args.dry_run,
                retries=args.retries,
                backoff_seconds=args.backoff_seconds,
            )
            results.append(result)
            if args.fail_fast and result.returncode != 0:
                break
    else:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(args.parallelism, len(tasks))
        ) as executor:
            futures = {
                executor.submit(
                    run_install_task,
                    task,
                    args.dry_run,
                    args.retries,
                    args.backoff_seconds,
                ): task
                for task in tasks
            }
            failed = False
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                if args.fail_fast and result.returncode != 0 and not failed:
                    failed = True
                    for pending in futures:
                        if not pending.done():
                            pending.cancel()
    total_duration = time.perf_counter() - started_all

    results.sort(key=lambda item: item.task.label)
    print("\n📊 Install telemetry:")
    for result in results:
        status = "ok" if result.returncode == 0 else f"failed ({result.classification})"
        print(
            f"  - {result.task.label}: {status}, "
            f"{result.duration_seconds:.2f}s, retries={result.retries}"
        )
        if result.returncode != 0 and result.stderr:
            print(f"    stderr: {result.stderr.strip().splitlines()[-1]}")

    failed_results = [result for result in results if result.returncode != 0]
    telemetry: dict[str, Any] = {
        "root": str(root),
        "profile": args.profile,
        "total_duration_seconds": total_duration,
        "task_count": len(results),
        "failed_count": len(failed_results),
        "results": [
            {
                "kind": result.task.kind,
                "label": result.task.label,
                "returncode": result.returncode,
                "duration_seconds": result.duration_seconds,
                "retries": result.retries,
                "classification": result.classification,
            }
            for result in results
        ],
        "diagnostics": diagnostics if diagnostics is not None else {},
    }
    if args.validate_checksums:
        manifest_checksums: dict[str, str] = {}
        for task in tasks:
            rel = str(task.manifest_path.relative_to(root))
            manifest_checksums[rel] = manifest_checksum(task.manifest_path)
        telemetry["manifest_checksums"] = manifest_checksums
    if args.telemetry_path:
        telemetry_path = Path(args.telemetry_path)
        if not telemetry_path.is_absolute():
            telemetry_path = root / telemetry_path
        telemetry_path.parent.mkdir(parents=True, exist_ok=True)
        telemetry_path.write_text(json.dumps(telemetry, indent=2), encoding="utf-8")
        print(f"\n📝 Telemetry written to {telemetry_path}")

    if failed_results:
        print(
            f"\nDependency installation failed in {len(failed_results)} task(s).",
            file=sys.stderr,
        )
        return failed_results[0].returncode

    print("\n✅ Repository dependency bootstrap complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
