# Master Roadmap Crosswalk

**Generated:** 2026-09-28T17:43:02-05:00 (America/Chicago)  
**Sources:** `docs/DREAMCO_MASTER_ROADMAP_2026.md`, `reports/PLAN_TO_GROK_BOT_COVERAGE.md` (2026-09-21 snapshot; original file no longer in checkout)  
**Method:** keyword heuristic mapping + spot-check for done claims. Needs human review. No `production_ready` flips.

## Counts

| metric | count |
|---|---:|
| ideas | 100 |
| mapped | 100 |
| unmapped | 0 |
| done_or_existing | 14 |
| done_without_evidence | 0 |
| plans | 37 |
| plans_with_zero_ideas | 15 |
| owners_live | 37 |

> All 37 plans now have a live owner bot. The coverage report's "covered 6 / uncovered 31" is stale on owners; owner existence is not evidence.

## Certify-first order

| # | plan_id | owner | status | current evidence |
|---:|---|---|---|---|
| 1 | `plan-buddy-bootcamp` | Grok-Buddy-Bootcamp-Commandant | partial | specs/config/tools; no graduation evidence |
| 2 | `plan-buddy-frontier` | Grok-Frontier-Loop-Captain | partial | G1-G7 defined; 0/7 evidence-passed |
| 3 | `plan-model-access` | Grok-Model-Access-Product-Owner | partial | path stubs; owner_500_authenticated_live=false |
| 4 | `plan-data-package` | Grok-Data-Package-Merchant | partial | SKU family designed; populatedDatasetCount 0; no live sales |
| 5 | `plan-fleet-capability-gap` | Grok-Fleet-Gap-Closer | partial | 1101 profiles; production_ready_profiles=0; sandbox/adapter/auth/telemetry false for all |
| 6 | `plan-prod-readiness-master` | Grok-PRC-Certifier | partial | 0/1101 bots production_ready; PRC 0 verified / 16 partial / 3 unknown |
| 7 | `plan-huggingface-mastery` | Grok-HF-Mastery-Coach | partial | inventory + Day-1 plan; study_packs not materialized (at scan time) |
| 8 | `plan-onet-mastery` | Grok-ONET-Ingest-Lead | stub | pinned O*NET ingest not verified |
| 9 | `plan-universal-sandbox-programs` | Grok-Universal-Sandbox-Director | partial | 0/1101 sandbox_test_defined |
| 10 | `plan-engineering-gap-closure` | Grok-Eng-Gap-Closure-Pilot | partial | CI Gap Closure noop on tip; not green-certified |

## Roadmap idea → plan crosswalk

