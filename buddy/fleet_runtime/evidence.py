"""Evidence records for fleet runs.

A run evidence record documents what happened in one execution. It is
deterministic (no wall-clock time unless ``stamp=True``) so CI can diff it.
It is NOT promotion evidence: VERIFIED/PRODUCTION need committed records under
evidence/fleet-runtime/<slug>.json carrying the release_readiness.yaml fields.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

SCHEMA = "dreamco.fleet_runtime.run_evidence.v1"

# release_readiness.yaml required_evidence, mirrored for promotion checks.
PROMOTION_FIELDS = {
    "VERIFIED": ("test_reference", "security_result", "build_result", "runtime_result"),
    "PRODUCTION": ("approval_reference", "deployment_reference", "health_result", "observability_reference"),
}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def run_record(*, manifest: dict[str, Any], task: dict[str, Any], status: str, mode: str,
               permission: dict[str, Any], guardrails: dict[str, Any], result: Any,
               error: dict[str, Any] | None = None, stamp: bool = False) -> dict[str, Any]:
    record = {
        "schema": SCHEMA,
        "bot": manifest.get("slug"),
        "division": manifest.get("division"),
        "engine": manifest.get("engine"),
        "status": status,
        "mode": mode,
        "permission": permission,
        "guardrails": guardrails,
        "task_digest": digest(task),
        "output_digest": digest(result),
        "manifest_digest": digest(manifest),
        "live_external_action_taken": False,
        "proves": "one execution of the shared runtime; not capability quality, not production readiness",
    }
    if error:
        record["error"] = error
    record["run_id"] = digest(record)[:16]
    if stamp:
        record["recorded_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return record


def promotion_gaps(record: dict[str, Any] | None, state: str) -> list[str]:
    """Return missing release_readiness fields for promoting to ``state``."""
    needed = list(PROMOTION_FIELDS.get("VERIFIED", ()))
    if state == "PRODUCTION":
        needed += list(PROMOTION_FIELDS["PRODUCTION"])
    if not record:
        return needed
    return [field for field in needed if not record.get(field)]
