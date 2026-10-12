# Research workbench scope and operating boundaries

Open `research-workbench.html` through the existing local Buddy bridge (`python3 tools/buddy_local_bridge.py --help` lists launch options). Enter its local session token. Public GitHub Pages displays the page but cannot execute local/private backends.

Implemented and tested locally:
- CPU/RAM/disk inspection and bounded NVIDIA free-memory probing; unsupported accelerators remain unknown. Model-memory lower-bound planning for 150,000 token vocabularies never grants training qualification.
- Exact UTF-8 byte-token counts and user-supplied runtime/provider-count accounting.
- A small, actually trainable autoregressive byte-transition model; seeded generation, temperature and exportable weights. This is educational, not a neural LLM.
- Deterministic educational BPE training, reversible pieces, target vocabulary 150001 with actual achieved size reported separately.
- Bounded comparison-attempt heuristic, configurable partial rewards, required safety checks, non-finite input rejection.
- Tenant-scoped SQLite dashboard/chat records; explicit consent, selected-chat context and deletion. The HTTP bridge is single-owner; multi-user identity infrastructure is not claimed.
- Safe escaped regional microsite HTML generated from user-supplied content, downloaded without publication.
- Double-entry local ledger with idempotency and tenant/currency isolation; paper-order validation with notional limits. No money movement, brokerage connectivity or verified fills.
- Thirty token examples, thirty RL research references, thirty optimizer/update references, fifteen design-pattern study topics.
- Thirty additive voice navigation mappings and thirty hand-command mappings. Existing voice controls are preserved. Camera hand recognition remains unimplemented.

Not implemented or not verified by this change:
- Commercial banking/brokerage operations, market data, live order routing, payments, or claims to be a bank.
- GPU neural pretraining, all 30 RL trainers/optimizers, universal training adapters, continual weight updates, or discovered superior algorithms.
- Multi-tenant public hosting, 1000-user load capacity, all-repository backend deployment, live dashboards for unconnected services.
- General API/MCP/A2A/CLI adapters for every provider, marketplace settlement, private chat access across providers, and n8n training datasets.
- All historical DreamCo project conversations, unidentified repositories and inaccessible files have not been exhaustively recovered.
- Model vocabulary expansion does not enlarge a pretrained model safely by itself. Tokenizer and embedding changes must be evaluated together.

A research catalog entry is not an installed training algorithm. Models must not reward their own outputs as independent verification. Keep held-out checks, baseline comparisons, data rights, explicit reward rubrics, budget ceilings and reviewed rollback. Do not punish safe refusal, honest uncertainty or necessary clarification.

Jev appears to refer to TypeSafe AI's structured-decision model. Its API can classify, choose and score with probabilities. It may be useful for routing and screening, subject to task-specific evaluation, authentication and budget controls. It is not integrated or live-tested here.
Official documentation: https://api.typesafe.ai/redoc
Tokenization reference: https://huggingface.co/docs/transformers/main/tokenizer_summary
GitHub Pages hosting: https://docs.github.com/en/pages

Latest readiness additions:
- Authenticated local bridge POST `qualify` estimates memory; POST `seo` audits supplied HTML. Existing system inspection now probes NVIDIA when available.
- Server-side payment readiness gate checks tenant ownership and strict provider capability flags. It is not wired to live onboarding and does not create a bank account. Never pass client-supplied account flags into this gate.
- Static SEO checks cover title, description, language, primary heading, canonical HTTPS URL and image alt attributes. Crawling, international/local search, structured data and performance require further validation.
- Capacity gate requires a scoped, hashed load-test receipt and isolation checks. No 1,000-user test has been run. Unlimited capacity is not claimed.
- Latest readiness regression suite plus existing workbench suites: 17 passed. Earlier full verification and browser evidence predates these additions; see evidence timestamps.

Do not delete the source chats yet. The accessible task inventory contains additional historical project conversations that have not been fully read and reconciled. Existing notes are requirements, not execution evidence.
