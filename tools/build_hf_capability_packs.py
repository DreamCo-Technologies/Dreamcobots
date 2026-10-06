#!/usr/bin/env python3
"""Materialize Hugging Face capability study-pack folders (metadata only).

Builds the union of packs from:
  - config/huggingface-capability-packs.json   (instruct, code, reason, tools, research, safety)
  - config/hf-capability-download-map.json     (adds embed, rerank, vision, speech, translate, summarize)

Hard rules: no weight downloads, no git-lfs, train_allowed false, revision null and
license "TBD" until pinned during Day-1 review, teacher xai/grok-best-available.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "config" / "huggingface-capability-packs.json"
MAP_SRC = ROOT / "config" / "hf-capability-download-map.json"
STUDY_SRC = ROOT / "config" / "huggingface-two-week-study.json"
OUT_ROOT = ROOT / "study_packs"
REPORT = ROOT / "reports" / "HUGGINGFACE_CAPABILITY_PACKS.md"

TEACHER = "xai/grok-best-available"
DEFAULT_FLOOR = 0.7
LICENSE_TBD = "TBD"
PIN_UNPINNED = "unpinned"

CARD = """# {pack_id}

Capability pack for Buddy study / future student training.

- capabilities: {capabilities}
- sources: {sources_from}
- train_allowed: {train_allowed}
- min_native_pass_rate: {floor}
- teacher: {teacher}
- automatic weight download: no
- git-lfs: not used
- hf_model_pipeline: {pipeline}
- hf_dataset_task: {dataset_task}
- seed models: {n_models} / seed datasets: {n_datasets}
- Day-1 pin status: {pin_status}

## License / revision pins

Every entry in `sources.json` starts with `revision: null`, `license: "TBD"`,
`pin_status: "unpinned"`. Pin exact Hugging Face `repo_id` + `revision` (commit sha)
and a verified license in sources.json before any eval or train job.

## Layout

- `sources.json` — HF ids + revisions + licenses
- `evals.json` — tasks and pass floors
- `recipes/sft.yaml` — stub, not run in default CI
- `recipes/dpo.yaml` — stub, only after SFT eval
- `evidence/` — before/after scores
"""

RECIPE = """# {kind} recipe stub for {pack_id} (metadata only; NOT run in default CI)
schema: dreamco.study_pack_recipe.v1
pack_id: {pack_id}
method: {kind}
enabled: false
train_allowed: false
teacher: {teacher}
student:
  repo_id: null
  revision: null
  license: {license}
