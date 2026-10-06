# Production Connectivity Scan

Generated: 2026-09-21 · `production_ready: false`

## Method
Walk repo (skip node_modules/.git/dist). Count artifacts. Reuse prior plans (Pages, Buddy OS, plan→bot coverage, goals gates, HF, packages). Sample markdown relative links for dangling refs. Merge known SET 2–6 gaps into one disconnect list.

## Counts
| Kind | Count |
| --- | ---: |
| Markdown | 1395 |
| website HTML | 94 |
| Actions workflows | 85 |
| config/* | 376 |
| reports/* | 22 |
| MD links sampled dangling | 0 (cap 40) |

## Already connected (partial)
- `website/actions.html` live (PR review + agents subsection)
- Pages site exists but legacy root → products under `/Dreamcobots/website/`
- PR #9575 frontier claim gates (fail closed)
- Plan→bot coverage 37/37 owners created
- LP-STRATEGIES export local; CP/F0 schemas drafting

## Top disconnects
See `PROD_RESOURCE_CONNECTION_QUEUE.md` (14 P0 / 4 P1 / 0 P2).

## SET 6 owners
Connectivity-Scanner · Resource-Graph · Evidence-Ledger · Config-Triangulator · Docs-Parity · Deps-Licenses · Data-Wiring · API-Surface · Plan-Closure · Cert-Gate

## Policy
Cert-Gate blocks `production_ready` unless connectivity + evidence ledger + soak agree. Yellow ≠ green.
