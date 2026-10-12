#!/usr/bin/env python3
"""Fleet runtime truth audit.

Tests every bot manifest through the shared runtime (buddy/fleet_runtime) and
classifies each bot as SPEC_ONLY / IMPLEMENTED / TESTED / CONNECTED /
VERIFIED / PRODUCTION / BLOCKED (see docs/UNIVERSAL_BOT_RUNTIME_CONTRACT.md).
Also audits bot/division folders and the top-level code folders by actually
compiling, importing, type-checking and running their mapped tests where the
toolchain is available, and checks every internal GitHub Pages link.

Outputs (deterministic for a given checkout + toolchain; no timestamps):
  reports/FLEET_RUNTIME_AUDIT.md
  website/data/fleet-runtime-status.json

Regression mode (CI): ``--baseline config/bots/fleet-runtime-baseline.json
--check-regressions`` fails only when a bot drops state, a new internal link
breaks, or the generated manifests drift. Pre-existing debt does not fail.
PRODUCTION is only reachable with committed evidence; nothing is hand-set.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from buddy.fleet_runtime.contract import (  # noqa: E402
    CONTRACT_PIECES, EVIDENCE_DIR, PIECE_IDS, READINESS_STATES, STATE_RANK,
    load_fixtures, load_schema, validate_bot_manifest,
)
from buddy.fleet_runtime.evidence import PROMOTION_FIELDS  # noqa: E402
from buddy.fleet_runtime.executor import FleetExecutor  # noqa: E402
from buddy.fleet_runtime.smoke import fixture_smoke, generic_smoke  # noqa: E402

REPORT = ROOT / "reports" / "FLEET_RUNTIME_AUDIT.md"
STATUS = ROOT / "website" / "data" / "fleet-runtime-status.json"
BASELINE = ROOT / "config" / "bots" / "fleet-runtime-baseline.json"
PAGE = ROOT / "website" / "fleet-runtime.html"
UNIT_TEST_MODULE = "tests.test_fleet_runtime_executor"
STATES_ALL = (*READINESS_STATES, "BLOCKED")
BOT_COLUMNS = ["slug", "name", "division", "engine", "state", "missing", "flags", "run_policy", "fixture"]

CODE_FOLDERS: dict[str, dict[str, Any]] = {
    "buddy": {"kind": "python"},
    "buddy_os": {"kind": "python"},
    "server": {"kind": "typescript", "node_tests": True},
    "client": {"kind": "typescript", "node_tests": True},
    "website": {"kind": "static", "node_tests": True},
    "benchmarks": {"kind": "python"},
    "eval": {"kind": "python"},
    "framework": {"kind": "typescript", "node_tests": True},
    "dreamco_platform": {"kind": "python"},
    "runtime": {"kind": "python"},
    "money_os": {"kind": "node"},
    "marketplace": {"kind": "python"},
    "systems": {"kind": "python"},
}
CODE_EXT = {".py", ".ts", ".tsx", ".js", ".mjs", ".cjs"}


# --------------------------------------------------------------------- utils
def run(cmd: list[str], timeout: int, cwd: Path = ROOT, env: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})})
        return {"code": proc.returncode, "out": proc.stdout[-20000:], "err": proc.stderr[-20000:], "timeout": False}
    except subprocess.TimeoutExpired as exc:
        return {"code": None, "out": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
                "err": "timeout", "timeout": True}
    except FileNotFoundError as exc:
        return {"code": None, "out": "", "err": f"missing tool: {exc}", "timeout": False}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


# ---------------------------------------------------------------------- bots
def load_evidence(slug: str) -> dict[str, Any] | None:
    path = EVIDENCE_DIR / f"{slug}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return {"_invalid": True}
    return data if isinstance(data, dict) else {"_invalid": True}


def connections_ok(manifest: dict[str, Any], record: dict[str, Any] | None) -> bool:
    if not record or record.get("_invalid"):
        return False
    conns = {c.get("id"): c for c in record.get("connections", []) if isinstance(c, dict)}
    required = set(record.get("required_apis", []))
    if manifest["engine"] == "drafting":
        required.add("model_router")
    if not required and not conns:
        return False  # evidence must show at least one checked connection
    return all(conns.get(r, {}).get("status") == "ok" and conns.get(r, {}).get("checked_at") for r in required)


def unit_tests_pass(skip: bool) -> bool | None:
    if skip:
        return None
    result = run([sys.executable, "-m", "unittest", "-q", UNIT_TEST_MODULE], timeout=600)
    return result["code"] == 0


def audit_bots(unit_ok: bool | None) -> dict[str, Any]:
    executor = FleetExecutor(env={})
    schema = load_schema()
    fixtures = load_fixtures()["fixtures"]
    profiles = executor.profiles
    known_divisions = {json.loads(p.read_text(encoding="utf-8")).get("division") for p in (ROOT / "App_bots").glob("*.json")}
    lanes_path = ROOT / "config" / "bots" / "teammate-lanes.json"
    if lanes_path.exists():
        known_divisions.add(json.loads(lanes_path.read_text(encoding="utf-8")).get("division", "GrokTeammates"))
    page_exists = PAGE.exists()
    rows = []
    for slug in sorted(executor.bots):
        m = executor.manifest(slug)
        problems = validate_bot_manifest(m, schema)
        mapped = m["engine"] != "unmapped"
        smoke = generic_smoke(executor, slug) if mapped and not problems else None
        fixture = fixtures.get(slug)
        fx = None
        if fixture and fixture.get("engine") == m["engine"] and mapped and not problems:
            fx = fixture_smoke(executor, slug, fixture)
        record = load_evidence(slug)
        bench_measured = bool(record and record.get("benchmark_results"))
        pieces = {
            "manifest": not problems,
            "division": m["division"] in known_divisions,
            "capabilities": bool(m["capabilities"]),
            "runtime_adapter": mapped,
            "model_router": m["model_router"] in profiles["model_router"],
            "tools_apis": all(t in profiles["tools"] for t in m["tools"]),
            "io_schema": bool(m["io_schema"]) and m["io_schema"] in profiles["io_schema"],
            "permissions": m["permissions"]["ceiling"] in {"read_only", "sandbox", "plan_only"},
            "error_handling": m["error_handling"] in profiles["error_handling"],
            "unit_test": mapped and bool(unit_ok),
            "smoke_test": bool(fx and fx["passed"]),
            "benchmark": bench_measured,
            "health_status": bool(smoke and smoke["passed"]),
            "pages_route": page_exists,
            "evidence_record": bool(record and not record.get("_invalid")),
            "readiness_state": True,
        }
        flags = set(m["flags"])
        if fixture and fixture.get("engine") != m["engine"]:
            flags.add("fixture_engine_mismatch")
        if fixture and fixture.get("origin") == "generated":
            flags.add("fixture_generated")
        blocked_reasons = []
        if problems:
            blocked_reasons.append("invalid_manifest")
        if smoke and not smoke["passed"]:
            blocked_reasons.append("generic_smoke_failed")
        if fx and not fx["passed"]:
            blocked_reasons.append("fixture_failed")
        if flags & {"invalid_slug", "duplicate_slug"}:
            blocked_reasons.append("slug_defect")
        if record and record.get("_invalid"):
            blocked_reasons.append("invalid_evidence_record")
        if blocked_reasons:
            state = "BLOCKED"
        elif not mapped:
            state = "SPEC_ONLY"
        elif not (pieces["smoke_test"] and pieces["unit_test"]):
            state = "IMPLEMENTED"
        elif not (pieces["pages_route"] and connections_ok(m, record)):
            state = "TESTED"
        elif not (bench_measured and all(record.get(f) for f in PROMOTION_FIELDS["VERIFIED"])):
            state = "CONNECTED"
        elif not all(record.get(f) for f in PROMOTION_FIELDS["PRODUCTION"]):
            state = "VERIFIED"
        else:
            state = "PRODUCTION"
        rows.append({
            "slug": slug, "name": m["name"], "division": m["division"], "engine": m["engine"],
            "state": state, "pieces": pieces, "flags": sorted(flags), "blocked_reasons": blocked_reasons,
            "run_policy": m.get("run_policy", "spec_only"), "enabled": m.get("enabled", True),
            "fixture_origin": (fixture or {}).get("origin", "hand-written") if fixture else None,
            "smoke_failures": (smoke or {}).get("failures", []) + (fx or {}).get("failures", []),
        })
    return {"rows": rows}


DIVISIONS_PATH = ROOT / "config" / "bots" / "division-manifests.generated.json"


def audit_divisions(rows: list[dict[str, Any]], unit_ok: bool | None) -> list[dict[str, Any]]:
    """Per-division state: SPEC_ONLY (no runnable source), BLOCKED (division smoke fails),
    IMPLEMENTED (smoke passes, engine unit tests not green) or TESTED."""
    from buddy.fleet_runtime.divisions import division_smoke

    if not DIVISIONS_PATH.exists():
        return []
    executor = FleetExecutor(env={})
    fixtures = load_fixtures()["fixtures"]
    by_div: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        by_div[r["division"]][r["state"]] += 1
    out = []
    for d in json.loads(DIVISIONS_PATH.read_text(encoding="utf-8"))["divisions"]:
        smoke = division_smoke(executor, d, fixtures)
        if not smoke["ran"]:
            state = "SPEC_ONLY"
        elif not smoke["passed"]:
            state = "BLOCKED"
        elif unit_ok:
            state = "TESTED"
        else:
            state = "IMPLEMENTED"
        out.append({
            "name": d["name"], "state": state, "bots": d["bots"], "bot_states": {k: by_div[d["name"]][k] for k in STATES_ALL if by_div[d["name"]][k]},
            "smoke_bots": d["smoke_bots"], "smoke_passed": smoke["passed"], "smoke_failures": [r for r in smoke["results"] if not r["passed"]],
            "runnable_bots": d["run_policy"].get("allowed", 0), "triggerable": d["triggerable"], "blocked_reason": d["blocked_reason"],
            "sources": d["sources"], "engines": d["engines"],
        })
    return out


def summarise_bots(rows: list[dict[str, Any]]) -> dict[str, Any]:
    totals = Counter(r["state"] for r in rows)
    by_div: dict[str, Counter] = defaultdict(Counter)
    by_engine: dict[str, Counter] = defaultdict(Counter)
    flags = Counter()
    missing = Counter()
    for r in rows:
        by_div[r["division"]][r["state"]] += 1
        by_engine[r["engine"]][r["state"]] += 1
        flags.update(r["flags"])
        missing.update(p for p, ok in r["pieces"].items() if not ok)
    order = lambda c: {s: c.get(s, 0) for s in STATES_ALL}  # noqa: E731
    return {
        "bots": len(rows),
        "by_state": order(totals),
        "by_division": {d: {**order(c), "total": sum(c.values())} for d, c in sorted(by_div.items())},
        "by_engine": {e: {**order(c), "total": sum(c.values())} for e, c in sorted(by_engine.items())},
        "flags": dict(sorted(flags.items())),
        "duplicates": flags.get("duplicate_profile", 0) + flags.get("duplicate_slug", 0),
        "placeholders": sum(1 for r in rows if any(f.startswith("placeholder") for f in r["flags"])),
        "missing_pieces": {p: missing.get(p, 0) for p in PIECE_IDS},
        "run_policy": dict(sorted(Counter(r.get("run_policy", "spec_only") for r in rows).items())),
    }


# ----------------------------------------------------------- bot/div folders
def audit_bot_folders(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_source: dict[str, list[str]] = defaultdict(list)
    state_of = {r["slug"]: r["state"] for r in rows}
    from buddy.fleet_runtime.contract import load_manifests
    for b in load_manifests()["bots"]:
        for src in b["sources"]:
            if src.startswith("App_bots/"):
                by_source[src].append(b["slug"])
    out = []
    required_keys = {"slug", "displayName", "capabilities", "description"}
    for path in sorted((ROOT / "App_bots").glob("*.json")):
        entry: dict[str, Any] = {"folder": rel(path), "kind": "division_manifest"}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            entry["config_valid"] = isinstance(data, dict) and isinstance(data.get("bots"), list)
            bots = data.get("bots", []) if isinstance(data, dict) else []
            entry["bots_declared"] = len(bots)
            entry["bots_missing_keys"] = sum(1 for b in bots if not required_keys <= set(b))
        except ValueError as exc:
            entry.update({"config_valid": False, "error": str(exc)[:200], "bots_declared": 0})
        entry["entrypoints"] = []  # JSON manifests carry no executable source
        states = Counter(state_of[s] for s in by_source.get(rel(path), []))
        entry["states"] = {s: states.get(s, 0) for s in STATES_ALL if states.get(s)}
        if not entry.get("bots_declared"):
            entry["verdict"] = "placeholder"
        else:
            entry["verdict"] = min(states, key=lambda s: STATE_RANK[s]) if states else "SPEC_ONLY"
        entry["note"] = "division state = lowest state any of its bots holds"
        out.append(entry)
    md = sorted((ROOT / "bots").glob("*.md"))
    md_states = Counter(state_of.get(p.stem.lower(), "SPEC_ONLY") for p in md)
    out.append({"folder": "bots/", "kind": "markdown_specs", "files": len(md), "entrypoints": [],
                "config_valid": True, "states": dict(md_states),
                "verdict": "SPEC_ONLY (Markdown specs; executed only through buddy/fleet_runtime manifests)"})
    sandbox = sorted((ROOT / "bots" / "sandbox").glob("*.js"))
    node = shutil.which("node")
    bad = []
    if node:
        for js in sandbox:
            if run([node, "--check", str(js)], timeout=60)["code"] != 0:
                bad.append(rel(js))
    out.append({"folder": "bots/sandbox/", "kind": "js_snippets", "files": len(sandbox), "entrypoints": [rel(p) for p in sandbox],
                "syntax_errors": bad if node else "node unavailable", "tests": 0,
                "verdict": ("broken" if bad else "untested") if node else "untested"})
    status_path = ROOT / "original-bots" / "STATUS.json"
    if status_path.exists():
        data = json.loads(status_path.read_text(encoding="utf-8"))
        states = Counter(b.get("state") for b in data.get("bots", []))
        out.append({"folder": "original-bots/", "kind": "plans", "files": len(data.get("bots", [])),
                    "entrypoints": [], "states": dict(states), "rule": data.get("rule"),
                    "verdict": "SPEC_ONLY" if set(states) <= {"planned"} else "mixed"})
    return out


# -------------------------------------------------------------- code folders
PY_IMPORT_SCRIPT = r"""
import importlib, importlib.util, json, sys, pathlib, io, contextlib
root = pathlib.Path(sys.argv[1]); folder = sys.argv[2]
sys.path.insert(0, str(root))
base = root / folder
internal = {p.name for p in root.iterdir() if p.is_dir()} | {p.stem for p in root.glob("*.py")}
local = {p.stem for p in base.rglob("*.py")} | {p.name for p in base.rglob("*") if p.is_dir()}
results = {"modules": 0, "failed": {}, "missing_deps": {}, "script_style": {}}
for path in sorted(base.rglob("*.py")):
    parts = path.relative_to(root).with_suffix("").parts
    if "__pycache__" in parts or path.name.startswith("test_") or "tests" in parts or path.name in {"__main__.py", "conftest.py"}:
        continue
    if parts[-1] == "__init__":
        parts = parts[:-1]
    name = ".".join(parts)
    results["modules"] += 1
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            if all(p.isidentifier() for p in parts):
                importlib.import_module(name)
            else:
                spec = importlib.util.spec_from_file_location("_probe_" + str(abs(hash(name))), path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
    except ModuleNotFoundError as exc:
        top = (exc.name or "").split(".")[0]
        if top in local:
            results["script_style"][name] = top  # sibling import that works only when run as a script
        elif top and top not in internal:
            results["missing_deps"][name] = top
        else:
            results["failed"][name] = f"ModuleNotFoundError: {str(exc)[:160]}"
    except SystemExit:
        pass
    except BaseException as exc:
        results["failed"][name] = f"{type(exc).__name__}: {str(exc)[:160]}"
print(json.dumps(results))
"""


def python_checks(folder: str, timeout: int, skip_tests: bool) -> dict[str, Any]:
    base = ROOT / folder
    files = sorted(p for p in base.rglob("*.py") if "__pycache__" not in p.parts)
    syntax = []
    for path in files:
        try:
            compile(path.read_text(encoding="utf-8", errors="replace"), str(path), "exec")
        except SyntaxError as exc:
            syntax.append(f"{rel(path)}:{exc.lineno}: {exc.msg}")
    result: dict[str, Any] = {"python_files": len(files), "syntax_errors": syntax}
    if files:
        imp = run([sys.executable, "-c", PY_IMPORT_SCRIPT, str(ROOT), folder], timeout=300,
                  env={"DREAMCO_IMPORT_PROBE": "1"})
        try:
            data = json.loads(imp["out"].strip().splitlines()[-1])
        except (ValueError, IndexError):
            data = {"modules": 0, "failed": {"<import-probe>": ("timeout" if imp["timeout"] else imp["err"][-300:])},
                    "missing_deps": {}, "script_style": {}}
        result["import_probe"] = {"modules": data["modules"], "failed": len(data["failed"]),
                                  "failures": dict(sorted(data["failed"].items())[:15]),
                                  "missing_third_party": sorted(set(data["missing_deps"].values())),
                                  "modules_needing_missing_deps": len(data["missing_deps"]),
                                  "script_style_imports": len(data["script_style"])}
    pat = re.compile(rf"^\s*(from|import)\s+{re.escape(folder)}(\.|\s|$)", re.M)
    tests = sorted({rel(p) for p in (ROOT / "tests").glob("test_*.py") if pat.search(p.read_text(encoding="utf-8", errors="replace"))}
                   | {rel(p) for p in base.rglob("test_*.py")})
    result["test_files"] = tests
    if tests and not skip_tests:
        res = run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", "-rN",
                   "--continue-on-collection-errors", *tests],
                  timeout=timeout)
        result["tests"] = parse_pytest(res)
    elif tests:
        result["tests"] = {"ran": False, "reason": "skipped (--skip-folder-tests)"}
    return result


def parse_pytest(res: dict[str, Any]) -> dict[str, Any]:
    if res["timeout"]:
        return {"ran": True, "timeout": True, "passed": 0, "failed": 0, "errors": 0}
    tail = (res["out"] + "\n" + res["err"]).strip().splitlines()
    summary = next((line for line in reversed(tail) if re.search(r"\d+ (passed|failed|error)", line)), "")
    counts = {k: int(n) for n, k in re.findall(r"(\d+) (passed|failed|errors?|skipped)", summary)}
    if "No module named pytest" in res["err"]:
        return {"ran": False, "reason": "pytest not installed"}
    if not counts or res["code"] == 5:
        return {"ran": False, "reason": "no tests collected"}
    return {"ran": True, "passed": counts.get("passed", 0), "failed": counts.get("failed", 0),
            "errors": counts.get("errors", counts.get("error", 0)), "skipped": counts.get("skipped", 0),
            "summary": summary.strip("= ").strip()[:200]}


def tsc_check(timeout: int) -> dict[str, Any]:
    tsc = ROOT / "node_modules" / ".bin" / "tsc"
    if not tsc.exists():
        return {"ran": False, "reason": "node_modules not installed (run npm ci)"}
    res = run([str(tsc), "--noEmit", "-p", "tsconfig.json", "--incremental", "false"], timeout=timeout)
    if res["timeout"]:
        return {"ran": True, "timeout": True, "errors_by_folder": {}}
    errors: Counter = Counter()
    samples: dict[str, list[str]] = defaultdict(list)
    for line in (res["out"] + res["err"]).splitlines():
        m = re.match(r"^([\w./-]+)\(\d+,\d+\): error TS\d+", line)
        if m:
            top = m.group(1).split("/")[0]
            errors[top] += 1
            if len(samples[top]) < 5:
                samples[top].append(line[:200])
    return {"ran": True, "exit_code": res["code"], "errors_by_folder": dict(errors), "samples": dict(samples)}


def node_tests_for(folder: str) -> list[str]:
    needle = re.compile(rf"(\.\./|['\"`]){re.escape(folder)}/")
    return sorted(rel(p) for p in (ROOT / "tests").glob("*.test.*")
                  if p.suffix in {".ts", ".mjs", ".js"} and needle.search(p.read_text(encoding="utf-8", errors="replace")))


def run_node_tests(files: list[str], timeout: int) -> dict[str, Any]:
    if not files:
        return {"ran": False, "reason": "no mapped node tests"}
    if not (ROOT / "node_modules" / "tsx").exists():
        return {"ran": False, "reason": "node_modules not installed (run npm ci)"}
    res = run(["node", "--import", "tsx", "--test", *files], timeout=timeout)
    if res["timeout"]:
        return {"ran": True, "timeout": True, "passed": 0, "failed": 0}
    text = res["out"] + res["err"]
    grab = lambda key: int((re.findall(rf"^# {key} (\d+)", text, re.M) or ["0"])[-1])  # noqa: E731
    failing = sorted(set(re.findall(r"^not ok \d+ - (.+)$", text, re.M)))[:10]
    return {"ran": True, "passed": grab("pass"), "failed": grab("fail"), "cancelled": grab("cancelled"),
            "failing_examples": failing}


def js_syntax(folder: str) -> dict[str, Any]:
    node = shutil.which("node")
    files = sorted(p for p in (ROOT / folder).rglob("*") if p.suffix in {".js", ".mjs", ".cjs"} and "node_modules" not in p.parts)
    if not node:
        return {"js_files": len(files), "ran": False}
    bad = [rel(p) for p in files if run([node, "--check", str(p)], timeout=60)["code"] != 0]
    return {"js_files": len(files), "ran": True, "syntax_errors": bad}


def verdict(entry: dict[str, Any]) -> str:
    if not entry.get("code_files"):
        return "placeholder"
    syntax = len(entry.get("syntax_errors", [])) + len((entry.get("js") or {}).get("syntax_errors", []))
    imp = entry.get("import_probe") or {}
    imp_fail_ratio = (imp.get("failed", 0) / imp["modules"]) if imp.get("modules") else 0.0
    ran, passed, failed = 0, 0, 0
    for key in ("tests", "node_tests"):
        t = entry.get(key) or {}
        if t.get("ran"):
            ran += 1
            passed += t.get("passed", 0)
            failed += t.get("failed", 0) + t.get("errors", 0) + t.get("cancelled", 0) + (1 if t.get("timeout") else 0)
    type_errors = entry.get("type_errors", 0)
    site_ok = entry.get("site_check_ok", True)
    if syntax and syntax >= max(1, entry["code_files"] // 2) or imp_fail_ratio > 0.5 or (ran and passed + failed and passed < failed):
        return "broken"
    if syntax or imp.get("failed") or failed or type_errors or not site_ok or entry.get("links_broken"):
        return "partial"
    if not ran or passed == 0:
        return "untested"
    return "working"


def git_dirty() -> set[str]:
    res = run(["git", "status", "--porcelain", "--untracked-files=all"], timeout=120)
    if res["code"] != 0:
        return set()
    return {line[3:] for line in res["out"].splitlines() if line}


def restore_test_side_effects(before: set[str]) -> dict[str, list[str]]:
    """Folder tests must not leave the checkout dirty. Restore tracked files
    that were clean before the run (identical to HEAD, so restoring is
    lossless) and report anything the tests wrote."""
    after = git_dirty()
    changed = sorted(after - before)
    tracked = [p for p in changed if run(["git", "ls-files", "--error-unmatch", p], timeout=60)["code"] == 0]
    if tracked:
        run(["git", "checkout", "--", *tracked], timeout=120)
    untracked = [p for p in changed if p not in tracked]
    return {"restored_tracked_files": tracked, "untracked_files_created": untracked}


def audit_code_folders(timeout: int, skip_tests: bool, links: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    before = git_dirty()
    try:
        out = _audit_code_folders(timeout, skip_tests, links)
    finally:
        side_effects = restore_test_side_effects(before)
    return out, side_effects


def _audit_code_folders(timeout: int, skip_tests: bool, links: dict[str, Any]) -> list[dict[str, Any]]:
    tsc = None if skip_tests else tsc_check(timeout)
    out = []
    for folder, spec in CODE_FOLDERS.items():
        base = ROOT / folder
        entry: dict[str, Any] = {"folder": folder, "kind": spec["kind"]}
        if not base.exists():
            entry.update({"code_files": 0, "verdict": "placeholder", "note": "folder missing"})
            out.append(entry)
            continue
        all_files = [p for p in base.rglob("*") if p.is_file() and "node_modules" not in p.parts and "__pycache__" not in p.parts]
        entry["files"] = len(all_files)
        entry["code_files"] = sum(1 for p in all_files if p.suffix in CODE_EXT)
        if any(p.suffix == ".py" for p in all_files):
            entry.update(python_checks(folder, timeout, skip_tests))
        if spec["kind"] in {"node", "static"} or any(p.suffix in {".js", ".mjs"} for p in all_files):
            entry["js"] = js_syntax(folder)
        if spec["kind"] == "typescript" and folder in {"server", "client"}:
            if tsc is None:
                entry["typecheck"] = {"ran": False, "reason": "skipped (--skip-folder-tests)"}
            else:
                entry["typecheck"] = {k: v for k, v in tsc.items() if k != "samples"} | {"samples": (tsc.get("samples") or {}).get(folder, [])}
                entry["type_errors"] = (tsc.get("errors_by_folder") or {}).get(folder, 0)
        elif spec["kind"] == "typescript":
            entry["typecheck"] = {"ran": False, "reason": "folder is outside tsconfig.json include"}
        if spec.get("node_tests"):
            files = node_tests_for(folder)
            entry["node_test_files"] = len(files)
            entry["node_tests"] = {"ran": False, "reason": "skipped (--skip-folder-tests)"} if skip_tests else run_node_tests(files, timeout)
        if folder == "website":
            if skip_tests:
                entry["site_check_ok"] = True
                entry["site_check"] = "skipped"
            else:
                res = run([sys.executable, "tools/build_buddy_public_site.py", "--check"], timeout=timeout)
                entry["site_check_ok"] = res["code"] == 0
                entry["site_check"] = "ok" if res["code"] == 0 else (res["err"] or res["out"])[-600:]
            entry["links_checked"] = links["links_checked"]
            entry["links_broken"] = links["broken_count"]
        if folder == "money_os":
            pkg = base / "backend" / "package.json"
            entry["deps_installed"] = (base / "backend" / "node_modules").exists() if pkg.exists() else None
        entry["verdict"] = verdict(entry)
        out.append(entry)
    return out


# --------------------------------------------------------------------- links
def audit_links() -> dict[str, Any]:
    import check_website_links as cwl

    return cwl.check_all(ROOT / "website")


# ------------------------------------------------------------------- outputs
def build_status(rows, summary, bot_folders, code_folders, links, unit_ok, manifest_digest) -> dict[str, Any]:
    piece_index = {p: i for i, p in enumerate(PIECE_IDS)}
    return {
        "schema": "dreamco.fleet_runtime_status.v1",
        "generated_by": "tools/fleet_runtime_audit.py",
        "truth_policy": "States are computed from manifests, offline runs of the shared runtime, fixtures and committed evidence. IMPLEMENTED/TESTED prove offline wiring only; CONNECTED and above need committed evidence records. PRODUCTION is never hand-set.",
        "manifest_digest": manifest_digest,
        "contract_pieces": list(PIECE_IDS),
        "states": list(STATES_ALL),
        "engine_unit_tests_passed": unit_ok,
        "summary": summary,
        "bot_folders": bot_folders,
        "code_folders": code_folders,
        "links": {k: links[k] for k in ("files_scanned", "links_checked", "broken_count", "broken", "server_api_refs")},
        "bot_columns": BOT_COLUMNS,
        "bots": [[r["slug"], r["name"], r["division"], r["engine"], r["state"],
                  [piece_index[p] for p, ok in r["pieces"].items() if not ok], r["flags"],
                  r.get("run_policy", "spec_only"), r.get("fixture_origin")] for r in rows],
    }


def fmt_tests(t: dict[str, Any] | None) -> str:
    if not t:
        return "—"
    if not t.get("ran"):
        return f"not run ({t.get('reason', '')})"
    if t.get("timeout"):
        return "timeout"
    extra = f", {t['errors']} errors" if t.get("errors") else ""
    return f"{t.get('passed', 0)} passed, {t.get('failed', 0)} failed{extra}"


def render_report(status: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    s = status["summary"]
    lines = [
        "# Fleet Runtime Truth Audit", "",
        "_Generated by `tools/fleet_runtime_audit.py`. Do not hand-edit; regenerate._", "",
        "States are computed, not declared (see `docs/UNIVERSAL_BOT_RUNTIME_CONTRACT.md`). "
        "IMPLEMENTED = the generic offline smoke runs through the shared runtime; TESTED = a bot-specific "
        "fixture also passes (hand-written, or generated from the bot's own capabilities by "
        "`buddy/fleet_runtime/fixtures.py`, flagged `fixture_generated`). Neither proves model quality or live integrations. CONNECTED and above need committed "
        "evidence records under `evidence/fleet-runtime/`.", "",
        f"Engine unit tests passed: **{status['engine_unit_tests_passed']}**", "",
        "## Bots by state", "", "| State | Bots |", "|---|---:|",
    ]
    lines += [f"| {k} | {v} |" for k, v in s["by_state"].items()]
    lines += [f"| **Total** | **{s['bots']}** |", "",
              f"Flags: duplicates **{s['duplicates']}**, placeholders **{s['placeholders']}**, " +
              ", ".join(f"{k} {v}" for k, v in s["flags"].items()), "",
              "## Missing contract pieces (bots missing each piece)", "", "| Piece | Missing |", "|---|---:|"]
    lines += [f"| {k} | {v} |" for k, v in s["missing_pieces"].items()]
    lines += ["", "## By engine", "", "| Engine | " + " | ".join(STATES_ALL) + " | Total |", "|---|" + "---:|" * (len(STATES_ALL) + 1)]
    for e, c in s["by_engine"].items():
        lines.append(f"| {e} | " + " | ".join(str(c[x]) for x in STATES_ALL) + f" | {c['total']} |")
    lines += ["", "## By division", "", "| Division | " + " | ".join(STATES_ALL) + " | Total |", "|---|" + "---:|" * (len(STATES_ALL) + 1)]
    for d, c in s["by_division"].items():
        lines.append(f"| {d} | " + " | ".join(str(c[x]) for x in STATES_ALL) + f" | {c['total']} |")
    divs = status.get("divisions") or []
    if divs:
        lines += ["", "## Divisions", "",
                  "Division state comes from a division-level smoke test: one of the division's own bots per engine runs end to end "
                  "through the shared runtime offline (`python -m buddy.fleet_runtime division-smoke --all`).", "",
                  "| Division | State | Bots | Runnable | Smoke bots | Smoke | Sources |", "|---|---|---:|---:|---|---|---|"]
        for d in divs:
            lines.append(f"| {d['name']} | **{d['state']}** | {d['bots']} | {d['runnable_bots']} | {', '.join(d['smoke_bots']) or '—'} | "
                         f"{'pass' if d['smoke_passed'] else ('no runnable bots' if not d['smoke_bots'] else 'FAIL')} | {', '.join(d['sources'])} |")
    lines += ["", "## Top-level code folders", "",
              "Verdicts come from actually compiling, importing, type-checking and running mapped tests in this environment.", "",
              "| Folder | Verdict | Code files | Syntax errors | Import probe | Python tests | Node tests | Typecheck |",
              "|---|---|---:|---:|---|---|---|---|"]
    for f in status["code_folders"]:
        imp = f.get("import_probe")
        imp_s = f"{imp['modules'] - imp['failed']}/{imp['modules']} ok" if imp else "—"
        syn = len(f.get("syntax_errors", [])) + len((f.get("js") or {}).get("syntax_errors", []) or [])
        tc = f.get("typecheck") or {}
        tc_s = (f"{f.get('type_errors', 0)} errors" if tc.get("ran") else f"not run ({tc.get('reason', '')})") if tc else "—"
        lines.append(f"| {f['folder']} | **{f['verdict']}** | {f.get('code_files', 0)} | {syn} | {imp_s} | "
                     f"{fmt_tests(f.get('tests'))} | {fmt_tests(f.get('node_tests'))} | {tc_s} |")
    lines += ["", "### Folder failure details", ""]
    for f in status["code_folders"]:
        details = []
        if f.get("syntax_errors"):
            details.append("syntax: " + "; ".join(f["syntax_errors"][:5]))
        if (f.get("js") or {}).get("syntax_errors"):
            details.append("js syntax: " + "; ".join(f["js"]["syntax_errors"][:5]))
        if (f.get("import_probe") or {}).get("failures"):
            details.append("imports: " + "; ".join(f"{k} ({v})" for k, v in list(f["import_probe"]["failures"].items())[:5]))
        if (f.get("tests") or {}).get("summary") and (f["tests"].get("failed") or f["tests"].get("errors")):
            details.append("pytest: " + f["tests"]["summary"])
        if (f.get("node_tests") or {}).get("failing_examples"):
            details.append("node: " + "; ".join(f["node_tests"]["failing_examples"][:5]))
        if (f.get("typecheck") or {}).get("samples"):
            details.append("tsc: " + "; ".join(f["typecheck"]["samples"][:3]))
        if f.get("site_check") not in (None, "ok", "skipped"):
            details.append("site check: " + str(f["site_check"])[:300])
        if details:
            lines.append(f"- **{f['folder']}**: " + " | ".join(details))
    fx = status.get("folder_test_side_effects") or {}
    if fx.get("restored_tracked_files") or fx.get("untracked_files_created"):
        lines += ["", "### Tests that write into the checkout", "",
                  "These files were modified/created by the folder test runs (tracked ones were restored by the auditor). "
                  "Tests should write to temp dirs instead:", ""]
        lines += [f"- `{p}`" for p in fx.get("restored_tracked_files", []) + fx.get("untracked_files_created", [])]
    lines += ["", "## Bot / division folders", "", "| Folder | Kind | Verdict | Detail |", "|---|---|---|---|"]
    for f in status["bot_folders"]:
        detail = f.get("states") or {}
        extra = f" bots={f['bots_declared']}" if "bots_declared" in f else (f" files={f.get('files')}" if "files" in f else "")
        lines.append(f"| {f['folder']} | {f['kind']} | {f['verdict']} | {json.dumps(detail)}{extra} |")
    links = status["links"]
    lines += ["", "## GitHub Pages internal links", "",
              f"Files scanned: {links['files_scanned']}; internal links/routes checked: {links['links_checked']}; "
              f"**broken: {links['broken_count']}**. Server-only `/api/*` references (cannot work on static Pages): "
              f"{len(links['server_api_refs'])}.", ""]
    lines += [f"- `{b['source']}` → `{b['href']}`" for b in links["broken"][:100]]
    blocked = [r for r in rows if r["state"] == "BLOCKED"]
    lines += ["", f"## Blocked bots ({len(blocked)})", ""]
    lines += [f"- `{r['slug']}`: {', '.join(r['blocked_reasons'])} {('— ' + '; '.join(r['smoke_failures'][:2])) if r['smoke_failures'] else ''}" for r in blocked[:100]]
    spec = [r for r in rows if r["state"] == "SPEC_ONLY"]
    lines += ["", f"## Spec-only bots ({len(spec)})", "", ", ".join(f"`{r['slug']}`" for r in spec), ""]
    tested = [r for r in rows if STATE_RANK[r["state"]] >= STATE_RANK["TESTED"]]
    hand = [r for r in tested if r.get("fixture_origin") == "hand-written"]
    lines += [f"## Bots at TESTED or above ({len(tested)})", "",
              f"{len(tested) - len(hand)} via generated fixtures (`fixture_generated`), {len(hand)} via hand-written fixtures: "
              + ", ".join(f"`{r['slug']}`" for r in hand), ""]
    policy: dict[str, list[str]] = {}
    for r in rows:
        policy.setdefault(r.get("run_policy", "spec_only"), []).append(r["slug"])
    reasons = {"blocked_money": "money movement / payments / billing / trading: never triggerable from Buddy",
               "blocked_destructive": "delete / purge / wipe: never triggerable from Buddy",
               "spec_only": "no shared engine fits (placeholder spec without specific capabilities)"}
    lines += ["## Run with Buddy", "", f"Run buttons enabled: **{len(policy.get('allowed', []))}**. Bots that cannot be run, and why:", ""]
    for key in ("blocked_money", "blocked_destructive", "spec_only"):
        items = policy.get(key, [])
        lines += [f"- **{key}** ({len(items)}) — {reasons[key]}: " + ", ".join(f"`{x}`" for x in items)]
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- regression
def manifest_drift() -> bool:
    import generate_bot_manifests as gen

    collection = gen.build()
    current = gen.OUT.read_text(encoding="utf-8") if gen.OUT.exists() else ""
    return current != gen.render(collection)


def compare_baseline(baseline: dict[str, Any], rows: list[dict[str, Any]], links: dict[str, Any], drift: bool,
                     divisions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    old = baseline.get("bots", {})
    dropped = []
    for r in rows:
        prev = old.get(r["slug"])
        if prev and STATE_RANK[r["state"]] < STATE_RANK[prev]:
            dropped.append({"slug": r["slug"], "from": prev, "to": r["state"], "reasons": r["blocked_reasons"]})
    removed = sorted(set(old) - {r["slug"] for r in rows})
    known_links = set(baseline.get("links_broken", []))
    new_links = [f"{b['source']} -> {b['href']}" for b in links["broken"] if f"{b['source']} -> {b['href']}" not in known_links]
    improved = sum(1 for r in rows if r["slug"] in old and STATE_RANK[r["state"]] > STATE_RANK[old[r["slug"]]])
    old_div = baseline.get("divisions", {})
    div_drops = [{"division": d["name"], "from": old_div[d["name"]], "to": d["state"]} for d in (divisions or [])
                 if d["name"] in old_div and STATE_RANK[d["state"]] < STATE_RANK[old_div[d["name"]]]]
    return {"state_drops": dropped, "division_state_drops": div_drops, "removed_bots": removed, "new_broken_links": new_links,
            "manifest_drift": drift, "improved_bots": improved,
            "ok": not dropped and not div_drops and not new_links and not drift}


def baseline_payload(rows: list[dict[str, Any]], links: dict[str, Any], divisions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "schema": "dreamco.fleet_runtime_baseline.v1",
        "policy": "CI fails when a bot drops below its baseline state, a new internal link breaks, or manifests drift. Raise the baseline (--write-baseline) in the PR that lifts bots; never lower it to hide a regression.",
        "bots": {r["slug"]: r["state"] for r in rows},
        "divisions": {d["name"]: d["state"] for d in (divisions or [])},
        "links_broken": sorted(f"{b['source']} -> {b['href']}" for b in links["broken"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-folder-tests", action="store_true", help="skip pytest/node/tsc/site runs (fast mode)")
    parser.add_argument("--folder-timeout", type=int, default=900)
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument("--check-regressions", action="store_true")
    parser.add_argument("--write-baseline", action="store_true")
    parser.add_argument("--no-write", action="store_true", help="do not write report/status files")
    parser.add_argument("--summary-json", type=Path, help="also write a machine summary (for CI artifacts)")
    args = parser.parse_args(argv)

    unit_ok = unit_tests_pass(skip=False)
    bots = audit_bots(unit_ok)
    rows = bots["rows"]
    summary = summarise_bots(rows)
    links = audit_links()
    bot_folders = audit_bot_folders(rows)
    divisions = audit_divisions(rows, unit_ok)
    code_folders, side_effects = audit_code_folders(args.folder_timeout, args.skip_folder_tests, links)
    if args.skip_folder_tests and STATUS.exists():
        # Fast mode must not erase the last full audit's folder verdicts from
        # the committed status/report; carry them over, clearly labelled.
        previous = json.loads(STATUS.read_text(encoding="utf-8"))
        if previous.get("code_folders"):
            code_folders = previous["code_folders"]
            side_effects = previous.get("folder_test_side_effects", side_effects)
    from buddy.fleet_runtime.contract import load_manifests
    status = build_status(rows, summary, bot_folders, code_folders, links, unit_ok, load_manifests()["source_digest"])
    status["folder_test_side_effects"] = side_effects
    status["divisions"] = divisions
    status["summary"]["divisions_by_state"] = dict(sorted(Counter(d["state"] for d in divisions).items()))
    if not args.no_write:
        STATUS.write_text(json.dumps(status, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        REPORT.write_text(render_report(status, rows), encoding="utf-8")
    if args.write_baseline:
        BASELINE.write_text(json.dumps(baseline_payload(rows, links, divisions), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    result: dict[str, Any] = {"by_state": summary["by_state"], "bots": summary["bots"],
                              "divisions_by_state": status["summary"]["divisions_by_state"],
                              "folders": {f["folder"]: f["verdict"] for f in code_folders},
                              "links_broken": links["broken_count"], "engine_unit_tests_passed": unit_ok}
    code = 0
    if args.check_regressions:
        baseline_path = args.baseline or BASELINE
        baseline = json.loads(baseline_path.read_text(encoding="utf-8")) if baseline_path.exists() else {}
        regress = compare_baseline(baseline, rows, links, manifest_drift(), divisions)
        result["regressions"] = regress
        if unit_ok is False:
            regress["ok"] = False
            regress["engine_unit_tests_failed"] = True
        code = 0 if regress["ok"] else 1
    if args.summary_json:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
