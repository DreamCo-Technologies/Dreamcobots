# Buddy Open-Source Multimodal Bootcamp

## Goal

Buddy Bootcamp is a continuously refreshed, evidence-based learning system for the 55 DreamCo domain divisions. It discovers upstream repositories, Hugging Face datasets/models/Spaces, technical documentation, and authorized video/audio/music material. It creates detailed independent study guides, lessons, projects, assessments, and training candidates. It does not claim that Buddy has mastered a topic simply because it indexed or summarized a source.

## Repositories first, not YouTube-first

The primary curriculum sources are versioned public repositories: source code, READMEs, documentation, examples, tests, notebooks, issue discussions where appropriate, release notes, and project architecture. YouTube is an optional media source, never the sole source of truth. The source catalog must retain repository URL, pinned commit or release, license identifier and evidence, discovery date, upstream attribution, division mapping, and a recheck date.

Buddy learns by *studying* upstream implementation and documentation, then building an independent exercise or compatible integration. It must not copy entire repositories into DreamCo or represent upstream code as original DreamCo work. License compatibility and security checks precede reuse.

## Hugging Face: all subjects, all artifact types

The discovery system searches the Hub's datasets, models, and Spaces separately. It uses task/subject terms and pagination, stores the Hub ID, card metadata, tags, license, revision, downloads/likes where available, and the source card URL. Each artifact gets its own summary and suitability review:
- Dataset guide: purpose, features, splits, sampling, data provenance, bias, privacy, license, preprocessing, recommended tasks, and evaluation plan.
- Model guide: intended use, architecture, task, inputs/outputs, inference, training disclosures, evaluation, limitations, license, hardware and safety.
- Space guide: demo purpose, user flow, model/dataset dependencies, code/dependencies, reproducibility, limitations and license.

"Every subject" means the subject taxonomy and discovery sweep must be broad and continually expanded from observed Hub tags. The Hub changes constantly; do not promise a fixed final count or claim every artifact was summarized unless inventory pagination and guide coverage prove it.

## Video, audio and music learning

Buddy needs a multimodal ingestion capability, not just a URL catalog. For authorized or user-provided videos, the pipeline can extract audio, transcribe speech, sample frames, detect scenes, align timestamps, explain code or demonstrations, and create a detailed chapter-by-chapter guide. Sparse frame sampling is the default; dense processing is reserved for tasks that need temporal understanding.

For audio and music, Buddy can learn speech recognition, sound classification, audio signal processing, music information retrieval, tempo/meter, harmony/key estimation, structure, timbre/instrument analysis where supported, production/mixing concepts, and MIDI/score analysis. Music generation and audio models are separate capabilities and require their own model, data, compute, and evaluation plan. Copyrighted recordings are not automatically training data: use public-domain, permissively licensed, or user-owned assets with explicit permissions.

## Detailed guide standard

Every eligible source should receive a guide comparable in depth to the freeCodeCamp guide format:
1. Executive summary and detailed explanation.
2. Chapter/section map with timestamps or repository paths/line references.
3. Learning objectives and prerequisites.
4. Key concepts and terminology.
5. Architecture and code walkthroughs.
6. Reproducible worked examples.
7. Common mistakes, debugging, security and performance notes.
8. At least three original exercises and one capstone.
9. Knowledge checks with answer key.
10. Division mapping, citations, upstream version and license evidence.
11. Independent practice evidence, reviewer status and last-verified date.

If the source is metadata-only, Buddy may create a metadata record and a pending task, but must not invent a detailed summary.

## Machine-learning strategy stack

The system uses complementary strategies rather than assuming one training method can teach every skill:
- Retrieval-augmented learning for current, cited facts and source navigation.
- Supervised instruction tuning for carefully curated, licensed examples.
- Self-supervised learning for permitted raw corpora.
- Contrastive learning for text/image/audio/video/code alignment.
- LoRA/adapters for affordable domain specialization.
- Knowledge distillation to transfer validated capabilities from teacher models.
- Preference optimization for consented, high-quality preference pairs.
- Sandboxed reinforcement learning for tool use and agent behavior.
- Continual learning with replay, versioning, forgetting tests and rollback.
- Curriculum learning, prerequisite graphs and spaced repetition.
- Program synthesis and execution-based learning from independent implementations.
- Ensembles and model routing to select specialist models by measured performance.

