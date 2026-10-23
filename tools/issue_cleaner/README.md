# Intelligent Issue Cleaner — read-only evidence review

The scheduled job inspects up to **500 open issues** per run. It no longer closes or labels issues. A newer failed workflow run is **not** proof that an older failure has been resolved.

## Behavior

| Record | Read-only result |
|---|---|
| `Actions run <id> failed: <workflow>` | Identify the newest two signals and list older records as potential supersession candidates; **preserve all issues** |
| `DreamCo failure root cause [key]: ...` | Identify possible duplicates; **preserve all issues** |
| Human-created issues and comments | **Never mutate** |
| Labels | **Never change** |

The script reports `would_close_superseded_ci` and `would_close_dup_root` as **review candidates**, not successful closures. The `closed_*` and `labeled` counts remain zero.

## Verification and schedule

The workflow runs hourly at minute 17 UTC and can be manually triggered. It uses only read permissions, forces `DRY_RUN=1`, and runs `python3 -m unittest tests.test_issue_cleaner_read_only` before scanning. Dispatch inputs cannot enable mutations.

An issue may be closed only through a **separate, explicitly authorized, evidence-backed review** that links passing tests and a verified fix. This scanner has no issue-closing path.
