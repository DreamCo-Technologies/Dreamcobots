# OS Observability (SET 5)

SLO/soak tiles for **Actions · PR · Issues · Agents** on existing Pages surfaces. No parallel dashboard empire.

## Paths

| Artifact | Path |
|----------|------|
| JSON Schema | `reports/schema/os-observability-metrics.schema.json` |
| Fail-closed stub | `reports/os-observability-metrics.stub.json` |
| Pages data | `website/data/os-observability-metrics.json` |
| Tile loader | `website/os-observability.js` |
| Surfaces | `website/actions.html`, `website/os.html` |
| Event bus notes | `reports/BUDDY_OS_SHELL.md` |

## Anti-vanity contract

- Green only with successful evidence on current commit/env + timestamp.
- Yellow / incomplete / stale / cancelled / skipped / planned **never** count as green.
- `os_green_pct = green / (green + red)` only; yellow reported separately.
- Soak = repeated acceptance (default N=3), not a single pass.
- `production_ready` stays `false` until evidence gates say otherwise.
- `agents_vanity_green_blocked` must stay `0`.

## Control-plane feed

When DreamCo Control Plane artifacts exist, overwrite `website/data/os-observability-metrics.json` (and keep the reports stub in sync). Missing or invalid JSON → loader fail-closes to yellow.
