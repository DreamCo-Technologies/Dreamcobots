#!/usr/bin/env python3
"""Drill 5 - audit every HF model id referenced by the Dreamcobots configs
(config/huggingface-two-week-study.json student_shortlist + config/hf-capability-download-map.json
seed_models), plus seed_datasets as a secondary section. Metadata API calls only; nothing downloaded.

Per id: exists, gated, license, latest sha (main), last_modified, pipeline_tag, status in
{ok, gated, missing, error}. Writes JSON evidence (default: ../evidence/drill_05_inventory_audit.json).

Exit: 0 audit complete and every model id exists; 1 audit complete but >=1 id missing
(finding - evidence still written); 2 Hub unreachable / unexplained errors.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from _common import (EXIT_CHECK_FAIL, EXIT_HUB_ERROR, EXIT_PASS, banner, inventory, token_present)


def audit_one(api, repo_id: str, kind: str) -> dict:
    from huggingface_hub.errors import HfHubHTTPError, RepositoryNotFoundError
    row = {"repo_id": repo_id, "kind": kind}
    try:
        info = api.model_info(repo_id) if kind == "model" else api.dataset_info(repo_id)
    except RepositoryNotFoundError as exc:
        row.update(exists=False, status="missing",
                   http_status=getattr(getattr(exc, "response", None), "status_code", None))
        return row
    except HfHubHTTPError as exc:
        row.update(exists=None, status="error", error=str(exc)[:300])
        return row
    card = info.card_data.to_dict() if info.card_data else {}
    lic = card.get("license") or next((t.split(":", 1)[1] for t in (info.tags or []) if t.startswith("license:")), None)
    gated = info.gated
    row.update(
        exists=True,
        resolved_id=info.id,
        renamed=info.id != repo_id,
        gated=gated,
        license=lic,
        license_name=card.get("license_name"),
        latest_sha=info.sha,
        last_modified=info.last_modified.isoformat() if info.last_modified else None,
        pipeline_tag=getattr(info, "pipeline_tag", None),
        base_model=card.get("base_model"),
        status="gated" if gated else "ok",
    )
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "evidence" / "drill_05_inventory_audit.json"))
    args = ap.parse_args()
    banner("drill_05_inventory_audit")
    from huggingface_hub import HfApi
    api = HfApi()
    inv = inventory()
    models, datasets = [], []
    try:
        for rid, src in inv["models"].items():
            r = audit_one(api, rid, "model"); r["sources"] = src; models.append(r)
        for rid, src in inv["datasets"].items():
            r = audit_one(api, rid, "dataset"); r["sources"] = src; datasets.append(r)
    except OSError as exc:
        print(f"HUB_ERROR: {exc}")
        return EXIT_HUB_ERROR

    def summary(rows):
        s = {"total": len(rows)}
        for k in ("ok", "gated", "missing", "error"):
            s[k] = sum(1 for r in rows if r["status"] == k)
        return s

    doc = {
        "schema": "dreamco.hf_hub_inventory_audit.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "anonymous": not token_present(),
        "weights_downloaded": False,
        "claimable": False,
        "sources": ["config/huggingface-two-week-study.json", "config/hf-capability-download-map.json"],
        "model_summary": summary(models),
        "dataset_summary": summary(datasets),
        "models": models,
        "datasets": datasets,
        "note": "latest_sha is the main-branch head at audit time; copy it into study_packs/*/sources.json "
                "revision only after license review. Gated status is from Hub metadata, not from accepting terms.",
    }
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    for r in models + datasets:
        print(f"  {r['kind']:<7} {r['status']:<7} gated={str(r.get('gated')):<6} lic={str(r.get('license')):<22} "
              f"sha={str(r.get('latest_sha'))[:12]:<12} {r['repo_id']}")
    print("model_summary  :", doc["model_summary"])
    print("dataset_summary:", doc["dataset_summary"])
    print("evidence written:", out)
    if doc["model_summary"]["error"] or doc["dataset_summary"]["error"]:
        print("RESULT: HUB_ERROR (some lookups errored)")
        return EXIT_HUB_ERROR
    missing = doc["model_summary"]["missing"]
    print("RESULT:", "PASS" if not missing else f"CHECK_FAIL ({missing} inventory model id(s) missing on the Hub)")
    return EXIT_PASS if not missing else EXIT_CHECK_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
