# Universal Bot Runtime Contract

**Schema:** [`config/bots/bot-runtime-contract.schema.json`](../config/bots/bot-runtime-contract.schema.json)
**Generated manifests:** [`config/bots/bot-manifests.generated.json`](../config/bots/bot-manifests.generated.json) (by `tools/generate_bot_manifests.py`)
**Shared runtime:** [`buddy/fleet_runtime/`](../buddy/fleet_runtime/)
**Readiness auditor:** `tools/fleet_runtime_audit.py` (added in the follow-up PR)

DreamCo has ~1,120 bot profiles (`bots/*.md`, `App_bots/<Division>.json`,
`server/seed-bots.ts`). They are **not** 1,120 codebases. Each bot is a
manifest that a small set of shared engines executes. A Markdown plan, a JSON
profile or a validated manifest is configuration, not proof that a bot works
(`original-bots/STATUS.json`: *"A markdown plan is not a running bot."*).
Readiness is computed from tests and evidence, never hand-set.

## The 16 required pieces

| # | Piece | Where it lives / how it is proven |
|---|-------|-----------------------------------|
| 1 | manifest | Entry in `bot-manifests.generated.json`; expanded form validates against `$defs/botManifest` |
| 2 | division | `division` resolves to an `App_bots/<Division>.json` file (else `division_missing` / `division_unknown`) |
| 3 | capabilities | ≥1 bot-specific capability. Tier packaging (“Advanced analytics dashboard”, “Priority email support”, “API access”…) is dropped and counted in `tier_features_dropped` |
| 4 | runtime adapter | `runtime_adapter: shared_engine:<engine>`; `null` when `engine: unmapped` |
| 5 | model/router config | Named profile (`offline_first` for drafting, `offline_only` otherwise) with deterministic offline fallback |
| 6 | tools/APIs | Tool ids resolve to `profiles.tools`; `external_api_candidates` lists optional integrations from the catalog |
| 7 | I/O schema | `io_schema: engine:<engine>` → `profiles.io_schema` input/output schemas; output is validated on every run |
| 8 | permissions | `permissions.ceiling` (`sandbox` or `plan_only`) derived from `buddy_os/governance/approval_policy.yaml`; bots whose text declares live actions (send, pay, trade, publish, deploy…) are capped at `plan_only` |
| 9 | error handling | `structured_v1`: exceptions, invalid input, permission denials and guardrail blocks return structured statuses; the executor never raises |
| 10 | unit test | Engine unit tests in `tests/test_fleet_runtime_executor.py` |
| 11 | smoke test | Bot-specific fixture in `config/bots/smoke-fixtures.json` that passes offline (generic per-engine smoke runs for every mapped bot) |
| 12 | benchmark | Declared benchmarks counted; **measured** only when a committed evidence record carries results |
| 13 | health status | Auditor-recorded result of the generic smoke run (`website/data/fleet-runtime-status.json`) |
| 14 | Pages card/route | `fleet-runtime.html#bot-<slug>` on GitHub Pages |
| 15 | evidence record | Committed `evidence/fleet-runtime/<slug>.json` carrying `buddy_os/governance/release_readiness.yaml` fields |
| 16 | readiness state | Computed by the auditor (`readiness.computed_by`), never edited by hand |

Pieces 1–9 and 14 are carried by the manifest (compact entry + shared
`defaults`/`profiles`, expanded by `buddy.fleet_runtime.contract.expand`).
Pieces 10–13, 15 and 16 are resolved from tests, fixtures and evidence.

## Readiness states

The ladder mirrors `release_readiness.yaml` (discovered → implemented → tested →
verified → canary → production; missing evidence = blocked).

