# Buddy full-fleet execution and specialist portfolio operating model

## Canonical structure

DreamCo retains 45 canonical business divisions. Eleven supplemental specialist portfolios sit beneath canonical owners; they do not create duplicate primary ownership.

| Specialist portfolio | Canonical owner | Exclusive operating domain | Specialist bots |
|---|---|---|---:|
| DreamAffiliate | DreamSalesPro | Affiliate program operations | 5 |
| DreamAgency | DreamProServices | Agency delivery operations | 5 |
| DreamFoundry | DreamAIInfra | Model productization and evaluation | 5 |
| DreamFranchise | DreamBizLaunch | Franchise system design and governance | 5 |
| DreamIntegrations | DreamCodeLab | Cross-system integration reliability | 5 |
| DreamLicensing | DreamLegal | Commercial IP rights administration | 5 |
| DreamRobotics | DreamAIInfra | Physical robotics task and safety operations | 5 |
| DreamSaaS | DreamAutomation | SaaS product and subscription lifecycle | 5 |
| DreamStreaming | DreamContent | Streaming channel and broadcast operations | 5 |
| DreamTravel | DreamTransport | Traveler journey planning and support | 5 |
| Dream3D | DreamCodeLab | Interactive Three.js, real-time 3D and GPU rendering | 19 |

The first ten portfolios contain 50 existing specialist identities. Dream3D adds 19 Three.js Markdown-only profiles that were previously UNASSIGNED. Each receives a distinct capability charter with five implementable capabilities, approved source types, monetization options and a measurable outcome event. DreamCodeLab retains general software engineering; Dream3D owns the narrower real-time 3D implementation domain, with DreamContent and DreamAIInfra as collaborators.

## GrokTeammates workforce routing

The 112 GrokTeammates profiles are a cross-functional execution pool, not a 46th business division. `config/bots/teammate-lane-division-crosswalk.json` assigns each lane to one of the 45 canonical owners. Each lane retains a shared platform MasterBot route (46–65) while its primary division route points to the appropriate canonical owner. All proposed domain matches remain non-privileged until owner approval.

## Full catalog execution map

`config/generated/buddy-fleet-execution-map.json` is generated from the complete `config/bots/bot-manifests.generated.json` catalog, not just the App_bots directory. Every manifest profile receives:

- one canonical division owner, with GrokTeammates shared-workforce identity preserved where applicable;
- one primary domain MasterBot route and shared access to platform MasterBots 46–65;
- a Buddy governed-queue, evidence-backed learning, benchmark and failure-recovery route;
- source paths, declared integrations and capability lineage;
- either a commercial opportunity-to-cash plan or an internal capability/value-delivery route;
- explicit duplicate-profile and duplicate-capability review signals.

The build fails if a specialist bot lacks a charter, a specialist capability exactly duplicates an indexed canonical-owner capability, or a revenue candidate lacks an approved opportunity-source category.

## Money OS coverage and opportunity-to-cash

The map separately includes all 15 registered Money OS bot modules and all seven newer Money OS entries (22 total). Entries are retained even when a code-module path does not exactly match a manifest slug; a known related manifest bot is linked explicitly, while unmatched modules remain visible for profile-link review. Each entry receives a canonical owner, MasterBot route, Buddy queue, learning and benchmark routes, revenue lane, approved source types, monetization options and evidence event.

Money OS opportunity sources must be official, licensed, authorized, or user-supplied with permission. The route is:

1. Discover from an approved source.
2. Verify source freshness, rights, terms and eligibility.
3. Score fit, value, cost, risk and confidence.
4. Prepare a distinct offer and fulfillment plan.
5. Simulate unit economics and downside.
6. Request required owner approval for outreach, spend, contracts and payments.
7. Execute only through approved connectors and bounded permissions.
8. Record the verified conversion, accepted lead, paid invoice, confirmed commission or completed transaction.
9. Send outcome and failure evidence to Buddy for reviewed learning.

Forecasts and simulated sales are never revenue. Declared API names are integration targets, not proof that credentials or live provider connections exist. No bot is live-enabled by this generator.

## Learning and mastery

Buddy is the orchestrator, not a blanket permission grant. Each bot's learning loop should consume only sanitized, rights-cleared and provenance-backed examples. Promotion requires reproducible test evidence, benchmark holdouts, review and lineage. Failures create structured recovery tasks; they do not silently modify production code or model weights.

## Readiness truth boundary

The generated manifest currently contains 1,232 profiles. The revenue-readiness builder now enumerates the full manifest rather than the older 1,051-profile App_bots-only source. Profiles missing business or sandbox curriculum remain blocked in readiness until those curricula and runtime evidence exist; they are not silently treated as passed.

The charters and execution map are planning and routing artifacts. They do not prove runtime availability, connected credentials, passing benchmarks, legal eligibility, customer demand, production readiness, model training or realized revenue. Proposed division routes remain planning-only pending owner review. Live monetization remains gated by `config/live-revenue-gate.json` and explicit owner authorization.
