# DreamCo Universal Expansion Blueprint

This blueprint turns the current benchmark framework into a connected operating program for human productivity, business services, workforce coverage, government/public-sector work, nonprofit support, creative mastery, advertising, sales and autonomous revenue discovery.

## Existing foundation preserved

The repository already contains universal human/computer/AI benchmarks, app/computer-use benchmark builders, business lifecycle benchmarks, creative mastery benchmarks, government/public-sector benchmarks and parallel benchmark-gap tooling. This expansion is additive: it should map and reuse those assets before creating duplicates.

## Universal benchmark contract

Benchmark the things people use AI for, computers for, apps for, websites for, professional services for and organizations for. Every benchmark must have measurable success criteria and a parallel path to close gaps: benchmark owner, gap analyst, builder, integration owner, sandbox QA, security/compliance, business-value evaluator and human reviewer when needed.

Coverage is not a capability claim. A target becomes an active capability only after repository evidence, sandbox evidence, permissions, safety checks and applicable legal/professional requirements pass.

## O*NET workforce lane

Use the O*NET database as an optional authoritative workforce source adapter. At the time this blueprint was authored, O*NET 30.3 was the current production release, with 1,016 occupation rows, 18,796 task statements and 57,543 job-title rows. Prefer pinned downloads for reproducible/offline builds and optionally refresh from official O*NET Web Services. O*NET must never become a hard dependency that prevents offline Buddy startup or core routing.

Map occupations, task statements, work activities, skills, knowledge, abilities, work context, work styles, technology skills and tools to DreamCo benchmark intents. Preserve O*NET-SOC codes, provenance, source version, retrieval date and required attribution.

## Business-as-a-service model

Every meaningful step of starting, operating, selling, marketing, supporting, automating, expanding and winding down a business should be representable as a separate billable service or a bundle. The machine-readable catalog is in `config/business-billable-lifecycle-catalog.json`.

Lead generation is only one subsystem. The universal revenue path is market definition -> lead discovery -> enrichment -> qualification -> outreach -> appointment -> discovery -> demo -> proposal -> objection handling -> close -> onboarding -> customer success -> upsell -> renewal -> referral -> win-back.

Each DreamCo bot should be able to inherit this sales system rather than rebuilding sales logic independently.

## 500-method advertising benchmark

`tools/build_500_advertising_methods.py` deterministically generates 500 advertising benchmark records by combining 25 channels with 20 campaign motions. Each method receives research, creative, compliance, sandbox, analytics and sales-handoff workers. These methods are experiments to test, not guaranteed results.

## Book of Associations

`config/book-of-associations.json` defines a shared association knowledge graph for trade groups, professional associations, chambers, standards bodies, licensing/certification organizations, economic-development groups, incubators, accelerators, investor networks, supplier-diversity groups, conferences, nonprofit networks and related organizations.

Use it for market intelligence, partnerships, sponsorships, events, referrals, public directories where permitted, procurement pathways, grants, standards and sales personalization. Never imply endorsement merely because an organization is in the graph.

## Government and public-sector mastery

Benchmark both sides of public-sector value:

1. Help residents save time using government services: benefit discovery, forms, appointments, records, permits, licenses, tax navigation, service routing, language access and accessibility.
2. Help government workers with administrative workflows, data analysis, document support, knowledge retrieval, constituent service, procurement, grants, planning, reporting and other job tasks where safe and allowed.
3. Help DreamCo prepare for eligible government contracts: opportunity discovery, NAICS/PSC mapping, readiness, capability statements, bid/no-bid scoring, requirements extraction, compliance matrices, proposal support, subcontractor discovery, past-performance libraries and deadline tracking.

Never fabricate certifications, eligibility or past performance; never submit a bid, filing or binding representation without appropriate authority and approval.

## Nonprofit and for-profit coverage

Benchmark major organizational models including sole proprietorships, partnerships, LLCs, corporations, cooperatives, franchises, startups, agencies, marketplaces, subscription businesses, ecommerce, manufacturing, retail and professional services, plus public charities, private foundations, membership nonprofits, education/arts/social-service organizations, trade/professional associations and other nonprofit structures.

Bots should understand formation/operating differences as workflow context, not provide regulated professional conclusions without qualified review where required.

## Creative mastery

Creative benchmarks should cover full production pipelines, not isolated generation:

- Books: idea -> research -> outline -> drafting -> editing -> fact-checking -> illustration -> layout -> cover -> metadata -> publishing -> distribution -> marketing -> rights tracking.
- Film/video: concept -> script -> storyboard -> shot list -> budget -> production planning -> editing -> VFX -> sound -> color -> captions -> trailers -> distribution -> marketing.
- Music: concept -> songwriting -> composition -> arrangement -> recording -> editing -> mixing -> mastering -> artwork -> metadata -> distribution -> promotion -> rights/royalty tracking.

Quality benchmarks should include coherence, originality, factuality where relevant, technical quality, accessibility, rights/attribution hygiene, audience fit, cost, speed and human-review needs.

## Sandbox standard

Every capability should graduate through evidence-based layers: unit, contract, integration, simulated external API, offline fallback, adversarial, permission-boundary, privacy, security, policy, load, latency, cost, reliability, recovery, human-review, red-team, regression and canary testing.

Each test needs a fixture, expected result, source evidence, risk classification, thresholds, failure injection, audit log, rollback and post-deploy monitoring. Never silently spend money, sign contracts, submit government forms/bids, bypass permissions, store secrets in test fixtures or promote a capability based only on self-reported success.

## Repository connectivity rule

Buddy should discover and map the bot registry, division registry, capability registry, tool registry, benchmark registry, workflow registry, integrations, revenue systems, sandbox systems, model routing and memory/knowledge systems. Connection health should track whether each component is present, importable, registered, routable, sandbox-tested, permissioned, observable and documented.

The goal is not to claim everything is connected merely because files exist. The goal is to make missing connections measurable and automatically assign a parallel bot path to close each gap.
