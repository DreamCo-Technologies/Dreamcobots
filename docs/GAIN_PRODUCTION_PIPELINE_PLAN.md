# plan-gain-production-pipeline (DRAFT, local only, not pushed)

Status: DRAFT 2026-09-28. Owner decision pending on scope (see "Open decisions").
Truth boundary: nothing here flips `production_ready`. No stage claim without linked evidence.

## Evidence baseline (from DreamCo-Technologies/Dreamcobots @ 24e95db)
- `config/generated/bot-production-readiness.json` (generated 2026-09-20 11:23 UTC):
  1101 bots, 56 divisions, `production_ready_true: 0`.
- `docs/BOT_PRODUCTION_READINESS.md`: runtime production = adapters configured,
  sandbox checks pass, auth scoped, deployment telemetry verified.
- `docs/NEXT_100_DEEP_REPO_UPGRADES.md` #100: release train dev -> sandbox -> canary -> production
  (planned, not implemented). #25 idempotency, #26 rollback, #47 sandbox-vs-prod creds, #64 error budgets.
- `DreamPayments/` package exists: gateway.py, router.py, pricing.py, fee_auditor.py, benchmark.py.
- No file or issue named plan-gain-production-pipeline existed at baseline.

## GAIN scope (proposed, needs owner confirmation)
Revenue-adjacent divisions: DreamPayments (23), DreamSalesPro (37), DreamAffiliate (5),
DreamAgency (5), DreamFinance (25), DreamEntFinance (25), DreamMarket (5), DreamSaaS (5),
DreamLicensing (5), DreamLoans (23), plus DreamAIInfra slugs `token-billing`, `api-monetization`.

## Stages and gates
| Stage | Entry gate (all required, each linked to evidence) |
|---|---|
| S0 profile | App_bots fields + production pack present (already true fleet-wide) |
| S1 sandbox | adapter contract tests pass; sandbox creds only; idempotency on every write; sandbox run log committed |
| S2 canary | S1 + auth scoped + telemetry/correlation ID live + rollback path tested + spend cap + error budget defined; owner approval |
| S3 live | S2 canary soak window green (length set by owner) + ledger entry + cert gate sign-off; owner approval for real money |

Money rule: no real-money path before S2, and S3 always needs explicit owner approval.

## Hand-offs
- Live money readiness: Grok-Live-Revenue-Readiness
- Per-division gates: Grok-Division-Production-Gates
- Sandbox runtimes: Grok-Universal-Sandbox-Director
- Evidence ledger / certification: Grok-Prod-Evidence-Ledger, Grok-Prod-Cert-Gate

## Open decisions (owner)
1. Confirm GAIN scope list above.
2. First lane: DreamPayments inventory vs full-scope plan.
3. Canary soak length and spend cap.
4. Write access: gh token gets 403 on DreamCo-Technologies/Dreamcobots, so this stays local until fixed.
