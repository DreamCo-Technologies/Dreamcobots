#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIB = 1024 * 1024


def main() -> int:
    policy = json.loads((ROOT / "config/buddy-deployment-cost-policy.json").read_text(encoding="utf-8"))
    vercel = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    dashboard_workflow = (ROOT / ".github/workflows/dreamco-live-dashboard.yml").read_text(encoding="utf-8")
    pages_workflow = (ROOT / ".github/workflows/deploy-buddy-pages.yml").read_text(encoding="utf-8")
    website = ROOT / policy["deployment"]["public_directory"]
    errors: list[str] = []

    if vercel.get("framework") is not None:
        errors.append("Vercel must remain framework-free for this static release.")
    if vercel.get("outputDirectory") != "website":
        errors.append("Vercel must publish only website/.")
    if vercel.get("git", {}).get("deploymentEnabled") is not False:
        errors.append("Automatic Vercel Git deployments must remain disabled.")
    if any(key in vercel for key in ("crons", "functions")):
        errors.append("Vercel functions and crons are outside the zero-cost static profile.")
    if "schedule:" in dashboard_workflow or "cron:" in dashboard_workflow:
        errors.append("The dashboard workflow must not run on a paid-time schedule by default.")

    upload_count = dashboard_workflow.count("uses: actions/upload-artifact@v4")
    retention_count = dashboard_workflow.count("retention-days: 1")
    if upload_count != retention_count:
        errors.append("Every dashboard artifact must expire after one day.")
    if "  push:" in pages_workflow or "  pull_request:" in pages_workflow:
        errors.append("The GitHub Pages fallback must be manually dispatched.")
    if not (website / "_headers").is_file() or not (website / "_redirects").is_file():
        errors.append("Provider-neutral static headers and redirects are required.")
    if (website / "api").exists() or (website / "functions").exists():
        errors.append("Server code cannot be included in the static public directory.")

    site_bytes = sum(path.stat().st_size for path in website.rglob("*") if path.is_file())
    site_mib = round(site_bytes / MIB, 2)
    maximum_mib = int(policy["cost_controls"]["maximum_public_site_mib"])
    if site_bytes > maximum_mib * MIB:
        errors.append(f"Static site is {site_mib} MiB; maximum is {maximum_mib} MiB.")

    report = {
        "ok": not errors,
        "monthly_hosting_target_usd": policy["monthly_hosting_target_usd"],
        "profile": policy["default_mode"],
        "public_site_mib": site_mib,
        "public_files": sum(1 for path in website.rglob("*") if path.is_file()),
        "automatic_vercel_deployments": vercel["git"]["deploymentEnabled"],
        "scheduled_dashboard_runs": False,
        "artifact_retention_days": policy["cost_controls"]["github_artifact_retention_days"],
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
