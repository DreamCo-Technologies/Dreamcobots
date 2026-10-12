# Human-Reviewed General Intelligence Evaluation

This framework measures bounded capabilities under human review. It does not certify AGI, frontier status, independent learning, production readiness, or changes to proprietary weights. Initial evidence is deliberately empty: 33 capability areas are **untested**.

## Existing owners and integration

| Concern | Existing owner | Extension |
|---|---|---|
| Model benchmarks | `server/model-benchmark-policy.ts` | Versioned evidence across 33 capability areas |
| Frontier evidence | `tools/verify_frontier_evidence.py` | Existing validator retained in native checks; broader evidence gates added |
| Fleet certification | `server/fleet-runtime.ts` and master bot registry | Division coverage references the canonical registry; no inferred certification |
| Router and promotion | `server/buddy-model-policy.ts`, `server/model-progress-policy.ts` | Evaluate exact model, policy, router and retrieval revisions together |
| Governance | `buddy_os/governance/approval_policy.yaml` | Durable scoped approval queue with atomic consumption |
| Autonomy | `buddy_os/actions/autonomy_guardrails.yaml` | Guided / Semi / High user-facing levels with conservative boundaries |
| Human review | `tools/buddy_local_bridge.py` | Separate reviewer session, same loopback server |
| Recurring work | `dreamco_platform/automation/task_runner.py` | `EvaluationTaskAdapter` uses existing scheduling and consumes fresh scope |
| Debate | `buddy_os/debate/debate_protocol.yaml` | Proposer/critic/reviewer evidence contract; no weight-change claims |
| Pages | existing nav, benchmark page, public-site validator and deployment workflow | Evidence page, source hashes, manifest and fail-closed checks |

Existing model/provider routes are not silently redirected through a new policy engine. The governed evaluation runner and scheduler adapter enforce these new gates at their execution boundary. Legacy runtime routes keep their current controls. Provider integration must explicitly use the governed adapter; this PR does not claim all legacy actions are globally intercepted.

## Run and inspect

```sh
python3 tools/general_intelligence.py
python3 tools/general_intelligence.py --check
python3 tools/general_intelligence.py --native reports/general-intelligence-controls.json
python3 -m unittest tests.test_general_intelligence
node --test tests/general-intelligence-page.test.mjs
python3 tools/buddy_cli.py local-start --review-console
```

The review console opens locally with an ephemeral reviewer credential. Agent and reviewer tokens are separate. The agent token can submit proposals but cannot read the private queue or approve requests. Browser credentials stay in memory and are removed from the URL fragment. The queue is stored in ignored `host-secrets/evaluation/reviews.sqlite3` with owner-only file permissions. No live model credentials are needed to run framework checks.

Approve/reject/edit/escalate bind to the full proposal hash and current revision. Edits invalidate prior approval. Approvals expire after 15 minutes by default and can be consumed once, atomically. Approval does not execute an action. A trusted adapter consumes it before execution and records independent post-action verification. Unknown effects or unknown cost require reconciliation; they do not trigger automatic retries.

## Autonomy and actions

- **Guided:** automatic read-only, low-risk, reversible, zero-cost actions.
- **Semi:** adds drafts with the same constraints.
- **High:** adds isolated sandbox work with the same constraints.
- Planning, code changes, external actions, deployments, payments, account changes, writes, secret access, destructive actions, high-impact decisions, promotions, rollback and marketing claims still require explicit scoped review.
- Deletes, force pushes, secret export and proprietary third-party weight changes are forbidden in this framework, even with an approval record.

The action class comes from trusted adapter code, not from the model. A local SQLite file and bearer token are a single-owner trust boundary, not enterprise identity infrastructure. Processes with access to the owner account can access the database. Hash chaining plus append-only SQL triggers detect accidental or partial tampering; an administrator can rewrite a local database. Export audit heads to independent protected storage for stronger integrity guarantees.

## Evaluation workflow

