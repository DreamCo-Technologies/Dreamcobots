#!/usr/bin/env python3
"""Fail-closed gate for the Buddy teacher->student distillation lane.

Enforces three rules, stdlib only, no network:
  1. eval-before-train: every run starts after a hidden-holdout baseline.
  2. no weights in default CI: no weight files in the tree outside allow paths.
  3. evidence before allowlist: allowlist_eligible needs a passing packet.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

CONTRACT_PATH = Path("config/buddy-distill-contract.json")
EVIDENCE_DIR = Path("evidence/distill")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_contract(root: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    path = root / CONTRACT_PATH
    if not path.is_file():
        return {}, [f"missing contract: {CONTRACT_PATH}"]
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"contract is not valid JSON: {exc}"]
    if contract.get("schema") != "dreamco.buddy_distill_contract.v1":
        errors.append("contract schema must be dreamco.buddy_distill_contract.v1")
    ci = contract.get("ci_policy", {})
    for key in ("default_ci_downloads_weights", "default_ci_trains", "default_ci_uploads_weights"):
        if ci.get(key) is not False:
            errors.append(f"ci_policy.{key} must be false")
    th = contract.get("thresholds", {})
    for key in ("minimum_holdout_score", "minimum_absolute_improvement", "maximum_regression", "minimum_repetitions"):
        if key not in th:
            errors.append(f"thresholds.{key} missing")
    if not contract.get("teacher", {}).get("teacher_terms_check_required"):
        errors.append("teacher.teacher_terms_check_required must be true")
    return contract, errors


def check_packet(packet: dict, th: dict, name: str) -> list[str]:
    """Return rule violations for one evidence packet."""
    errs: list[str] = []
    req = ["adapter_id", "teacher", "student", "baseline", "runs", "safety_suite", "provenance", "owner_approval", "allowlist_eligible"]
    missing = [k for k in req if k not in packet]
    if missing:
        return [f"{name}: missing fields {missing}"]

    baseline = packet["baseline"]
    runs = packet["runs"] or []
    try:
        base_at = _ts(baseline["evaluated_at_utc"])
    except (KeyError, ValueError):
        return [f"{name}: baseline.evaluated_at_utc missing or not ISO-8601"]
    if len(str(baseline.get("holdout_fixture_sha256", ""))) != 64:
        errs.append(f"{name}: baseline.holdout_fixture_sha256 must be a sha256 hex digest")

    for i, run in enumerate(runs):
        try:
            if _ts(run["train_started_at_utc"]) <= base_at:
                errs.append(f"{name}: run {i} trained before or at baseline eval (eval-before-train violated)")
        except (KeyError, ValueError):
            errs.append(f"{name}: run {i} train_started_at_utc missing or invalid")

    if not packet["allowlist_eligible"]:
        return errs

    # Rule 3: evidence before allowlist.
    if len(runs) < th["minimum_repetitions"]:
        errs.append(f"{name}: {len(runs)} runs < minimum_repetitions {th['minimum_repetitions']}")
    for i, run in enumerate(runs):
        score = run.get("holdout_score", 0)
        if score < th["minimum_holdout_score"]:
            errs.append(f"{name}: run {i} holdout {score} < {th['minimum_holdout_score']}")
        if score - baseline.get("holdout_score", 1) < th["minimum_absolute_improvement"]:
            errs.append(f"{name}: run {i} improvement below {th['minimum_absolute_improvement']}")
        if run.get("regression", 1) > th["maximum_regression"]:
            errs.append(f"{name}: run {i} regression {run.get('regression')} > {th['maximum_regression']}")
    terms = packet["teacher"].get("teacher_terms_check", {})
    if terms.get("permitted") is not True:
        errs.append(f"{name}: teacher_terms_check.permitted is not true")
    if packet["student"].get("base_model_license_ok") is not True:
        errs.append(f"{name}: student.base_model_license_ok is not true")
    if packet["student"].get("weight_format") not in ("safetensors", "gguf"):
        errs.append(f"{name}: student.weight_format must be safetensors or gguf")
    if packet["safety_suite"].get("passed") is not True:
        errs.append(f"{name}: safety_suite.passed is not true")
    if packet["provenance"].get("sources_approved") is not True:
        errs.append(f"{name}: provenance.sources_approved is not true")
    if packet["owner_approval"].get("approved") is not True:
        errs.append(f"{name}: owner_approval.approved is not true")
    return errs


def scan_weights(root: Path, contract: dict) -> list[str]:
    ci = contract.get("ci_policy", {})
    exts = tuple(ci.get("weight_file_extensions", []))
    allow = [root / p for p in ci.get("weight_file_allow_paths", [])]
    found = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name.lower().endswith(exts) and not any(a in path.parents for a in allow):
            found.append(f"weight file in tree: {path.relative_to(root)}")
    return found


def run(root: Path) -> tuple[int, list[str]]:
    lines: list[str] = []
    contract, errors = load_contract(root)
    if contract:
        th = contract["thresholds"] if "thresholds" in contract else {}
        packets: dict[str, dict] = {}
        ev_dir = root / EVIDENCE_DIR
        for p in sorted(ev_dir.glob("*.json")) if ev_dir.is_dir() else []:
            try:
                packet = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{p.name}: invalid JSON: {exc}")
                continue
            if th:
                errors.extend(check_packet(packet, th, p.name))
            packets[packet.get("adapter_id", p.stem)] = packet
        passing = {aid for aid, pk in packets.items() if pk.get("allowlist_eligible")}
        claims = [a.get("id") for a in contract.get("adapters", []) if a.get("allowlist_eligible")]
        claims += list(contract.get("truth", {}).get("allowlisted_adapters", []))
        for aid in claims:
            if aid not in passing:
                errors.append(f"adapter {aid} claims allowlist without an evidence packet")
        errors.extend(scan_weights(root, contract))
        lines.append(f"packets checked: {len(packets)}; allowlist claims: {len(set(claims))}")
    if errors:
        lines.append("DISTILL GATE: FAIL")
        lines.extend(f"  - {e}" for e in errors)
        return 1, lines
    lines.append("DISTILL GATE: PASS (no unproven allowlist claims, no weight files, eval-before-train holds)")
    return 0, lines


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    code, lines = run(root.resolve())
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
