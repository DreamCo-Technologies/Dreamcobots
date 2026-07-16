#!/usr/bin/env python3
"""Generate Google Cloud readiness guidance for Buddy and DreamCo."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "reports" / "google_cloud_readiness.json"
OUTPUT_MD = ROOT / "reports" / "GOOGLE_CLOUD_READINESS.md"

REQUIRED_APIS = [
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "iamcredentials.googleapis.com",
    "secretmanager.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "cloudscheduler.googleapis.com",
    "pubsub.googleapis.com",
    "firestore.googleapis.com",
    "storage.googleapis.com",
]

GITHUB_SECRETS = [
    "GCP_PROJECT_ID",
    "GCP_WORKLOAD_IDENTITY_PROVIDER",
    "GCP_SERVICE_ACCOUNT",
    "GCP_REGION",
]

DEPLOYMENT_TARGETS = [
    {
        "id": "cloud_run",
        "label": "Cloud Run",
        "use": "Host Buddy, dashboards, API services, webhook receivers, and client apps as containers.",
    },
    {
        "id": "artifact_registry",
        "label": "Artifact Registry",
        "use": "Store built DreamCo containers before Cloud Run deployment.",
    },
    {
        "id": "secret_manager",
        "label": "Secret Manager",
        "use": "Store Stripe, email, webhook, AI provider, and database secrets outside the repository.",
    },
    {
        "id": "cloud_build",
        "label": "Cloud Build",
        "use": "Build containers from GitHub and prepare deployable artifacts.",
    },
    {
        "id": "workload_identity_federation",
        "label": "Workload Identity Federation",
        "use": "Let GitHub Actions deploy without storing long-lived Google service account keys.",
    },
    {
        "id": "cloud_scheduler",
        "label": "Cloud Scheduler",
        "use": "Trigger supervised recurring jobs for scans, reports, and sandbox tests.",
    },
    {
        "id": "pubsub",
        "label": "Pub/Sub",
        "use": "Queue bot jobs, webhook events, report refreshes, and approval-gated actions.",
    },
    {
        "id": "firestore",
        "label": "Firestore",
        "use": "Store dashboard state, bot run records, approval packets, and client-facing metadata.",
    },
    {
        "id": "cloud_storage",
        "label": "Cloud Storage",
        "use": "Store generated assets, reports, exports, and sandbox artifacts.",
    },
]

GUARDRAILS = [
    "Never commit Google service account keys or Stripe secrets.",
    "Prefer Workload Identity Federation over downloaded JSON keys.",
    "Keep production deploys approval-gated until tests, rollback, billing alerts, and secret checks pass.",
    "Use Secret Manager for live credentials and GitHub Secrets only for deployment identity values.",
    "Separate sandbox, staging, and production projects before taking client payments.",
    "Enable budgets and alerts before running always-on workloads.",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def gcloud_version() -> dict[str, str | bool]:
    gcloud = shutil.which("gcloud") or "/Users/mamas/google-cloud-sdk/bin/gcloud"
    cloudsdk_python = "/Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
    if not Path(gcloud).exists():
        return {"installed": False, "path": "", "version": ""}
    try:
        env = os.environ.copy()
        if Path(cloudsdk_python).exists():
            env.setdefault("CLOUDSDK_PYTHON", cloudsdk_python)
        result = subprocess.run(
            [gcloud, "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
            env=env,
        )
        first_line = result.stdout.splitlines()[0] if result.stdout else ""
        return {"installed": True, "path": gcloud, "version": first_line}
    except Exception as exc:  # pragma: no cover - host-specific diagnostics
        return {"installed": False, "path": gcloud, "version": "", "error": str(exc)}


def build_report() -> dict:
    cli = gcloud_version()
    return {
        "schema": "dreamco.google_cloud_readiness.v1",
        "generated_at": utc_now(),
        "summary": {
            "gcloud_installed": bool(cli.get("installed")),
            "deployment_targets": len(DEPLOYMENT_TARGETS),
            "required_apis": len(REQUIRED_APIS),
            "github_secrets_required": len(GITHUB_SECRETS),
            "workload_identity_recommended": True,
            "production_deploy_approval_required": True,
            "secret_values_stored_in_repo": False,
        },
        "local_cli": cli,
        "recommended_region": "us-central1",
        "required_google_apis": REQUIRED_APIS,
        "github_secrets": GITHUB_SECRETS,
        "deployment_targets": DEPLOYMENT_TARGETS,
        "setup_steps": [
            "Run gcloud auth login in a local Terminal window.",
            "Run gcloud auth application-default login for local SDK-backed development only.",
            "Create or select a Google Cloud project for DreamCo staging.",
            "Enable the required APIs listed in this report.",
            "Create Artifact Registry repositories for containers and build outputs.",
            "Create a deployer service account with least-privilege Cloud Run, Artifact Registry, Secret Manager read, and logging permissions.",
            "Connect GitHub through Workload Identity Federation, not a downloaded JSON key.",
            "Add the GitHub Secrets listed in this report.",
            "Deploy the first service to Cloud Run from the google-cloud-run-deploy workflow.",
            "Enable budgets, alerts, logs, uptime checks, and rollback before production traffic.",
        ],
        "guardrails": GUARDRAILS,
    }


def write_markdown(report: dict) -> None:
    summary = report["summary"]
    lines = [
        "# Google Cloud Readiness",
        "",
        f"- gcloud installed: {summary['gcloud_installed']}",
        f"- Deployment targets: {summary['deployment_targets']}",
        f"- Required APIs: {summary['required_apis']}",
        f"- GitHub secrets required: {summary['github_secrets_required']}",
        f"- Workload Identity recommended: {summary['workload_identity_recommended']}",
        f"- Production deploy approval required: {summary['production_deploy_approval_required']}",
        "",
        "## Required APIs",
        "",
    ]
    lines.extend(f"- {api}" for api in report["required_google_apis"])
    lines.extend(["", "## GitHub Secrets", ""])
    lines.extend(f"- {secret}" for secret in report["github_secrets"])
    lines.extend(["", "## Guardrails", ""])
    lines.extend(f"- {guardrail}" for guardrail in report["guardrails"])
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("Google Cloud readiness report missing; run the generator")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        existing["local_cli"] = report["local_cli"]
        if json.dumps(existing, indent=2, sort_keys=True) + "\n" != rendered:
            raise SystemExit("Google Cloud readiness report stale; run the generator")
        return 0

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    write_markdown(report)
    print(
        "google_cloud_ready={ready} targets={targets} apis={apis}".format(
            ready=report["summary"]["gcloud_installed"],
            targets=report["summary"]["deployment_targets"],
            apis=report["summary"]["required_apis"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
