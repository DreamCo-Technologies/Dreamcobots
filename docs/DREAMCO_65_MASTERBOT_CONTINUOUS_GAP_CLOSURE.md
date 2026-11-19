# DreamCo 65-MasterBot Continuous Gap Closure

## Canonical fleet

The single source of truth is config/masterbot-65-registry.json. It declares exactly 65 MasterBots: 45 domain MasterBots and 20 platform MasterBots. Every entry has a stable ID, unique key, dedicated logical lane ID, mission, dashboard route, command-center handoff, prospectus route, and training queue reference.

Do not maintain a second handwritten 65-name matrix. The workflow matrix is generated from the canonical registry by tools/validate_masterbot_registry.py. The public Actions manifest is generated from that same registry by tools/generate_masterbot_public_manifest.py.

## 24x7 logical training policy

24x7 describes the persistent operating policy and queue lifecycle, not a guarantee of continuous compute. Every MasterBot maintains a logical queue and checkpoint. Work is prioritized by expected benchmark-gap closure per runner minute:

1. Failed benchmark remediation
2. Near-miss capabilities
3. Weak capabilities
4. New capability discovery
5. Regression testing
6. Maintenance

Each lane checkpoints its current gap selection, queue digest, sequence, commit, run ID, prior checkpoint sequence, next actions, and evidence state. The Actions cache is used as a best-effort checkpoint continuation layer. Each run also uploads a named artifact. Cache eviction or artifact expiry must not be interpreted as completed work.

If no eligible gap exists, no adapter is approved, or runner capacity is unavailable, the lane records an idle/blocked state and waits. It must not generate artificial tasks to consume runner time.

## GitHub Actions capacity policy

- Canonical matrix size: 65 MasterBots.
- Bounded matrix parallelism: max-parallel 5.
- Each lane has a four-minute hard job timeout and a 45-second logical work budget.
- Five-minute cron is best-effort; GitHub may delay or queue scheduled runs.
- The matrix does not bypass concurrency, quotas, rate limits, or public runner controls.
- No paid model API or GPU is called by the checkpoint-only workflow.
- No credentials are read from public repository content or written into artifacts.
- The workflow does not modify production, deploy, merge PRs, or promote model weights.
- A checkpoint is not a training run; training is only claimed when a registered adapter produces reproducible baseline, training, held-out, repeat, transfer and regression evidence.

## Requirement-to-evidence traceability

tools/audit_markdown_requirement_traceability.py inventories tracked Markdown and MDX headings, checklists, list items and table rows. Stable requirement IDs include the source path and content label. config/requirement-evidence-map.json is the explicit mapping register.

For each requirement, the auditor records:
- originating specification and line;
- implementation paths;
- test paths;
- runtime route paths;
- benchmark evidence paths;
- missing paths and current evidence state.

The auditor never guesses a source-to-code mapping from similar words. Unmapped requirements remain documented_unmapped. Existing paths do not prove that tests pass or a runtime route works. Even when all evidence paths exist, the state remains evidence_artifacts_present_requires_review until independent run evidence is reviewed. This is a traceability inventory, not an automated semantic proof of implementation.

## Buddy Bootcamp

The canonical config config/buddy-bootcamp-65.json defines eight levels:
1. Foundation
2. Guided Practice
3. Independent Practice
4. Adversarial Practice
5. Benchmark Preparation
6. Benchmark Trial
7. Mastery Verification
8. Maintenance

Sandbox modes include training, practice, coach, challenge, repair lab, exam preparation, benchmark simulation, adversarial, time-trial, resource-limited, tool-limited, multi-agent, human-vs-Buddy and MasterBot-vs-MasterBot.

A mastery claim requires baseline, post-training evidence, held-out pass, repeat pass, transfer pass and regression pass. Self-report and training activity are not mastery evidence. User-owned datasets and models remain isolated by workspace, with explicit permission and licensing requirements.

## Actions page and individual MasterBot views

The Actions Control Room exposes all 65 cards with search and domain/platform filtering. Each MasterBot has a query-scoped dashboard and prospectus, a command-center handoff, training queue/checkpoint link, training workflow controls, and links to Bootcamp and sandbox/benchmark pages. Capacity telemetry displays the configured matrix size and parallelism; live run status must come from GitHub Actions evidence.

A UI link to a GitHub workflow opens the operator's GitHub workflow interface. It does not imply that a browser button executed a training run.

## Acceptance gates

- Registry validation: exactly 65 unique MasterBots, 45 domain, 20 platform, 65 unique lanes.
- Matrix generation: every matrix name comes from the canonical registry.
- Checkpoint runner: bounded item count and time budget; no arbitrary shell commands.
- Requirement audit: all tracked Markdown/MDX files included; unmapped requirements visible.
- Bootcamp: eight ordered levels and supported sandbox modes.
- Actions UI: all 65 registry entries render; each view links back to its canonical MasterBot.
- Evidence truth: no runtime, benchmark, mastery, or production claim without its own evidence.
