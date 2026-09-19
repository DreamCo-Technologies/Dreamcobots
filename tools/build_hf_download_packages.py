#!/usr/bin/env python3
"""Build downloadable Hugging Face capability package manifests.

Does not download weights. Writes pinned package folders and an opt-in
download script. "Everything on Hugging Face" is not a valid target.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "config" / "hf-capability-download-map.json"
OUT = ROOT / "study_packs" / "hf_packages"
REPORT = ROOT / "reports" / "HF_DOWNLOADABLE_PACKAGES.md"
SCRIPT = ROOT / "tools" / "download_hf_package.sh"


def item(repo_id: str, kind: str) -> dict:
    return {
        "repo_id": repo_id,
        "kind": kind,
        "revision": "main",
        "revision_must_be_pinned_before_train": True,
        "license": "verify-on-model-card",
        "download": False,
        "hub_url": f"https://huggingface.co/{'' if kind == 'model' else 'datasets/'}{repo_id}".replace("datasets/datasets/", "datasets/"),
    }


def main() -> int:
    mapping = json.loads(MAP.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    packages = []
    for pack in mapping["packs"]:
        pack_id = pack["id"]
        dest = OUT / pack_id
        dest.mkdir(parents=True, exist_ok=True)
        models = [item(repo, "model") for repo in mapping.get("seed_models", {}).get(pack_id, [])][: mapping["max_items_per_pack"]]
        datasets = [item(repo, "dataset") for repo in mapping.get("seed_datasets", {}).get(pack_id, [])][: mapping["max_items_per_pack"]]
        manifest = {
            "schema": "dreamco.hf_capability_package.v1",
            "pack_id": pack_id,
            "capability_ids": pack["capability_ids"],
            "hf_model_pipeline": pack.get("hf_model_pipeline"),
            "hf_dataset_task": pack.get("hf_dataset_task"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "models": models,
            "datasets": datasets,
            "automatic_download": False,
            "how_to_download": f"HF_PACK={pack_id} bash tools/download_hf_package.sh",
        }
        (dest / "package.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        packages.append(manifest)
    index = {
        "schema": "dreamco.hf_capability_package_index.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(packages),
        "covers_entire_huggingface_hub": False,
        "automatic_download_in_ci": False,
        "packs": [row["pack_id"] for row in packages],
    }
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    SCRIPT.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\n"
        "# Opt-in downloader. Not used by default GitHub Actions.\n"
        "PACK=${HF_PACK:?set HF_PACK to a pack id such as pack.code}\n"
        "DEST=${HF_DEST:-$HOME/dreamco-hf-packages/$PACK}\n"
        "MANIFEST=study_packs/hf_packages/$PACK/package.json\n"
        "if ! command -v huggingface-cli >/dev/null 2>&1; then\n"
        "  echo 'Install huggingface_hub CLI first' >&2\n"
        "  exit 1\nfi\n"
        "mkdir -p \"$DEST\"\n"
        "python3 - <<'PY'\n"
        "import json, os, pathlib\n"
        "pack=os.environ['PACK']\n"
        "manifest=json.loads(pathlib.Path(f'study_packs/hf_packages/{pack}/package.json').read_text())\n"
        "print('Would download', len(manifest['models']), 'models and', len(manifest['datasets']), 'datasets to', os.environ.get('HF_DEST'))\n"
        "print('Pin revisions and confirm licenses before huggingface-cli download')\n"
        "PY\n",
        encoding="utf-8",
    )
    lines = [
        "# Hugging Face Downloadable Capability Packages",
        "",
        "These are **capability packages**, not a dump of the entire Hub.",
        "",
        f"- Packs: **{len(packages)}**",
        "- CI download: **off**",
        "",
        "| Pack | Models | Datasets |",
        "| --- | --- | --- |",
    ]
    for row in packages:
        lines.append(f"| `{row['pack_id']}` | {len(row['models'])} | {len(row['datasets'])} |")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "packs": len(packages), "covers_entire_hub": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
