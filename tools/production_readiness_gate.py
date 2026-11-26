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
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/production-readiness-contract.json"
OUT = ROOT / "data/production-readiness-report.json"
MD_OUT = ROOT / "reports/PRODUCTION_READINESS_REPORT.md"
AREA_EVIDENCE = ROOT / "governance/production-readiness-area-evidence.json"
AREA_EVIDENCE_SCHEMA = "dreamco.production_readiness_area_evidence.v1"

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
            "status": "pass" if all(name in scripts for name in ["build", "check", "buddy:laptop:check", "buddy:site:check", "production:readiness", "production:certification"]) else "fail",
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


def verify_github_check(repository: str, check_id: str, current_sha: str, token: str | None) -> bool:
    """Require a successful Actions run/check-run on the exact current revision."""
    if not token or not check_id.isdigit():
        return False
    endpoints = (
        f"https://api.github.com/repos/{repository}/actions/runs/{check_id}",
        f"https://api.github.com/repos/{repository}/check-runs/{check_id}",
    )
    for url in endpoints:
        request = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            return False
        except Exception:
            return False
        return (
            payload.get("head_sha") == current_sha
            and payload.get("status") == "completed"
            and payload.get("conclusion") == "success"
        )
    return False


def build_area_reports(
    contract: dict,
    evidence_manifest: dict,
    current_sha: str,
    repository: str,
    token: str | None,
    *,
    root: Path = ROOT,
    verify_check=verify_github_check,
) -> list[dict]:
    """Resolve every contract area from evidence, never from file presence alone."""
    if evidence_manifest.get("schema") != AREA_EVIDENCE_SCHEMA:
        raise ValueError("unsupported production-readiness area evidence schema")
    entries = evidence_manifest.get("areas")
    if not isinstance(entries, dict):
        raise ValueError("production-readiness area evidence must contain an areas object")
    reports = []
    check_cache: dict[tuple[str, str, str | None], bool] = {}
    for area in contract.get("areas", []):
        area_id = area["id"]
        entry = entries.get(area_id)
        refs = entry.get("evidence", []) if isinstance(entry, dict) else []
        errors = []
        verified_refs = []
        if not isinstance(entry, dict):
            errors.append("no evidence entry recorded")
        else:
            resolution_errors = entry.get("resolution_errors", [])
            if isinstance(resolution_errors, list):
                errors.extend(str(item) for item in resolution_errors if item)
            if entry.get("status") != "VERIFIED" and not resolution_errors:
                errors.append("area evidence status is not VERIFIED")
        if not isinstance(refs, list) or not refs:
            errors.append("no evidence references recorded")
        else:
            for ref in refs:
                if not isinstance(ref, dict) or not all(ref.get(key) for key in ("path", "sha", "check_id")):
                    errors.append("evidence reference is missing path, sha, or check_id")
                    continue
                relative = Path(str(ref["path"]))
                if relative.is_absolute() or ".." in relative.parts:
                    errors.append("evidence path is unsafe")
                    continue
                artifact = (root / relative).resolve()
                try:
                    artifact.relative_to(root.resolve())
                except ValueError:
                    errors.append("evidence path escapes repository root")
                    continue
                if not artifact.is_file():
                    errors.append(f"evidence artifact does not exist: {relative.as_posix()}")
                    continue
                if ref["sha"] != current_sha:
                    errors.append("evidence SHA does not match current revision")
                    continue
                check_id = str(ref["check_id"])
                if not check_id.isdigit():
                    errors.append("check_id must be a GitHub Actions run or check-run ID")
                    continue
                cache_key = (repository, check_id, token)
                if cache_key not in check_cache:
                    check_cache[cache_key] = verify_check(repository, check_id, current_sha, token)
                if not check_cache[cache_key]:
                    errors.append("linked GitHub check is not successful on the current revision")
                    continue
                verified_refs.append(ref)
        verified = (
            isinstance(entry, dict)
            and entry.get("status") == "VERIFIED"
            and isinstance(refs, list)
            and not errors
            and len(verified_refs) == len(refs)
        )
        status = "verified" if verified else ("partial" if isinstance(entry, dict) else "unknown")
        reports.append({
            "id": area_id,
            "label": area.get("label", area_id),
            "status": status,
            "evidence": verified_refs,
            "evidence_errors": errors,
            "revision": current_sha,
            "required_evidence": area.get("required", []),
        })
    return reports


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
    if report.get("blocking_unknowns") or (strict and report.get("blocking_runtime_checks")):
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
        f"- Production certified: {report.get('production_ready', False)}",
        f"- Incomplete evidence areas: {len(report.get('incomplete_areas', []))}",
        f"- Runtime checks: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
        "",
        "## Incomplete Evidence Areas",
        "",
        *[f"- `{item}`" for item in report.get("incomplete_areas", [])],
        "",
        "## Area Evidence Details",
        "",
    ]
    for area in report.get("areas", []):
        lines.append(f"### {area.get('label', area.get('id'))} — `{area.get('status')}`")
        evidence = area.get("evidence", [])
        errors = area.get("evidence_errors", [])
        if evidence:
            lines.extend(f"- Verified reference: `{item.get('path')}`" for item in evidence)
        if errors:
            lines.extend(f"- Evidence gap: {item}" for item in errors)
        if not evidence and not errors:
            lines.append("- No evidence references recorded")
        lines.append("")
    lines.extend([
        "## Certification Blockers",
        "",
        *[f"- `{item}`" for item in report.get("certification_blockers", [])],
        "",
        "## Runtime Checks",
        "",
        "| Check | Status | Evidence |",
        "|---|---:|---|",
    ])
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
    parser.add_argument("--evidence-manifest", help="Use a revision-bound evidence manifest generated for this exact commit.")
    args = parser.parse_args()
    contract=json.loads(CONTRACT.read_text())
    current_sha = git_sha()
    repository = os.getenv("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots")
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    evidence_path = Path(args.evidence_manifest or os.getenv("DREAMCO_PRODUCTION_EVIDENCE_MANIFEST", str(AREA_EVIDENCE)))
    evidence_manifest = json.loads(evidence_path.read_text()) if evidence_path.exists() else {
        "schema": AREA_EVIDENCE_SCHEMA, "areas": {}
    }
    reports = build_area_reports(contract, evidence_manifest, current_sha, repository, token)
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
    for report in reports:
        report["repository_evidence"] = exists_any(common.get(report["id"], []))
    runtime_checks = check_runtime_contracts()
    readiness = summarize_readiness(reports, runtime_checks)
    report={"schema_version":4,"generated_at":datetime.now(timezone.utc).isoformat(),"commit":current_sha,"policy":"evidence-first","areas":reports,"runtime_checks":runtime_checks,**readiness,"note":"Repository file presence is inventory only. Production certification requires every area to be evidence-verified, runtime checks to pass, and external production configuration to be confirmed. This report is not a claim of production certification unless production_ready is true."}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    write_markdown(report)
    print(json.dumps(report,indent=2))
    if should_fail_gate(report, strict=args.strict, certification=args.certification):
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
