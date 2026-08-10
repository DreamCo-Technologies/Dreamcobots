# DreamCo Owner Control Center Prospectus

## What this is
The Owner Control Center is the plain-English operating surface for DreamCo. It is designed so an owner who is not a developer can understand what a system action does, while developers and investors can inspect the exact scripts, evidence, permissions, failure boundaries, and architecture behind it.

## Who it is for
- **Owner:** choose a goal, read what it does, run it safely, and see a human-readable result.
- **Users:** understand how Buddy protects data, memory, files, approvals, and connected apps.
- **Developers/engineers:** find the canonical command, input/output contract, logs, artifacts, tests, source files, and extension points.
- **Investors/partners:** understand what is implemented, what is measured, what is still gated, and how DreamCo can scale without pretending unverified capability is production-ready.

## Operating principles
1. Master bots coordinate; specialists and temporary sub-bots do bounded work.
2. Like-minded low-use specialists may merge as reversible aliases only when capability evidence and usage evidence support it.
3. User data stays user-controlled. Imports from apps require authorization, documented adapters, and clear retention/export/delete controls.
4. Every consequential external action stays approval-gated.
5. Every control-center action produces evidence instead of a success claim based only on intent.
6. Missing repository features or external integrations are labeled unavailable or unverified rather than treated as working.
7. The repository should be portable: core logic, policies, adapters, and tests should be separable enough to reuse in another project.

## Essential master-bot system
DreamCo defines 30 master-grade operational roles in `config/dreamco-essential-master-bots.json`. These roles are capability contracts, not an excuse to create duplicate permanent profiles. An existing canonical bot may satisfy a role; otherwise DreamBot/Buddy may hold the role and form a task-scoped sub-team.

## Personal Data Vault vision
Buddy should be able to help a user organize and search data the user is authorized to provide, including:
- documents and PDFs;
- notes and text;
- photos and user-owned images;
- audio/video metadata and user-owned media;
- spreadsheets and structured exports;
- bookmarks and links;
- calendar/contact/email exports when explicitly connected and authorized;
- app export files and API-accessible user data;
- local folders or user-selected cloud storage through approved adapters;
- user preferences, projects, goals, memories, receipts, records, and personal knowledge.

The system should prefer **import/export standards, official APIs, user-selected files, local-first indexes, and scoped connectors**. It must not bypass app permissions, scrape private data without authorization, or silently centralize sensitive information.

## Action catalog
The Owner Control Center exposes the following high-level actions. Each run explains its purpose in the GitHub Actions summary before reporting evidence.

| Action | Plain-English purpose | Primary evidence |
| --- | --- | --- |
| `health` | Check whether GitHub Actions definitions are structurally healthy. | Actions health report |
| `quick-check` | Run a fast Buddy verification pass. | Universal verification |
| `full-certification` | Run the strongest configured repository certification path. | Certification receipt |
| `fleet` | Verify fleet catalogs, routing, and fleet quality. | Fleet reports |
| `master-bots` | Build the reversible specialist-to-master consolidation plan. | Master-bot plan |
| `builder-readiness` | Check whether the builder team roles exist and are usable. | Builder readiness JSON |
| `debug` | Run debugging-oriented verification and dependency checks. | Test logs and reports |
| `security` | Run configured code/security/dependency checks. | Security outputs |
| `dependencies` | Audit packages, imports, libraries, and dependency health. | Dependency report |
| `connections` | Refresh declared connection/adaptor truth. | Connection catalog |
| `data-vault` | Check user-data/storage/search architecture and policies. | Data policy evidence |
| `memory` | Check memory and knowledge controls. | Memory policy evidence |
| `search` | Rebuild searchable DreamCo indexes. | Search index |
| `models` | Refresh model-routing and benchmark configuration. | Model router/benchmarks |
| `agents` | Check agent orchestration and sub-team policies. | Agent/fleet evidence |
| `automation` | Check automation and self-working-system policies. | Automation evidence |
| `reliability` | Check recovery, restart, checkpoint, and failure-handling systems. | Runtime evidence |
| `performance` | Run speed/accuracy/performance benchmarks that are available locally. | Benchmark report |
| `cost` | Check cost controls and deployment-cost policy. | Cost policy evidence |
| `developer-experience` | Verify setup, repository registry, tests, docs, and portability signals. | Registry/test evidence |
| `api` | Check API contracts and connection policy tests. | API test outputs |
| `deployment` | Run deployment preflight without silently deploying. | Deployment preflight |
| `product` | Refresh product/success program evidence. | Success program |
| `ux` | Check public-site and accessibility-oriented build surfaces. | Site checks |
| `business` | Refresh business-owner and revenue-readiness evidence. | Business readiness |
| `sales` | Check governed lead/sales support contracts. | Sales tests |
| `market-intelligence` | Refresh public/open-source/organization intelligence where approved. | Intelligence catalogs |
| `knowledge` | Rebuild knowledge/search/repository indexes. | Indexed records |
| `governance` | Check approval, policy, and trusted-code gates. | Governance tests |
| `recovery` | Recover/account for legacy assets without deleting canonical assets. | Recovery manifest |
| `run-everything` | Run the maximum configured orchestrated verification sequence. | Run Everything receipt |

## Investor view
DreamCo's value is not the raw count of bots. The defensible direction is a governed system that can organize many capabilities behind understandable master roles, form temporary specialized teams, preserve evidence, support local/user-controlled data, route among models and tools, and measure whether work actually completes. Bot count alone is inventory; orchestration, reliability, trust, portability, and user outcomes are product value.

## Developer extension contract
A developer adapting DreamCo should be able to:
1. add or replace an adapter without rewriting the whole system;
2. add a capability contract and tests before exposing it as working;
3. map a new specialist to an existing master before creating a permanent new bot;
4. run a narrow verification lane rather than the entire repository;
5. inspect generated evidence in `config/generated`, `reports`, and Actions artifacts;
6. disable or replace external providers while retaining core local behavior;
7. preserve user-data boundaries and explicit approvals.

## Truth boundary
This prospectus describes the intended operating contract and the repository controls being built. It is not a claim that every external connector, user-data source, model provider, deployment target, or production workflow has already passed live verification.
