# Production Resource Connection Queue

Evidence-only. No `production_ready` vanity flips.

## P0
- **missing-page:website/bootcamp.html** — `website/bootcamp.html` · owner `Grok-Prod-Connectivity-Scanner` · Create page + nav absolute /Dreamcobots/website/
- **missing-page:website/packages.html** — `website/packages.html` · owner `Grok-Prod-Connectivity-Scanner` · Create page + nav absolute /Dreamcobots/website/
- **missing-page:website/data-packages.html** — `website/data-packages.html` · owner `Grok-Prod-Connectivity-Scanner` · Create page + nav absolute /Dreamcobots/website/
- **missing-page:website/frontier.html** — `website/frontier.html` · owner `Grok-Prod-Connectivity-Scanner` · Create page + nav absolute /Dreamcobots/website/
- **missing-page:website/issues.html** — `website/issues.html` · owner `Grok-Prod-Connectivity-Scanner` · Create page + nav absolute /Dreamcobots/website/
- **missing-page:website/agents.html** — `website/agents.html` · owner `Grok-Prod-Connectivity-Scanner` · Create page + nav absolute /Dreamcobots/website/
- **missing-page:website/pulls.html** — `website/pulls.html` · owner `Grok-Prod-Connectivity-Scanner` · Create page + nav absolute /Dreamcobots/website/
- **pages-publisher-race** — `.github/workflows/pages.yml vs deploy-buddy-pages` · owner `Grok-Pages-Universe-Linker` · Single publisher; absolute nav
- **path-d-allowlist** — `config/path-d-buddy-selector-allowlist.json` · owner `Grok-OS-Permissions` · Land Path D SoT synced with approved-models allowlist
- **os-event-bus** — `shared/os-event-bus-contract.ts` · owner `Grok-OS-Event-Bus` · Stub contract+catalog+os-events.json
- **buddy-os-bus** — `website/buddy-os-bus.js` · owner `Grok-OS-Pages-Integrator` · Session+event bus across Actions/PR/Issues/Agents
- **frontier-claim-gates** — `PR #9575` · owner `Grok-Buddy-Frontier-Trust` · Merge fail-closed Pages vanity guard
- **study-packs-missing** — `study_packs/` · owner `Grok-HF-Mastery-Coach` · Materialize HF study packs
- **production-ready-zero** — `fleet catalog` · owner `Grok-Prod-Cert-Gate` · Keep 0 vanity flips; evidence ledger only

## P1
- **os-timer-catalog** — `reports/OS_TIMER_CATALOG.md` · owner `Grok-OS-Scheduler` · Catalog ~50 crons; Bootcamp system timer
- **f0-schema** — `schemas/buddy-f0-evidence-packet` · owner `Grok-Buddy-F0-Scorecard` · Land schema; claimable=false
- **lp-strategies** — `buddy/learning LP-STRATEGIES` · owner `Grok-Buddy-Learning-Packager` · PR export; gates false
- **cp-schema-v2** — `capabilities/capability_package.schema` · owner `Grok-Buddy-Capability-Packager` · Land v2 + CP-TASK-ROUTE-L1 stub

## P2 (sample dangling links)

- **cron-contention** — `.github/workflows` (~85) · owner `Grok-OS-Scheduler` · OS timer catalog; Bootcamp system cron off-peak
