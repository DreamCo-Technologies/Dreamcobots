"""Offline, evidence-gated task-to-model candidate router.

No model is downloaded or executed. Candidate metadata must come from an
authorized catalog; a listing is never proof of quality or training rights.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "config" / "task-model-taxonomy.json"


def load_taxonomy(path: Path = TAXONOMY) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "dreamco.task_model_taxonomy.v1":
        raise ValueError("Unsupported task taxonomy")
    return data


def classify_task(text: str, taxonomy: dict | None = None) -> str:
    taxonomy = taxonomy or load_taxonomy()
    aliases = {
        "code_repair": ("debug", "fix code", "repair code", "failing test"),
        "code_generation": ("write code", "build app", "implement"),
        "sql": ("sql", "database query"),
        "forecasting": ("forecast", "predict revenue", "time series"),
        "retrieval": ("search documents", "find information", "knowledge base"),
        "ranking": ("rank", "lead matching", "recommend"),
        "speech_recognition": ("transcribe", "speech to text"),
        "vision": ("recognize image", "analyze photo"),
        "image_generation": ("generate image", "draw image"),
        "simulation": ("simulate", "simulation"),
        "tool_calling": ("call tool", "use api", "connect app"),
    }
    lowered = text.lower()
    for family, terms in aliases.items():
        if family in taxonomy["dimensions"]["task_families"] and any(t in lowered for t in terms):
            return family
    return "reasoning"


def rank_candidates(task_family: str, candidates: list[dict], *, training: bool = False) -> dict:
    """Fail closed: unknown rights, costs, adapters or benchmarks are ineligible."""
    eligible = []
    rejected = []
    for model in candidates:
        missing = []
        if task_family not in model.get("task_families", []):
            missing.append("task_unsupported")
        if model.get("license_reviewed") is not True:
            missing.append("license_unreviewed")
        if training and model.get("training_rights_verified") is not True:
            missing.append("training_rights_unverified")
        if model.get("adapter_verified") is not True:
            missing.append("adapter_unverified")
        if model.get("benchmark_verified") is not True:
            missing.append("benchmark_unverified")
        if model.get("safety_verified") is not True:
            missing.append("safety_unverified")
        cost = model.get("estimated_cost_usd")
        if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not 0 <= cost < float("inf"):
            missing.append("cost_unknown")
        elif cost != 0:
            missing.append("not_free")
        score = model.get("benchmark_score")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 1:
            missing.append("score_invalid")
        if missing:
            rejected.append({"id": model.get("id"), "reasons": missing})
        else:
            eligible.append(model)
    eligible.sort(key=lambda m: (-m["benchmark_score"], str(m.get("id", ""))))
    return {
        "task_family": task_family,
        "training": training,
        "selected": eligible[0]["id"] if eligible else None,
        "eligible_count": len(eligible),
        "rejected": rejected,
        "fallback": "buddy_native" if not eligible else None,
        "note": "Metadata-only selection; does not execute or distill a model.",
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--candidates", type=Path, required=True, help="JSON array of reviewed candidate metadata")
    parser.add_argument("--training", action="store_true")
    args = parser.parse_args()
    taxonomy = load_taxonomy()
    candidates = json.loads(args.candidates.read_text(encoding="utf-8"))
    if not isinstance(candidates, list):
        raise ValueError("Candidates must be a JSON array")
    print(json.dumps(rank_candidates(classify_task(args.task, taxonomy), candidates, training=args.training), indent=2))


if __name__ == "__main__":
    main()