datasets: []
prerequisites:
{prereqs}
notes: "Stub only. No weight download, no git-lfs. Fill after Day-1 pins and Phase 3 eval."
"""

SFT_PREREQS = [
    "license allows derivatives",
    "exact revision recorded",
    "contamination check documented",
    "Grok teacher held-out 20-item critique shows student weak on this pack",
]
DPO_PREREQS = ["SFT eval completed and recorded in evidence/"] + SFT_PREREQS


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# Seeds whose Hub card license is already known to be non-commercial. They stay unpinned, but the
# license is labelled now so they cannot drift into a sellable package while still marked "TBD".
KNOWN_NON_COMMERCIAL = {
    "tatsu-lab/alpaca": "cc-by-nc-4.0",
    "facebook/nllb-200-distilled-600M": "cc-by-nc-4.0",
}
NON_COMMERCIAL_NOTE = ("NON-COMMERCIAL (Hub card: cc-by-nc-4.0). Study/eval only; never in paid packages or "
                       "trained-weight outputs sold.")


def _entry(repo_id: str) -> dict:
    if repo_id in KNOWN_NON_COMMERCIAL:
        return {"repo_id": repo_id, "revision": None, "license": KNOWN_NON_COMMERCIAL[repo_id],
                "pin_status": PIN_UNPINNED, "commercial_ok": False, "note": NON_COMMERCIAL_NOTE}
    return {"repo_id": repo_id, "revision": None, "license": LICENSE_TBD, "pin_status": PIN_UNPINNED}


def build_packs() -> list[dict]:
    """Return the ordered union of packs from both configs."""
    caps_doc = _load(SRC)
    map_doc = _load(MAP_SRC)
    seed_models = map_doc.get("seed_models", {})
    seed_datasets = map_doc.get("seed_datasets", {})
    merged: dict[str, dict] = {}
    for pack in caps_doc["packs"]:
        merged[pack["id"]] = {
            "id": pack["id"],
            "capability_ids": list(pack["capability_ids"]),
            "min_native_pass_rate": pack.get("min_native_pass_rate", DEFAULT_FLOOR),
            "search_hints": list(pack.get("search_hints", [])),
            "hf_model_pipeline": None,
            "hf_dataset_task": None,
            "sources_from": ["huggingface-capability-packs.json"],
        }
    for pack in map_doc["packs"]:
        cur = merged.get(pack["id"])
        if cur is None:
            cur = merged[pack["id"]] = {
                "id": pack["id"],
                "capability_ids": [],
                "min_native_pass_rate": DEFAULT_FLOOR,
                "search_hints": [],
                "hf_model_pipeline": None,
                "hf_dataset_task": None,
                "sources_from": [],
            }
        for cap in pack.get("capability_ids", []):
            if cap not in cur["capability_ids"]:
                cur["capability_ids"].append(cap)
        cur["hf_model_pipeline"] = pack.get("hf_model_pipeline")
        cur["hf_dataset_task"] = pack.get("hf_dataset_task")
        for hint in (pack.get("hf_model_pipeline"), pack.get("hf_dataset_task")):
            if hint and hint not in cur["search_hints"]:
                cur["search_hints"].append(hint)
        cur["sources_from"].append("hf-capability-download-map.json")
    for pack in merged.values():
        pack["train_allowed"] = False  # hard rule regardless of config
        pack["seed_models"] = list(dict.fromkeys(seed_models.get(pack["id"], [])))
        pack["seed_datasets"] = list(dict.fromkeys(seed_datasets.get(pack["id"], [])))
    return list(merged.values())


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj: dict) -> None:
    _write(path, json.dumps(obj, indent=2) + "\n")


def write_pack(pack: dict, now: str) -> None:
    dest = OUT_ROOT / pack["id"]
    n_models, n_datasets = len(pack["seed_models"]), len(pack["seed_datasets"])
    _write(
        dest / "CARD.md",
        CARD.format(
            pack_id=pack["id"],
            capabilities=", ".join(pack["capability_ids"]),
            sources_from=", ".join(pack["sources_from"]),
            train_allowed=str(pack["train_allowed"]).lower(),
            floor=pack["min_native_pass_rate"],
            teacher=TEACHER,
            pipeline=pack["hf_model_pipeline"] or "n/a",
            dataset_task=pack["hf_dataset_task"] or "n/a",
            n_models=n_models,
            n_datasets=n_datasets,
            pin_status=PIN_UNPINNED,
        ),
    )
    _write_json(
        dest / "sources.json",
        {
            "schema": "dreamco.study_pack_sources.v1",
            "pack_id": pack["id"],
            "generated_at": now,
            "teacher": TEACHER,
            "automatic_weight_download": False,
            "hf_models": [_entry(r) for r in pack["seed_models"]],
            "hf_datasets": [_entry(r) for r in pack["seed_datasets"]],
            "search_hints": pack["search_hints"],
            "note": "Seeds are inventory targets only. Pin revision + verify license during Day-1 review.",
        },
    )
    _write_json(
        dest / "evals.json",
        {
            "schema": "dreamco.study_pack_evals.v1",
            "pack_id": pack["id"],
            "capability_ids": pack["capability_ids"],
            "floor": pack["min_native_pass_rate"],
            "min_native_pass_rate": pack["min_native_pass_rate"],
            "tasks": [],
            "train_allowed": pack["train_allowed"],
        },
    )
    for kind, prereqs in (("sft", SFT_PREREQS), ("dpo", DPO_PREREQS)):
        _write(
            dest / "recipes" / f"{kind}.yaml",
            RECIPE.format(
                kind=kind,
                pack_id=pack["id"],
                teacher=TEACHER,
                license=LICENSE_TBD,
                prereqs="\n".join(f'  - "{p}"' for p in prereqs),
            ),
        )
    (dest / "evidence").mkdir(parents=True, exist_ok=True)
    (dest / "evidence" / ".gitkeep").touch()


def write_readme(packs: list[dict]) -> None:
    lines = [
        "# DreamCo Study Packs",
        "",
        "Metadata-only Hugging Face capability packs (spec: `docs/HUGGINGFACE_MASTERY_PLAN.md`).",
        "",
        f"- Packs: **{len(packs)}**",
        f"- Teacher: `{TEACHER}`",
        "- Automatic weight download: **no** (no git-lfs)",
        "- train_allowed: **false** for every pack",
        "- All revisions `null` and licenses `TBD` until pinned (see `DAY1_INVENTORY.md`)",
        "",
        "| Pack | Capabilities | Seeds (models + datasets) | train_allowed | Day-1 pin status | Card |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for p in packs:
        seeds = len(p["seed_models"]) + len(p["seed_datasets"])
        lines.append(
            f"| `{p['id']}` | {', '.join(p['capability_ids'])} | {seeds} "
            f"({len(p['seed_models'])} + {len(p['seed_datasets'])}) | "
            f"{str(p['train_allowed']).lower()} | {PIN_UNPINNED} | [CARD.md]({p['id']}/CARD.md) |"
        )
    lines += ["", "Regenerate with `python3 tools/build_hf_capability_packs.py`."]
    _write(OUT_ROOT / "README.md", "\n".join(lines) + "\n")


def write_day1(packs: list[dict]) -> None:
    study = _load(STUDY_SRC)
    day1 = next((d["focus"] for d in study.get("days", []) if d.get("day") == 1), "")
    lines = [
        "# Day 1 Inventory — License, Provenance, Exact Checkpoints",
        "",
        f"Focus: {day1}",
        "",
        "No weights are downloaded. Inspect model/dataset cards and commit history on the Hub only.",
        "",
        "## Checklist",
        "",
        "- [ ] For every seed in `study_packs/*/sources.json`, record the license from the Hub card",
        "- [ ] Confirm license allows eval (and note whether derivatives/training are allowed)",
        "- [ ] Record exact `revision` (commit sha) and set `pin_status` to `pinned`",
        "- [ ] Record provenance: publisher org, gated/ungated, paper or data card link",
        "- [ ] Flag gated / restricted / non-commercial repos; keep `train_allowed: false`",
        "- [ ] Record exact checkpoint inventory for each `student_shortlist` entry below",
        "- [ ] Confirm no weight download and no git-lfs used",
        "",
        "## Seed inventory by pack",
        "",
        "| Pack | Models | Datasets | Status |",
        "| --- | --- | --- | --- |",
    ]
    for p in packs:
        lines.append(
            f"| `{p['id']}` | {len(p['seed_models'])} | {len(p['seed_datasets'])} | "
            f"{PIN_UNPINNED if p['seed_models'] or p['seed_datasets'] else 'no seeds (search_hints only)'} |"
        )
    lines += [
        "",
        "## student_shortlist (inventory targets only — not approved for training)",
        "",
        "| repo_id | license | revision | pin_status |",
        "| --- | --- | --- | --- |",
    ]
    for repo in study.get("student_shortlist", []):
        lines.append(f"| `{repo}` | {LICENSE_TBD} | TBD | {PIN_UNPINNED} |")
    lines += ["", f"Teacher route: `{TEACHER}`."]
    _write(OUT_ROOT / "DAY1_INVENTORY.md", "\n".join(lines) + "\n")


def main() -> int:
    packs = build_packs()
    now = datetime.now(timezone.utc).isoformat()
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for pack in packs:
        write_pack(pack, now)
    ids = [p["id"] for p in packs]
    _write_json(
        OUT_ROOT / "index.json",
        {
            "schema": "dreamco.study_packs_index.v1",
            "generated_at": now,
            "teacher": TEACHER,
            "automatic_weight_download": False,
            "train_in_default_ci": False,
            "count": len(ids),
            "packs": ids,
            "lanes": [
                {
                    "id": p["id"],
                    "capability_ids": p["capability_ids"],
                    "floor": p["min_native_pass_rate"],
                    "train_allowed": p["train_allowed"],
                    "seed_models": len(p["seed_models"]),
                    "seed_datasets": len(p["seed_datasets"]),
                    "pin_status": PIN_UNPINNED,
                    "card": f"{p['id']}/CARD.md",
                }
                for p in packs
            ],
        },
    )
    write_readme(packs)
    write_day1(packs)
    lines = [
        "# Hugging Face Capability Packs",
        "",
        f"- Packs: **{len(ids)}**",
        "",
        "| Pack | Capabilities | Floor | Seeds | Train allowed |",
        "| --- | --- | --- | --- | --- |",
    ]
    for p in packs:
        lines.append(
            f"| `{p['id']}` | {', '.join(p['capability_ids'])} | {p['min_native_pass_rate']} | "
            f"{len(p['seed_models']) + len(p['seed_datasets'])} | {p['train_allowed']} |"
        )
    _write(REPORT, "\n".join(lines) + "\n")
    print(json.dumps({"ok": True, "count": len(ids), "packs": ids}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
