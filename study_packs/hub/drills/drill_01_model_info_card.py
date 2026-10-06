#!/usr/bin/env python3
"""Drill 1 - HfApi.model_info + model card YAML metadata + license for an inventory model.

Default target: BAAI/bge-small-en-v1.5 (config/hf-capability-download-map.json seed_models.pack.embed).
Downloads only README.md (the model card). Exit codes: see _common.py.
"""
from __future__ import annotations

import argparse
import sys

from _common import EXIT_CHECK_FAIL, EXIT_PASS, EXIT_USAGE, banner, hub_error_exit, inventory


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_id", nargs="?", default="BAAI/bge-small-en-v1.5")
    args = ap.parse_args()
    banner("drill_01_model_info_card")
    inv = inventory()["models"]
    if args.repo_id not in inv:
        print(f"USAGE: {args.repo_id} is not in the Dreamcobots inventory", file=sys.stderr)
        return EXIT_USAGE
    print(f"inventory source(s): {inv[args.repo_id]}")

    from huggingface_hub import HfApi, ModelCard
    from huggingface_hub.errors import HfHubHTTPError, RepositoryNotFoundError
    api = HfApi()
    try:
        info = api.model_info(args.repo_id)
    except RepositoryNotFoundError as exc:
        print(f"CHECK_FAIL: repo not found: {exc}")
        return EXIT_CHECK_FAIL
    except (HfHubHTTPError, OSError) as exc:
        return hub_error_exit(exc)

    card = info.card_data.to_dict() if info.card_data else {}
    print(f"id            : {info.id}")
    print(f"sha (main)    : {info.sha}")
    print(f"last_modified : {info.last_modified}")
    print(f"gated         : {info.gated}")
    print(f"private       : {info.private}")
    print(f"pipeline_tag  : {info.pipeline_tag}")
    print(f"library_name  : {info.library_name}")
    print(f"downloads     : {info.downloads}  likes: {info.likes}")
    print(f"card.license  : {card.get('license')}")
    print(f"card.base_model: {card.get('base_model')}")
    print(f"card.language : {card.get('language')}")
    lic_tags = [t for t in (info.tags or []) if t.startswith("license:")]
    print(f"license tags  : {lic_tags}")
    print(f"siblings      : {len(info.siblings or [])} files (not downloaded)")

    # Load the actual model card (README.md) and show its YAML header keys.
    try:
        mc = ModelCard.load(args.repo_id)
        yaml_keys = sorted(mc.data.to_dict().keys())
        print(f"README YAML keys: {yaml_keys}")
        print(f"README body chars: {len(mc.text)}")
    except Exception as exc:  # card may be missing; that is itself a finding
        print(f"CHECK_FAIL: could not load model card: {type(exc).__name__}: {exc}")
        return EXIT_CHECK_FAIL

    ok = bool(card.get("license")) and info.sha is not None
    print("RESULT:", "PASS" if ok else "CHECK_FAIL (license or sha missing)")
    return EXIT_PASS if ok else EXIT_CHECK_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
