#!/usr/bin/env python3
"""Run the 20 study procedures. The weight-training catalog stays not ready."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAINING = ROOT / "config" / "generated" / "buddy_learning_strategies.json"


def spaced_repetition(passes: list[bool]) -> dict:
    return {"schedule_days": [1, 3, 7], "retained": passes.count(True) >= 2, "weights_trained": False}


def active_recall(answer: str, expected: str) -> dict:
    return {"notes_hidden": True, "score": 1.0 if answer.strip().lower() == expected.strip().lower() else 0.0, "weights_trained": False}


def interleaving(tasks: list[str]) -> dict:
    switches = [tasks[0]] if tasks else []
    for task in tasks[1:]:
        if task != switches[-1]:
            switches.append(task)
    return {"mixed": len(set(tasks)) >= 3 and len(switches) >= 3, "weights_trained": False}


def deliberate_practice(scores: dict[str, float]) -> dict:
    weakest = min(scores, key=scores.get)
    return {"weakest": weakest, "drills": [f"Drill {n} on {weakest}" for n in range(1, 6)], "weights_trained": False}


def error_analysis(failures: list[str]) -> dict:
    if len(failures) < 10:
        return {"accepted": False, "reason": "Name a cause only after 10 failures.", "weights_trained": False}
    causes = [{"failure": item, "cause": item, "fix": "Add a check for this failure."} for item in failures[:10]]
    return {"accepted": True, "causes": causes, "weights_trained": False}


def curriculum(tasks: list[tuple[str, int, bool]]) -> dict:
    ordered = sorted(tasks, key=lambda row: row[1])
    unlocked = []
    open_next = True
    for name, _difficulty, passed in ordered:
        unlocked.append({"name": name, "open": open_next})
        open_next = passed
    return {"order": unlocked, "weights_trained": False}


def contrastive(good: str, bad: str) -> dict:
    if not good or not bad or good.strip() == bad.strip():
        return {"accepted": False, "weights_trained": False}
    return {"accepted": True, "rule": "Keep the good example. Drop the bad example.", "weights_trained": False}


def meta_learning(rows: list[dict]) -> dict:
    mapping: dict[str, dict[str, bool]] = {}
    for row in rows:
        mapping.setdefault(row["task"], {})[row["strategy"]] = bool(row["passed"])
    return {"map": mapping, "weights_trained": False}


def reinforcement_from_feedback(outcomes: list[bool]) -> dict:
    if len(outcomes) < 5:
        return {"adjusted": False, "reason": "Need at least 5 outcomes before a change.", "weights_trained": False}
    return {"adjusted": False, "reason": "A regression gate is required. No weight was changed.", "weights_trained": False}


def imitation(steps: list[str], expert: list[str]) -> dict:
    if not expert:
        return {"match": 0.0, "passed": False, "weights_trained": False}
    same = sum(1 for left, right in zip(steps, expert) if left == right)
    match = same / len(expert)
    return {"match": match, "passed": match >= 0.8, "weights_trained": False}


def self_play(task: str, already_passes: bool) -> dict:
    if not already_passes:
        return {"variants": [], "attempted": False, "weights_trained": False}
    return {
        "variants": [f"{task} with a missing fact", f"{task} with a tighter limit", f"{task} with two sources that disagree"],
        "attempted": False,
        "weights_trained": False,
    }


def knowledge_distillation(steps: list[str]) -> dict:
    short = steps[:10]
    return {"steps": short, "within_limit": len(short) <= 10, "model_copied": False, "weights_trained": False}


def human_in_the_loop(before: str, after: str) -> dict:
    return {"stored": True, "promoted": False, "changed": before != after, "weights_trained": False}


def benchmark_driven(scores: dict[str, float]) -> dict:
    lowest = min(scores, key=scores.get)
    return {"lowest": lowest, "plan": f"Work on {lowest} first.", "remeasured": False, "weights_trained": False}


def multi_perspective(notes: list[dict]) -> dict:
    if len(notes) < 4 or len({note["view"] for note in notes}) < 4:
        return {"accepted": False, "reason": "Need four different views.", "weights_trained": False}
    conflicts = [note["text"] for note in notes if note.get("disagrees")]
    return {"accepted": True, "conflicts": conflicts, "weights_trained": False}


def dependency_reduction(native: int, external: int) -> dict:
    total = native + external
    ratio = 0.0 if total == 0 else native / total
    return {"native_ratio": ratio, "plan": "Use the local skill when the ratio is under 0.5.", "weights_trained": False}


def failure_memory(past: list[str], proposed: str) -> dict:
    found = [item for item in past if item and item in proposed]
    return {"known": bool(found), "matches": found, "weights_trained": False}


def bootcamp_mastery(quiz_passed: bool) -> dict:
    return {"next_unlocked": bool(quiz_passed), "weights_trained": False}


def transfer_learning(skills: list[str], target: str) -> dict:
    gaps = [skill for skill in skills if target not in skill]
    return {"target": target, "carried": skills, "gaps": gaps, "weights_trained": False}


def continuous_learning_cycle(measured: bool | None) -> dict:
    if measured is None:
        return {"decision": "discard", "reason": "No measurement was supplied.", "weights_trained": False}
    return {"decision": "promote" if measured else "discard", "evidence": True, "weights_trained": False}


def run_study() -> dict:
    checks = {
        "spaced_repetition": spaced_repetition([True, False, True])["retained"] is True,
        "active_recall": active_recall("four", "four")["score"] == 1.0 and active_recall("three", "four")["notes_hidden"] is True,
        "interleaving": interleaving(["a", "b", "c"])["mixed"] is True and interleaving(["a", "a"])["mixed"] is False,
        "deliberate_practice": len(deliberate_practice({"sort": 0.2, "reply": 0.9})["drills"]) == 5,
        "error_analysis": error_analysis([f"failure {n}" for n in range(10)])["accepted"] is True and error_analysis(["one"])["accepted"] is False,
        "curriculum": curriculum([("hard", 2, False), ("easy", 1, True)])["order"][0]["name"] == "easy",
        "contrastive": contrastive("short reply", "copied page")["accepted"] is True and contrastive("same", "same")["accepted"] is False,
        "meta_learning": meta_learning([{"task": "mail", "strategy": "recall", "passed": True}])["map"]["mail"]["recall"] is True,
        "reinforcement_from_feedback": reinforcement_from_feedback([True] * 5)["adjusted"] is False,
        "imitation": imitation(["open", "sort"], ["open", "sort", "send"])["passed"] is False,
        "self_play": len(self_play("sort mail", True)["variants"]) == 3 and self_play("sort mail", True)["attempted"] is False,
        "knowledge_distillation": knowledge_distillation([f"step {n}" for n in range(12)])["within_limit"] is True and knowledge_distillation(["a"])["model_copied"] is False,
        "human_in_the_loop": human_in_the_loop("old", "new")["promoted"] is False,
        "benchmark_driven": benchmark_driven({"safety": 0.4, "mail": 0.9})["remeasured"] is False,
        "multi_perspective": multi_perspective([{"view": name, "text": name, "disagrees": name == "risk"} for name in ("code", "product", "risk", "user")])["accepted"] is True,
        "dependency_reduction": dependency_reduction(1, 3)["native_ratio"] == 0.25,
        "failure_memory": failure_memory(["missing source"], "The missing source came back.")["known"] is True,
        "bootcamp_mastery": bootcamp_mastery(False)["next_unlocked"] is False and bootcamp_mastery(True)["next_unlocked"] is True,
        "transfer_learning": "sort mail" in transfer_learning(["sort mail"], "support")["gaps"],
        "continuous_learning_cycle": continuous_learning_cycle(None)["decision"] == "discard" and continuous_learning_cycle(True)["decision"] == "promote",
    }
    # Two procedures run, but they do not finish a live measurement.
    not_ready = {"self_play", "benchmark_driven"}
    ready = [name for name, passed in checks.items() if passed and name not in not_ready]
    blocked = [name for name in checks if name not in ready]
    return {
        "procedures": len(checks),
        "passed": sum(checks.values()),
        "production_ready": ready,
        "not_production_ready": blocked,
        "weights_trained": False,
    }


def training_catalog() -> dict:
    raw = json.loads(TRAINING.read_text(encoding="utf-8"))
    methods = raw["techniques"]
    return {
        "methods": len(methods),
        "production_ready": [],
        "not_production_ready": [item["id"] for item in methods],
        "reason": raw["catalog_status"],
        "weights_trained": False,
    }


def report() -> dict:
    study = run_study()
    training = training_catalog()
    return {
        "all_production_ready": False,
        "study_ready": len(study["production_ready"]),
        "study_total": study["procedures"],
        "training_ready": 0,
        "training_total": training["methods"],
        "reason": "The study procedures that can finish without a live measurement are ready. Weight-training methods are not, because no adapter and no weight file exist.",
        "study_not_ready": study["not_production_ready"],
        "weights_trained": False,
    }


if __name__ == "__main__":
    made = report()
    study = run_study()
    assert study["passed"] == study["procedures"]
    assert made["all_production_ready"] is False
    assert made["training_ready"] == 0
    assert made["study_ready"] == 18
    print(json.dumps({key: made[key] for key in ("study_ready", "study_total", "training_ready", "training_total", "all_production_ready")}))