1. Choose capability templates from `config/general-intelligence/framework.json`. Define at least three independent task families, including withheld structural variants and cross-domain transfer.
2. Register and human-review a suite in `config/general-intelligence/suites.json` **before** executing it. Pin its version, seed, grader, case IDs, fixture hashes, splits, task families and dataset rights. Keep secret holdout content outside Pages. Dataset version and model/provider revision must be exact.
3. Prepare an action containing the concrete suite, subject version, component revisions, time and spend limits, tools, data, preview, verification and rollback. Use `ReviewStore.propose`. Network or paid adapters require `external_action` approval.
4. Inject a trusted `SubjectAdapter` and independent grader into `run_suite`. This code does not accept arbitrary shell commands or execute model-generated code. Provider adapters must enforce isolation, permissions, deadlines and spend limits before each call. Code benchmarks require an independently provisioned sandbox.
5. The runner records all attempts, fixture/response hashes, elapsed time, measured cost and errors. Unknown cost remains unknown. No failed case is dropped. Outputs are created exclusively, avoiding overwrite of prior evidence.
6. Complete calibration, abstention, red-team and independent artifact reviews. Import reviewed runs into the ledger with content-addressed artifacts; do not put private prompts, responses, customer data or secrets in this public repository.
7. Validate and regenerate Pages. A missing artifact, mismatch, incomplete suite, contaminated family or failed safety gate blocks verified status. Framework checks are never imported as model scores.
8. Distillation creates evidence-linked lesson drafts and failure analyses at beginner/intermediate/expert levels, exercises, quizzes and benchmark update proposals. Holdout examples are not training candidates. New training examples need disjoint families, rights review and independent held-out validation.
9. Compare champion/challenger under identical suites, fixtures, graders, seeds, hardware and runtime. Any task regression rejects promotion. Promotion and rollback need separate reviewed actions and update only local component pointers. They do not install models, deploy code or change third-party weights.

Public benchmarks are discoverable but disabled by default. HumanEval, SWE-bench and the LM Evaluation Harness are linked to their official repositories. Pin exact revisions and review each dataset's terms; a harness license is not a blanket license for its datasets. No benchmark data is downloaded or executed automatically.

## Labels, uncertainty and claims

- **Untested:** no qualifying model runtime evidence.
- **Partial:** submitted evidence is incomplete, failed or not independently verified.
- **Verified:** validated artifacts and preregistered suite pass this framework's bounded requirements. This is not proof of general intelligence, nor proof that a third-party provider's pretraining never contained a benchmark.
- **Reviewed:** a human has reviewed the exact evidence. Private review records remain local; public Pages does not infer this label from self-reported JSON.

Assisted and unassisted results must remain distinct. Calibration reports Brier score, expected calibration error, answer coverage, selective accuracy and abstention error. No samples means unknown, never zero. The help policy abstains on unsupported capabilities, missing evidence, invalid/low confidence or high-impact decisions.

A marketing claim is a separate exact-text, evidence-hash-bound review action. There is no automatic AGI/frontier label or scalar “AGI achieved” threshold.

## Long horizon and recovery

`LongHorizon.preflight` must precede each step; checkpoint after every verified or failed action. Step, time and cost caps stop further work. Paused tasks need a reviewed, verified rollback/recovery action. Checkpoints retain immutable evidence hashes and intervention counts. Completion cannot follow an unverified recovery. Crash reconciliation is deliberately manual when an action was consumed but its external effect is unknown.

## Automation and deployment

`human-reviewed-evaluation.yml` runs read-only native control checks, evidence generation checks, page interactions and link checks on relevant PRs, manual dispatch and weekly schedule. It uploads measured framework results. It does not execute paid models, approve requests, promote models, export private queues, merge or deploy.

The existing Pages deployment checks the generated evidence manifest. This branch does not deploy automatically; merge/release remains a human decision. Static GitHub Pages cannot act as an authenticated review backend. Missing local backend is an explicit blocked state.

## Remaining environment-dependent work

Live provider adapters, licensed benchmark datasets, private novel holdouts, independent graders, modality-capable runtimes and reviewed human evidence are required to demonstrate actual capability. The initial ledger contains none of these results. No benchmark improvement, model promotion or AGI claim is implied by implementing and testing this framework.
