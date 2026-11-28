# Stage 08 Repo Sentinel

## What it does

- Scans top-level Python functions, async functions, and classes under configured roots.
- Reports duplicate symbols and syntax/encoding errors.
- Consolidates only AST-identical duplicates when a canonical owner is explicitly registered.
- Leaves semantically different implementations untouched for human review. It never picks the longest or newest implementation.
- Audits FreeCodeCamp catalog freshness and can run the existing Stage 00 append-only metadata delta sync when the catalog is stale.

## Safe AST behavior

The default is audit-only. Rewriting requires both `--apply-ast` and an explicit `--backup-dir`. Before replacing a duplicate definition, the tool verifies that its AST digest exactly matches the registered canonical implementation. It writes a backup first and validates the rewritten module syntax. Unknown owners and semantic conflicts are reported, not modified.

The forwarding shim uses `importlib.import_module` so stage directory names such as `00_catalog_sync` do not create invalid Python import syntax.

## FreeCodeCamp sync

The compatibility entry point `stages/00_catalog_sync/sync_fcc_catalog.py` delegates to the existing append-only Stage 00 catalog implementation and uses the official FreeCodeCamp channel URL from the Sentinel registry. The underlying policy registry must allow metadata cataloging. Only metadata is fetched; media and transcripts are never downloaded.

The scheduled workflow refreshes a stale catalog and opens or updates a reviewable pull request for the JSONL delta. It does not push catalog data directly to the default branch.

## Run locally

```sh
python stages/08_repo_sentinel/sentinel.py --report reports/repo-sentinel/sentinel_report.json
python stages/08_repo_sentinel/sentinel.py --sync-fcc
python stages/08_repo_sentinel/sentinel.py --apply-ast --backup-dir .sentinel_backups
python -m unittest discover -s tests -p 'test_repo_sentinel.py' -v
```

## Limitations

The AST digest proves structural identity of the parsed node, not equivalence of the entire module environment. Import side effects and runtime behavior still require tests. Eight-token originality checks are similarly heuristic and do not establish legal originality or rights. All commercial-use decisions remain with the policy and human-review gates.
