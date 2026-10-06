# Final production certification gate (SET 6)

Owner: **Grok-Prod-Cert-Gate**  
Aligned with: **Grok-PRC-Certifier** + Frontier-Trust [PR #9575](https://github.com/DreamCo-Technologies/Dreamcobots/pull/9575)

## Hard rule

`production_ready` / ship / `claimable` is **blocked** unless **all three** pillars are green with linked evidence on the **same git SHA** (CI success + runtime proof where required).

**Vanity greens do not count:** profile completeness, keep-green alone, Empire HQ `GROK_CERTIFIED.md`, checklist ticks without artifacts, status emoji.

## Three pillars

| Pillar | Must be green | Canonical evidence | PR #9575 map |
|--------|---------------|--------------------|--------------|
| **Connectivity** | Runtime/connection truth — not config-only | Full-system `resource_connections` + connection_rule in `config/full-system-operational-certification.json`; adapters via `config/buddy/500-model-operating-contract.json` + `config/buddy-frontier-readiness-gates.json` (`never_claim_frontier_without_evidence: true`); platform/bot reports must not claim connected without probe evidence | Allowlist + model contract |
| **Ledger** | Evidence ledger shape + PRC outputs current | Contract: `config/production-readiness-contract.json`. Platform: `data/production-readiness-report.json` + `reports/PRODUCTION_READINESS_REPORT.md`. Fleet: `config/generated/bot-production-readiness.json` + `reports/BOT_PRODUCTION_READINESS.md`. Full-system: `config/full-system-operational-certification.json`. Frontier claim: `evidence/frontier/current-status.assessment.json`. Entry shape: **Grok-Prod-Evidence-Ledger schema v0.1** (claim→artifact→SHA→soak + CI + runtime on SAME git SHA) | Provenance + disclosure/`claimable` |
| **Soak** | Timed sandbox soak passed | Workflow `.github/workflows/buddy-24h-sandbox-soak.yml` + `tools/run_24h_sandbox_soak.py` → tick `config/generated/sandbox-24h-tick.json` (`sandbox_tick_ok`) + `reports/SANDBOX_24H.md` | Sandbox soak |

## Checklist (fail closed)

### A. Connectivity
- [ ] No integration marked runtime-verified without a successful probe (full-system connection_rule)
- [ ] Operating contract + readiness gates present; `never_claim_frontier_without_evidence` is true
- [ ] Bot-scoped `adapter_configured` / `auth_scoped` only true with artifact links

### B. Ledger
- [ ] `config/production-readiness-contract.json` release_blockers / status_rules respected
- [ ] Platform gate outputs present and current for the certify SHA
- [ ] Bot fleet report present; `production_ready_true` only when evidence_complete (today: **0 / 1101**)
- [ ] Frontier assessment honest: ship requires `claimable: true` and `status: claimable`
- [ ] Evidence-Ledger v0.1 entries: claim → artifact → SHA → soak + CI + runtime (same SHA)

### C. Soak
- [ ] Soak workflow/tool run recorded for the certify SHA
- [ ] `sandbox-24h-tick.json` status `sandbox_tick_ok`
- [ ] `reports/SANDBOX_24H.md` present for the same window (stale ticks = red)

### D. Vanity blockers (auto-fail)
- [ ] `tools/check_frontier_claim_trust_gates.py` — no vanity Pages copy while gates red
- [ ] Profile greens from `tools/ensure_bots_production_ready.py` ≠ runtime production
- [ ] Empire HQ `GROK_CERTIFIED.md` ≠ final gate pass
- [ ] Keep-green / partial CI ≠ certify

## Certify decision

```
IF connectivity AND ledger AND soak
   AND CI success + runtime proof on SAME git SHA:
  MAY set production_ready / claimable (owner approval still required for external actions)
ELSE:
  MUST keep production_ready=false AND claimable=false
  MUST fail closed on claim/deploy (--require-all-gates)
```

## PRC references (cite these)

- `docs/PRODUCTION_READINESS_MASTER_PLAN.md`
- `docs/BOT_PRODUCTION_READINESS.md`
- `config/production-readiness-contract.json`
- `config/full-system-operational-certification.json`
- Workflows: `production-readiness.yml`, `bot-production-readiness.yml`, `full-system-certification.yml`, `buddy-24h-sandbox-soak.yml`

## Current gate posture (SET 6 + PRC align)

| Pillar | Status | Notes |
|--------|--------|-------|
| Connectivity | Partial | Contracts/gates present; connection_rule requires runtime probes |
| Ledger | Red for ship | Assessment `claimable: false`; fleet `production_ready_true: 0` |
| Soak | Missing artifacts on `main` | Soak workflow/tool exist; tick + SANDBOX_24H.md not on `main` |

**Decision: DO NOT certify. DO NOT flip `production_ready`.**
