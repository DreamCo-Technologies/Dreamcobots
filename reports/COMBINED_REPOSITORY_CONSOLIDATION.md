# Combined Repository Consolidation

Generated: 2026-07-21T03:17:04Z

## Result

- Active source of truth: `/Users/mamas/Documents/New project/dreamcobots-recovery`
- Recovery files read: 11097
- External source files read: 45765
- Sources compared: 7
- Safe unique candidates: 38
- Outside-builder metadata excluded: 5314

## Policy

- Do not blindly overwrite the active recovery repo.
- Preserve old code in archives first, then promote only tested pieces.
- Keep outside-builder-specific metadata out of the repository.
- Run local checks before anything becomes active.

## Source Comparison

### github_desktop_copy

- Files read: 10237
- Already active with same content: 9591
- Same path but changed content: 390
- Already preserved in archive with same content: 178
- Preserved in archive with changed content: 40
- Safe unique candidates: 38
- Excluded outside-builder metadata: 0

Unique safe sample:
- `.local_buddy_runner.pid`
- `.pytest_cache/.gitignore`
- `.pytest_cache/CACHEDIR.TAG`
- `.pytest_cache/README.md`
- `.pytest_cache/v/cache/lastfailed`
- `.pytest_cache/v/cache/nodeids`
- `logs/local_buddy_runner/20260717T132306Z-aggressive.json`
- `logs/local_buddy_runner/20260717T132316Z-cheap.json`
- `logs/local_buddy_runner/20260717T135155Z-aggressive.json`
- `logs/local_buddy_runner/20260717T140322Z-aggressive.json`
- `logs/local_buddy_runner/20260717T140400Z-aggressive.json`
- `logs/local_buddy_runner/20260717T141553Z-aggressive.json`
- `logs/local_buddy_runner/20260717T141634Z-aggressive.json`
- `logs/local_buddy_runner/20260717T142301Z-aggressive.json`
- `logs/local_buddy_runner/20260717T142337Z-aggressive.json`
- `logs/local_buddy_runner/20260717T143028Z-aggressive.json`
- `logs/local_buddy_runner/20260717T143902Z-aggressive.json`
- `logs/local_buddy_runner/20260717T145047Z-aggressive.json`
- `logs/local_buddy_runner/20260717T151456Z-aggressive.json`
- `logs/local_buddy_runner/20260717T152419Z-aggressive.json`

### codex_zip:dreamco-command-center-main.zip

- Files read: 328
- Already active with same content: 0
- Same path but changed content: 5
- Already preserved in archive with same content: 288
- Preserved in archive with changed content: 27
- Safe unique candidates: 0
- Excluded outside-builder metadata: 8

### codex_zip:dreamcobots-buddy-dashboard.zip

- Files read: 7064
- Already active with same content: 5341
- Same path but changed content: 469
- Already preserved in archive with same content: 107
- Preserved in archive with changed content: 85
- Safe unique candidates: 0
- Excluded outside-builder metadata: 1062

### codex_zip:dreamcobots-main-final.zip

- Files read: 7050
- Already active with same content: 5335
- Same path but changed content: 467
- Already preserved in archive with same content: 104
- Preserved in archive with changed content: 82
- Safe unique candidates: 0
- Excluded outside-builder metadata: 1062

### codex_zip:dreamcobots-main-latest.zip

- Files read: 7047
- Already active with same content: 5331
- Same path but changed content: 468
- Already preserved in archive with same content: 104
- Preserved in archive with changed content: 82
- Safe unique candidates: 0
- Excluded outside-builder metadata: 1062

### codex_zip:dreamcobots-main.zip

- Files read: 6983
- Already active with same content: 5275
- Same path but changed content: 469
- Already preserved in archive with same content: 99
- Preserved in archive with changed content: 82
- Safe unique candidates: 0
- Excluded outside-builder metadata: 1058

### codex_zip:dreamcobots-stripe-tracking.zip

- Files read: 7056
- Already active with same content: 5339
- Same path but changed content: 466
- Already preserved in archive with same content: 105
- Preserved in archive with changed content: 84
- Safe unique candidates: 0
- Excluded outside-builder metadata: 1062
