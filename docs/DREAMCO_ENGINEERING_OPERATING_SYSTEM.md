# DreamCo Engineering Operating System

DreamCo is operated as one governed system rather than a collection of unrelated bots. The repository separates canonical production identities, recovered legacy material, generated specialists, runtime evidence, sandbox evidence, ontology state, business/work benchmarks, and release certification so that scale does not hide uncertainty.

## Sources of truth

- `App_bots/` — canonical bot profiles. These are the identities counted in the canonical fleet.
- `original-bots/` and `bots/` — legacy recovery sources. They are inventoried, deduplicated, tested, and proposed for capability merge or promotion.
- `attached_assets/` — supporting legacy/source material. Files here are preserved with provenance but are not assumed to be bots.
- `config/dreamco-operational-ontology.json` — object/link/action/function model for the operating system.
- `config/buddy-runtime-supervisor.json` — durable runtime coordination contract.
- `config/trusted-code-delivery-program.json` — code trust and release-quality policy.
- `config/run-everything-now.json` — broad owner-triggered verification and repair program.

## Canonical + legacy merge model

Legacy material never expands the live fleet by filename count. `tools/recover_legacy_bots.py` inventories every source file. Exact legacy duplicates become capability-merge candidates; distinct candidates enter `legacy-bot-promotion-backlog.json`. Promotion requires identity review, canonical ownership, normalized category/capabilities, a runtime route, sandbox evidence, regression tests, fleet accounting regeneration, and Code Trust.

The generated `unified-bot-system.json` is the one accounting view across canonical bots and recovered candidates while keeping the canonical count truthful.

## Runtime model

"Always on" means supervised, restartable execution rather than one immortal process. Workers use deterministic lanes, owners, heartbeats, leases, checkpoints, idempotency keys, retries/backoff, circuit breakers, and failure queues. Consequential external actions remain approval gated.

`tools/build_runtime_sync_plan.py` materializes the current worker-to-lane plan. Canonical bots can be eligible for supervised runtime; recovered occupation/task workers remain sandbox-only until their evidence gates pass.

## Ontology

DreamCo models real operating concepts as typed objects and links: users, organizations, bots, divisions, capabilities, tasks, occupations, businesses, resources, datasets, models, evaluations, tests, evidence, bugs, gaps, deployments, connections, payments, manufacturers, RFQs, contracts and more.

Actions and functions are explicit so work can be permission checked, audited, benchmarked and improved. The ontology may propose schema evolution when recurring concepts are missing, but ontology migrations still require compatibility review and tests.

## Work and business coverage

The universal work factory is designed to ingest authoritative occupation/task datasets and create sandbox-only occupation and task specialists dynamically. This avoids bloating the canonical fleet while allowing DreamCo to benchmark very large numbers of human jobs/tasks.

Task/platform benchmarking separates applicability from evidence. A task may look suitable for a freelance, employment, creator, ecommerce, developer, procurement or direct-business channel, but current platform permission, pricing, demand and profitability are never invented.

Manufacturing productivity is evaluated through measurable outcomes such as OEE, throughput, cycle time, first-pass yield, downtime, scrap, rework, changeover, inventory turns, supplier quality, labor/unit, energy/unit and on-time delivery.

## Sandbox and evidence

The maximum sandbox matrix covers canonical bots, recovered legacy candidates, occupation specialists and task specialists. Applicable cases receive overlays for happy path, negative behavior, boundaries, malformed input, permissions, privacy, security, recovery, idempotency, concurrency, speed, accuracy, cost, observability and rollback.

Planning is not evidence. `sandbox-runtime-evidence.json` records executable evidence, while canonical fleet E2E may be inherited because it already executes repository-controlled bot and capability contracts. Noncanonical workers require their own evidence.

## Code trust

No finite test suite proves that software has no bugs. DreamCo therefore aims for zero known release-blocking defects, relevant regression evidence, fail-closed high-risk gates, reproducible receipts and fast rollback/repair.

High-risk payment/auth/security/privacy/database/deployment changes require domain-relevant tests. The change-impact audit detects unrelated test evidence, deleted tests and added skip markers. CodeQL/dependency review and repository-controlled testing remain separate defense layers.

## Run Everything Now

`tools/run_everything_now.py --mode maximum` is the broad owner verification lane. It inventories legacy bots, rebuilds the unified system/runtime plan, refreshes work/manufacturing benchmarks and ontology, runs sandbox/accounting/connection/code-trust checks, production verification, fleet E2E, speed/accuracy, production smoke, full certification, live-user readiness, and system progress.

The scheduled GitHub workflow runs this repeatedly and creates/updates repair issues when blockers are found. Independent checks continue after failures so the evidence packet shows the breadth of damage instead of only the first failing command.

## Release path

1. Draft/change.
2. Focused tests and Code Trust.
3. Maximum applicable sandbox evidence.
4. Production verification and fleet E2E.
5. Speed/accuracy/security/dependency gates.
6. Production runtime health smoke.
7. Full System Certification.
8. Controlled live-user readiness.
9. Owner pilot → closed alpha → closed beta → limited release → general release based on measured evidence.

A generated config, plan, worker or adapter is never treated as runtime proof. External integrations are only called connected when an authorized runtime probe succeeds.
