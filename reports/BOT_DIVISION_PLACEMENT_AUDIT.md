# Bot Division Placement Audit

Profiles scanned: **1051** across **45** expected divisions.

## Fleet placement status

- `well_placed`: 322
- `review_cross_division`: 87
- `move_candidate`: 35
- `keep_low_confidence`: 607

## Division strengthening and placement

| Division | Profiles | Move candidates | Cross-division review | Strengthen next |
| --- | ---: | ---: | ---: | --- |
| CommandCore | 13 | 1 | 1 | single canonical orchestration graph; global permissions/approval engine; fleet health and evidence dashboard |
| DreamAIInfra | 25 | 2 | 2 | model routing benchmarks; local/cloud inference adapters; cost/latency/quality telemetry |
| DreamAdmin | 21 | 0 | 4 | calendar/email/document workflows; records retention rules; meeting-to-task automation |
| DreamAgents | 20 | 3 | 2 | agent templates and tool contracts; Bootcamp certification; multi-agent coordination |
| DreamAgriculture | 20 | 0 | 0 | crop/livestock data packs; weather/soil integrations; farm economics |
| DreamArts | 18 | 2 | 1 | rights/provenance tooling; portfolio and commission workflows; multimodal creation pipelines |
| DreamAutomation | 21 | 3 | 0 | canonical workflow runtime; connector retry/idempotency framework; human approval steps |
| DreamBizLaunch | 21 | 1 | 3 | idea-to-launch checklist; entity/permit resource packs; offer/pricing validation |
| DreamCodeLab | 146 | 0 | 6 | language/library mastery; CI/debug agents; secure code generation |
| DreamConstruction | 19 | 0 | 1 | estimating benchmarks; project scheduling; permit/code resource packs |
| DreamContent | 16 | 0 | 2 | podcast/video/writing studios; cross-platform publishing preparation; content rights checks |
| DreamCrypto | 20 | 0 | 2 | testnet-first tooling; wallet/custody education; market-risk dashboards |
| DreamCustIntel | 25 | 1 | 2 | consented customer data model; feedback/journey analytics; retention prediction benchmarks |
| DreamCyber | 25 | 0 | 1 | authorized device posture checks; secure coding benchmarks; incident response drills |
| DreamData | 16 | 0 | 0 | universal data catalog; Mastery Data Pack factory; data quality/provenance tests |
| DreamDecision | 25 | 0 | 2 | decision templates; scenario/uncertainty engine; evidence quality scoring |
| DreamEducation | 20 | 1 | 3 | subject mastery packs; adaptive tutoring; assessment generators |
| DreamEmpire | 5 | 0 | 0 | portfolio KPI system; capital/resource allocation; business graduation dashboard |
| DreamEntFinance | 25 | 0 | 4 | three-statement planning; treasury/cash forecasting; controls/audit trails |
| DreamFinance | 25 | 0 | 2 | budget/cash-flow engine; fraud watch; credit education |
| DreamFlow | 5 | 0 | 0 | work graph and dependencies; queue ownership; SLA/deadline engine |
| DreamFood | 20 | 0 | 0 | menu/cost engineering; inventory/waste reduction; supplier comparison |
| DreamGlobal | 16 | 1 | 1 | country intelligence packs; localization; cross-border business setup research |
| DreamHealth | 20 | 0 | 1 | health education data packs; records organization; care-preparation workflows |
| DreamInfluence | 25 | 0 | 3 | creator growth analytics; partnership/sponsorship scout; campaign benchmarks |
| DreamLegal | 25 | 0 | 1 | jurisdiction-aware research; contract/document analysis; deadline/calendaring |
| DreamLoans | 23 | 3 | 3 | loan comparison engine; eligibility preparation; APR/fee affordability tests |
| DreamMaintenance | 21 | 1 | 1 | asset registry; predictive/preventive maintenance; parts/supplier scout |
| DreamMarket | 5 | 0 | 0 | Master Scout integration; competitor intelligence; demand/pricing experiments |
| DreamMilitary | 20 | 1 | 3 | non-weapon logistics; maintenance/readiness; veteran resources |
| DreamOps | 26 | 0 | 1 | operating scorecards; capacity/service-level planning; incident playbooks |
| DreamPayments | 23 | 1 | 2 | processor comparison; checkout/billing/subscription adapters; fraud/chargeback workflows |
| DreamPersonalCare | 30 | 3 | 5 | personal routines and goals; beauty/grooming product research; care service marketplace |
| DreamPlanetary | 25 | 0 | 1 | climate/environment datasets; earth/space monitoring; disaster/resource planning |
| DreamProServices | 25 | 0 | 3 | professional service templates; client intake; scope/proposal generation |
| DreamProduction | 20 | 0 | 1 | manufacturing planning; BOM/quality workflows; supplier/manufacturer scout |
| DreamProtection | 20 | 2 | 3 | personal/business safety planning; fraud/scam prevention; emergency preparedness |
| DreamRealEstate | 25 | 0 | 1 | property/deal scout; rental/homebuyer workflows; assistance/low-cash-entry program research |
| DreamRetail | 26 | 2 | 3 | product/supplier catalog; pricing/margin optimization; inventory |
| DreamSalesPro | 37 | 2 | 3 | permission-based lead systems; sales call coaching; CRM pipeline |
| DreamScience | 20 | 2 | 5 | research retrieval; experiment/evaluation templates; scientific data packs |
| DreamSocial | 33 | 1 | 7 | social publishing adapters; community management; social listening |
| DreamTrade | 12 | 1 | 0 | supplier/import-export discovery; tariff/customs research; landed-cost models |
| DreamTransport | 19 | 1 | 1 | route/fleet planning; maintenance integration; shipping/logistics comparison |
| GameTitan | 4 | 0 | 0 | game design/build pipeline; NPC/agent simulation; multiplayer/network benchmarks |

