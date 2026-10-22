"""Offline structural validator for 24-hour sandbox runtime receipts.

Hash links check accidental corruption, not independently attested execution.
No positive result from this helper alone certifies a benchmark or model.
"""
import hashlib
import json
import math
import re
from datetime import datetime, timezone


def validate_runtime_soak(tick: dict, history: object, errors: list[str]) -> bool:
    """Reject inventory-only, unmeasured, inconsistent, or incomplete runtime evidence."""
    if tick.get("runtime_verified") is not True:
        errors.append("sandbox soak runtime_verified must be true (inventory is not runtime evidence)")
        return False
    coverage = tick.get("coverage")
    if not isinstance(coverage, dict) or coverage.get("runtime_24h_verified") is not True:
        errors.append("sandbox soak missing verified runtime_24h coverage")
        return False
    if not isinstance(history, list) or len(history) < 25:
        errors.append("sandbox soak needs at least 25 runtime receipts")
        return False

    previous = ""
    previous_at = None
    first_at = None
    commit = None
    fleet = None
    seen_runs: set[str] = set()
    for index, receipt in enumerate(history):
        if not isinstance(receipt, dict):
            errors.append(f"sandbox soak receipt {index} is not an object")
            return False
        if (receipt.get("schema") != "dreamco.sandbox_runtime_receipt.v1"
                or receipt.get("status") != "runtime_probe_passed"
                or receipt.get("runtime_verified") is not True
                or not isinstance(receipt.get("probe"), dict)
                or receipt["probe"].get("ok") is not True):
            errors.append(f"sandbox soak receipt {index} lacks passing runtime probe evidence")
            return False
        sha = receipt.get("receipt_sha256")
        body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if receipt.get("previous_sha256") != previous or sha != digest:
            errors.append(f"sandbox soak receipt {index} breaks hash chain")
            return False
        previous = sha
        run_id = receipt.get("run_id")
        if not isinstance(run_id, str) or not run_id or run_id in seen_runs:
            errors.append(f"sandbox soak receipt {index} has missing/duplicate run identity")
            return False
        seen_runs.add(run_id)
        this_commit, this_fleet = receipt.get("repo_commit"), receipt.get("fleet_sha256")
        if (not isinstance(this_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", this_commit)
                or not isinstance(this_fleet, str) or not re.fullmatch(r"[0-9a-f]{64}", this_fleet)):
            errors.append(f"sandbox soak receipt {index} lacks immutable source identity")
            return False
        if commit is None:
            commit, fleet = this_commit, this_fleet
        elif (this_commit, this_fleet) != (commit, fleet):
            errors.append(f"sandbox soak receipt {index} changed commit or fleet")
            return False
        try:
            timestamp = datetime.fromisoformat(receipt["generated_at"])
        except (KeyError, ValueError, TypeError):
            errors.append(f"sandbox soak receipt {index} has invalid timestamp")
            return False
        if timestamp.tzinfo is None:
            errors.append(f"sandbox soak receipt {index} has naive timestamp")
            return False
        timestamp = timestamp.astimezone(timezone.utc)
        if previous_at is not None and not 0 < (timestamp - previous_at).total_seconds() <= 5400:
            errors.append(f"sandbox soak receipt {index} has duplicate, reversed, or excessive gap")
            return False
        if first_at is None:
            first_at = timestamp
        previous_at = timestamp

    span = (previous_at - first_at).total_seconds()
    reported_span = coverage.get("coverage_seconds")
    if (span < 86400 or not isinstance(reported_span, (int, float))
            or isinstance(reported_span, bool) or not math.isfinite(reported_span)
            or reported_span != span):
        errors.append("sandbox soak has insufficient or inconsistent 24-hour elapsed coverage")
        return False
    if (tick.get("receipt_sha256") != previous or tick.get("repo_commit") != commit
            or tick.get("fleet_sha256") != fleet):
        errors.append("sandbox soak tick does not match final runtime receipt")
        return False
    return True
