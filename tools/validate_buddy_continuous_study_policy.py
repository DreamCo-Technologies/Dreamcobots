#!/usr/bin/env python3
"""Validate the governed continuous Buddy study policy without running study jobs."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "buddy-continuous-study-policy.json"
REGISTRY = ROOT / "config" / "masterbot-65-registry.json"


def validate(policy: dict, registry: dict) -> list[str]:
    errors: list[str] = []
    if policy.get("schema") != "dreamco.buddy_continuous_study_policy.v1":
        errors.append("unsupported policy schema")
    schedule = policy.get("schedule", {})
    divisions = registry.get("divisions", registry.get("masterbots", []))
    if len(divisions) != 65:
        errors.append("canonical registry must contain exactly 65 divisions")
    expected_slots = schedule.get("daily_lesson_slots_per_division", 0) * len(divisions)
    if schedule.get("daily_planned_slots") != expected_slots:
        errors.append("daily_planned_slots must equal per-division slots times registry size")
    if schedule.get("mode") != "continuous_24x7_with_resource_governors":
        errors.append("continuous schedule must retain resource governors")
    mastery = policy.get("mastery", {})
    if not mastery.get("require_holdout_for_mastery") and not mastery.get("regression_must_pass"):
        errors.append("mastery requires holdout and regression gates")
    if not mastery.get("regression_must_pass"):
        errors.append("regression must pass before mastery")
    resources = policy.get("resource_governors", {})
    if resources.get("paid_compute_requires_separate_approval") is not True:
        errors.append("paid compute must require separate approval")
    if resources.get("pause_when_no_authorized_work_exists") is not True:
        errors.append("scheduler must pause when no authorized work exists")
    permissions = policy.get("source_permissions", {})
    for key in ("transcript_download_default", "media_download_default", "model_training_default"):
        if permissions.get(key) is not False:
            errors.append(f"{key} must remain false by default")
    if permissions.get("unknown_rights") != "BLOCKED":
        errors.append("unknown rights must be blocked")
    model = policy.get("model_build", {})
    if model.get("target_parameters_per_division") != 45_000_000:
        errors.append("per-division parameter target must be 45,000,000")
    if model.get("no_claim_of_gpt5_equivalence") is not True:
        errors.append("parameter count must not be presented as GPT-5 equivalence")
    return errors


def main() -> int:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    errors = validate(policy, registry)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Continuous study policy valid: 65 divisions, 325 daily slots, governed 24x7 schedule, rights and budget gates enforced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