| State | Requires |
|-------|----------|
| `SPEC_ONLY` | Profile text exists but no shared engine could be mapped honestly (`engine: unmapped`). |
| `IMPLEMENTED` | Valid manifest + mapped engine + the generic offline smoke task runs through the shared runtime (status `ok`, evidence record produced). Proves wiring only. |
| `TESTED` | IMPLEMENTED + a reviewed bot-specific smoke fixture passes (engine in the fixture matches the manifest) + engine unit tests exist. Proves deterministic offline behaviour for that bot, not model quality. |
| `CONNECTED` | TESTED + Pages route + committed evidence record whose required connections (live model for drafting bots; any `required_apis`) report `status: ok`. |
| `VERIFIED` | CONNECTED + evidence carries `test_reference`, `security_result`, `build_result`, `runtime_result` and ≥1 measured benchmark. |
| `PRODUCTION` | VERIFIED + `approval_reference`, `deployment_reference`, `health_result`, `observability_reference`. |
| `BLOCKED` | Invalid manifest, generic smoke error, failing fixture, or slug defect. |

Flags (orthogonal to state): `duplicate_profile`, `duplicate_slug`,
`placeholder_no_specific_capabilities`, `placeholder_no_description`,
`engine_unmapped`, `engine_low_confidence`, `division_missing`,
`division_conflict_seed`, `md_only`, `claims_production_ready_without_evidence`.

Nothing in this contract flips `production_ready`, `claimable` or `mastered`.
Existing profile fields such as `production_ready` are reported as *claims*
(`readiness.claimed_production_ready`) and flagged when unbacked.

## Shared engines

| Engine | Does | Offline behaviour |
|--------|------|-------------------|
| `analysis` | Stats, group-by, top-N, filters and lookup over **caller-supplied** records | Fully deterministic; returns `needs_input` instead of inventing figures |
| `classification` | Ranks labels (default: bot capabilities) by token overlap; escalation keywords → `escalate_to_human` | Fully deterministic |
| `workflow` | Ordered checklist from steps/capabilities; tracks completed steps; live-action steps require owner approval | Fully deterministic |
| `drafting` | Drafts text through the model router | Deterministic outline clearly labelled “No model was called” |

Bots map to an engine by deterministic keyword scoring over name, slug,
category, description and capabilities (`tools/generate_bot_manifests.py`).
Weak signal → `unmapped` (SPEC_ONLY), never forced. Low-confidence mappings are
flagged; the fixture review that lifts a bot to TESTED is where a human
confirms the mapping.

## Execution path

```
manifest (expand) → validate manifest → validate task → permission policy
  → guardrails (buddy.safety.guardrails) → engine → model router (drafting only)
  → guardrails on output → output schema → evidence record
```

* **Model router** (`buddy/fleet_runtime/router.py`): live calls reuse
  `buddy.openrouter.gateway.BuddyGateway` and only happen when
  `DREAMCO_FLEET_LIVE_MODEL=1` **and** `OPENROUTER_API_KEY` are set
  server-side. CI sets neither, so smoke tests need no secrets.
* **Permissions** (`permissions.py`): levels from `approval_policy.yaml`;
  only `approval: none` levels inside the bot's ceiling run. Everything else
  returns `approval_required` without acting. The runtime never self-approves.
* **Evidence** (`evidence.py`): deterministic run record (digests of manifest,
  task and output; permission and guardrail decisions; run id). A run record
  proves one execution — it is not promotion evidence.

## Usage

```bash
python3 tools/generate_bot_manifests.py            # regenerate manifests
python3 tools/generate_bot_manifests.py --check    # CI drift check
python3 -m buddy.fleet_runtime run analytics-hub --objective "Cost by division" \
  --input '{"records":[{"division":"A","cost":2},{"division":"B","cost":1}],"metric":"cost","group_by":"division"}'
python3 -m buddy.fleet_runtime smoke --all          # generic offline smoke for every mapped bot
python3 -m unittest tests.test_fleet_runtime_executor tests.test_generate_bot_manifests
```

## Adding or fixing a bot

1. Edit the canonical profile (`App_bots/<Division>.json` and/or `bots/<slug>.md`). Never edit the generated manifest.
2. Run `python3 tools/generate_bot_manifests.py`.
3. If the bot is `unmapped`, improve its description/capabilities or extend `ENGINE_KEYWORDS` deliberately (and review the resulting mapping changes).
4. Add a fixture in `config/bots/smoke-fixtures.json` with synthetic data and assertions that would fail if the bot were mis-mapped.
5. Promotion past TESTED needs committed evidence; see the state table.