No single strategy is assumed to be appropriate for all divisions. Each training run must state its hypothesis, dataset provenance, license, baseline, compute budget, evaluation split, expected gain, safety checks, and rollback plan.

## Weekly build loop

The weekly scheduled workflow should:
1. Discover new/changed repositories and Hugging Face artifacts.
2. Refresh versions and license metadata.
3. Deduplicate and run security/PII checks.
4. Queue rights review and source summarization.
5. Generate division-specific bootcamp lessons and projects.
6. Schedule five lessons per day per division as a target, subject to source eligibility and capacity.
7. Assess Buddy on eligible material, including weekly source/transcript coverage.
8. Build training candidates only from approved data.
9. Run regression, transfer, safety, latency and cost evaluations.
10. Publish a weekly report and next-week curriculum.

A successful discovery workflow is not proof that the model trained. A successful guide workflow is not proof of mastery. Reports must separate discovered, rights-cleared, summarized, studied, assessed, trained, and mastered counts.

## Operational limits

The scheduled workflow can discover and prepare work, but actual GPU training requires a configured runner/provider, secrets, quotas and a budget. It must fail closed when compute is unavailable rather than silently consuming paid resources. The repository can define and validate the training pipeline before an accelerator is connected.


## Hugging Face subject coverage and training paths

The current curriculum starts with 189 subject labels spanning language, vision, audio, video, multimodal systems, code, science, health, education, law, finance, business, robotics, geospatial data, accessibility, fitness and public services. This is a seed taxonomy, not a claim that the Hub itself has exactly 189 subjects. The weekly discovery process must refresh task/tag taxonomies from the Hub, record newly seen tags, preserve unknown tags for review, and report coverage separately for models, datasets and Spaces. Hugging Face supports searching these three artifact types through its Hub APIs; task tags and dataset tags are separate taxonomies. The system must not mistake a successful search for exhaustive enumeration.

For every division, the bootcamp builder should generate a subject map, prerequisites, sequence of lessons, source-by-source detailed guides, hands-on exercises, a capstone, weekly knowledge checks, transfer tasks and evidence-based mastery state. Each guide must use the same depth standard as the freeCodeCamp study-guide pipeline. The five-lessons-per-day target is a scheduling target; source eligibility, review capacity and compute budgets control actual execution.

## O*NET and Department of Labor occupational curriculum

O*NET is the occupational backbone. The official database publishes task statements and task ratings, and the Web Services API exposes all occupation records and paginated task details. The current API reference documents 1,016 occupation records and the detailed task endpoint; the downloadable database also publishes a versioned task-statement table. Keep source version, task IDs, occupation codes, task type, importance when available and attribution with every generated guide.

Use `tools/fetch_onet_task_curricula.py` with an `ONET_API_KEY` to retrieve occupation/task records from the official Web Services API. A free developer registration is required. Alternatively, provide the official Task Statements export to `tools/build_onet_task_curricula.py`. Generated paths group tasks by occupation and create a task-by-task practice plan.

For every task, Buddy should:
1. Explain the task and the occupation context.
2. Identify knowledge, skills, tools, credentials, safety requirements and prerequisites.
3. Build a detailed study guide and realistic practice simulation.
4. Create a verified service/product pathway where there is a real buyer and a lawful scope.
5. Prepare a sales discovery plan, truthful proposal outline, price/cost model and delivery checklist.
6. Separate employability practice from permission to perform regulated or licensed work.

Buddy can act as a sales-development representative for DreamCo's verified offers across relevant tasks: research buyers, qualify needs, draft outreach, prepare capability statements, maintain a CRM and propose scoped work. It must not claim that DreamCo or a user is qualified for every occupation, impersonate a licensed professional, spam prospects, or contact buyers/submit bids without human approval.

## Government, procurement and grant business school

