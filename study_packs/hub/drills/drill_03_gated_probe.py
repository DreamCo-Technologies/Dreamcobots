#!/usr/bin/env python3
"""Drill 3 - gated-repo probe: classify each repo as accessible / needs-token / needs-accept / missing.

Never crashes on 401/403/404. Probes by attempting to fetch config.json metadata only
(HEAD via get_hf_file_metadata; no file body is written). Default targets are inventory repos
chosen to cover both open and gated cases.

Exit: 0 if every probe was classified (any class is a valid result), 2 if the Hub was unreachable,
1 if a probe returned an unexplained error.
"""
from __future__ import annotations

import argparse

from _common import EXIT_CHECK_FAIL, EXIT_HUB_ERROR, EXIT_PASS, banner, token_present

DEFAULT = [
    "sentence-transformers/all-MiniLM-L6-v2",  # open
    "meta-llama/Llama-Guard-3-1B",             # gated (Meta license)
    "meta-llama/Llama-3.1-8B-Instruct",        # gated
    "google/gemma-2-9b-it",                    # gated (Gemma terms)
    "mistralai/Mistral-Large-Instruct",        # inventory id; may not exist
]


def probe(repo_id: str) -> dict:
    from huggingface_hub import HfApi, get_hf_file_metadata, hf_hub_url
    from huggingface_hub.errors import (EntryNotFoundError, GatedRepoError, HfHubHTTPError,
                                        RepositoryNotFoundError)
    api = HfApi()
    row = {"repo_id": repo_id, "gated_flag": None, "http_status": None}
    try:
        info = api.model_info(repo_id)
        row["gated_flag"] = info.gated
    except RepositoryNotFoundError as exc:
        row.update(status="missing", http_status=getattr(exc.response, "status_code", None),
                   note="model_info: repo not found (or private) - anonymous 401/404")
        return row
    except HfHubHTTPError as exc:
        row.update(status="error", note=str(exc)[:200])
        return row
    try:
        meta = get_hf_file_metadata(hf_hub_url(repo_id, "config.json"))
        row.update(status="accessible", http_status=200, note=f"config.json etag={meta.etag} size={meta.size}")
    except GatedRepoError as exc:
        code = getattr(exc.response, "status_code", None)
        row["http_status"] = code
        if not token_present() or code == 401:
            row.update(status="needs-token", note="gated repo; anonymous request refused (401). Log in + accept terms.")
        else:
            row.update(status="needs-accept", note="token sent but terms not accepted for this account (403).")
    except EntryNotFoundError:
        row.update(status="accessible", http_status=404, note="repo readable but has no config.json")
    except RepositoryNotFoundError as exc:
        row.update(status="missing", http_status=getattr(exc.response, "status_code", None))
    except HfHubHTTPError as exc:
        row.update(status="error", http_status=getattr(exc.response, "status_code", None), note=str(exc)[:200])
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_ids", nargs="*", default=DEFAULT)
    args = ap.parse_args()
    banner("drill_03_gated_probe")
    from huggingface_hub import whoami
    try:
        me = whoami()
        print(f"whoami: {me.get('name')} (token scopes: {me.get('auth', {}).get('accessToken', {}).get('role')})")
    except Exception as exc:
        print(f"whoami: anonymous ({type(exc).__name__})")
    rows = []
    for rid in args.repo_ids:
        try:
            rows.append(probe(rid))
        except OSError as exc:
            print(f"HUB_ERROR probing {rid}: {exc}")
            return EXIT_HUB_ERROR
    for r in rows:
        print(f"  {r['status']:<13} http={r['http_status']!s:<5} gated={r['gated_flag']!s:<7} {r['repo_id']}  {r.get('note','')}")
    errors = [r for r in rows if r["status"] == "error"]
    print("RESULT:", "PASS" if not errors else f"CHECK_FAIL ({len(errors)} unexplained errors)")
    return EXIT_PASS if not errors else EXIT_CHECK_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
