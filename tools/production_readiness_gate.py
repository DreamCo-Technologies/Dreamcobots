#!/usr/bin/env python3
"""Evidence-first DreamCo production readiness gate.

This tool deliberately refuses to infer runtime capability from documentation alone.
It inventories evidence-bearing repository assets and emits a machine-readable report.
It never marks a capability verified merely because a design document exists.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/production-readiness-contract.json"
OUT = ROOT / "data/production-readiness-report.json"
MD_OUT = ROOT / "reports/PRODUCTION_READINESS_REPORT.md"

def exists_any(patterns: list[str]) -> list[str]:
    found=[]
    for p in patterns:
        if any(ROOT.glob(p)):
            found.append(p)
    return found

def git_sha() -> str:
    try:
        return subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"

def read(path: str) -> str:
    file_path = ROOT / path
    if not file_path.exists():
        return ""
    return file_path.read_text(encoding="utf-8", errors="replace")

def file_exists(path: str) -> bool:
    return (ROOT / path).exists()

def package_json() -> dict:
    package_path = ROOT / "package.json"
    if not package_path.exists():
        return {}
    return json.loads(package_path.read_text())

def check_runtime_contracts() -> list[dict]:
    env_example = read(".env.example")
    gitignore = read(".gitignore")
    package = package_json()
    scripts = package.get("scripts", {})
    vercel = read("vercel.json")
    server_index = read("server/index.ts")
    webhook = read("server/webhookHandlers.ts")
    stripe = read("server/stripeClient.ts")
    openai_config = read("server/openaiConfig.ts")
    observability = read("server/observability.ts")
    master_plan = read("docs/PRODUCTION_READINESS_MASTER_PLAN.md")
    cost_policy = read("docs/DEPLOYMENT_COST_POLICY.md")

    checks = [
        {
            "id": "env_database_url_documented",
            "label": "DATABASE_URL is documented for production Postgres",
            "status": "pass" if "DATABASE_URL=" in env_example else "fail",
            "evidence": [".env.example"],
            "release_blocker": True,
        },
        {
            "id": "stripe_live_keys_documented",
            "label": "Stripe live secret and publishable keys are documented",
            "status": "pass" if "STRIPE_LIVE_SECRET_KEY=" in env_example and "STRIPE_LIVE_PK=" in env_example else "fail",
            "evidence": [".env.example"],
            "release_blocker": True,
        },
        {
            "id": "stripe_webhook_secret_documented",
            "label": "Stripe webhook secret is documented and enforced",
            "status": "pass" if "STRIPE_WEBHOOK_SECRET=" in env_example and "constructEvent" in webhook else "fail",
            "evidence": [".env.example", "server/webhookHandlers.ts"],
            "release_blocker": True,
        },
        {
            "id": "stripe_aliases_supported",
            "label": "Stripe supports deployment-friendly and live-key aliases",
            "status": "pass" if "STRIPE_SECRET_KEY" in stripe and "STRIPE_LIVE_SECRET_KEY" in stripe and "STRIPE_PUBLISHABLE_KEY" in stripe and "STRIPE_LIVE_PK" in stripe else "fail",
            "evidence": ["server/stripeClient.ts"],
            "release_blocker": True,
        },
        {
            "id": "openai_aliases_supported",
            "label": "OpenAI provider accepts AI_INTEGRATIONS_OPENAI_API_KEY and OPENAI_API_KEY",
            "status": "pass" if "AI_INTEGRATIONS_OPENAI_API_KEY" in openai_config and "OPENAI_API_KEY" in openai_config else "fail",
            "evidence": ["server/openaiConfig.ts"],
            "release_blocker": False,
        },
        {
            "id": "health_endpoint_reports_runtime",
            "label": "Health endpoint reports database and Stripe configuration",
            "status": "pass" if "/api/health" in server_index and "databaseConfigured" in server_index and "stripeConfigured" in server_index else "fail",
            "evidence": ["server/index.ts"],
            "release_blocker": True,
        },
        {
            "id": "readiness_endpoint_reports_runtime",
            "label": "Readiness endpoint exposes production dependency status",
            "status": "pass" if "/api/ready" in server_index and "productionReadinessSnapshot" in observability else "fail",
            "evidence": ["server/index.ts", "server/observability.ts"],
            "release_blocker": True,
        },
        {
            "id": "structured_request_observability",
            "label": "API requests emit request IDs and structured logs",
            "status": "pass" if "x-request-id" in observability and "api_request" in observability else "fail",
            "evidence": ["server/observability.ts"],
            "release_blocker": True,
        },
        {
            "id": "pages_marked_static",
            "label": "GitHub/Vercel static site boundary is explicit",
            "status": "pass" if '"outputDirectory": "website"' in vercel and "GitHub Pages" in cost_policy else "warn",
            "evidence": ["vercel.json", "docs/DEPLOYMENT_COST_POLICY.md"],
            "release_blocker": False,
        },
        {
            "id": "required_scripts_exist",
            "label": "Build, typecheck, local app, Pages, and readiness scripts exist",
            "status": "pass" if all(name in scripts for name in ["build", "check", "buddy:laptop:check", "buddy:site:check", "production:readiness"]) else "fail",
            "evidence": ["package.json"],
            "release_blocker": True,
        },
        {
            "id": "secret_files_ignored",
            "label": "Local secret files are ignored while examples stay committable",
            "status": "pass" if ".env" in gitignore and "!.env.example" in gitignore else "fail",
            "evidence": [".gitignore"],
            "release_blocker": True,
        },
        {
            "id": "release_rule_documented",
            "label": "Production certification requires executable evidence",
            "status": "pass" if "Documentation alone is not proof" in master_plan else "fail",
            "evidence": ["docs/PRODUCTION_READINESS_MASTER_PLAN.md"],
            "release_blocker": False,
        },
    ]

    environment_required = [
        "DATABASE_URL",
        "STRIPE_WEBHOOK_SECRET",
    ]
    environment_any_of = {
        "stripe_secret_key": ["STRIPE_SECRET_KEY", "STRIPE_LIVE_SECRET_KEY"],
        "stripe_publishable_key": ["STRIPE_PUBLISHABLE_KEY", "STRIPE_LIVE_PK"],
        "openai_key": ["AI_INTEGRATIONS_OPENAI_API_KEY", "OPENAI_API_KEY", "OPENAI_ADMIN_KEY"],
    }
    missing_required = [name for name in environment_required if not os.environ.get(name)]
    missing_any_of = {
        key: options
        for key, options in environment_any_of.items()
        if not any(os.environ.get(option) for option in options)
    }
    checks.append({
        "id": "live_environment_configured",
        "label": "Current runner has live production environment variables",
        "status": "pass" if not missing_required and not missing_any_of else "external_config_required",
        "evidence": [],
        "release_blocker": False,
        "missing_required": missing_required,
        "missing_any_of": missing_any_of,
        "note": "CI and local scans do not prove customer readiness until deployment secrets are configured in the production host.",
    })
    return checks

def summarize_readiness(areas: list[dict], runtime_checks: list[dict]) -> dict:
    """Classify certification from evidence states, never from file presence alone."""
    critical_ids = {"buddy_orchestration", "benchmark_framework", "security", "deployment", "observability"}
    blocking_unknowns = [
        area["id"] for area in areas
        if area.get("status") == "unknown" and area.get("id") in critical_ids
    ]
    incomplete_areas = [
        area["id"] for area in areas if area.get("status") != "verified"
    ]
    blocking_runtime = [
        check["id"] for check in runtime_checks
        if check.get("status") == "fail" and check.get("release_blocker")
    ]
    external_config = [
        check["id"] for check in runtime_checks
        if check.get("status") == "external_config_required"
    ]
    production_ready = not blocking_unknowns and not incomplete_areas and not blocking_runtime and not external_config
    if blocking_unknowns or blocking_runtime:
        release_status = "blocked"
    elif incomplete_areas:
        release_status = "evidence_incomplete"
    elif external_config:
        release_status = "external_config_required"
    else:
        release_status = "production_ready"
    blockers = (
        [f"critical_unknown:{item}" for item in blocking_unknowns]
        + [f"incomplete_evidence:{item}" for item in incomplete_areas]
        + [f"runtime_check_failed:{item}" for item in blocking_runtime]
        + [f"external_configuration_missing:{item}" for item in external_config]
    )
    return {
        "release_status": release_status,
        "production_ready": production_ready,
        "blocking_unknowns": blocking_unknowns,
        "incomplete_areas": incomplete_areas,
        "blocking_runtime_checks": blocking_runtime,
        "external_config_required": external_config,
        "certification_blockers": blockers,
    }


def should_fail_gate(report: dict, *, strict: bool, certification: bool) -> bool:
    if report.get("blocking_unknowns") or report.get("blocking_runtime_checks"):
        return True
    return certification and not report.get("production_ready", False)


def write_markdown(report: dict) -> None:
    counts: dict[str, int] = {}
    for check in report["runtime_checks"]:
        counts[check["status"]] = counts.get(check["status"], 0) + 1
    lines = [
        "# Production Readiness Report",
        "",
        f"- Commit: `{report['commit']}`",
        f"- Generated: `{report['generated_at']}`",
        f"- Release status: `{report['release_status']}`",
        f"- Runtime checks: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
        "",
        "## Runtime Checks",
        "",
        "| Check | Status | Evidence |",
        "|---|---:|---|",
    ]
    for check in report["runtime_checks"]:
        evidence = ", ".join(f"`{item}`" for item in check.get("evidence", [])) or "runtime env"
        lines.append(f"| {check['label']} | `{check['status']}` | {evidence} |")
    lines.extend([
        "",
        "## Certification Note",
        "",
        report["note"],
        "",
        "External production services still require live smoke tests on the actual deployment host before customers use the platform.",
        "",
    ])
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Fail on critical unknowns or release-blocking runtime failures (code gate).")
    parser.add_argument("--certification", action="store_true", help="Fail unless every area is evidence-verified and all runtime/external configuration gates pass.")
    args = parser.parse_args()
    contract=json.loads(CONTRACT.read_text())
    reports=[]
    common={
        "buddy_orchestration":["buddy_os/**","tools/*buddy*","tests/*buddy*"],
        "benchmark_framework":["docs/*BENCHMARK*","tools/*benchmark*","tests/*benchmark*"],
        "capability_genome":["*capability*","config/*capability*","tests/*capability*"],
        "model_research":["docs/*MODEL*","tools/*model*","config/*model*"],
        "teacher_model":["*teacher*","docs/*DISTILL*","tools/*distill*"],
        "experiment_engine":["*experiment*","tools/*experiment*","tests/*experiment*"],
        "ablation":["*ablation*","tools/*ablation*","tests/*ablation*"],
        "distillation":["*distill*","tools/*distill*","tests/*distill*"],
        "free_first":["*resource*","*budget*","tools/*resource*","tests/*resource*"],
        "resource_optimization":["*vram*","*ram*","*resource*","tools/*resource*"],
        "regression":["tests/**",".github/workflows/**"],
        "security":["SECURITY.md",".github/workflows/**","*license*","*security*"],
        "actions":["client/**","tests/actions*",".github/workflows/actions*"],
        "daily_scan":[".github/workflows/*daily*",".github/workflows/*scan*","tools/*scan*"],
        "source_ingestion":["*source*","*ingest*","tools/*source*","tools/*ingest*"],
        "superbot":["*superbot*","*module*","tools/*fleet*","tests/*fleet*"],
        "deployment":["app.yaml","cloudbuild.yaml","Dockerfile*","firebase.json","vercel.json",".github/workflows/*deploy*"],
        "observability":["*observability*","server/*observability*","tests/*observability*","*telemetry*","*tracing*","tools/*observ*"],
        "cost_accounting":["*cost*","*billing*","*usage*","tools/*cost*","tools/*usage*"]
    }
    for area in contract["areas"]:
        found=exists_any(common.get(area["id"],[]))
        status="partial" if found else "unknown"
        reports.append({"id":area["id"],"label":area["label"],"status":status,"repository_evidence":found,"required_evidence":area["required"]})
    runtime_checks = check_runtime_contracts()
    readiness = summarize_readiness(reports, runtime_checks)
    report={"schema_version":3,"generated_at":datetime.now(timezone.utc).isoformat(),"commit":git_sha(),"policy":"evidence-first","areas":reports,"runtime_checks":runtime_checks,**readiness,"note":"Repository file presence is inventory only. Production certification requires every area to be evidence-verified, runtime checks to pass, and external production configuration to be confirmed. This report is not a claim of production certification unless production_ready is true."}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    write_markdown(report)
    print(json.dumps(report,indent=2))
    if should_fail_gate(report, strict=args.strict, certification=args.certification):
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
