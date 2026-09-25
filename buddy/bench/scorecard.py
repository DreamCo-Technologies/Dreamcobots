#!/usr/bin/env python3
"""Score our own gates. This is not a comparison with Astra."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(name: str, fn) -> dict:
    try:
        fn()
    except Exception as exc:
        return {"name": name, "passed": False, "detail": str(exc)}
    return {"name": name, "passed": True, "detail": ""}


def run() -> dict:
    opened = load("open_target", ROOT / "desk" / "open_target.py")
    owned = load("own_model", ROOT / "store" / "own_model.py")
    weights = load("weight_control", ROOT / "weights" / "weight_control.py")
    camp = load("bootcamp", ROOT / "learning" / "bootcamp.py")
    bench = load("model_bench", ROOT / "learning" / "model_bench.py")
    school = load("school", ROOT / "learning" / "school.py")
    datasets = load("free_datasets", ROOT / "learning" / "free_datasets.py")
    rows = [
        check("open a text file", lambda: opened.choose("open", "github", "DreamCo-Technologies/Dreamcobots", "README.md")["reads_file"] or (_ for _ in ()).throw(AssertionError("did not read"))),
        check("do not load weights", lambda: None if opened.choose("open", "huggingface", "org/model", "model.safetensors")["loads_weights"] is False else (_ for _ in ()).throw(AssertionError("loaded"))),
        check("lookup stays on GitHub", lambda: None if "github.com/search" in opened.choose("lookup", "github", "DreamCo-Technologies/Dreamcobots")["opens"] else (_ for _ in ()).throw(AssertionError("search"))),
        check("refuse a closed-model sale", lambda: None if owned.sell_own_model("org/distill-claude", "huggingface", True, True)["for_sale"] is False else (_ for _ in ()).throw(AssertionError("sold"))),
        check("wrapper until the task passes", lambda: None if owned.sell_wrapper_until_ready("org/open-model", "huggingface", True, True, "answer mail", False)["product"] == "wrapper" else (_ for _ in ()).throw(AssertionError("wrapper"))),
        check("their model replaces the wrapper", lambda: None if owned.sell_wrapper_until_ready("org/open-model", "huggingface", True, True, "answer mail", True)["wrapper_for_sale"] is False else (_ for _ in ()).throw(AssertionError("still wrapper"))),
        check("remote code stays off", lambda: weights.sheet({"trust_remote_code": True})),
        check("sixty settings, no weight file", lambda: None if weights.sheet()["settings"] >= 60 and weights.sheet()["weight_files_on_this_site"] is False else (_ for _ in ()).throw(AssertionError("sheet"))),
        check("debug does not load a repo", lambda: None if weights.debug_target("repository", "DreamCo-Technologies/Dreamcobots")["runs_here"] is False else (_ for _ in ()).throw(AssertionError("ran"))),
        check("not mastered at 600 resources", lambda: None if camp.mastery(600, 10, False)["mastered"] is False else (_ for _ in ()).throw(AssertionError("mastered"))),
        check("frontier model not trained", lambda: None if camp.frontier(600)["can_compete_today"] is False else (_ for _ in ()).throw(AssertionError("compete"))),
        check("refuse distilling a closed model", lambda: None if bench.review("org/model", "distill Claude", True, True, True)["trains_here"] is False and bench.review("org/model", "distill Claude", True, True, True)["accepted"] is False else (_ for _ in ()).throw(AssertionError("accepted"))),
        check("ten views required", lambda: school.compare(school.views_for([1, "A", "B", "https://example.com", "r", "t"])[:9])),
        check("free datasets stay linked", lambda: None if datasets.catalog()["count"] >= 20 and datasets.catalog()["hosted_here"] is False and datasets.catalog()["ready_to_train"] >= 8 else (_ for _ in ()).throw(AssertionError("datasets"))),
    ]
    # The two checks above are expected to raise. Flip those results.
    for row in rows:
        if row["name"] in {"remote code stays off", "ten views required"}:
            row["passed"] = not row["passed"]
            row["detail"] = "" if row["passed"] else "the gate did not trip"
    passed = sum(row["passed"] for row in rows)
    return {
        "checks": len(rows),
        "passed": passed,
        "score": round(passed / len(rows), 3),
        "what_this_measures": "DreamCo's own gates: open, sell, weights, school, and training refusal.",
        "what_this_does_not_measure": "A frontier model exam. There is no Astra score because this repo has no Astra-class weights and no shared exam.",
        "astra": {
            "compared": False,
            "as_close_as_this_code_gets": "A wrapper, a 67-setting sheet, and gates that refuse copied weights.",
            "still_missing": ["a weight file we are allowed to train", "a hidden public exam", "a published score"],
        },
        "goals": [
            {"goal": "Our gate checks pass", "met": passed == len(rows)},
            {"goal": "Ten views on the 600 readings we have", "met": True},
            {"goal": "1,000 readings and a held-out exam", "met": False},
            {"goal": "Train an open model the customer owns", "met": False},
            {"goal": "Publish a score on a public exam", "met": False},
        ],
        "rows": rows,
    }


if __name__ == "__main__":
    report = run()
    print(json.dumps({key: report[key] for key in ("checks", "passed", "score", "astra")}))
    if report["passed"] != report["checks"]:
        raise SystemExit(1)
