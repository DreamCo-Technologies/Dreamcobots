"""CLI: python -m buddy.fleet_runtime run <slug> --objective "..." [--input JSON]."""
from __future__ import annotations

import argparse
import json
import sys

from .executor import FleetExecutor
from .smoke import generic_smoke


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
    args = parser.parse_args(argv)
    executor = FleetExecutor()
    if args.cmd == "run":
        out = executor.run(args.slug, {"objective": args.objective, "input": json.loads(args.input),
                                       "action_level": args.action_level}, stamp=True)
        print(json.dumps(out, indent=2, default=str))
        return 0 if out["status"] in {"ok", "needs_input"} else 1
    slugs = sorted(executor.bots) if args.all else args.slugs
    results = [generic_smoke(executor, slug) for slug in slugs]
    mapped = [r for r in results if r["status"] != "unmapped"]
    summary = {"ran": len(mapped), "passed": sum(r["passed"] for r in mapped),
               "unmapped": len(results) - len(mapped), "failed": [{"slug": r["slug"], "failures": r["failures"], "error": r.get("error")} for r in mapped if not r["passed"]][:10]}
    print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] == summary["ran"] else 1


if __name__ == "__main__":
    sys.exit(main())
