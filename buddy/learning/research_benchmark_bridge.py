"""Bridge research findings to benchmark candidates and verified learning points."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from buddy.frontier.learning_orchestrator import EvaluationFailure, propose_learning_jobs
from buddy.learning.benchmark_learning_adapter import benchmark_to_event


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "config" / "buddy-research-benchmark-token-policy.json"
EVIDENCE_TYPES = {"real_robot", "simulation", "benchmark_only", "preprint", "official_docs", "speculation", "mixed"}


class ResearchBridgeError(ValueError):
    """Raised when a research item or learning reward lacks trustworthy evidence."""


def _policy() -> dict[str, Any]:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def research_item_to_benchmark_candidate(item: dict[str, Any]) -> dict[str, Any]:
    """Turn one cited discovery into a reviewed benchmark proposal, never a score."""
    required = ("title", "source_url", "source_date", "huggingface_category", "task_name",
                "evidence_type", "demonstrated_capability", "limitations", "proposed_test")
    missing = [name for name in required if not item.get(name)]
    if missing:
        raise ResearchBridgeError("Research item is missing required evidence fields: " + ", ".join(missing))
    source = urlsplit(str(item["source_url"]))
    if source.scheme != "https" or not source.hostname or source.username or source.password:
        raise ResearchBridgeError("Research source must be a credential-free HTTPS URL.")
    evidence_type = str(item["evidence_type"])
    if evidence_type not in EVIDENCE_TYPES:
        raise ResearchBridgeError("Choose an evidence type that distinguishes hardware, simulation, benchmark, preprint, docs, or speculation.")
    category = str(item["huggingface_category"]).strip()
    task = str(item["task_name"]).strip()
    if len(category) > 120 or len(task) > 160:
        raise ResearchBridgeError("Hugging Face category and task labels exceed supported limits.")
    signature = "\n".join((str(item["source_url"]), str(item["source_date"]), category, task,
                           str(item["title"]))).encode("utf-8")
    candidate_id = "hf-research-" + hashlib.sha256(signature).hexdigest()[:20]
    policy = _policy()
    mappings = policy["category_benchmark_domains"]
    domains = mappings.get(category, ["task_specific_benchmark"])
    return {
        "schema": "dreamco.research_benchmark_candidate.v1",
        "candidate_id": candidate_id,
        "finding": {"title": str(item["title"])[:300], "source_url": str(item["source_url"]),
                    "source_date": str(item["source_date"]), "huggingface_category": category,
                    "task_name": task, "evidence_type": evidence_type,
                    "demonstrated_capability": str(item["demonstrated_capability"])[:1_000],
                    "limitations": str(item["limitations"])[:2_000]},
        "benchmark": {"candidate_domains": domains, "proposed_test": str(item["proposed_test"])[:2_000],
                      "existing_benchmark_id": item.get("existing_benchmark_id"),
                      "task_fixture_status": "not_created", "adapter_status": "not_verified",
                      "holdout_status": "not_created", "run_status": "not_run"},
        "source_review": {"license_or_terms_reviewed": bool(item.get("license_or_terms_reviewed", False)),
                           "dataset_rights_reviewed": bool(item.get("dataset_rights_reviewed", False)),
                           "content_is_training_data": False},
        "status": "needs_fixture_and_adapter_review",
        "benchmark_score": None,
        "mastery_claimed": False,
        "training_started": False,
        "points_awarded": 0,
    }


def research_benchmark_failure_to_learning_jobs(result: dict[str, Any]) -> dict[str, Any]:
    """Feed a measured benchmark failure to the repository's diagnostic job planner."""
    if result.get("passed") is not False or not result.get("verified"):
        raise ResearchBridgeError("Only verified benchmark failures create diagnostic learning jobs.")
    capability = str(result.get("capability", "")).strip()
    failure_mode = str(result.get("failure_mode", "")).strip()
    evaluation_id = str(result.get("run_id") or result.get("benchmark_id") or "").strip()
    if not capability or not failure_mode or not evaluation_id:
        raise ResearchBridgeError("Verified failure needs capability, failure mode, and run/benchmark ID.")
    refs = result.get("evidence_refs", [])
    if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
        raise ResearchBridgeError("Evidence references must be a list of strings.")
    failure = EvaluationFailure(evaluation_id=evaluation_id, capability=capability, failure_mode=failure_mode,
                                baseline_score=float(result.get("baseline_score", 0.0)),
                                current_score=float(result.get("current_score", 0.0)),
                                external_assistance_used=bool(result.get("external_assistance", False)),
                                evidence_refs=tuple(refs), system_area=str(result.get("system_area", "")))
    jobs = propose_learning_jobs([failure])
    return {
        "schema": "dreamco.research_benchmark_failure_jobs.v1",
        "learning_event": benchmark_to_event(result),
        "jobs": [{"capability": job.capability, "action": job.action.value,
                  "source_failures": job.source_failures, "regression_tests": job.regression_tests,
                  "held_out_required": job.held_out_required, "status": job.status,
                  "proposed_steps": job.proposed_steps, "execution_started": job.execution_started,
                  "source_code_copied": job.source_code_copied, "model_weights_changed": job.model_weights_changed}
                 for job in jobs],
        "training_started": False,
        "source_executed": False,
        "mastery_claimed": False,
    }


