"""CLI: python -m buddy.fleet_runtime run <slug> --objective "..." [--input JSON]."""
from __future__ import annotations

import argparse
import json
import sys

from .executor import FleetExecutor
from .contract import load_fixtures
from .smoke import fixture_smoke, generic_smoke


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m buddy.fleet_runtime")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="run one bot through the shared runtime (offline unless live is enabled)")
    run.add_argument("slug")
    run.add_argument("--objective", required=True)
    run.add_argument("--input", default="{}", help="JSON object passed as task.input")
    run.add_argument("--action-level", default="sandbox")
    smoke = sub.add_parser("smoke", help="run the generic smoke task for bots")
    smoke.add_argument("slugs", nargs="*")
    smoke.add_argument("--all", action="store_true")
    job = sub.add_parser("job", help="Run with Buddy: generic + fixture smoke for one bot, refusing money/delete bots")
    job.add_argument("slug")
    job.add_argument("--out", help="write the run evidence JSON here")
    cust = sub.add_parser("customize", help="validate (and optionally apply) a /buddy customize patch")
    cust.add_argument("--issue-body-file", required=True, help="file holding the issue body with the fenced YAML patch")
    cust.add_argument("--apply", action="store_true", help="write the accepted patch to config/bots/customizations.json")
    args = parser.parse_args(argv)
    if args.cmd == "customize":
        return run_customize(args.issue_body_file, args.apply)
    executor = FleetExecutor()
    if args.cmd == "job":
        return run_job(executor, args.slug, args.out)
    if args.cmd == "run":
        out = executor.run(args.slug, {"objective": args.objective, "input": json.loads(args.input),
                                       "action_level": args.action_level}, stamp=True)
        print(json.dumps(out, indent=2, default=str))
        return 0 if out["status"] in {"ok", "needs_input"} else 1
    slugs = sorted(executor.bots) if args.all else args.slugs
    results = [generic_smoke(executor, slug) for slug in slugs]
    mapped = [r for r in results if r["status"] != "unmapped"]
    fixtures = load_fixtures()["fixtures"]
    fixture_results = [fixture_smoke(executor, slug, fixtures[slug]) for slug in slugs if slug in fixtures]
    failed = [r for r in mapped + fixture_results if not r["passed"]]
    summary = {"ran": len(mapped), "passed": sum(r["passed"] for r in mapped),
               "fixtures_ran": len(fixture_results), "fixtures_passed": sum(r["passed"] for r in fixture_results),
               "unmapped": len(results) - len(mapped),
               "failed": [{"slug": r["slug"], "failures": r["failures"], "error": r.get("error")} for r in failed][:10]}
    print(json.dumps(summary, indent=2))
    return 0 if not failed else 1


def run_customize(body_file: str, apply: bool) -> int:
    from .customize import BOT_STORE, PatchError, apply_bot_patch, extract_from_issue, validate_bot_patch

    try:
        with open(body_file, encoding="utf-8") as handle:
            target, patch = extract_from_issue(handle.read())
        if target.startswith("file:"):
            raise PatchError(["file: targets are validated by tools/build_file_prospectus.py customize"])
        clean = apply_bot_patch(target, patch) if apply else validate_bot_patch(target, patch)
    except PatchError as exc:
        print(json.dumps({"accepted": False, "errors": exc.errors}, indent=2))
        return 1
    print(json.dumps({"accepted": True, "target": target, "fields": clean, "applied": apply,
                      "store": str(BOT_STORE.relative_to(BOT_STORE.parents[2]))}, indent=2))
    return 0


def run_job(executor: FleetExecutor, slug: str, out_path: str | None) -> int:
    """Entry point of the 'Run with Buddy' workflow. Offline, sandbox-only."""
    if slug not in executor.bots:
        print(json.dumps({"status": "unknown_bot", "bot": slug}))
        return 2
    manifest = executor.manifest(slug)
    policy = manifest.get("run_policy", "spec_only")
    record: dict = {"schema": "dreamco.fleet_runtime.job_evidence.v1", "bot": slug, "run_policy": policy,
                    "engine": manifest["engine"], "live_external_action_taken": False}
    if manifest.get("enabled") is False:
        policy = record["run_policy"] = "disabled"
    if policy != "allowed":
        record["status"] = "refused"
        record["reason"] = {"blocked_money": "money bots are never triggerable from Buddy",
                            "blocked_destructive": "delete/destructive bots are never triggerable from Buddy",
                            "spec_only": "no shared engine fits this bot yet",
                            "disabled": "disabled by an accepted customization"}[policy]
    else:
        generic = generic_smoke(executor, slug)
        fixture = load_fixtures()["fixtures"].get(slug)
        fx = fixture_smoke(executor, slug, fixture) if fixture else None
        record["generic_smoke"] = {"passed": generic["passed"], "failures": generic["failures"]}
        record["fixture_smoke"] = None if fx is None else {"passed": fx["passed"], "failures": fx["failures"],
                                                          "origin": fixture.get("origin", "hand_written")}
        record["status"] = "passed" if generic["passed"] and (fx is None or fx["passed"]) else "failed"
    text = json.dumps(record, indent=2, sort_keys=True)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    print(text)
    return {"passed": 0, "refused": 3}.get(record["status"], 1)


if __name__ == "__main__":
    sys.exit(main())
