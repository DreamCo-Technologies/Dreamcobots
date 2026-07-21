# Buddy Source Fusion Report

Scan local source pools for bots, code, instructions, and data, then identify what is already active, preserved, or worth promoting into Buddy's unified system.

## Completion Estimate

- Registry And Buddy Connection: 100%
- Source Recovery And Archiving: 95%
- Actions Page Visibility: 92%
- Sandbox And Local First Policy: 90%
- All Bot End To End Testing: 62%
- Production Runtime Depth Per Bot: 58%
- Overall Buildout Estimate: 82%

## Source Scan Summary

- Master registry bots: 1230
- Sources scanned: 4
- Useful unique candidates: 4869
- Policy-excluded candidates: 11520
- Missing bot slug candidates: 751
- Duplicate bot slug candidates: 2053

## Source Summaries

### active_recovery

- bot: 2375
- code: 7686
- data_config: 451
- files_read: 10979
- instruction: 153
- other: 314

### new_project


### github_desktop

- bot: 7157
- code: 2316
- data_config: 467
- files_read: 10124
- instruction: 57
- other: 127

### codex_archives

- bot: 25986
- code: 29807
- data_config: 1153
- excluded_policy: 11520
- files_read: 58515
- instruction: 1029
- other: 540

## Fusion Policy

- Keep the recovery repo as the source of truth.
- Do not overwrite active files with same-path older copies.
- Promote bot/code/instruction/data candidates only after they pass banned-name, syntax, registry, and build checks.
- Treat every imported bot as Buddy-governed, local-first, sandbox-first, and approval-gated for live actions.
- Store only useful compact summaries, source references, test results, approval packets, and reusable capability data.

## Next Actions

- Review missing_bot_slug_sample and promote only real bots that are not duplicates or generated cache files.
- Map useful unique instructions into Buddy's capability, workflow, prompt, sandbox, and API libraries.
- Turn archived command-center code into active modules only after targeted tests prove it improves the current app.
