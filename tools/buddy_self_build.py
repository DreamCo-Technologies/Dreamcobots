#!/usr/bin/env python3
"""Self-build every repository part. Missing evidence is not a pass."""

from __future__ import annotations

import compileall
import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Every top-level area from the owner audit, plus GitHub and website overlay.
PARTS: list[dict[str, object]] = [
    {"id": "website", "path": "website", "kind": "pages", "lane": "pages", "fix": "Regenerate overlay pages; keep buddy.html as home."},
    {"id": "tools", "path": "tools", "kind": "python", "lane": "catalog", "fix": "py_compile failing tools; do not weaken tests."},
    {"id": "workflows", "path": ".github/workflows", "kind": "yaml", "lane": "actions", "fix": "Repair workflow YAML; never rewrite history green."},
    {"id": "docs", "path": "docs", "kind": "markdown", "lane": "detect", "fix": "Index docs. Do not mass-delete."},
    {"id": "config", "path": "config", "kind": "json", "lane": "catalog", "fix": "Re-parse JSON contracts."},
    {"id": "tests", "path": "tests", "kind": "python", "lane": "actions", "fix": "Fix the test, never skip it."},
    {"id": "buddy", "path": "buddy", "kind": "python", "lane": "runtime", "fix": "Compile buddy package."},
    {"id": "buddy_os", "path": "buddy_os", "kind": "python", "lane": "runtime", "fix": "Compile buddy_os contracts."},
    {"id": "bots", "path": "bots", "kind": "mixed", "lane": "catalog", "fix": "Inventory bots. Catalogued ≠ runnable."},
    {"id": "original-bots", "path": "original-bots", "kind": "mixed", "lane": "catalog", "fix": "Preserve original bots."},
    {"id": "command-center", "path": "command-center", "kind": "json", "lane": "catalog", "fix": "Regenerate command-center data."},
    {"id": "server", "path": "server", "kind": "python", "lane": "runtime", "fix": "Compile server adapters."},
    {"id": "shared", "path": "shared", "kind": "mixed", "lane": "runtime", "fix": "Compile shared modules."},
    {"id": "scripts", "path": "scripts", "kind": "mixed", "lane": "actions", "fix": "Syntax-check scripts."},
    {"id": "schemas", "path": "schemas", "kind": "json", "lane": "catalog", "fix": "Validate schema JSON."},
    {"id": "capabilities", "path": "capabilities", "kind": "mixed", "lane": "catalog", "fix": "Index capabilities."},
    {"id": "benchmarks", "path": "benchmarks", "kind": "mixed", "lane": "catalog", "fix": "Keep blocked until harness evidence exists."},
    {"id": "framework", "path": "framework", "kind": "python", "lane": "runtime", "fix": "Compile framework."},
    {"id": "marketplace", "path": "marketplace", "kind": "mixed", "lane": "catalog", "fix": "Catalog only until live listing evidence."},
    {"id": "money_os", "path": "money_os", "kind": "mixed", "lane": "safety", "fix": "Human only. No auto-edit.", "money": True},
    {"id": "DreamPayments", "path": "DreamPayments", "kind": "mixed", "lane": "safety", "fix": "Human only. Live Stripe stays off.", "money": True},
    {"id": "money", "path": "money", "kind": "mixed", "lane": "safety", "fix": "Human only.", "money": True},
    {"id": "automation-tools", "path": "automation-tools", "kind": "python", "lane": "actions", "fix": "Compile automation tools."},
    {"id": "App_bots", "path": "App_bots", "kind": "mixed", "lane": "catalog", "fix": "Inventory App_bots."},
    {"id": "clients", "path": "clients", "kind": "mixed", "lane": "runtime", "fix": "Compile client packages."},
    {"id": "client", "path": "client", "kind": "mixed", "lane": "runtime", "fix": "Compile client package."},
    {"id": "settings", "path": "settings", "kind": "json", "lane": "catalog", "fix": "Parse settings JSON."},
    {"id": "reports", "path": "reports", "kind": "json", "lane": "detect", "fix": "Regenerate reports. Do not invent green."},
]


