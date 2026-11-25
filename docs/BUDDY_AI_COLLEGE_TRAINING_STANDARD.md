# DreamCo Buddy AI College: curriculum and authoring standard

## Mission and roles

ChatGPT is the teacher, curriculum designer, explainer, question setter and reviewer during authorized learning sessions. Buddy is the student. Buddy must demonstrate independent understanding through original work, practical labs, unseen transfer tasks, delayed retention checks and teach-back. The goal is a living, cross-disciplinary program that is benchmarked against strong open curricula, university open courseware, official vendor academies, professional standards and maintained technical repositories.

This is an internal learning program, not an accredited degree, professional license or third-party certification. We do not claim to equal or outperform every global training provider without independent, measured comparison.

## Coverage is larger than Hugging Face and freeCodeCamp

The canonical configuration is `config/buddy-university-curriculum.json`. It currently defines 45 knowledge domains and nine source families. Hugging Face and freeCodeCamp are major inputs, not the outer boundary of the program.

Source families include:
- Hugging Face models, datasets, Spaces, tasks, benchmarks, papers and Hub metadata.
- freeCodeCamp interactive certifications, current and legacy curriculum, chapters, modules, blocks, challenges, projects, official videos, tutorials, publications, community and open-source contribution pathways.
- O*NET occupations, task statements, skills, knowledge, abilities, work activities and tools/technology.
- Official language, framework, cloud, security, database, standards and vendor documentation.
- Maintained open-source repositories, examples, tests, issue histories, architecture and releases.
- Open academic research, papers, open textbooks, theses, replication packages and scholarly data.
- Government laws, regulations, procurement, grants, public budgets, open data and agency guidance.
- Professional standards, competency frameworks and certification objectives.
- Community practice, case studies and postmortems, clearly labeled as practitioner evidence rather than authoritative fact.

New subjects outside known taxonomies must be retained in an unclassified review queue, not discarded. The university map suggests routes to the 55 canonical DreamCo divisions; mappings remain suggestions until owner review. All divisions can start shared foundations and diagnostics in parallel. The coding mastery gate applies to advanced software-engineering promotion, not unrelated foundational study.

## Hugging Face coverage

Refresh model, dataset and Space tag taxonomies from the official Hub APIs where available. Search all three artifact types, paginate bounded inventories, merge live task tags with configured seeds and subjects discovered in cards, repositories and papers. Record:
- source ID, URL, artifact type and pinned revision
- tags/task categories and discovery query
- license, model/data terms and rights evidence
- dataset provenance, splits, features, privacy and bias
- model architecture, intended use, inputs/outputs, evaluation, hardware and limitations
- Space user flow, dependencies, code and reproducibility
- pagination completion, API errors, rate limits, deduplication and per-query limits

A live tag taxonomy is not an exhaustive list of every Hub artifact or every discipline. Report terms discovered, artifact types searched, pages/cursors completed, unique artifacts, failed queries and guide coverage separately. Public availability does not automatically authorize model-weight training.

## freeCodeCamp coverage

Use `config/freecodecamp-complete-learning-path.json` and its official-source refresh process. Cover current and legacy certifications, interactive curriculum, theory lessons, workshops, labs, review pages, quizzes, projects, official public videos, tutorials, articles, community, contribution paths and linked partner references. Keep current and legacy versions distinct.

Maintain a canonical record for every unique public official video ID. Reconcile discovered playlists/channel inventory against catalog IDs and report missing IDs and incomplete refreshes. A roadmap or metadata row is not a completed video guide. For every source with separately evidenced study, derivative-summary and evaluation permissions, create a detailed original guide. If the transcript or source permission is absent, leave the guide pending and do not infer lesson contents from the title.

The university builder routes freeCodeCamp specialist tracks and video subject categories to divisions. The existing freeCodeCamp runtime adapter remains the source-specific path into the evidence-driven scheduler; the generic DreamCo summary adapter handles approved original summary packages. Neither adapter claims a source was studied merely because it was queued.

## Occupation, job, hustle and venture curriculum

O*NET is the occupational backbone. Every imported occupation and task statement receives a source-versioned learning path and task-specific guide-authoring brief. Every task guide must explain:
1. The real task, customer problem, context, inputs, outputs and complete workflow.
2. Prerequisites, knowledge, skills, abilities, proficiency, credentials and safety.
3. Routine, specialist and high-end software categories and named tools verified from official product documentation, employer requirements and occupational evidence.
4. Open-source, local/offline and lower-cost alternatives, with verified pricing/licensing and last-checked dates.
5. Agent capabilities: research, planning, document handling, structured data, APIs, browser/computer use within approved scope, workflow automation, coding, analytics, CRM, customer communication, scheduling, procurement, quality checks and audit evidence.
6. Integrations, data schemas, tool permissions, secrets handling, human approval points and failure recovery.
7. Quality standards, acceptance tests, privacy, cybersecurity, accessibility, records, legal and regulatory boundaries.
8. Time, labor, materials, software, compute, insurance, overhead, acquisition costs, support and working-capital requirements.
9. Buyer segments, demand evidence, competitors, procurement channels, offer design, scope, pricing and unit economics.
10. Ethical sales discovery, qualification, CRM, truthful capability statements, proposals, negotiation preparation, delivery SOPs, customer support and closeout.
11. Beginner, intermediate and advanced exercises, sandbox simulation, portfolio capstone, answer key, independent assessment and citations.