Government work is a dedicated bootcamp with federal, state, county and municipal tracks:
- SAM.gov: federal opportunity research, entity registration, UEI, active registration, solicitation alerts and award research.
- SBA: NAICS selection, size standards, certification eligibility, market research, subcontracting, capability statements and procurement counseling.
- Wisconsin: eSupplier registration and state bid/RFP notifications.
- Local governments: city/county procurement pages, purchasing thresholds, vendor registration, public bid calendars, RFP/RFQ/RFB formats, council approvals and open-records research.
- DOL and workforce: WIOA, apprenticeship, employment services, VETS programs, HVRP, JVSG and Stand Down opportunities.
- Grants.gov and USAspending: assistance notices, applicant eligibility, prior awards, funding history and performance research.

The government-contract learning path is: buyer research; entity/UEI setup; NAICS and size-standard review; insurance and licensing; capability statement; past-performance evidence or qualified partners; solicitation compliance matrix; bid/no-bid decision; labor/material/overhead/risk pricing; proposal; human approval; delivery; reporting; invoice; closeout and past-performance capture.

Important reality check: government contracts and grants are competitive, not easy money. SBA warns that first-contract pursuit can be expensive and can take a long time to return the investment. SAM.gov registration is free; an active registration and UEI are required for federal prime awardees. Buddy must never promise that a city will award a contract or that a grant will be approved.

## DOL, homeless services, veterans and public-benefit navigation

The community-enterprise track should help DreamCo and qualified partners design employment pathways, training, apprenticeship, supportive services, housing referrals, veteran transition services and accessible digital services. DOL's VETS programs include HVRP, JVSG and Stand Down, but each has different eligible applicants. JVSG is limited to state agencies; HVRP has a broader eligible-applicant list that includes certain for-profit and nonprofit entities, local workforce boards and public institutions. Buddy must check each funding announcement's current eligibility rather than generalize across programs.

For people receiving public benefits, Buddy is a navigator and referral assistant, not a benefits adjudicator. It must explain that work income can affect benefits differently by program and jurisdiction, encourage users to contact authorized benefits counselors/caseworkers before changes, and avoid promises about eligibility, exemptions or benefit amounts. Collect the minimum sensitive information, with informed consent, and keep service access free where a public/partner-funded model permits. A community program should use qualified nonprofit, workforce-board, veteran-service and municipal partners; DreamCo should clearly disclose whether it is a contractor, subcontractor, vendor or program operator.

## Entrepreneurial tracks

The Bootcamp includes:
- Small-business formation, market research, pricing, accounting, cash flow, customer discovery and operations.
- Sales, prospecting, ethical outreach, CRM, discovery, proposal writing, negotiation and account management.
- Remote work, portfolio building, interviews, freelancing, client delivery and contractor compliance.
- Autonomous revenue systems: e-commerce, affiliate programs, digital products, lead generation and subscription services, with unit economics and fraud checks.
- Personal finance and long-term wealth-building: budgeting, debt management, saving, risk, diversified investing concepts and scam detection. No get-rich-quick promises, guaranteed returns or financial-product sales without required authorization.
- Strength training, muscle-building education and sports science: anatomy, progressive overload, recovery, nutrition fundamentals, injury prevention and referral boundaries. No medical diagnosis or unsafe coaching claims.
- Real estate and property services, including maintenance, facility operations, public records, fair housing and properly licensed activity.
- Government contracting, grants, public administration, civic literacy and community workforce services.

Autonomous income means automating repeatable business processes with clear human oversight, not guaranteed passive income. Every business experiment must report gross revenue, expenses, fees, taxes/reserves, refunds, labor, customer acquisition cost and net profit.

## Weekly build and business-development report

Each weekly run should add:
- Newly discovered Hugging Face task/tag taxonomy and coverage by artifact type.
- Subject-by-division curricula and source-guide completion counts.
- O*NET occupation/task inventory version, task-to-guide coverage and missing occupations.
- DOL program and government procurement opportunity watchlist with deadlines and eligibility checks.
- Lead pipeline, buyer qualification, bid/no-bid recommendations and human-approved next actions.
- Remote-work, freelance and business experiments with costs and measured outcomes.
- Community impact measures: training completions, referrals, job placements verified by partners, veteran/homeless services delivered, and privacy/compliance incidents.

No automated contact, application, bid, benefits action, financial transaction or grant submission is permitted without explicit human authorization.