## Move candidates

- `self-debug-engine`: CommandCore → **DreamCodeLab** (current 0, recommended 8; hits: debug, developer, software, test)
- `finetune-orchestrator`: DreamAIInfra → **DreamData** (current 2, recommended 8; hits: analytics, data, dataset, pipeline)
- `data-quality-engine`: DreamAIInfra → **DreamData** (current 0, recommended 10; hits: analytics, data, data quality, pipeline)
- `devin-agent`: DreamAgents → **DreamCodeLab** (current 2, recommended 10; hits: code, coding, debug, software, test)
- `openagents-web3`: DreamAgents → **DreamCrypto** (current 2, recommended 12; hits: blockchain, crypto, defi, token, wallet)
- `deep-research-agent`: DreamAgents → **DreamMarket** (current 2, recommended 8; hits: market, market research, trend)
- `video-editor-ai`: DreamArts → **DreamContent** (current 0, recommended 8; hits: audio, content, script, video)
- `copywriting-ai`: DreamArts → **DreamContent** (current 0, recommended 8; hits: content, script, writer, writing)
- `scheduling-bot`: DreamAutomation → **DreamAdmin** (current 2, recommended 10; hits: administrative, calendar, email, meeting, scheduling)
- `social-scheduler`: DreamAutomation → **DreamSocial** (current 2, recommended 8; hits: post, social, social media)
- `quality-control`: DreamAutomation → **DreamProduction** (current 2, recommended 8; hits: manufacturing, quality control)
- `market-research-biz`: DreamBizLaunch → **DreamMarket** (current 2, recommended 10; hits: competitor, market, market research, trend)
- `brand-perception-monitor`: DreamCustIntel → **DreamSocial** (current 4, recommended 10; hits: social, social listening, social media)
- `school-safety-ai`: DreamEducation → **DreamAdmin** (current 0, recommended 8; hits: document, email, office, scheduling)
- `customs-tariffs`: DreamGlobal → **DreamTrade** (current 0, recommended 8; hits: customs, export, import, tariff)
- `financial-literacy`: DreamLoans → **DreamEducation** (current 2, recommended 8; hits: education, lesson, quiz, tutor)
- `legal-money-bot`: DreamLoans → **DreamLegal** (current 0, recommended 8; hits: attorney, case, law, legal)
- `rental-cashflow-bot`: DreamLoans → **DreamRealEstate** (current 0, recommended 10; hits: landlord, property, real estate, rental)
- `medical-app-bot`: DreamMaintenance → **DreamHealth** (current 0, recommended 12; hits: care, clinical, health, medical, patient, provider)
- `cybersecurity-mil`: DreamMilitary → **DreamCyber** (current 2, recommended 10; hits: cyber, incident, security, threat, vulnerability)
- `finance-app-bot`: DreamPayments → **DreamFinance** (current 2, recommended 14; hits: budget, expense, finance, financial, personal finance, saving)
- `education-app-bot`: DreamPersonalCare → **DreamEducation** (current 0, recommended 8; hits: education, learning, quiz, teacher)
- `food-drink-app-bot`: DreamPersonalCare → **DreamFood** (current 0, recommended 8; hits: allergen, food, menu, restaurant)
- `home-buyer-bot`: DreamPersonalCare → **DreamRealEstate** (current 0, recommended 10; hits: homebuyer, property, real estate, realtor)
- `threat-assessment`: DreamProtection → **DreamCyber** (current 0, recommended 8; hits: incident, security, threat, vulnerability)
- `cyber-physical`: DreamProtection → **DreamCyber** (current 0, recommended 8; hits: cyber, incident, security, threat)
- `fraud-shield`: DreamRetail → **DreamPayments** (current 0, recommended 8; hits: chargeback, payment, transaction)
- `social-commerce`: DreamRetail → **DreamSocial** (current 4, recommended 14; hits: facebook, instagram, post, social, social media, tiktok)
- `stripe-billing`: DreamSalesPro → **DreamPayments** (current 0, recommended 8; hits: billing, payment, stripe, subscription)
- `wholesale-trade-bot`: DreamSalesPro → **DreamTrade** (current 0, recommended 8; hits: sourcing, supplier, trade, wholesale)
- `chemical-inventory`: DreamScience → **DreamAdmin** (current 2, recommended 8; hits: document, email, office, scheduling)
- `lab-equipment-mgr`: DreamScience → **DreamAdmin** (current 2, recommended 8; hits: assistant, calendar, email, scheduling)
- `influencer-bot`: DreamSocial → **DreamInfluence** (current 0, recommended 8; hits: campaign, influence, influencer, partnership)
- `logistics-router`: DreamTrade → **DreamTransport** (current 0, recommended 8; hits: delivery, logistics, route, shipping)
- `customs-clearance`: DreamTransport → **DreamTrade** (current 0, recommended 8; hits: customs, export, import, trade)

## Rule

This report recommends. It does not auto-move bots. Any move must update the canonical source, generated fleet artifacts, tests, benchmark ownership, business blueprint references, and cross-division collaboration metadata together.