Do not attach every software product to every occupation. Each task must select tools based on evidence and relevance, compare alternatives, and record actual integration availability. A written playbook is not proof of professional competence or permission to perform licensed work.

## Agent capability catalog

The shared catalog is a starting inventory, not a claim that every tool fits every task:
- Research and intelligence: official registries, public records, source verification, citation management, competitive intelligence, OCR, document extraction, knowledge graphs and RAG.
- Software and platform engineering: programming languages, IDEs, Git, GitHub, databases, API clients, testing, Docker, Kubernetes, Linux, CI/CD, cloud, infrastructure as code and observability.
- AI and data: PyTorch, TensorFlow, scikit-learn, Hugging Face, Jupyter, MLflow, data warehouses, ETL/ELT, dbt, Spark, BI, vector databases, model serving, evaluation and fine-tuning.
- Office and business operations: spreadsheets, documents, presentations, email, calendars, forms, e-signature, accounting, ERP, inventory, procurement and contract lifecycle.
- Sales and customer success: CRM, lead enrichment, sales engagement, CPQ, proposal automation, customer support, ticketing, knowledge bases and call analytics.
- Marketing and commerce: CMS, SEO, analytics, tag management, email marketing, social publishing, ad platforms, storefronts, product feeds, affiliate tracking, payments and subscriptions.
- Design and media: Figma, Canva, Adobe Creative Cloud, video/audio editing, CAD/BIM, 3D, prototyping, accessibility and digital asset management.
- Automation and integration: workflow orchestration, webhooks, OAuth, MCP servers, RPA, iPaaS, queues, schedulers, secrets vaults and event-driven systems.
- Security and governance: IAM, SSO, least privilege, vulnerability scanning, SAST/DAST, SIEM, DLP, audit logs, privacy impact, backup and recovery.
- Field and physical operations: scheduling, dispatch, routing, work orders, maintenance, safety, IoT/SCADA awareness and quality inspection.

For every named product, verify official documentation, current availability, license, price, API/integration, data residency and security posture. Never invent integrations or pricing.

## Teaching and progression

Each course is structured as a stackable sequence:
- 100 Foundation: vocabulary, literacy, principles and guided practice.
- 200 Practitioner: routine independent work with standard tools and tested projects.
- 300 Advanced: complex workflows, exceptions, integrations, architecture and professional standards.
- 400 Specialist and Research: independent design, original research, advanced capstone, review and teach-back.

The teacher-student loop is diagnostic, prerequisite check, original explanation, worked example, guided practice, independent practice, retrieval quiz, teach-back, unseen transfer, capstone, independent scoring, remediation, spaced review and versioned progress record.

The five-lessons-per-day target is five eligible, verified original lesson packages per division—not five metadata records or placeholders. Weekly review assesses each source with evaluation permission at least once, then retests gaps. The schedule is capacity-aware and should not reward superficial completion.

## Summary ownership and user data

The user is the designated owner of original DreamCo-authored summaries, explanations, concept maps, exercises, assessments, study paths and curriculum organization produced for this project, subject to applicable law, actual authorship, contributor agreements and upstream license terms. Keep the author, creation date, revision, provenance and ownership record with every package.

This ownership does not transfer rights in third-party facts, source code, datasets, documentation, videos, transcripts, music, images, model weights or other upstream material. Preserve attribution and license restrictions. Do not reproduce source works wholesale.

User-provided data remains user-owned. Keep it in a separate private registry, never publish it in the public curriculum, and require separate explicit consent for study, summary creation, evaluation, retention and model-weight training. An empty manifest means no personal files have been authorized yet. Do not silently ingest personal data from connected services or private repositories.

## Progress and model-training controls

Keep these states distinct: discovered, rights-reviewed, summary-authored, summary-approved, assigned, studied, practiced, assessed, trained and mastered. Store source revision, asset ID, division, lesson, attempt, model version, test ID, evidence hash, score, reviewer and next action. Mastery requires independent assessment, practical work, unseen transfer and delayed retention; reading alone is not mastery.

Retrieval and study permission is separate from model-weight training permission. Fine-tuning, distillation or other weight updates require asset-level training rights, a manifest, data minimization and privacy checks, baseline, validation and holdout sets, compute/budget approval, versioned checkpoint, regression tests and rollback. Do not claim that Buddy's weights changed until a training backend run and evaluation are recorded.

## Weekly coverage report

Publish counts by source family, artifact type, subject, division, task and rights state. Report discovered resources, completed guides, unclassified topics, source revisions, training eligibility, study attempts, benchmark passes, failures, remediation, cost, latency and compute. The report must show missing subjects and source gaps, not hide them. The next curriculum version is a draft until independent validation and governance review pass.
