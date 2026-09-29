#!/usr/bin/env python3
"""Drill 4 - snapshot_download with allow_patterns (configs + tokenizer only) into a temp cache,
then print the cache layout (blobs / refs / snapshots) and scan_cache_dir summary.

Default target: sentence-transformers/all-MiniLM-L6-v2 (seed_models.pack.embed).
Fails (exit 1) if any weight-like file lands in the cache or total size exceeds --max-mb.
"""
from __future__ import annotations

import argparse
import os
import shutil
import tempfile
from pathlib import Path

from _common import EXIT_CHECK_FAIL, EXIT_PASS, banner, hub_error_exit, is_weight

PATTERNS = ["config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json",
            "vocab.txt", "modules.json", "sentence_bert_config.json", "config_sentence_transformers.json",
            "README.md"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_id", nargs="?", default="sentence-transformers/all-MiniLM-L6-v2")
    ap.add_argument("--max-mb", type=float, default=10.0)
    ap.add_argument("--keep", action="store_true", help="keep the temp cache for inspection")
    args = ap.parse_args()
    banner("drill_04_snapshot_patterns")
    from huggingface_hub import HfApi, scan_cache_dir, snapshot_download
    from huggingface_hub.errors import HfHubHTTPError

    try:
        sha = HfApi().model_info(args.repo_id).sha
    except (HfHubHTTPError, OSError) as exc:
        return hub_error_exit(exc)
    cache = tempfile.mkdtemp(prefix="hf-drill04-")
    print(f"temp cache_dir: {cache}")
    print(f"allow_patterns: {PATTERNS}")
    try:
        snap = snapshot_download(args.repo_id, revision=sha, cache_dir=cache, allow_patterns=PATTERNS)
    except (HfHubHTTPError, OSError) as exc:
        shutil.rmtree(cache, ignore_errors=True)
        return hub_error_exit(exc)
    print(f"snapshot path : {snap}")
    print("cache layout:")
    total, weights = 0, []
    for root, dirs, files in sorted(os.walk(cache)):
        depth = Path(root).relative_to(cache).parts
        indent = "  " * len(depth)
        print(f"{indent}{Path(root).name}/")
        for f in sorted(files):
            p = Path(root) / f
            if p.is_symlink():
                print(f"{indent}  {f} -> {os.readlink(p)}")
            else:
                size = p.stat().st_size
                total += size
                print(f"{indent}  {f}  ({size} B)")
            if is_weight(f):
                weights.append(str(p))
    info = scan_cache_dir(cache)
    for repo in info.repos:
        print(f"scan_cache_dir: {repo.repo_type} {repo.repo_id} size_on_disk={repo.size_on_disk} "
              f"revisions={[r.commit_hash for r in repo.revisions]} files={repo.nb_files}")
    print(f"total blob bytes: {total} ({total/1e6:.2f} MB); weight files: {weights}")
    ok = not weights and total <= args.max_mb * 1e6 and Path(snap).name == sha
    if args.keep:
        print(f"kept cache at {cache}")
    else:
        shutil.rmtree(cache, ignore_errors=True)
    print("RESULT:", "PASS" if ok else "CHECK_FAIL")
    return EXIT_PASS if ok else EXIT_CHECK_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
