#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "data-discovery-bot-program.json"


def clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a Data Discovery Bot candidate for package-building review.")
    parser.add_argument("candidate", help="Path to a candidate JSON record")
    args = parser.parse_args()

    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    dims = program["scoring"]["dimensions"]

    hard_fail_reasons = []
    flags = candidate.get("flags", [])
    for blocked in program["scoring"]["hard_failures"]:
        if blocked in flags:
            hard_fail_reasons.append(blocked)

    scores = candidate.get("scores", {})
    weighted = 0.0
    max_weight = sum(dims.values())
    missing = []
    for name, weight in dims.items():
        if name not in scores:
            missing.append(name)
            continue
        weighted += clamp(float(scores[name])) * weight

    total = weighted / max_weight if max_weight else 0.0
    redistribution = candidate.get("redistribution_allowed")
    commercial = candidate.get("commercial_use_allowed")
    rights = candidate.get("rights_basis")

    if hard_fail_reasons:
        status = "blocked"
    elif not rights:
        status = "rights_review"
    elif missing:
        status = "quality_review"
    elif redistribution is True and commercial is True and total >= 80:
        status = "approved_for_package_build"
    elif total >= 70:
        status = "approved_for_private_use"
    else:
        status = "quality_review"

    report = {
        "candidate_id": candidate.get("candidate_id"),
        "score": round(total, 2),
        "status": status,
        "missing_score_dimensions": missing,
        "hard_fail_reasons": hard_fail_reasons,
        "truth_boundary": "This score is triage evidence only. Rights, privacy/security, provenance, and package verification still require review before publication or sale."
    }
    print(json.dumps(report, indent=2))
    return 1 if status == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
