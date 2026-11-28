"""Standard-library extensions for the DreamCo 10-pillar evidence-first loop.

All functions are offline and side-effect free unless a caller explicitly writes
an output file. They do not execute model-generated code, call providers, train
weights, open GitHub issues, or certify a buyer kit without verified evidence.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math
import re
from datetime import datetime, timezone
from typing import Any, Iterable

SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)\bsk-[A-Za-z0-9_-]{20,}\b"),
)
DRILL_FOCI = (
    "recognize the failure signal", "reconstruct the minimal reproduction",
    "identify the root cause", "separate symptoms from causes",
    "choose the safest diagnostic tool", "write a deterministic regression test",
    "define the expected output contract", "identify missing preconditions",
    "detect unsafe assumptions", "check authorization boundaries",
    "check privacy and secret handling", "design a negative test",
    "design an edge-case test", "explain the repair strategy",
    "verify the repair against the regression test", "check for unintended side effects",
    "compare before-and-after evidence", "verify idempotency",
    "verify timeout and resource limits", "plan rollback conditions",
    "write a concise incident summary", "identify remaining uncertainty",
    "route unresolved work to human review", "record reproducibility metadata",
    "teach the transferable debugging principle",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def redact(value: Any, limit: int = 1200) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()[:limit]
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def _finite(value: Any, name: str, *, minimum: float | None = None) -> float:
    number = float(value)
    if not math.isfinite(number) or (minimum is not None and number < minimum):
        raise ValueError(f"{name} must be finite and >= {minimum}")
    return number


def update_curriculum_state(
    state: dict[str, Any],
    *,
    scope_type: str,
    scope_id: str,
    pass_rate: float,
    difficulty: float | None = None,
    interval_days: int | None = None,
    evidence_split: str = "practice",
) -> dict[str, Any]:
    """Adjust one of 55 domain divisions or 65 MasterBot lanes from practice only."""
    if scope_type not in {"domain_division", "masterbot_lane"}:
        raise ValueError("scope_type must be domain_division or masterbot_lane")
    if not str(scope_id).strip():
        raise ValueError("scope_id is required")
    if evidence_split not in {"practice", "curriculum"}:
        raise ValueError("evaluation and holdout evidence cannot change curriculum state")
    rate = _finite(pass_rate, "pass_rate", minimum=0.0)
    scope_key = f"{scope_type}:{scope_id}"
    stored = state.get("scopes", {}).get(scope_key, {}) if isinstance(state, dict) else {}
    level = _finite(
        difficulty if difficulty is not None else stored.get("difficulty", 1.0),
        "difficulty", minimum=0.5,
    )
    interval = int(interval_days if interval_days is not None else stored.get("spaced_interval_days", 1))
    if rate > 1 or level > 5 or interval < 1:
        raise ValueError("pass_rate must be <= 1, difficulty <= 5, interval >= 1")
    next_level, next_interval = level, interval
    if rate >= 0.95:
        next_level = min(5.0, round(level * 1.10, 2))
        next_interval = min(30, interval * 2)
    elif rate < 0.70:
        next_level = max(0.5, round(level * 0.90, 2))
        next_interval = 1
    updated = {
        "scope_type": scope_type,
        "scope_id": str(scope_id),
        "difficulty": next_level,
        "spaced_interval_days": next_interval,
        "last_practice_pass_rate": round(rate, 4),
        "last_updated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_split": evidence_split,
        "mastery_awarded": False,
    }
    scopes = dict(state.get("scopes", {})) if isinstance(state, dict) else {}
    scopes[scope_key] = updated
    return {
        "schema": "dreamco.curriculum_state.v1",
        **updated,
        "scopes": scopes,
        "truth_boundary": "Practice scheduling is not a model certification or mastery award.",
    }


def _minhash_signature(text: str, permutations: int = 32) -> tuple[int, ...]:
    tokens = sorted(set(re.findall(r"[a-z0-9]{2,}", text.lower())))
    if not tokens:
        return tuple([0] * permutations)
    return tuple(
        min(int(hashlib.sha256(f"{seed}:{token}".encode()).hexdigest()[:16], 16) for token in tokens)
        for seed in range(permutations)
    )


def _signature_similarity(left: tuple[int, ...], right: tuple[int, ...]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    return sum(a == b for a, b in zip(left, right)) / len(left)


def distill_verified_repair(
    evidence: dict[str, Any],
    *,
    existing_signatures: Iterable[tuple[int, ...]] = (),
    similarity_threshold: float = 0.90,
) -> list[dict[str, Any]]:
    """Create 25 original rubric-backed drills from one approved, non-holdout repair."""
    required = (
        "evidence_id", "lesson_id", "division_id", "status", "human_review_status",
        "source_rights_approved", "training_use_approved", "dataset_release_approved", "pii_scrubbed", "privacy_review_status", "holdout",
        "evidence_split", "failure_summary", "root_cause_summary",
        "repair_summary", "regression_test_summary", "evidence_sha256",
    )
    missing = [key for key in required if key not in evidence]
    if missing:
        raise ValueError(f"repair evidence missing fields: {', '.join(missing)}")
    payload = {key: value for key, value in evidence.items() if key != "evidence_sha256"}
    if evidence["evidence_sha256"] != sha256_json(payload):
        raise ValueError("repair evidence SHA-256 does not match its canonical payload")
    if evidence["status"] != "VERIFIED_REPAIR" or evidence["human_review_status"] != "APPROVED":
        raise ValueError("only human-approved verified repairs can be distilled")
    if (evidence["source_rights_approved"] is not True
            or evidence["training_use_approved"] is not True
            or evidence["dataset_release_approved"] is not True
            or evidence["pii_scrubbed"] is not True
            or evidence["privacy_review_status"] != "APPROVED"):
        raise ValueError("source rights, training use, dataset release, PII scrub, and privacy review must be approved")
    if evidence["holdout"] is not False or evidence["evidence_split"] not in {"practice", "curriculum"}:
        raise ValueError("holdout or evaluation evidence is never eligible for distillation")
    summaries = {
        "failure": redact(evidence["failure_summary"]),
        "root_cause": redact(evidence["root_cause_summary"]),
        "repair": redact(evidence["repair_summary"]),
        "regression_test": redact(evidence["regression_test_summary"]),
    }
    if any(not value for value in summaries.values()):
        raise ValueError("all repair summaries must be non-empty")
    similarity_threshold = _finite(similarity_threshold, "similarity_threshold", minimum=0.0)
    if similarity_threshold > 1:
        raise ValueError("similarity_threshold must be <= 1")
    lesson_basis = " ".join(summaries.values())
    lesson_signature = _minhash_signature(lesson_basis)
    prior_signatures = [tuple(signature) for signature in existing_signatures]
    for old_signature in prior_signatures:
        if len(old_signature) != len(lesson_signature):
            raise ValueError("existing MinHash signatures must use the same permutation count")
    for old_signature in prior_signatures:
        if _signature_similarity(lesson_signature, old_signature) >= similarity_threshold:
            raise ValueError("MinHash deduplication rejected a near-duplicate repair lesson")
    drills = []
    for ordinal, focus in enumerate(DRILL_FOCI, 1):
        prompt = (
            f"DreamCo Bootcamp debugging drill: {focus}. "
            f"Failure signal: {summaries['failure']} "
            f"Root-cause note: {summaries['root_cause']} "
            f"Verified repair note: {summaries['repair']} "
            f"Regression evidence: {summaries['regression_test']} "
            "Explain your reasoning, list verification steps, and state uncertainty. "
            "Do not assume access to external systems."
        )
        drill_id = hashlib.sha256(
            f"{evidence['evidence_id']}|{ordinal}|{focus}".encode()
        ).hexdigest()[:20]
        drills.append({
            "schema": "dreamco.bootcamp_cleanroom_drill.v1",
            "drill_id": f"DRILL-{drill_id.upper()}",
            "lesson_id": evidence["lesson_id"],
            "division_id": evidence["division_id"],
            "ordinal": ordinal,
            "focus": focus,
            "prompt": prompt,
            "rubric": [
                "identifies the supported failure signal",
                "uses only supplied evidence",
                "proposes a reproducible verification",
                "checks privacy and authorization",
                "states uncertainty and escalation criteria",
            ],
            "source_evidence_sha256": evidence["evidence_sha256"],
            "lesson_minhash_signature": list(lesson_signature),
            "training_eligible": True,
            "holdout": False,
            "human_review_status": "APPROVED_SOURCE_REPAIR",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    if len(drills) != 25:
        raise ValueError(f"expected 25 distinct drill foci; generated {len(drills)}")
    return drills


def evaluate_swarm_handoff(
    *,
    expected_route: str,
    actual_route: str,
    router_latency_ms: float,
    schema_valid: bool,
    tool_calls_used: int,
    optimal_tool_calls: int,
    max_latency_ms: float = 5.0,
    minimum_precision: float = 0.80,
) -> dict[str, Any]:
    latency = _finite(router_latency_ms, "router_latency_ms", minimum=0.0)
    used, optimal = int(tool_calls_used), int(optimal_tool_calls)
    if used < 0 or optimal < 0:
        raise ValueError("tool call counts cannot be negative")
    precision = min(1.0, optimal / max(1, used))
    checks = {
        "route_correct": bool(expected_route) and actual_route == expected_route,
        "latency_within_budget": latency <= _finite(max_latency_ms, "max_latency_ms", minimum=0.0),
        "contract_schema_valid": bool(schema_valid),
        "tool_selection_precision": precision >= _finite(minimum_precision, "minimum_precision", minimum=0.0),
    }
    return {
        "schema": "dreamco.swarm_handoff_evaluation.v1",
        "passed": all(checks.values()),
        "checks": checks,
        "router_latency_ms": latency,
        "tool_selection_precision": round(precision, 4),
        "tool_calls_used": used,
        "optimal_tool_calls": optimal,
        "external_actions_executed": False,
    }


def build_regression_issue_draft(
    *,
    model_id: str,
    baseline_score: float,
    current_score: float,
    baseline_sha256: str,
    current_sha256: str,
    reproduction_command: str,
    threshold: float = 0.005,
) -> dict[str, Any]:
    baseline = _finite(baseline_score, "baseline_score", minimum=0.0)
    current = _finite(current_score, "current_score", minimum=0.0)
    threshold = _finite(threshold, "threshold", minimum=0.0)
    if baseline <= 0 or current > 1 or baseline > 1 or threshold >= 1:
        raise ValueError("scores must be in (0,1] and threshold in [0,1)")
    for name, digest in (("baseline_sha256", baseline_sha256), ("current_sha256", current_sha256)):
        if not re.fullmatch(r"[0-9a-f]{64}", str(digest)):
            raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    drop = max(0.0, (baseline - current) / baseline)
    regressed = drop > threshold
    return {
        "schema": "dreamco.pr_regression_issue_draft.v1",
        "status": "ISSUE_DRAFT_REQUIRES_REVIEW" if regressed else "NO_REGRESSION",
        "title": f"Benchmark regression: {model_id}" if regressed else "",
        "model_id": model_id,
        "baseline_score": baseline,
        "current_score": current,
        "relative_drop": round(drop, 8),
        "threshold": threshold,
        "baseline_evidence_sha256": baseline_sha256,
        "current_evidence_sha256": current_sha256,
        "reproduction_command": redact(reproduction_command, 500),
        "github_issue_created": False,
        "truth_boundary": "This is an issue draft only; no GitHub issue is created by this module.",
    }


def sign_isolation_receipt(receipt: dict[str, Any], key: str, key_id: str) -> dict[str, Any]:
    if len(key) < 32 or not key_id.strip():
        raise ValueError("managed HMAC key and key ID are required")
    payload = {key: value for key, value in receipt.items() if key != "authentication"}
    signed = {**payload, "authentication": {"algorithm": "HMAC-SHA256", "key_id": key_id, "value": ""}}
    signature = hmac.new(key.encode(), canonical_json(signed).encode(), hashlib.sha256).hexdigest()
    signed["authentication"]["value"] = signature
    return signed


def verify_isolation_receipt(receipt: dict[str, Any], key: str, expected_key_id: str) -> bool:
    auth = receipt.get("authentication", {})
    if auth.get("algorithm") != "HMAC-SHA256" or auth.get("key_id") != expected_key_id:
        return False
    payload = dict(receipt)
    payload_auth = dict(auth)
    supplied = payload_auth.get("value", "")
    payload_auth["value"] = ""
    payload["authentication"] = payload_auth
    expected = hmac.new(key.encode(), canonical_json(payload).encode(), hashlib.sha256).hexdigest()
    return bool(supplied) and hmac.compare_digest(supplied, expected)


def audit_buyer_readiness(
    *,
    fp16_score: float,
    q8_score: float,
    q4_score: float,
    isolation_receipt: dict[str, Any] | None,
    hmac_key: str = "",
    key_id: str = "",
    max_q8_drift: float = 0.02,
    max_q4_drift: float = 0.03,
) -> dict[str, Any]:
    fp16 = _finite(fp16_score, "fp16_score", minimum=0.0)
    q8 = _finite(q8_score, "q8_score", minimum=0.0)
    q4 = _finite(q4_score, "q4_score", minimum=0.0)
    if any(score > 1 for score in (fp16, q8, q4)):
        raise ValueError("quantization scores must be in [0,1]")
    q8_drift, q4_drift = round(fp16 - q8, 6), round(fp16 - q4, 6)
    receipt_ok = bool(
        isolation_receipt and hmac_key and key_id
        and verify_isolation_receipt(isolation_receipt, hmac_key, key_id)
        and isolation_receipt.get("network_blocked") is True
        and isolation_receipt.get("egress_probe_attempted") is True
        and isolation_receipt.get("egress_probe_blocked") is True
        and isolation_receipt.get("kit_sha256")
        and re.fullmatch(r"[0-9a-f]{64}", str(isolation_receipt.get("kit_sha256", "")))
    )
    quality_ok = q8_drift <= max_q8_drift and q4_drift <= max_q4_drift
    return {
        "schema": "dreamco.buyer_readiness_audit.v1",
        "status": "READY_FOR_HUMAN_BUYER_REVIEW" if receipt_ok and quality_ok else "BLOCKED_PENDING_EVIDENCE",
        "quantization": {"fp16": fp16, "q8_0_drift": q8_drift, "q4_k_m_drift": q4_drift},
        "isolation_receipt_verified": receipt_ok,
        "quantization_within_policy": quality_ok,
        "buyer_certification_awarded": False,
        "truth_boundary": "This audit does not issue legal, security, or enterprise compliance certification.",
    }


def propose_upgrade_101(telemetry: Iterable[dict[str, Any]], *, minimum_observations: int = 3) -> dict[str, Any]:
    rows = list(telemetry)
    qualified = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        digest = str(row.get("evidence_sha256", ""))
        if (
            row.get("status") == "VERIFIED"
            and row.get("bottleneck")
            and re.fullmatch(r"[0-9a-f]{64}", digest)
            and row.get("holdout") is False
        ):
            qualified.append(row)
    counts: dict[str, list[dict[str, Any]]] = {}
    for row in qualified:
        counts.setdefault(str(row["bottleneck"]), []).append(row)
    candidates = sorted(
        ((name, evidence) for name, evidence in counts.items() if len(evidence) >= minimum_observations),
        key=lambda item: (-len(item[1]), item[0]),
    )
    if not candidates:
        return {
            "schema": "dreamco.upgrade_101_proposal.v1",
            "status": "NO_PROPOSAL_INSUFFICIENT_VERIFIED_TELEMETRY",
            "proposal": None,
            "human_approval_required": True,
        }
    bottleneck, evidence = candidates[0]
    proposal = {
        "proposal_id": "UPGRADE-101-" + hashlib.sha256(bottleneck.encode()).hexdigest()[:12].upper(),
        "hypothesis": f"Investigate whether targeted remediation for '{bottleneck}' improves measured task performance.",
        "observed_bottleneck": bottleneck,
        "observation_count": len(evidence),
        "evidence_sha256": sorted({row["evidence_sha256"] for row in evidence}),
        "status": "DRAFT_REQUIRES_HUMAN_REVIEW",
        "sandbox_required": True,
        "automatic_merge": False,
        "claimed_improvement_percent": None,
    }
    return {
        "schema": "dreamco.upgrade_101_proposal.v1",
        "status": "PROPOSAL_DRAFTED",
        "proposal": proposal,
        "human_approval_required": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
