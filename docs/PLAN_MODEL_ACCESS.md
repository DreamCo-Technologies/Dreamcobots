# Plan: Model Access (plan-model-access)

Status: DRAFT PR #13176 (branch `plan-model-access/route-gate-allowlist`). Route coverage and Path D verified; branch merged with current main.
Rule: evidence before live. Nothing here claims live connectivity, live benchmarks, or live billing.

## Path A — Owner 500 registry
- Existing: `config/buddy/500-model-registry.json`, `config/buddy/500-model-operating-contract.json`,
  `.github/workflows/buddy-500-model-governance.yml` (asserts 500 slots, PR-only writes, trust domains).
- Docs: `docs/500_MODEL_RESEARCH.md`, `docs/UNIFIED_500_MODEL_BENCHMARK_OPERATING_PLAN.md`.
- State: governance contract only. The workflow itself says live provider connectivity "must be verified separately".
- Gate to live: a slot is `live_benchmark_ok` only with exact provider+model id, fixture hash, response hash,
  latency, cost, grader version, UTC timestamp (per `reports/BUDDY_LOCAL_OWNER_AND_MODEL_LAB.md`).
- Owner: Grok-500-Model-Bench-Runner feeds evidence; this plan consumes it.

## Path B — HF / GitHub open-weight
- Existing: `docs/HUGGINGFACE_MASTERY_PLAN.md`, `config/huggingface-*.json`, `config/open_model_advancement_policy.json`,
  `.github/workflows/grok-twins-hf-study.yml`.
- State: router connector `local_open_model` is `contract_only` in `config/buddy-model-router.json`.
- Gate to live: license-clean + pinned revision + safetensors, adapter passes sandbox tests, then flip
  `implementation_status` to `adapter_implemented`. No auto weight execution in Actions.

## Path C — Paid ultimate
- Existing: `buddy_os/actions/paid_model_access_and_resource_import.yaml` (provider-authorized access only,
  explicit billing owner, visible cost, revocation), `server/buddy-model-policy.ts` premium mode
  (per-request approval, `automaticPaidUpgrade: false`, free fallback `buddy_native`).
- Billing: Stripe stub over parallel billing. `server/stripeClient.ts`, `server/seed-stripe-products.ts`,
  `tests/stripe-checkout.test.ts` exist; `.agents/memory/stripe-status.md` says activation needs backend
  secrets + owner-approved deploy. `DreamPayments/` stays processor-neutral sandbox; no second billing stack.
- Gate to live: Stripe test-mode checkout evidence (test run log + webhook receipt), then owner approval
  for live keys. Paid "ultimate" tier is not in seeded tiers yet (Free/Pro/Enterprise/Elite) and must not be
  added as a live price without that evidence.

## Path D — Buddy selector, allowlist-only
- Code: `selectBuddyModelsForTask` / `resolveBuddyModelPlan` in `server/buddy-model-policy.ts`;
  route gate in `server/buddy-model-route-gate.ts`; allowlist in `config/buddy/model-allowlist.json`.
- Was (main @ 5ba09f2): `allowDiscovery` defaulted to `true`, so selection admitted `discoveryTarget` candidates;
  `matchDemandReasonToModels` hard-coded `allowDiscovery: true`; no model route checked caller identity.
