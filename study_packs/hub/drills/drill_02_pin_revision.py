#!/usr/bin/env python3
"""Drill 2 - list refs, pin a commit SHA, download config.json at that revision, verify.

Default target: openai/whisper-tiny (seed_models.pack.speech). Only config.json is downloaded,
into a throwaway temp cache. Verifications:
  a) the snapshot folder name equals the pinned SHA
  b) model_info(revision=sha).sha == sha
  c) config.json parses as JSON
  d) blob file name == git blob SHA-1 of the content (non-LFS file integrity)
  e) refs/main in the cache points at the pinned SHA (when pinned to the main head)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

from _common import EXIT_CHECK_FAIL, EXIT_PASS, banner, hub_error_exit


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_id", nargs="?", default="openai/whisper-tiny")
    ap.add_argument("--filename", default="config.json")
    args = ap.parse_args()
    banner("drill_02_pin_revision")

    from huggingface_hub import HfApi, hf_hub_download
    from huggingface_hub.errors import HfHubHTTPError
    api = HfApi()
    try:
        refs = api.list_repo_refs(args.repo_id)
        print("branches:", [(b.name, b.target_commit) for b in refs.branches])
        print("tags    :", [(t.name, t.target_commit) for t in refs.tags])
        print("converts:", [(c.name, c.target_commit) for c in (refs.converts or [])])
        main_ref = next(b for b in refs.branches if b.name == "main")
        sha = main_ref.target_commit
        commits = api.list_repo_commits(args.repo_id)
        print(f"commit history length: {len(commits)}; latest 3:")
        for c in commits[:3]:
            print(f"  {c.commit_id}  {c.created_at}  {c.title!r}")
        print(f"PINNED revision = {sha}")
        info_at = api.model_info(args.repo_id, revision=sha)
    except (HfHubHTTPError, OSError, StopIteration) as exc:
        return hub_error_exit(exc)

    checks: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="hf-drill02-") as cache:
        try:
            path = Path(hf_hub_download(args.repo_id, args.filename, revision=sha, cache_dir=cache))
            path_main = Path(hf_hub_download(args.repo_id, args.filename, revision="main", cache_dir=cache))
        except (HfHubHTTPError, OSError) as exc:
            return hub_error_exit(exc)
        print(f"downloaded: {path}")
        checks["snapshot_dir_is_pinned_sha"] = path.parent.name == sha
        checks["model_info_revision_sha_matches"] = info_at.sha == sha
        data = path.read_bytes()
        try:
            cfg = json.loads(data)
            checks["config_json_parses"] = True
            print(f"config keys (first 8): {sorted(cfg)[:8]} ... model_type={cfg.get('model_type')}")
        except json.JSONDecodeError:
            checks["config_json_parses"] = False
        blob = path.resolve()
        print(f"blob      : {blob}")
        checks["blob_name_equals_git_sha1"] = blob.name == git_blob_sha1(data)
        ref_main = Path(cache) / f"models--{args.repo_id.replace('/', '--')}" / "refs" / "main"
        checks["cache_refs_main_equals_pin"] = ref_main.read_text().strip() == sha
        checks["main_and_pin_same_blob"] = path_main.resolve() == blob
        print(f"size bytes: {len(data)}")

    for k, v in checks.items():
        print(f"  [{'ok' if v else 'FAIL'}] {k}")
    ok = all(checks.values())
    print("RESULT:", "PASS" if ok else "CHECK_FAIL")
    return EXIT_PASS if ok else EXIT_CHECK_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
