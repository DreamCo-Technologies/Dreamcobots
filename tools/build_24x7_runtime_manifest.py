#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "buddy-24x7-system-runtime-program.json"
OUT = ROOT / "config" / "generated" / "buddy-24x7-runtime-manifest.json"

KNOWN_PROGRAMS = {
    "buddy-core": {"runtime_class": "always_on_service", "stop_condition": "until_stopped"},
    "bot-fleet": {"runtime_class": "event_driven_worker", "stop_condition": "until_task_complete"},
    "builder-bots": {"runtime_class": "event_driven_worker", "stop_condition": "until_task_complete"},
    "benchmark-gap-builders": {"runtime_class": "event_driven_worker", "stop_condition": "until_task_complete"},
    "competitor-intel": {"runtime_class": "scheduled_worker", "stop_condition": "until_task_complete"},
    "open-source-scout": {"runtime_class": "scheduled_worker", "stop_condition": "until_task_complete"},
    "library-refresh": {"runtime_class": "scheduled_worker", "stop_condition": "until_task_complete"},
    "model-refresh": {"runtime_class": "scheduled_worker", "stop_condition": "until_task_complete"},
    "data-discovery": {"runtime_class": "scheduled_worker", "stop_condition": "until_task_complete"},
    "data-package-tests": {"runtime_class": "batch_worker", "stop_condition": "until_batch_complete"},
    "buddy-bootcamp": {"runtime_class": "interactive_session", "stop_condition": "idle_timeout"},
    "api-test-arsenal": {"runtime_class": "batch_worker", "stop_condition": "until_batch_complete"},
    "training-jobs": {"runtime_class": "manual_only", "stop_condition": "explicit_user_stop_or_completion"},
    "production-health": {"runtime_class": "always_on_service", "stop_condition": "until_stopped"},
}


def main() -> int:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    defaults = policy["duration_controls"]
    services = []
    for name, spec in KNOWN_PROGRAMS.items():
        services.append({
            "id": name,
            "runtime_class": spec["runtime_class"],
            "start_condition": "system_start_or_matching_event",
            "stop_condition": spec["stop_condition"],
            "timeout": "bounded_by_task_or_config; always_on services use external supervisor health policy",
            "retry_policy": "bounded_exponential_backoff_then_dead_letter",
            "checkpoint_policy": "required_for_long_running_or_resumable_tasks",
            "resource_budget": "per-task/per-worker configured limit",
            "approval_policy": "external/paid/destructive actions remain gated",
            "status": "runtime_contract_defined_not_deployment_evidence"
        })

    payload = {
        "schema": "dreamco.buddy_24x7_runtime_manifest.v1",
        "source": str(POLICY.relative_to(ROOT)),
        "global_stop_supported": defaults.get("global_stop", False),
        "pause_resume_supported": defaults.get("pause_resume", False),
        "fleet_availability_rule": policy.get("fleet_availability_rule"),
        "services": services,
        "service_count": len(services),
        "truth_boundary": "This manifest defines intended runtime behavior. It does not prove an always-on host is deployed or that every service is currently running."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "services": len(services), "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