## Relationship to existing code

* `server/fleet-runtime.ts` (TypeScript) produces sandbox *task packets* for the
  web API and `npm run buddy:fleet:e2e`. This Python runtime executes engines and
  is what the readiness auditor and CI smoke use. They share the same profile
  sources; neither is production evidence by itself.
* `tools/compile_md_bots.py` emits one Python module per Markdown bot with a
  `runtime_ready`/`sandbox_tested` label but no tests behind it; only two of
  its modules are committed (`runtime/compiled_bots/`), and they can't be
  imported (`base.py` is missing and the module names start with a digit). The
  shared runtime replaces per-bot code generation. The compiler is left alone
  in this PR; retiring it is an owner decision.

## Teammate lanes (division `GrokTeammates`)

`config/bots/teammate-lanes.json` lists the 112 jobs Grok teammates have done
for the owner (name + description only, no internal ids). The generator turns
each lane into a bot manifest like any other: capabilities are split from the
description deterministically (flag `capabilities_derived_from_description`)
and mapped to a shared engine. A lane manifest proves the lane's job can be
run through the runtime offline; it is not evidence the lane's work is done.

## Engine fallback

When keyword scoring is too weak to clear the mapping threshold the generator
no longer leaves a bot unmapped if it has real capabilities:

* some signal → best-scoring engine, flags `engine_weak_signal` + `engine_low_confidence`;
* no signal at all → `workflow` (a checklist over the declared capabilities), flag `engine_fallback_workflow`, confidence `0.0`.

Bots with no specific capabilities (placeholder specs) stay `unmapped` / `spec_only`.

## Run policy (`run` in the compact entry, `run_policy` when expanded)

| value | meaning |
|---|---|
| `allowed` | may get a working **Run with Buddy** button |
| `blocked_money` | money movement, payments, billing, trading: never triggerable |
| `blocked_destructive` | delete / purge / wipe: never triggerable |
| `spec_only` | no shared engine fits |

The money pattern is intentionally broad; a false positive only costs a Run
button, a false negative could cost money. `python -m buddy.fleet_runtime job
<slug> --out evidence.json` is the job entry point and refuses anything not
`allowed` (exit code 3).

## Generated smoke fixtures

`buddy/fleet_runtime/fixtures.py` derives one fixture per mapped bot from its
own capabilities at load time (nothing committed, so no drift). Expectations
come from set logic, not from running the engine: e.g. for classification the
probe text contains exactly one label's full token set, so that label must win
with confidence 1.0; for workflow the step count equals the capability count
and every live-action step must be waiting for owner approval. A test swaps a
bot's capabilities and confirms its fixture then fails. Hand-written fixtures
in `config/bots/smoke-fixtures.json` override generated ones (`origin` shows
which). Passing proves wiring and determinism, not output quality.

## Customization (`/buddy customize`)

Pages holds no tokens. The Customize form on a bot or file page builds a
fenced YAML patch and opens a prefilled issue:

````
/buddy customize ad-copy

```yaml
enabled: true
model: dreamco/fast
prompt: "Keep it under 50 words"
schedule: 17 9 * * 1
capabilities:
  SEO: false
```
````

`buddy/fleet_runtime/customize.py` validates it: a restricted YAML subset (no
anchors, tags, lists, multi-docs); only `enabled`, `display_name`, `prompt`,
`model` (gateway aliases `dreamco/*` only), `schedule` (fixed minute and
hour), `division` (existing) and `capabilities` (toggle existing ones, at
least one stays on). Secrets, money, deletes, permissions, workflows, engines,
readiness and evidence keys are rejected by name; credential-looking values
and markup are rejected; money and destructive bots cannot be customized at
all. Accepted patches are written to `config/bots/customizations.json` and
overlaid by the executor (`enabled: false` makes runs return `disabled`; a
custom prompt is prepended to the objective *before* guardrails run).

The router side (actor allowlist + write permission, branch + PR) lives in the
Buddy control plane (#13197): `python -m buddy.fleet_runtime customize
--issue-body-file body.md [--apply]`.
