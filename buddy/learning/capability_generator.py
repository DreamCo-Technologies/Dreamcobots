#!/usr/bin/env python3
"""Generate a capability package for every dimension other models are compared on.

A generated package is cataloged, not mastered. Empty evidence is intentional.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "config/model-prospectus-benchmark-contract.json"
PACKAGES = ROOT / "capabilities"
OUT = ROOT / "capabilities/generated"
REPORT = ROOT / "config/generated/capability-coverage.json"

OWN = {
    "speech": ["capabilities/voice_clone.capability.json", "buddy/speech/speak.py"],
    "vision": ["capabilities/image_clone.capability.json"],
    "creative_generation": ["buddy/content/make.py", "capabilities/image_clone.capability.json"],
    "planning": ["buddy/learning/gap_plan.py", "buddy/local_core.py"],
    "education": ["buddy/learning/study_methods.py", "buddy/learning/school_proof.py"],
    "writing": ["buddy/content/make.py"],
    "research": ["buddy/learning/free_datasets.py"],
}


def contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def dimensions() -> list[str]:
    rows = contract()["capability_matrix_dimensions"]
    if len(rows) < 20:
        raise RuntimeError("The reference capability matrix is too small.")
    return rows


def package(dimension: str) -> dict:
    title = dimension.replace("_", " ")
    return {
        "capability_id": f"{dimension}.v1",
        "name": title[:1].upper() + title[1:],
        "domain": "model_parity",
        "sources": [
            "config/model-prospectus-benchmark-contract.json",
            f"capabilities/generated/{dimension}.capability.json",
        ],
        "prerequisites": [],
        "objectives": [
            f"Cover the {title} dimension used to compare Buddy with other models",
            "Record a same-fixture result before calling the gap closed",
        ],
        "tasks": [
            f"Run a {title} fixture with Buddy's own code",
            "Score every user-approved model on the same fixture",
            "Keep the highest score without calling an untested model a winner",
        ],
        "benchmarks": [
            "Same fixture and rubric as the reference models",
            "Independent pass without a frontier model writing the answer",
            "Regression on the previous fixture",
        ],
        "sandbox_profile": "capability_parity_sandbox",
        "mastery": {
            "threshold": 0.85,
            "independent_passes": 3,
            "transfer_required": True,
            "regression_required": True,
        },
        "safety_constraints": [
            "Do not mark this mastered without current passing evidence",
            "Do not copy a closed model's weights or output as the answer key",
            "A catalog entry is not a capability Buddy can already do",
        ],
        "automation_opportunities": [],
        "monetization_opportunities": [],
        "evidence": [],
    }


def cover() -> dict:
    wanted = dimensions()
    existing = {path.name for path in PACKAGES.glob("*.capability.json")}
    generated = []
    already = []
    OUT.mkdir(parents=True, exist_ok=True)
    for dimension in wanted:
        name = f"{dimension}.capability.json"
        if name in existing:
            already.append(dimension)
            continue
        path = OUT / name
        path.write_text(json.dumps(package(dimension), indent=2) + "\n", encoding="utf-8")
        generated.append(dimension)
    rows = []
    for dimension in wanted:
        own = [item for item in OWN.get(dimension, []) if (ROOT / item).is_file()]
        rows.append({
            "dimension": dimension,
            "package": f"capabilities/generated/{dimension}.capability.json" if dimension not in already else f"capabilities/{dimension}.capability.json",
            "state": "cataloged",
            "mastered": False,
            "own_code": own,
            "evidence": [],
        })
    report = {
        "schema": "dreamco.capability_coverage.v1",
        "reference": "config/model-prospectus-benchmark-contract.json",
        "dimensions": len(wanted),
        "generated": generated,
        "already_present": already,
        "mastered": 0,
        "called_a_model": False,
        "rows": rows,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    report = cover()
    assert report["dimensions"] == len(dimensions())
    assert report["mastered"] == 0 and report["called_a_model"] is False
    assert len(report["generated"]) + len(report["already_present"]) == report["dimensions"]
    print(json.dumps({"dimensions": report["dimensions"], "generated": len(report["generated"]), "mastered": 0}))