def check_json(path: Path) -> list[str]:
    errors = []
    for file in path.rglob("*.json"):
        if any(part in {".git", "node_modules", "dist"} for part in file.parts):
            continue
        try:
            json.loads(file.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{file.relative_to(ROOT)}: {exc}")
            if len(errors) >= 12:
                break
    return errors


def check_python(path: Path) -> list[str]:
    errors: list[str] = []
    ok = compileall.compile_dir(str(path), quiet=1, maxlevels=4, rx=None)
    if not ok:
        for file in path.rglob("*.py"):
            try:
                py_compile.compile(str(file), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(str(exc).splitlines()[-1][:240])
                if len(errors) >= 8:
                    break
        if not errors:
            errors.append("compileall reported failure")
    return errors


def check_pages(path: Path) -> list[str]:
    required = ["buddy.html", "index.html", "nav.js"]
    missing = [name for name in required if not (path / name).exists()]
    return [f"missing {name}" for name in missing]


def check_yaml_exists(path: Path) -> list[str]:
    files = list(path.glob("*.yml")) + list(path.glob("*.yaml"))
    if not files:
        return ["no workflow yaml files"]
    empty = [str(f.relative_to(ROOT)) for f in files if f.stat().st_size < 20]
    return [f"empty {name}" for name in empty[:8]]


def check_markdown(path: Path) -> list[str]:
    if not any(path.glob("*.md")):
        return ["no markdown files"]
    return []


def build_part(part: dict[str, object]) -> dict[str, object]:
    rel = str(part["path"])
    path = ROOT / rel
    money = bool(part.get("money"))
    result = {
        "id": part["id"],
        "path": rel,
        "kind": part["kind"],
        "lane": part["lane"],
        "fix": part["fix"],
        "money_sensitive": money,
        "present": path.exists(),
        "status": "absent",
        "errors": [],
        "self_build": f"python3 tools/buddy_self_build.py --part {part['id']}",
        "self_fix": "safety hold" if money else f"route to {part['lane']} recovery lane",
    }
    if not path.exists():
        result["status"] = "absent"
        return result
    kind = part["kind"]
    errors: list[str] = []
    try:
        if kind == "python":
            errors = check_python(path)
        elif kind == "json":
            errors = check_json(path)
        elif kind == "pages":
            errors = check_pages(path)
            errors.extend(check_json(path / "data") if (path / "data").exists() else [])
        elif kind == "yaml":
            errors = check_yaml_exists(path)
        elif kind == "markdown":
            errors = check_markdown(path)
        else:
            if list(path.rglob("*.py")):
                errors.extend(check_python(path))
            if list(path.rglob("*.json")):
                errors.extend(check_json(path)[:6])
    except Exception as exc:
        errors.append(str(exc)[:240])

    if money:
        result["status"] = "gated"
        result["errors"] = ["Money path present. Self-fix will not auto-edit."]
        return result
    result["errors"] = errors
    result["status"] = "failed" if errors else "built"
    return result


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--part", default="")
    args = parser.parse_args()
    selected = [p for p in PARTS if not args.part or p["id"] == args.part]
    rows = [build_part(p) for p in selected]
    report = {
        "schema": "dreamco.buddy_self_build.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "truth": "built = local syntax/contract check. Not a benchmark, regression, or production verification.",
        "parts": rows,
        "counts": {
            "parts": len(rows),
            "built": sum(r["status"] == "built" for r in rows),
            "failed": sum(r["status"] == "failed" for r in rows),
            "absent": sum(r["status"] == "absent" for r in rows),
            "gated": sum(r["status"] == "gated" for r in rows),
        },
        "auto_merge_main": False,
        "live_stripe": False,
    }
    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / "self-build.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    site = ROOT / "website" / "data"
    if site.exists():
        (site / "self-build.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], indent=2))
    return 1 if report["counts"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