def learning_points_award(result: dict[str, Any], *, user_id: str,
                          policy: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create an idempotent non-cash achievement event after verified mastery only."""
    active_policy = policy or _policy()
    point_policy = active_policy["learning_points"]
    if not user_id.strip():
        raise ResearchBridgeError("A user scope is required for a learning-point award.")
    if not point_policy.get("requires_owner_approval") or not result.get("owner_approved"):
        raise ResearchBridgeError("Explicit owner approval is required before awarding points.")
    benchmark_id = str(result.get("benchmark_id", "")).strip()
    benchmark_version = str(result.get("benchmark_version", "")).strip()
    capability_id = str(result.get("capability_id", "")).strip()
    if not all((benchmark_id, benchmark_version, capability_id)):
        raise ResearchBridgeError("A benchmark ID, immutable version, and capability ID are required.")
    runs = result.get("runs")
    if not isinstance(runs, list) or len(runs) < int(point_policy["minimum_repeated_runs"]):
        raise ResearchBridgeError("Learning points require the configured number of repeated verified runs.")
    required_passes = set(point_policy["every_run_must_pass"])
    run_ids = []
    for run in runs:
        if not isinstance(run, dict) or not run.get("run_id") or not run.get("verified"):
            raise ResearchBridgeError("Every repeated run must be individually verified and identified.")
        if run.get("benchmark_version") != benchmark_version:
            raise ResearchBridgeError("Repeated runs must use the same immutable benchmark version.")
        flags = {
            "verified": bool(run.get("verified")),
            "task_score_floor": bool(run.get("task_score_floor_passed")),
            "hidden_holdout": bool(run.get("hidden_holdout_passed")),
            "regression": bool(run.get("regression_passed")),
            "safety": bool(run.get("safety_passed")),
            "native_success": bool(run.get("native_success")) and not bool(run.get("external_assistance")),
        }
        if not all(flags.get(name, False) for name in required_passes):
            raise ResearchBridgeError("A required task, holdout, regression, safety, or native-success gate failed.")
        run_ids.append(str(run["run_id"]))
    if len(set(run_ids)) != len(run_ids):
        raise ResearchBridgeError("Repeated run IDs must be distinct to prevent reward replay.")
    award_key = hashlib.sha256(f"{user_id}:{capability_id}:{benchmark_id}:{benchmark_version}".encode()).hexdigest()
    event_id = "learning-award-" + award_key[:24]
    return {
        "schema": "dreamco.learning_points_award.v1",
        "event_id": event_id,
        "idempotency_key": award_key,
        "user_id": user_id,
        "capability_id": capability_id,
        "benchmark_id": benchmark_id,
        "benchmark_version": benchmark_version,
        "verified_run_ids": run_ids,
        "points": int(point_policy["mastery_award_points"]),
        "unit": point_policy["unit_name"],
        "transferable": bool(point_policy["transferable"]),
        "cash_value": int(point_policy["cash_value"]),
        "crypto_or_blockchain_transfer": bool(point_policy["crypto_or_blockchain_transfer"]),
        "source_finding_awarded_points": False,
        "mastery_gate_passed": True,
        "persisted_to_wallet": False,
    }


def record_learning_points_award(ledger_root: str | Path, award: dict[str, Any]) -> dict[str, Any]:
    """Persist one idempotent non-cash points event in a user-owned external ledger directory."""
    if award.get("schema") != "dreamco.learning_points_award.v1":
        raise ResearchBridgeError("Only a validated learning-points award can be recorded.")
    if award.get("transferable") is not False or award.get("cash_value") != 0 or award.get("crypto_or_blockchain_transfer") is not False:
        raise ResearchBridgeError("The learning ledger accepts non-transferable, non-cash points only.")
    user_key = hashlib.sha256(str(award.get("user_id", "")).encode("utf-8")).hexdigest()
    event_id = str(award.get("event_id", ""))
    if (not str(award.get("user_id", "")).strip()
            or not re.fullmatch(r"learning-award-[a-f0-9]{24}", event_id)
            or not re.fullmatch(r"[a-f0-9]{64}", str(award.get("idempotency_key", "")))
            or not isinstance(award.get("points"), int) or not 1 <= award["points"] <= 1_000):
        raise ResearchBridgeError("A user-scoped, idempotent learning award event is required.")
    root_path = Path(ledger_root).expanduser()
    if root_path.is_symlink():
        raise ResearchBridgeError("The user-owned learning ledger root must not be a symlink.")
    root_path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if stat.S_IMODE(root_path.stat().st_mode) & 0o077:
        raise ResearchBridgeError("Learning-points ledger directory must be private to the user account (permissions 0700).")
    user_dir = root_path / user_key
    user_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    if user_dir.is_symlink():
        raise ResearchBridgeError("The user learning ledger directory must not be a symlink.")
    if stat.S_IMODE(user_dir.stat().st_mode) & 0o077:
        raise ResearchBridgeError("User-specific learning-points records must be private (permissions 0700).")
    event_path = user_dir / f"{event_id}.json"
    payload = {**award, "persisted_to_wallet": False, "ledger_type": "user_owned_learning_points", "financial_transfer": False}
    try:
        descriptor = os.open(event_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return {"recorded": False, "duplicate": True, "event_id": event_id, "points_balance": summarize_learning_points(ledger_root, str(award["user_id"]))["balance"]}
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        event_path.unlink(missing_ok=True)
        raise
    summary = summarize_learning_points(ledger_root, str(award["user_id"]))
    return {"recorded": True, "duplicate": False, "event_id": event_id, "points_balance": summary["balance"]}


def summarize_learning_points(ledger_root: str | Path, user_id: str) -> dict[str, Any]:
    """Read a user's learning-only points ledger; crypto balances are not consulted."""
    user_key = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
    user_dir = Path(ledger_root).expanduser() / user_key
    events = []
    if user_dir.is_dir():
        for event_path in sorted(user_dir.glob("learning-award-*.json")):
            try:
                event = json.loads(event_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if event.get("user_id") == user_id and event.get("schema") == "dreamco.learning_points_award.v1" and event.get("cash_value") == 0 and event.get("transferable") is False:
                events.append(event)
    return {"user_id": user_id, "balance": sum(max(0, int(event.get("points", 0))) for event in events),
            "award_count": len(events), "unit": "learning_points", "cash_value": 0,
            "transferable": False, "financial_or_crypto_system_connected": False}
