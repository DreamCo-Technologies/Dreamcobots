# Frontier claim trust gates

Buddy may not ship frontier or sellable capability claims on Pages or public API surfaces until all four gates are green.

## Gates

1. **Provenance** — `config/buddy-training-data-provenance-policy.json` present with ownership classes including `unknown_do_not_publish`.
2. **Allowlist** — `config/buddy-frontier-readiness-gates.json` sets `never_claim_frontier_without_evidence`, and `config/buddy/500-model-operating-contract.json` exists.
3. **Sandbox soak** — `config/generated/sandbox-24h-tick.json` status `sandbox_tick_ok` and `reports/SANDBOX_24H.md` present.
4. **Disclosure + claimable** — `config/buddy-frontier-claim-disclosure.json` defines required public disclosure fields, and `evidence/frontier/current-status.assessment.json` reports `claimable: true` / `status: claimable`.

## Enforcement

- `tools/check_frontier_claim_trust_gates.py` — deploy mode blocks vanity claim phrases in `website/` while gates are red.
- Same tool with `--require-all-gates` — hard-fails unless all four are green (claim surfaces).
- Wired into `.github/workflows/deploy-buddy-pages.yml` and `.github/workflows/frontier-claim-trust-gate.yml`.

## Current posture

Evidence assessment remains `claimable: false` until `tools/verify_frontier_evidence.py` passes a live comparison bundle. Vanity phrases are listed in the disclosure config and must not appear on Pages until then.
