# Buddy Resource Map

Source of truth: [`config/buddy/resource-registry.json`](../config/buddy/resource-registry.json) (schema `dreamco.buddy.resource_registry.v1`).
Scanned on 2026-10-05 with read-only `gh api` calls, a repo grep and the box-local Grok teammate roster.

> Listing a resource is not a live integration. 'connected' means wired in this repository or the GitHub org, with evidence named in wired_into. Secrets are recorded by name and presence only, never by value. Nothing here sets production_ready, claimable or mastered.

Validation: `npm run buddy:resource-connections` (`tools/generate_resource_connection_catalog.py --check`) checks this registry and embeds a summary in
`website/data/buddy-resource-connection-catalog.json` under `buddy_resource_registry`. The check fails if:

- a status is not one of the allowed values,
- a secret value (not just a name) appears anywhere in the registry,
- a `wired_into` path doesn't exist,
- a router reference names an unknown connector, or its secret names differ from that connector's `secret_references`,
- a `contract_only` connector is marked connected,
- a license block lacks a matching `usage_terms` on the router connector,
- a promotion flag (`production_ready`, `claimable`, `mastered`) appears, or
- any registry id is missing from this page.

## Status meanings

- **connected**: Already wired in repo config, workflows or the org. Evidence is in wired_into.
- **contract_only**: A router or contract entry exists, but there is no governed execution adapter yet.
- **needs_secret**: An adapter or workflow exists but waits on the named secret.
- **needs_owner_decision**: Needs a business, compute, scope or vendoring decision from the owner.
- **blocked_by_license**: License or provider terms forbid the intended use.
- **retired_upstream**: The provider has shut the service down. Do not wire it.

## Top 15 resources for Buddy (ranked)