| # | idea | section | roadmap status | plan_ids | evidence (done only) |
|---:|---|---|---|---|---|
| 1 | Command Tower meta-workflow and GitHub Pages dashboard | Workflow Organization & Dashboard | done | `plan-actions-consolidation` | docs/DREAMCO_MASTER_ROADMAP_2026.md |
| 2 | Emoji/tiered workflow naming | Workflow Organization & Dashboard | done | `plan-actions-consolidation` | tools/generate_bot_fleet_catalog.ts |
| 3 | Workflow categories/tags | Workflow Organization & Dashboard | planned | `plan-actions-consolidation` |  |
| 4 | Mermaid workflow map | Workflow Organization & Dashboard | done | `plan-actions-consolidation` | docs/DREAMCO_MASTER_ROADMAP_2026.md |
| 5 | Dynamic README badges | Workflow Organization & Dashboard | done | `plan-actions-consolidation` | docs/BUDDY_BOOTCAMP_SANDBOX_SPEC.md |
| 6 | Multi-language matrix testing | Workflow Organization & Dashboard | done | `plan-actions-consolidation` | .github/workflows/repository-test-matrix.yml |
| 7 | Reusable composite actions | Workflow Organization & Dashboard | done | `plan-actions-consolidation` | docs/DREAMCO_CHAT_CONTEXT_2026-08-11.md |
| 8 | Dream Mode | Workflow Organization & Dashboard | done | `plan-actions-consolidation` | docs/DREAMCO_CHAT_CONTEXT_2026-08-11.md |
| 9 | Archive stale workflows | Workflow Organization & Dashboard | planned | `plan-actions-consolidation` |  |
| 10 | PR label workflow selector | Workflow Organization & Dashboard | planned | `plan-actions-consolidation` |  |
| 11 | Central secrets/environment management | Workflow Organization & Dashboard | planned | `plan-actions-consolidation` |  |
| 12 | Public Workflow Marketplace | Workflow Organization & Dashboard | planned | `plan-actions-consolidation` |  |
| 13 | AI workflow generator | Workflow Organization & Dashboard | future | `plan-actions-consolidation`, `plan-platform-expansion` |  |
| 14 | Template version pinning/migrations | Workflow Organization & Dashboard | planned | `plan-actions-consolidation` |  |
| 15 | Parallel feature-branch testing | Workflow Organization & Dashboard | planned | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 16 | Full CI for all bots | CI/CD & Deployment | in progress | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 17 | External builder import → GitHub sync | CI/CD & Deployment | planned | `plan-legacy-recovery` |  |
| 18 | Blue/green deployment | CI/CD & Deployment | planned | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 19 | Production bot containerization | CI/CD & Deployment | planned | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 20 | Multi-target deployment | CI/CD & Deployment | planned | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 21 | Semantic release/changelog | CI/CD & Deployment | planned | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 22 | Anomaly-triggered rollback | CI/CD & Deployment | planned | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 23 | Zero-downtime updates | CI/CD & Deployment | planned | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 24 | Dependency graph and automated security PRs | CI/CD & Deployment | planned | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 25 | Performance benchmarking | CI/CD & Deployment | planned | `plan-500-model-benchmark` |  |
| 26 | API/OAuth secret scanning | CI/CD & Deployment | planned | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 27 | Enterprise policy/compliance automation | CI/CD & Deployment | future | `plan-prod-readiness-master` |  |
| 28 | Visual regression testing | CI/CD & Deployment | planned | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 29 | IoT/firmware extension hooks | CI/CD & Deployment | future | `plan-manufacturer-rfq` |  |
| 30 | Feature flags by tier | CI/CD & Deployment | planned | `plan-model-access` |  |
| 31 | BuddyAI PR reviewer | Intelligence & Learning | planned | `plan-trusted-code-delivery`, `plan-github-competitor` |  |
| 32 | Self-evolution triggers | Intelligence & Learning | done | `plan-endgame-architecture`, `plan-gain-to-production` | docs/DREAMCO_MASTER_ROADMAP_2026.md |
| 33 | Predictive bot health | Intelligence & Learning | planned | `plan-buddy-success-fleet-quality` |  |
| 34 | Natural-language evolution commands | Intelligence & Learning | planned | `plan-endgame-architecture`, `plan-gain-to-production` |  |
| 35 | Test generation from learning history | Intelligence & Learning | planned | `plan-endgame-architecture`, `plan-gain-to-production` |  |
| 36 | Event/learning anomaly detection | Intelligence & Learning | planned | `plan-buddy-success-fleet-quality` |  |
| 37 | Conversation sentiment/success analysis | Intelligence & Learning | future | `plan-buddy-success-fleet-quality` |  |
| 38 | Cross-bot knowledge sharing | Intelligence & Learning | planned | `plan-endgame-architecture`, `plan-gain-to-production` |  |
| 39 | Milestone creative generation | Intelligence & Learning | future | `plan-multimodal-learning`, `plan-media-game-mastery` |  |
| 40 | Autonomous improvement PRs | Intelligence & Learning | planned | `plan-trusted-code-delivery`, `plan-github-competitor` |  |
| 41 | Tier enforcement | Intelligence & Learning | done | `plan-model-access` | tools/generate_buddy_model_benchmarks.ts |
| 42 | Global learning synchronization | Intelligence & Learning | done | `plan-endgame-architecture`, `plan-gain-to-production` | .github/workflows/dreamco-control-plane.yml |
| 43 | Context-aware AI code review | Intelligence & Learning | planned | `plan-trusted-code-delivery`, `plan-github-competitor` |  |
| 44 | Adaptive runner scaling | Intelligence & Learning | future | `plan-actions-consolidation` |  |
| 45 | Memory-injection tests | Intelligence & Learning | planned | `plan-prod-readiness-master` |  |
| 46 | Revenue simulations before deploy | Intelligence & Learning | planned | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 47 | Agent safety controls | Intelligence & Learning | planned | `plan-prod-readiness-master` |  |
| 48 | Multimodal testing | Intelligence & Learning | future | `plan-multimodal-learning`, `plan-media-game-mastery` |  |
| 49 | What-if business simulator | Intelligence & Learning | future | `plan-universal-sandbox-programs` |  |
| 50 | Auto-document learned behaviors | Intelligence & Learning | planned | `plan-endgame-architecture`, `plan-gain-to-production` |  |
| 51 | Per-bot/division revenue attribution | Revenue & Governance | planned | `plan-live-revenue`, `plan-division-production` |  |
| 52 | Automated governance reports | Revenue & Governance | planned | `plan-prod-readiness-master` |  |
| 53 | Builder-to-monetization recommendations | Revenue & Governance | planned | `plan-startup-factory`, `plan-live-revenue` |  |
| 54 | Partner opportunity detection | Revenue & Governance | planned | `plan-startup-factory`, `plan-live-revenue` |  |
| 55 | Company lookup → lead pipeline | Revenue & Governance | planned | `plan-startup-factory`, `plan-live-revenue` |  |
| 56 | Max-parallel delivery control | Revenue & Governance | existing | `plan-actions-consolidation` | .github/workflows/buddy-65-masterbot-training.yml |
| 57 | Enterprise invoicing/payment | Revenue & Governance | future | `plan-live-revenue` |  |
| 58 | Contributor revenue bounty system | Revenue & Governance | planned | `plan-live-revenue` |  |
| 59 | Live division revenue dashboards | Revenue & Governance | planned | `plan-live-revenue`, `plan-division-production` |  |
| 60 | Subscription migration testing | Revenue & Governance | planned | `plan-live-revenue` |  |
| 61 | Marketplace deployment automation | Revenue & Governance | future | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 62 | Tax/compliance reporting | Revenue & Governance | future | `plan-prod-readiness-master`, `plan-live-revenue` |  |
| 63 | A/B testing for revenue flows | Revenue & Governance | planned | `plan-live-revenue` |  |
| 64 | Revenue forecasting | Revenue & Governance | planned | `plan-live-revenue` |  |
| 65 | Community royalty distribution | Revenue & Governance | future | `plan-live-revenue` |  |
| 66 | Real-time observability dashboard | Community, Observability & DevEx | planned | `plan-buddy-success-fleet-quality` |  |
| 67 | Contributor onboarding | Community, Observability & DevEx | done | `plan-education-curriculum-programs` | .github/workflows/model-progress-center.yml |
| 68 | PR demo environments | Community, Observability & DevEx | planned | `plan-platform-expansion` |  |
| 69 | Discord/Slack/Telegram notifications | Community, Observability & DevEx | planned | `plan-platform-expansion` |  |
| 70 | Community priority voting | Community, Observability & DevEx | future | `plan-platform-expansion` |  |
| 71 | Contributor thank-yous/leaderboards | Community, Observability & DevEx | planned | `plan-startup-factory`, `plan-live-revenue` |  |
| 72 | Hackathon mode | Community, Observability & DevEx | future | `plan-education-curriculum-programs` |  |
| 73 | Localization pipelines | Community, Observability & DevEx | future | `plan-education-curriculum-programs` |  |
| 74 | Accessibility testing | Community, Observability & DevEx | planned | `plan-platform-expansion` |  |
| 75 | Educational content generation | Community, Observability & DevEx | future | `plan-education-curriculum-programs` |  |
| 76 | Star-gazer engagement | Community, Observability & DevEx | planned | `plan-platform-expansion` |  |
| 77 | Fork synchronization | Community, Observability & DevEx | planned | `plan-platform-expansion` |  |
| 78 | Safe public workflow API | Community, Observability & DevEx | future | `plan-actions-consolidation`, `plan-platform-expansion` |  |
| 79 | Mobile Actions status page | Community, Observability & DevEx | done | `plan-platform-expansion` | framework/dreamco_source_learning/__init__.py |
| 80 | Post-run DreamScore summaries | Community, Observability & DevEx | planned | `plan-buddy-success-fleet-quality` |  |
| 81 | Bot-fleet digital twin | Advanced Innovation | future | `plan-universal-sandbox-programs` |  |
| 82 | Federated learning | Advanced Innovation | future | `plan-open-source-invention` |  |
| 83 | AR/VR workflow visualization | Advanced Innovation | future | `plan-actions-consolidation`, `plan-multimodal-learning` |  |
| 84 | Compute sustainability tracking | Advanced Innovation | planned | `plan-platform-expansion` |  |
| 85 | Quantum-readiness placeholders | Advanced Innovation | future | `plan-platform-expansion` |  |
| 86 | Haptic/multisensory testing | Advanced Innovation | future | `plan-multimodal-learning`, `plan-media-game-mastery` |  |
| 87 | Patent-idea extraction | Advanced Innovation | future | `plan-open-source-invention` |  |
| 88 | Automated launch storytelling | Advanced Innovation | future | `plan-multimodal-learning`, `plan-media-game-mastery` |  |
| 89 | Physical bot integration | Advanced Innovation | future | `plan-manufacturer-rfq` |  |
| 90 | Cross-division synergy finder | Advanced Innovation | planned | `plan-division-production` |  |
| 91 | Chaos engineering | Advanced Innovation | done | `plan-universal-sandbox-programs` | docs/DREAMCO_CHAT_CONTEXT_2026-08-11.md |
| 92 | Zero-trust bot communication | Advanced Innovation | planned | `plan-prod-readiness-master` |  |
| 93 | Blockchain transaction attestation | Advanced Innovation | future | `plan-platform-expansion` |  |
| 94 | Research-paper generation | Advanced Innovation | future | `plan-open-source-invention` |  |
| 95 | Empire growth simulator | Advanced Innovation | future | `plan-universal-sandbox-programs`, `plan-platform-expansion` |  |
| 96 | Autonomous workflow designer | Transformative | future | `plan-actions-consolidation`, `plan-platform-expansion` |  |
| 97 | Metaverse-ready deployment | Transformative | future | `plan-engineering-gap-closure`, `plan-modernization` |  |
| 98 | Global timezone handoff | Transformative | planned | `plan-actions-consolidation` |  |
| 99 | Threshold-gated advanced self-modification | Transformative | future | `plan-endgame-architecture`, `plan-gain-to-production` |  |
| 100 | DreamCo Actions as a product | Transformative | future | `plan-platform-expansion` |  |

## Gaps

**Done/existing claims without evidence (0):** none

**Unmapped ideas (0):** none

**Plans with no roadmap ideas (15):** `plan-goals-to-gates`, `plan-fleet-capability-gap`, `plan-branch-cleanup`, `plan-buddy-bootcamp`, `plan-buddy-frontier`, `plan-data-package`, `plan-huggingface-mastery`, `plan-onet-mastery`, `plan-dreamco-master-roadmap`, `plan-superbot-migration`, `plan-repair-orchestrator`, `plan-65-masterbot`, `plan-notes-to-code`, `plan-china-us-scout`, `plan-business-productivity-programs`

**Conflicts, roadmap done vs plan stub (1):** #67 Contributor onboarding vs `plan-education-curriculum-programs`

## Next actions

1. Owners of certify-first plans post evidence paths; this crosswalk refreshes from their reports.
2. Verify or downgrade each done claim lacking evidence in the 2026 roadmap.
3. Add roadmap entries for plans with zero ideas (mostly Buddy/learning/data-package tracks added after the roadmap was written), or mark them out of roadmap scope.
4. Replace heuristic mappings with owner-confirmed mappings.
