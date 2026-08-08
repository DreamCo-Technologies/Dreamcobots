#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "config" / "coding-tech-workforce-competition-program.json"

REQUIRED_ROLES = {
    "software engineer","frontend engineer","backend engineer","full-stack engineer","mobile engineer","game engineer",
    "embedded engineer","data engineer","data scientist","machine-learning engineer","AI engineer","cloud engineer",
    "DevOps engineer","site reliability engineer","security engineer","QA engineer","test automation engineer",
    "solutions architect","integration engineer","developer-experience engineer","database engineer","performance engineer"
}
REQUIRED_UPGRADE = {
    "automatic preflight checks","one-command or one-button upgrade path where practical","rollback or restore path",
    "clear release notes","config migration helpers","plugin/adapter compatibility checks"
}


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    roles = set(data.get("job_families", []))
    missing_roles = sorted(REQUIRED_ROLES - roles)
    if missing_roles:
        errors.append(f"missing core tech job families: {', '.join(missing_roles)}")
    if len(roles) < 50:
        errors.append(f"expected broad tech-workforce coverage, found {len(roles)} roles")

    clean = data.get("clean_code_standard", {})
    if clean.get("required") is not True or len(clean.get("principles", [])) < 12:
        errors.append("clean-code standard is incomplete")

    bug = data.get("bug_policy", {})
    if bug.get("goal") != "zero known release-blocking bugs":
        errors.append("bug policy must target zero known release-blocking bugs")
    if "No software process can guarantee zero bugs" not in bug.get("truth_boundary", ""):
        errors.append("truthful zero-bug boundary is missing")
    if len(bug.get("required_practices", [])) < 10:
        errors.append("bug prevention practices are incomplete")

    upgrade = data.get("easy_upgrade_standard", {})
    if not REQUIRED_UPGRADE.issubset(set(upgrade.get("required", []))):
        errors.append("easy-upgrade requirements are incomplete")

    competition = data.get("competition_program", {})
    if int(competition.get("top_competitor_target", 0)) < 30:
        errors.append("coding bots must target top-30 competitor discovery")
    if len(data.get("release_definition_of_done", [])) < 10:
        errors.append("release definition of done is incomplete")

    report = {
        "ok": not errors,
        "tech_job_families": len(roles),
        "clean_code_principles": len(clean.get("principles", [])),
        "upgrade_requirements": len(upgrade.get("required", [])),
        "competitor_target": competition.get("top_competitor_target"),
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
