# BRANCH_PLAN_READINESS

**Owner:** Grok-Branch-Plan-Steward  
**Repo:** DreamCo-Technologies/Dreamcobots (canonical fleet)  
**Policy:** Keep this file current. Document what each branch needs to work as planned. Prefer **supersede** / **rebase** language only — **no mass deletes**.

Companion operational scan: `reports/branch-health-daily.md` + `reports/branch-health-daily.json` (from `tools/branch_health_daily.py`). That report measures freshness / completeness / mergeability / safety / scope. This file maps **plan intent → branch work → readiness gaps**.

---

## Snapshot (steward first pass — 2026-09-21 CT)

| Signal | Value | Notes |
|---|---|---|
| Live branches (`main` default) | **398** (Sep 28; was 391 on Sep 21) | `gh` branch list |
| Last daily health scan | **2026-09-19** | `reports/branch-health-daily.*` |
| Scan branch count | 372–373 | Scan is ~2 days behind live count |
| Healthy / watch / blocked (scan) | **0 / 293 / 79** | Zero healthy — most work is watch or blocked |
| Open PRs (scan) | 14 | Auto-merge to `main` is off |
| HQ board repo branches | `main` + dependabot | `ireanjordan24/Dreamcobots-Grok-Revolutionary` is not the branch surface |

**Status of this doc:** Was **missing** on `main` (checked `docs/`, `reports/`, repo root, `evidence/`). This file is the steward baseline; treat prior informal notes as superseded by this revision when merged.

---

## Operating rules (non-negotiable)

1. **No mass deletes.** Stale or superseded lines of work stay until a successor branch/PR clearly replaces them.
2. Say **superseded by** `branch-or-PR` or **rebase onto** `main` / named base — never “delete all X”.
3. A branch is **plan-ready** only when required paths exist, it is not hopelessly behind `main` without a rebase plan, and its PR (if any) states the plan outcome + evidence.
4. Money / Stripe / DreamPayments paths: conflict automation must not force-merge; steward notes them as **safety-gated**.
5. Inventory ≠ mastery. Listing a branch here does not certify production.

### Required paths (from branch-health REQUIRED set)

A branch working “as planned” for site/fleet continuity should retain:

- `website/buddy.html`, `website/index.html`, `website/nav.js`
- `website/connections.html`, `website/wiring.html`, `website/desks.css`
- `.github/workflows/pages.yml`
- `AGENTS.md`, `README.md`

Missing any of these → **blocked** until restored or explicitly superseded by a docs/site successor plan.

---

## Branch families → what they need

| Family (prefix) | Approx. live count | Plan role | Needs to work as planned |
|---|---:|---|---|
| `copilot/` | ~258 | Exploratory / agent PRs | Most are far behind `main`. Prefer **rebase onto main** or mark **superseded by** a current `feat/` / `grok/` line. Do not mass-delete. |
| `feat/` | ~38 | Feature tracks | Open or refresh PR; restore missing REQUIRED files; rebase when behind ≫ ahead. |
| `codex/` | ~15 | Codex plan tracks | Same as `feat/`; several blocked on `pages.yml`. |
| `agent/` | ~9 | Agent experiment lines | Many 1000+ behind; **supersede** with a single current agent line when intent duplicates (v2/v3). |
| `actions-control-plane-batch-*` / `feat/actions-control-plane-*` | ~8+ | Actions control plane batches | Batch-01 has PR #5123; others need rebase + `pages.yml` or explicit supersession by the live control-plane branch. |
| `buddy*` / `feat/buddy-openrouter-*` / PR-recovery series | many | Buddy ops / OpenRouter / PR backlog | Classic version sprawl (`v2`…`v10`, `q`…`z`). Keep newest intended line; older siblings **superseded by** that tip — do not delete. |
| `grok/` | ~5 | Steward / Grok operator lines | Keep near `main`; use for readiness/docs PRs. |
| `dependabot/` | ~5 | Dependency bumps | Merge or rebase when green; skip money-gated conflicts. |
| `dreamco/` | ~9 | DreamCo-named tracks | Map each to a named plan owner before promoting. |
| `main` | 1 | Integration trunk | Source of truth; no auto-merge from health bot. |

Empire HQ (`Dreamcobots-Grok-Revolutionary`) stays on `main` for board/docs — branch readiness work lands in the **fleet** repo unless HQ explicitly needs a plan branch.

---

## Top blocked themes (from 2026-09-19 scan)

1. **Missing `.github/workflows/pages.yml`** — dominant blocker across agent/codex/actions/65-masterbot lines. Fix: restore from `main` via rebase, or supersede with a pages-aware successor.
2. **Missing `website/wiring.html` / `website/desks.css`** — blocks mergeability for several near-main branches (incl. some `grok/` / dependabot). Fix: bring those files from `main` before merge.
3. **Extreme behind counts (300–1500+)** — branch cannot “work as planned” until **rebase onto main** (or declared superseded).
4. **Version forks** (openrouter `q`–`z`, PR-recovery `v3`–`v10`, civic education v2/v3) — pick tip of intent; mark siblings superseded.

---

## Readiness grades (steward)

| Grade | Meaning |
|---|---|
| **R0** | No active plan; historical / superseded |
| **R1** | Intent known; behind or missing REQUIRED paths |
| **R2** | Rebased or near `main`; REQUIRED present; PR open with plan outcome |
| **R3** | CI green + evidence cited; ready for human merge decision |
| **R4** | Merged to `main` / plan certified elsewhere |

Most of the fleet is **R0–R1** today. Target for active plan owners: move their tip branch to **R2+** without deleting superseded siblings.

---

## Steward backlog

- [ ] Merge this file to `main` (create if absent; later edits supersede in place).
- [ ] Refresh link to latest `branch-health-daily` after next workflow run.
- [ ] For each active plan steward (Bootcamp, Frontier, Model Access, …), name **one** tip branch and list superseded siblings.
- [ ] Re-scan when live branch count drifts >10 from last health report.

---

## Changelog

| Date | Change |
|---|---|
| 2026-09-28 | Live branch count refreshed to 398; daily health report still dated 2026-09-19 (stale 9 days). Doc still absent on `main`. |
| 2026-09-21 | Initial steward baseline. Doc was missing on `main`; seeded from `reports/branch-health-daily` (2026-09-19) + live branch inventory (391). Supersedes informal absence of a branch-plan readiness surface. |
