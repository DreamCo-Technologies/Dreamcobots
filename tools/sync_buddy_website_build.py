#!/usr/bin/env python3
"""Sync Buddy generated reports into the static website build."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WEBSITE_DATA = ROOT / "website" / "data" / "buddy-site-status.json"
WEBSITE_REPORT = ROOT / "reports" / "BUDDY_WEBSITE_BUILD_SYNC.md"

NATIVE_COVERAGE = ROOT / "config" / "generated" / "buddy_native_bot_coverage.json"
BOT_SPRINT = ROOT / "config" / "generated" / "buddy_bot_completion_sprint.json"
API_ROUTER = ROOT / "config" / "generated" / "buddy_professional_api_router.json"
FREE_MODELS = ROOT / "config" / "generated" / "buddy_free_model_task_library.json"
GIT_RECOVERY = ROOT / "config" / "generated" / "buddy_git_recovery_audit.json"
CREATIVE_STUDIO = ROOT / "config" / "generated" / "buddy_multimodal_studio.json"
INNOVATION_ENGINE = ROOT / "config" / "generated" / "buddy_innovation_engine.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_payload() -> dict[str, Any]:
    native = read_json(NATIVE_COVERAGE)
    sprint = read_json(BOT_SPRINT)
    router = read_json(API_ROUTER)
    free = read_json(FREE_MODELS)
    recovery = read_json(GIT_RECOVERY)
    creative_studio = read_json(CREATIVE_STUDIO)
    innovation_engine = read_json(INNOVATION_ENGINE)

    native_summary = native.get("summary", {})
    sprint_summary = sprint.get("summary", {})
    router_routes = router.get("routes", [])
    free_models = free.get("models", [])
    recovery_summary = recovery.get("summary", {})
    queue = sprint.get("completion_queue", [])

    total_product = sprint_summary.get("product_bot_files", native_summary.get("python_bot_agent_files", 0))
    ready = sprint_summary.get("product_native_runnable_candidates", native_summary.get("native_runnable_candidates", 0))
    partial = sprint_summary.get("product_partial_implementations", native_summary.get("partial_native_implementations", 0))
    core = sprint_summary.get("product_need_core_runtime", native_summary.get("needs_native_completion", 0))
    completion_queue = sprint_summary.get("product_completion_queue", partial + core)
    readiness_pct = round((ready / total_product) * 100, 1) if total_product else 0

    return {
        "schema": "dreamco.buddy_website_build_status.v1",
        "generated_at": utc_now(),
        "site_build": {
            "source": "website/",
            "style": "static_empire_os",
            "sync_rule": "Website reads this file so Buddy report updates show up on the go-live static site.",
        },
        "summary": {
            "product_bot_files": total_product,
            "native_runnable_candidates": ready,
            "partial_product_bots": partial,
            "need_core_runtime": core,
            "completion_queue": completion_queue,
            "readiness_percent": readiness_pct,
            "native_task_routes": native_summary.get("task_route_count", 0),
            "free_model_resources": len(free_models),
            "professional_api_routes": len(router_routes),
            "git_recovery_refs_seen": recovery_summary.get("total_branches_seen", 0),
            "git_repositories_scanned": recovery_summary.get("git_repositories_found", 0),
            "creative_studio_tracks": len(creative_studio.get("project_types", [])),
            "innovation_design_lenses": len(innovation_engine.get("design_lenses", [])),
            "innovation_modes": len(innovation_engine.get("modes", {})),
        },
        "top_completion_queue": queue[:12],
        "native_routes": native.get("task_routes", [])[:16],
        "api_router_modes": ["free_first", "local_only", "premium_optional", "quality_first"],
        "guardrails": [
            "Native DreamCo bot code is tried first.",
            "Free/local model resources are optional backup.",
            "Paid, live, money, account, outreach, deploy, and personal-data actions require approval.",
            "The website can show readiness and queue data without claiming unfinished bots are fully complete.",
            "Voice and likeness rendering requires active adult-owner consent and a configured media engine.",
        ],
    }


def write_report(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Buddy Website Build Sync",
        "",
        "The static website build now has a generated Buddy status file. Future Buddy audits can refresh the go-live site data without redesigning the pages.",
        "",
        "## Synced Metrics",
        "",
        f"- Product bot files: {summary['product_bot_files']}",
        f"- Native runnable candidates: {summary['native_runnable_candidates']}",
        f"- Partial product bots: {summary['partial_product_bots']}",
        f"- Product bots needing core runtime: {summary['need_core_runtime']}",
        f"- Completion queue: {summary['completion_queue']}",
        f"- Free model/resources: {summary['free_model_resources']}",
        f"- Professional API routes: {summary['professional_api_routes']}",
        f"- Creative Studio production tracks: {summary['creative_studio_tracks']}",
        f"- Innovation design lenses: {summary['innovation_design_lenses']}",
        f"- Innovation priority modes: {summary['innovation_modes']}",
        "",
        "## Website Files",
        "",
        "- `website/data/buddy-site-status.json`",
        "- `website/buddy-site-sync.js`",
    ]
    WEBSITE_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Buddy generated report data into website/.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        if not WEBSITE_DATA.exists() or not WEBSITE_REPORT.exists():
            raise SystemExit("Website sync files are missing. Run without --check.")
        payload = read_json(WEBSITE_DATA)
        assert payload["summary"]["product_bot_files"] >= 1
        print(json.dumps({"ok": True, **payload["summary"]}, indent=2, sort_keys=True))
        return 0

    WEBSITE_DATA.parent.mkdir(parents=True, exist_ok=True)
    WEBSITE_REPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = load_payload()
    WEBSITE_DATA.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(payload)
    print(json.dumps({"ok": True, **payload["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