| Rank | Id | Resource | What it gives Buddy | Status | Secrets (names only) |
|---|---|---|---|---|---|
| 1 | `xai_grok_api` | xAI Grok API (router connector `xai`) | Hosted frontier reasoning, coding and general chat for Buddy's premium route, called by a backend adapter inside a DreamCo product (a Bundled Service under the xAI Enterprise terms, section 1.1). | **contract_only** | `XAI_API_KEY` (not set) |
| 2 | `grok_teammate_fleet` | Grok teammate bot roster (~112 lanes, box-local profiles, not in this repo) | Named owners for each Buddy capability lane. They open evidence-gated PRs for routing, evals, study packs, OS surfaces and production gates. | **connected** | - |
| 3 | `openai_adapter` | OpenAI route (router connector `openai`, the only adapter_implemented premium route) | The one premium route with a working server adapter (server/provider_integrations/chat, image, audio, batch). | **needs_secret** | `OPENAI_API_KEY`, `AI_INTEGRATIONS_OPENAI_API_KEY` (not set) |
| 4 | `local_open_model_route` | Local open-model route (`local_open_model`) + tools/buddy_local_chat.py | A free, private route through an OpenAI-compatible local server (Ollama, llama.cpp, vLLM or TGI). buddy_local_chat.py is a dependency-light CLI that expects a `buddy_local_runtime` adapter module. No script or workflow calls it yet, and it ships no weights. | **needs_owner_decision** | - |
| 5 | `huggingface_hub` | Hugging Face Hub (router `huggingface`, Path B open weights, HF sync workflows) | Open-weight models, datasets and metadata for the Buddy student path (catalog, LoRA base models, eval metrics). | **needs_secret** | `HF_TOKEN`, `HUGGINGFACE_TOKEN` (not set) |
| 6 | `study_packs` | study_packs/ (12 capability packs with sources, evals, SFT/DPO recipes) | Curated per-capability curricula and eval sets (instruct, code, reason, tools, research, safety, embed, rerank, vision, speech, translate, summarize). | **needs_owner_decision** | - |
| 7 | `benchmark_runner` | benchmarks/buddy_benchmark_runner.py + benchmarks/tasks + eval/edu_benchmark + F0 scorecards | An offline, free-first benchmark harness and holdout packets for scoring Buddy routes without provider calls. | **connected** | - |
| 8 | `local_rag` | foundry/local_rag.py (dependency-free local RAG store) | Retrieval over DreamCo docs for grounding, on laptops and in the sandbox, with no hosted embeddings. Covered by tests/test_foundry_local_rag.py, but the router and runtime don't call it yet. | **connected** | - |
| 9 | `github_actions` | GitHub Actions on Dreamcobots (146 workflows registered, GitHub-hosted runners, 0 self-hosted) | Scheduled and dispatchable compute for checks, catalogs, benchmarks and Pages builds. GITHUB_TOKEN is available to every workflow. | **connected** | - |
| 10 | `github_pages` | GitHub Pages (legacy build from main:/, HTTPS enforced, status built) | A public static UI for Buddy's chat, model picker, resource center and catalogs. Provider calls from the static site are disabled by policy. | **connected** | - |
| 11 | `gcp_workload_identity` | GCP deploy identity (Actions secrets present: GCP_PROJECT_ID, GCP_REGION, GCP_SERVICE_ACCOUNT, GCP_WORKLOAD_IDENTITY_PROVIDER) + cloudbuild.yaml/app.yaml | A keyless OIDC path to run Buddy's backend, where provider secrets and adapters belong, on Google Cloud. | **needs_owner_decision** | `GCP_PROJECT_ID`, `GCP_REGION`, `GCP_SERVICE_ACCOUNT`, `GCP_WORKLOAD_IDENTITY_PROVIDER` (set in Actions) |
| 12 | `copilot_agents` | Copilot coding agent config (.github/agents/*.agent.md, copilot environment, copilot-instructions.md) | Repo-native agent profiles (grok-buddy-bridge, buddy-debugger, grok-fleet-debugger and others) that keep agent work routed through Buddy's single runtime. | **connected** | - |
| 13 | `local_training_toolchain` | Unwired local training tools: buddy_train_local.py, buddy_weights.py, buddy_capability_scheduler.py, buddy_code_asset_scanner.py, foundry/lora_plan.py | A from-scratch or LoRA training loop, a checkpoint lifecycle, value-per-compute job selection, and a scan of repo code assets for training candidates. | **needs_owner_decision** | - |
| 14 | `azure_foundry` | Azure AI Foundry (router `azure_foundry`, GitHub's named successor to GitHub Models) | A broad hosted model catalog, including third-party models, that replaces what GitHub Models used to offer. | **contract_only** | `AZURE_OPENAI_API_KEY`, `AZURE_AI_FOUNDRY_API_KEY` (not set) |
| 15 | `sibling_repositories` | Sibling repos: Dreamcobots-Grok-Revolutionary, Dreamcobots-frontier-trust, DreamCo-Command-Center, Dreamco, Ai-bots | Grok system prompts and a plugin registry (Grok-Revolutionary system/), a bot manifest schema and api-server (Command Center), and a trust fork for frontier PRs. | **connected** | - |

## Other inventoried resources

| Rank | Id | Resource | What it gives Buddy | Status | Secrets (names only) |
|---|---|---|---|---|---|
| - | `github_discussions` | GitHub Discussions on Dreamcobots (enabled, 6 categories, 0 threads) | A possible public Q&A and feedback channel for Buddy users and evals. | **needs_owner_decision** | - |
| - | `github_models` | GitHub Models (marketplace catalog + inference) | Nothing now. The service was retired upstream. | **retired_upstream** | - |
| - | `github_token_scope_gaps` | GitHub surfaces not readable with the current token: App installations, Packages, Copilot seats, org secrets | Unknown until visible. | **needs_owner_decision** | - |
| - | `starred_oss_blocked` | Starred OSS not reusable: elder-plinius/CL4R1T4S (AGPL-3.0, leaked vendor system prompts), tinyhumansai/openhuman (GPL-3.0) | Nothing safe to reuse. CL4R1T4S content may violate vendor terms. GPL and AGPL code would force copyleft on Buddy. | **blocked_by_license** | - |
| - | `starred_oss_permissive` | Starred OSS with permissive licenses (continuedev/continue, cline/cline, microsoft/ai-agents-for-beginners, K-Dense-AI/scientific-agent-skills, usestrix/strix, TauricResearch/TradingAgents, mattpocock/sandcastle) | Reference designs for coding agents, agent curricula, skill libraries, security testing and sandboxed agent orchestration. | **needs_owner_decision** | - |
| - | `starred_oss_unclear_license` | Starred OSS with unclear license (rasbt/LLMs-from-scratch, oven-sh/bun, tech-leads-club/agent-skills: NOASSERTION) | An LLM-from-scratch training curriculum that fits tools/buddy_train_local.py, plus runtime tooling. | **needs_owner_decision** | - |
| - | `stripe_and_github_key_secrets` | Other Actions secrets present: STRIPE, GITHUBKEY | Payments and a GitHub credential for backend jobs. Neither is referenced by any workflow. | **needs_owner_decision** | `STRIPE`, `GITHUBKEY` (set in Actions) |
| - | `xai_outputs_for_training` | Grok outputs as teacher data for Buddy (distillation, SFT, DPO targets) | Would supply teacher traces for Buddy student adapters. The study packs and the distill contract name xAI as the teacher. | **blocked_by_license** | - |

## xAI / Grok: what Buddy may and may not do

- **Allowed:** Buddy may call Grok at runtime through a backend adapter as part of a DreamCo product. The xAI Enterprise Terms, section 1.1(b)-(c), allow integrations ("Bundled Services") offered to end users.
  This is the router's `xai` connector. It stays `contract_only` until an adapter passes the sandbox tests and `XAI_API_KEY` is stored in a backend secret store.
- **Not allowed without a signed Order Form:** training or distilling Buddy on Grok outputs.
  - [xAI Terms of Service - Enterprise](https://x.ai/legal/terms-of-service-enterprise) (last updated 2026-08-14), section 3.2: the customer will not "use any Output to train any foundation models, large language models, or other artificial intelligence systems except as may be expressly permitted in an Order Form."
  - The [Acceptable Use Policy](https://x.ai/legal/acceptable-use-policy) also prohibits "distilling model data or Outputs" and using Outputs "to develop ... machine learning models ... that compete" with xAI.
  - This repo records the result in `config/buddy-model-router.json` (`xai.usage_terms`) and in the registry entry `xai_outputs_for_training`.
  - `config/buddy-distill-contract.json` already requires a teacher-terms check. That check now resolves to **blocked**. Use a permissively licensed open-weight teacher or human-written data for student adapters.
- **Retention:** xAI API data is retained for 30 days by default unless Zero Data Retention is enabled ([xAI security FAQ](https://docs.x.ai/developers/faq/security)). Do not send personal data except through ZDR.

## Grok teammate lanes (box-local roster, about 112 bots)

The roster lives in agent profiles on the shared Grok box, not in this repo. Lanes are grouped by the Buddy capability each bot owns.

| Lane | Bots | Examples |
|---|---|---|
| model_routing_access | 7 | Grok-HF-Router-Wiring, Grok-Model-Access-Product-Owner, Grok-HF-Inference-Serve, Grok-Buddy-Metacog-Coach, Grok-Buddy-Vs500-Bench |
| distillation_training_adapters | 9 | Grok-Buddy-Distill-Lead, Grok-Buddy-LoRA-Foundry, Grok-HF-PEFT-LoRA, Grok-HF-TRL-Train, Grok-Buddy-Adapter-Registry |
| evaluation_frontier_gates | 14 | Grok-Buddy-Eval-Harness, Grok-Buddy-F0-Scorecard, Grok-Frontier-Loop-Captain, Grok-HF-Evaluate, Grok-Prod-Cert-Gate |
| reasoning_coding_tooluse | 9 | Grok-Buddy-Reasoning-Coach, Grok-Buddy-Logic-Reasoner, Grok-Buddy-ToolUse-Arena, Grok-Buddy-Debug-Arena, Grok-Buddy-RCA-Trainer |
| learning_data_curriculum | 28 | Grok-Buddy-Bootcamp-Commandant, Grok-HF-StudyPack-Builder, Grok-HF-Datasets-Master, Grok-Edu-K12-Curriculum, Grok-ONET-Ingest-Lead |
| os_github_surfaces | 13 | Grok-Buddy-OS-Shell, Grok-OS-Actions-Panel, Grok-OS-Event-Bus, Grok-OS-Scheduler, Grok-Pages-Universe-Linker |
| production_readiness_ops | 17 | Grok-Prod-Resource-Graph, Grok-Prod-Config-Triangulator, Grok-Prod-Connectivity-Scanner, Grok-Prod-Deps-Licenses, Grok-Repair-Orchestrator |
| products_revenue_packages | 12 | Grok-Buddy-Capability-Packager, Grok-Buddy-Package-Market, Grok-Live-Revenue-Readiness, Grok-Universal-Sandbox-Director, Grok-Platform-Expansion-Lead |
| general | 3 | Grok Bot, Grok-Eng-Gap-Closure-Pilot, Grok-HF-Deps-Pins |

## Owner actions

- `xai_grok_api`: Store XAI_API_KEY in the backend secret store only, then approve building the xAI adapter behind the existing sandbox tests.
- `openai_adapter`: Set OPENAI_API_KEY in the backend runtime secret store if a premium route is wanted. Per-request approval stays on.
- `local_open_model_route`: Pick a host and pinned open-weight model (license-checked), then set LOCAL_MODEL_BASE_URL in the backend env.
- `huggingface_hub`: Add an HF_TOKEN Actions secret (read scope first) if the HF sync and study workflows should run with authentication.
- `study_packs`: Pick a terms-compatible teacher (a permissive open-weight model or human-written data) for the recipes. Router changes are not required.
- `gcp_workload_identity`: Decide whether Buddy's backend (model adapters plus secret store) should deploy to GCP from Actions.
- `local_training_toolchain`: Approve a compute budget and host before any training run.
- `azure_foundry`: Decide whether to open an Azure subscription before anyone builds an adapter.
- `github_discussions`: Decide whether Buddy feedback should go to Discussions.
- `github_models`: Optional follow-up: remove the github-models hub from config/model-hub-scan-targets.json and use azure_foundry instead.
- `github_token_scope_gaps`: Grant read scopes if this inventory should cover them.
- `starred_oss_blocked`: Do not ingest.
- `starred_oss_permissive`: Approve vendoring case by case.
- `starred_oss_unclear_license`: Review LICENSE files before copying any code.
- `stripe_and_github_key_secrets`: Confirm the intended use or rotate. Values were not inspected.
- `xai_outputs_for_training`: Keep Grok as a runtime and inference route only. Do not train Buddy on Grok outputs unless DreamCo gets a signed xAI Order Form that expressly allows it. Train students on permissively licensed open-weight teachers or human-written data instead.

## GitHub scan notes (2026-10-05)

- **Account:** `ireanjordan24`. Visible repos: DreamCo-Technologies/{Dreamcobots, Ai-bots, Dreamco, DreamCo-Command-Center} (public), plus one private demo repo, and ireanjordan24/{Dreamcobots-frontier-trust, Dreamcobots-Grok-Revolutionary}.
- **Dreamcobots Actions secrets (names only):** GCP_PROJECT_ID, GCP_REGION, GCP_SERVICE_ACCOUNT, GCP_WORKLOAD_IDENTITY_PROVIDER, GITHUBKEY, STRIPE. No Actions variables.
  - Workflows reference `secrets.HF_TOKEN`, which is not set.
- **Environments:** copilot, github-pages, Preview, production, Stripe.
- **Pages:** legacy build from `main:/`, HTTPS enforced, status built.
- **Discussions:** enabled, 0 threads. No Projects (v2), no Codespaces, 0 self-hosted runners.
- **HTTP 403 for this token:** App installations, Packages, Copilot billing and org secrets.
- **GitHub Models:** retired upstream on 2026-07-30, so no router connector was added.