- Now (branch `plan-model-access/route-gate-allowlist`, PR #13176 draft, not deployed):
  - `allowDiscovery` defaults to `false`. A non-owner request with `allowDiscovery: true` is rejected
    (`403 discovery_owner_only` at the gate; `BuddyModelAccessError` in the policy as defense in depth).
  - Normal callers only ever receive targets listed in `config/buddy/model-allowlist.json`
    (`default_policy: deny_unlisted`). The owner without `allowDiscovery` is also allowlist-only.
  - Owner + `allowDiscovery: true` sees non-allowlisted targets, marked `allowlisted: false` with readiness
    `allowlist_evidence_required` or `official_catalog_discovery_required`. Nothing is executed
    (`providerCallExecuted: false`, `access.discoveryExecuted: false`).
  - Paid/freemium targets still return `paid_approval_required` until `approvePaidModelForThisRequest: true`;
    `automaticPaidUpgrade` stays `false`. Approved OpenAI targets stop at `exact_model_verification_required`.
  - Owner identity = existing Buddy OAuth session (`buddy_auth_session`, `server/oauth-login.ts`) whose
    `provider:sub` is listed in `BUDDY_MODEL_OWNER_SUBJECTS`. No new auth system.
  - Production setting `BUDDY_MODEL_OWNER_SUBJECTS` (see below): comma-separated `provider:sub` list.
    When unset/empty, `buddyModelOwnerSubjects()` returns an empty set — nobody is owner, so discovery
    is 403 for all callers; allowlisted selection still works for any signed-in user.
- Allowlist seed (5 entries). Entries are validated against the catalog and router at load; a bad entry fails closed:
  - `14 Buddy Native` → `buddy_native` (`local_ready`) — Path B, connector and target.
  - `1 GPT-4o`, `2 GPT-4.5`, `26 DALL-E 3`, `33 Whisper` → `openai` (`adapter_implemented`) — Path B,
    **connector-only** evidence: the adapters in `server/provider_integrations/{chat,image,audio}` call
    `gpt-5.1` / `gpt-image-1` / `gpt-audio`, not these catalog targets' exact IDs. The owner may want to trim
    these until exact model IDs are recorded.
- No Path A (`live_benchmark_ok`) entries exist yet; the schema requires provider model id, fixture hash,
  response hash, latency, cost, grader version, and UTC timestamp before one can be added.
- Tests: `tests/buddy-model-policy.test.ts`, `tests/demand-model-policy.test.ts`, `tests/buddy-model-route-gate.test.ts`.

## Route coverage
Inventory of `server/routes.ts` and `server/provider_integrations/*` on main @ 5ba09f2. "Policy" means the
route calls `resolveBuddyModelPlan` / `selectBuddyModelsForTask` (directly or via a helper). "Identity" means a
caller session is required. Line numbers are main → patched.

### Model policy routes (gated by this patch)
| Method | Path | routes.ts line | Policy on main | Identity on main | After patch (kind) |
|---|---|---|---|---|---|
| GET | /api/buddy/model-benchmarks/catalog-audit | 3335 → 3337 | no | no | gated (catalog) |
| GET | /api/buddy/models/encyclopedia | 3339 → 3341 | no | no | gated (catalog) |
| GET | /api/buddy/models/connections | 3343 → 3345 | no | no | gated (catalog) |
| GET | /api/buddy/models/progress | 3365 → 3367 | no | no | gated (catalog) |
| GET | /api/buddy/models/council | 3369 → 3371 | no (own paid-approval check) | no | gated (selection); members not allowlist-filtered |
| GET | /api/buddy/models/demand-ontology | 3383 → 3385 | no | no | gated (catalog) |
| POST | /api/buddy/models/demand-match | 3387 → 3389 | yes, indirect (`allowDiscovery: true` hard-coded) | no | gated (selection), allowlist-only for users |
| POST | /api/buddy/models/select | 3401 → 3403 | yes | no | gated (selection), allowlist-only for users |
| POST | /api/buddy/model-benchmarks/plan | 3411 → 3418 | no | no | gated (plan) |
| POST | /api/buddy/models/improvement-plan | 3425 → 3432 | no (own paid-budget check) | no | gated (plan) |
| GET | /api/buddy/open-model-lab/catalog | 3439 → 3446 | no | no | gated (catalog) |
| POST | /api/buddy/open-model-lab/comparison-plan | 3538 → 3545 | no | no | gated (plan) |
| POST | /api/buddy/open-secure-ai-defense/model-discovery-plan | 3630 → 3637 | no | no | gated (discovery_plan, owner only) |
| POST | /api/buddy/route-capability | 809 → 811 | yes, indirect (`FleetRuntimeRegistry.routeCapability`) | no | gated (plan) |

Gate behavior (`buddyModelRouteGate`): 401 `caller_identity_required` without a valid session; 403
`discovery_owner_only` for non-owner discovery; 503 if router policy invariants drift
(`automatic_paid_upgrade` false, `paid_use_requires_per_request_approval` true, `free_fallback_required` true);
then runs `resolveBuddyModelPlan` for the requested mode/approval and sets `X-Buddy-Model-Policy` and
`X-Buddy-Model-Plan-Status` headers. `tests/buddy-model-route-gate.test.ts` fails if a new `/api/...model...`
route appears in routes.ts without the gate.

Frontend effect: `website/buddy.js` (route-capability) and `website/models.js` (connections) are the only
`website/*.js` callers of the gated routes (grep of all 14 paths). Both keep the existing local/static
fallback on any non-OK response. On **401** specifically they also show a small notice —
"Sign in to see live model data" with a link to the existing `sign-in.html` flow (same target as
`website/nav.js`) — without console error spam or a broken render. Other statuses stay silent fallback.

## Production setting: `BUDDY_MODEL_OWNER_SUBJECTS`
Documented in `.env.example`, `.env.buddy-local.example`, and `docs/CUSTOMER_PRODUCTION_RUNBOOK.md`.
- **Format:** comma-separated `provider:sub` values matching the Buddy OAuth session identity
  (regex used by the gate: `^[a-z]+:.+$`). Example shape only: `google:example-oauth-subject`
  or `apple:example-oauth-subject`. Never commit a real production value.
- **How the owner finds their own `provider:sub`:** sign in through the existing Buddy OAuth flow,
  then call `GET /api/auth/session`. The JSON returns `provider` and `profile.subject` (from
  `server/oauth-login.ts` / the sealed `buddy_auth_session` cookie). Concatenate as
  `${provider}:${profile.subject}` and set that on the host (and in GitHub Actions secrets if used).
- **When unset or empty:** `buddyModelOwnerSubjects()` → empty set; no caller is treated as owner.
  Discovery routes and `allowDiscovery: true` return **403** `discovery_owner_only` for everyone.
  Normal allowlisted selection/catalog/plan routes still work for any signed-in user (401 only when
  the session cookie is missing).

### Routes that execute provider models directly (NOT gated; owner decision needed)
These call `openai.chat.completions.create` / provider adapters directly, with no Buddy model policy, no
per-request paid approval, and no caller identity. Gating them changes core chat/tool UX, so it is left out of
this patch.
- routes.ts (main lines): POST /api/search/web (683), /api/buddy/train (904), /api/buddy/study-book (926),
  /api/buddy/vibe-code (948), /api/buddy/build-game (971), /api/buddy/simulate-course (994),
  /api/intel/competitive (1017), /api/harness/run-suite (1100), /api/governance/test (1214),
  /api/buddy/execute-code (1251), /api/buddy/analyze-image (1306), /api/buddy/agent-run (1329),
  /api/buddy/security-scan (1377), /api/buddy/architect (1402), /api/buddy/translate-code (1427),
  /api/buddy/code-review (1451), /api/buddy/generate-pr (1476), /api/buddy/deploy-config (1501),
  /api/buddy/debug-deep (1526), /api/buddy/refactor (1575), /api/conversations/:id/messages (2003),
  /api/conversations/:id/stream (2051), /api/tasks/:id/run (2180, via `runAutonomousTask`),
  /api/batch/process (3128), /api/code/run (3237), /api/bot-builder/generate (4337).
- `server/provider_integrations/image/routes.ts:5` POST /api/generate-image;
  `server/provider_integrations/audio/routes.ts:13` POST /api/conversations/:id/voice (both registered in routes.ts).
- `server/provider_integrations/chat/routes.ts` is not registered.

### Known pre-existing issues on main @ 5ba09f2
- `server/routes.ts` throws at import: "Bot seeds contain duplicate canonical/supplemental identities"
  (8 duplicate slugs, e.g. `portfolio-rebalancer`, `warehouse-ops`). The server cannot boot until this is fixed.
  The full-boot test is skipped for this reason. With that check disabled locally (not committed), all 7 gate tests passed.
- `config/generated/repository_test_registry.json` is already stale (`generate_repository_test_registry.py --check` exits 1).

## Next ship steps (in order)
1. Path D: allowlist-only default + model route gate + tests (local branch `plan-model-access/route-gate-allowlist`; needs push access).
2. Path C: Stripe test-mode evidence pack (no live keys).
3. Path B: `local_open_model` adapter sandbox test.
4. Path A: first evidenced `live_benchmark_ok` slots from bench runner.

## Blockers
- Owner must set `BUDDY_MODEL_OWNER_SUBJECTS` on the production host before discovery works for anyone.
- Pre-existing main issue: duplicate bot seed identities still skip the full-boot gate test.
