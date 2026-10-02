#!/usr/bin/env python3
"""How close this repository is to a frontier model. It does not train one."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _report() -> dict:
    path = Path(__file__).with_name("study_methods.py")
    spec = importlib.util.spec_from_file_location("study_methods_for_frontier", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.report()


def scan() -> dict:
    study = _report()
    release = json.loads((ROOT / "website/data/command-center/release-readiness.json").read_text(encoding="utf-8"))
    health = json.loads((ROOT / "website/data/actions-health-report.json").read_text(encoding="utf-8"))
    summary = health["summary"]
    missing = []
    if release.get("production_ready") is not True:
        missing.append("The release file says this repository is not production ready.")
    unknown = summary.get("runtime_unknown_workflows", 0)
    if summary.get("runtime_passing_workflows", 0) == 0:
        missing.append(f"{unknown} benchmark workflows have no runtime result.")
    if study["training_ready"] == 0:
        missing.append(f"{study['training_total']} weight-training methods have no adapter and no weight file.")
    missing.append("No hidden public exam has a published score.")
    return {
        "ready_study_methods": study["study_ready_names"],
        "can_compete_with_a_frontier_model": False,
        "missing": missing,
        "weights_trained": False,
    }


if __name__ == "__main__":
    made = scan()
    assert made["can_compete_with_a_frontier_model"] is False
    assert len(made["ready_study_methods"]) == 18
    assert "spaced_repetition" in made["ready_study_methods"]
    assert "contrastive" in made["ready_study_methods"]
    print(json.dumps({"ready": len(made["ready_study_methods"]), "missing": len(made["missing"]), "competes": False}))
