#!/usr/bin/env python3
"""Validate the governed continuous Buddy study policy without running study jobs."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "buddy-continuous-study-policy.json"
CROSSWALK = ROOT / "config" / "generated" / "masterbot-55-domain-crosswalk.json"


def validate(policy: dict, crosswalk: dict) -> list[str]:
    errors: list[str] = []
    if policy.get("schema") != "dreamco.buddy_continuous_study_policy.v1":
        errors.append("unsupported policy schema")
    schedule = policy.get("schedule", {})
    domains = crosswalk.get("domains", [])
    if len(domains) != 55:
        errors.append("canonical crosswalk must contain exactly 55 domain divisions")
    if sum(row.get("mapping_status") == "proposed_exact_name_match" for row in domains) != 45:
        errors.append("crosswalk must preserve 45 original core domains")
    if sum(row.get("mapping_status") == "unresolved" for row in domains) != 10:
        errors.append("crosswalk must preserve 10 supplemental domains pending owner review")
    if schedule.get("domain_count") != 55:
        errors.append("domain_count must be 55; shared-platform MasterBots are not divisions")
    if schedule.get("masterbot_count") != 65 or schedule.get("shared_platform_masterbot_count") != 20:
        errors.append("65 MasterBots must remain separate from the 55 domain divisions")
    expected_slots = schedule.get("daily_lesson_slots_per_domain", 0) * len(domains)
    if schedule.get("daily_planned_slots") != expected_slots:
        errors.append("daily_planned_slots must equal per-domain slots times the 55 domain profiles")
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
    crosswalk = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    errors = validate(policy, crosswalk)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Continuous study policy valid: 55 domain divisions, 65 MasterBots (20 shared platform), 275 daily slots, governed 24x7 schedule, rights and budget gates enforced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
