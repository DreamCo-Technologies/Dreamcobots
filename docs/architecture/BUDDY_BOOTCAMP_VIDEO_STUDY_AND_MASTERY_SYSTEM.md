# Buddy Bootcamp: complete video study-guide system

## Purpose

Build a DreamCo-authored Bootcamp that turns an authorized learning-resource inventory into detailed, teachable study guides, subject categories, division-specific learning paths, practical labs, assessments, and governed training examples. The Bootcamp's lessons, explanations, examples, exercises, projects, and assessment rubrics must be independently authored for DreamCo rather than copied or lightly paraphrased from source material.

## Current verified baseline

- The repository's checked-in video catalog contains 1,740 metadata records.
- That catalog explicitly declares its inventory status as `partial`.
- Metadata records are not completed summaries, transcripts, or evidence of learning.
- The existing catalog marks entries as not studied and rights review required.
- A separate learning-path document also says its video inventory is a snapshot and requires a refreshed completeness check.
- Consequently, the honest starting status is **partial metadata inventory; detailed study guides not yet verified complete**. Do not report all videos summarized, all sources ingested, or Buddy mastered until evidence gates pass.

## Completion model: every video gets a durable record

Each unique video/resource must have a record keyed by stable source ID and canonical URL. Required fields:

- source identity and private provenance reference; title, URL, publication date and duration when available
- inventory discovery date, enumerator version, content hash where lawful, and duplicate/alias relationships
- primary category, secondary categories, confidence score, prerequisite skills, learning outcomes, and division routes
- transcript/source-material availability and authorization state
- study-guide status, reviewer status, quality score, assessment status, and links to generated artifacts
- explicit blockers and next action when material is unavailable, restricted, ambiguous, or low quality

Permitted statuses are separate and must not be conflated:
`discovered` → `metadata_verified` → `source_material_pending` → `authorized_for_study` → `studying` → `guide_drafted` → `guide_quality_checked` → `human_reviewed` → `assessment_passed` → `division_adopted`.
A record may be blocked or excluded at any stage, with a reason. Do not mark a source mastered merely because a summary exists.

## Detailed study-guide standard

For every item with authorized source material, produce an original study guide with:

1. **Executive overview:** what the lesson teaches, who it is for, scope, expected effort, and practical value.
2. **Learning objectives:** observable outcomes using action verbs, prerequisites, and mastery criteria.
3. **Structured lesson notes:** topic-by-topic explanation in the source's actual sequence. Include timestamps only when verified from the source.
4. **Deep concept explanations:** plain-language explanation, precise technical definition, why it matters, how it works, trade-offs, assumptions, and limitations.
5. **Glossary:** every important technical term, acronym, API, command, data structure, model concept, and domain phrase; definition, context, example, related terms, and common confusion.
6. **Worked examples:** original examples that teach the underlying concept, with steps, expected output, tests, and explanation. Do not invent that an example appeared in the source.
7. **Code and configuration patterns:** only when source material supports them; explain inputs, outputs, dependencies, security implications, failure modes, and validation.
8. **Architecture and mental models:** diagrams or text descriptions of components, data flow, interfaces, and decision points where useful.
9. **Common mistakes and debugging:** symptom → likely cause → diagnosis → safe fix → regression prevention.
10. **Hands-on labs:** beginner, intermediate, and advanced tasks; starter state, instructions, constraints, expected artifacts, automated checks, and cleanup.
11. **Original projects:** at least one applied project where appropriate, with requirements, milestones, acceptance criteria, test plan, and extension ideas.
12. **Knowledge checks:** at least five questions with answer explanations; include recall, comprehension, application, and troubleshooting.
13. **Practical assessment:** rubric with measurable criteria, required score, allowed retries, and evidence artifacts.
14. **Division applications:** exact relevant divisions, how each would use the skill, prerequisite dependencies, and where the lesson is shared foundational knowledge.
15. **Safety, privacy, and responsible-use notes:** data handling, credential boundaries, licensing, security, and human approval where applicable.
16. **Provenance and quality record:** source reference, material authorization, source hash where appropriate, guide version, generation method, citations, reviewer, test results, and unresolved uncertainty.

A title or description alone may support metadata and tentative categorization; it cannot support a detailed content summary. If no authorized transcript, notes, or equivalent material exists, keep the study guide pending and do not fabricate chapters, timestamps, code, or instructor claims.

## Category structure

Use a multi-label taxonomy with one primary category, optional secondary categories, prerequisites, and capability tags. Initial top-level categories:

1. Computer science, algorithms, data structures, and programming foundations
2. Programming languages and software engineering
3. Web, frontend, backend, APIs, and mobile engineering
4. Databases, SQL, data engineering, analytics, and visualization
5. Mathematics, statistics, and scientific computing
6. AI, machine learning, deep learning, and model evaluation
7. Language models, tokenization, tokenizer training, pretraining, fine-tuning, and inference
8. Agentic AI, tool use, orchestration, and workflow automation
9. Cloud computing, networking, Linux, containers, and infrastructure
10. DevOps, CI/CD, testing, reliability, and observability
11. Cybersecurity, privacy, identity, and defensive operations
12. Robotics, embedded systems, computer vision, audio, and multimodal systems
13. Product design, UX, accessibility, and creative technology
14. Business, entrepreneurship, finance, operations, marketing, and sales
15. Research methods, technical communication, and teaching

Categories may be expanded when evidence shows a meaningful distinct subject. Cloud computing lessons are grouped together as a coherent Bootcamp track, with subtracks such as cloud foundations, architecture, networking, identity, storage, compute, containers, deployment, reliability, cost, and security.

## Division routing

- Every division receives shared foundations where relevant and a subject-specific track aligned to its actual responsibilities.
- A lesson can serve multiple divisions; do not force exactly one division when skills are genuinely cross-cutting.
- Each route records why it applies, required prior skills, expected practical capability, and evidence of completion.
- The canonical division registry is the source of truth. Do not invent or hard-code a division count in generators.
- Division-specific model training consumes only approved, relevant, quality-scored examples. Reading a lesson or glossary does not itself update model weights.

## Token and tokenizer curriculum

Create a dedicated language-data and tokenization pathway, with division-specific domain vocabularies:

- text normalization, Unicode, byte encodings, whitespace, punctuation, and multilingual text
- tokenization goals and trade-offs; character, word, subword, byte-level, and special-token approaches
- vocabulary construction, corpus sampling, frequency analysis, deduplication, contamination checks, and data quality
- BPE, WordPiece, Unigram, and byte-level BPE concepts and implementation labs
- training, saving, versioning, loading, and testing a tokenizer
- token fertility, sequence length, unknown-token behavior, reversibility, normalization consistency, and multilingual/domain coverage
- domain glossary extraction and review for each division; acronyms, synonyms, abbreviations, product terms, units, and disambiguation
- tokenizer/model compatibility, embedding resizing, checkpoint compatibility, migration, and regression testing
- privacy, licensing, PII removal, sensitive-term handling, and corpus governance

Each division's glossary is a reviewed domain asset. Do not promise that a tokenizer "knows every business term"; measure coverage against versioned, reviewed glossaries and test sets. A tokenizer segments text; semantic knowledge comes from model training, retrieval, and validated domain resources.

## Learning and mastery: accelerated, evidence-based schedule

A one-week target can be used for an intensive first learning sprint, but cannot honestly guarantee mastery of roughly 1,700+ videos. The number of videos is not the same as the amount of learning: duration, difficulty, prerequisites, practice, and assessment all matter.

Use a rolling, parallel plan:

- **Day 0 / setup:** reconcile inventory, validate rights, deduplicate, assign categories and division routes, calculate estimated learning hours, and identify missing transcripts.
- **Days 1–2 / foundations:** study shared prerequisites and high-priority core lessons; create and quality-check guides; run baseline diagnostics.
- **Days 3–4 / specialist tracks:** study division-specific content and complete guided labs; build glossaries and tokenization test corpora.
- **Days 5–6 / application:** complete projects, debugging drills, and cross-division scenarios; generate original practice examples from verified work where authorized.
- **Day 7 / assessment:** run independent tests, spaced recall, practical demonstrations, and remediation. Report mastered, proficient, in-progress, blocked, and not-started separately.

The sprint prioritizes a useful, assessed core capability in a week; the complete catalog remains an ongoing program. Parallel workers may draft independent guides, but every output must pass validation and bounded review before adoption.

## Mastery criteria

A lesson is mastered only when Buddy can:
- explain the concepts accurately in plain language and technical language
- answer held-out questions with a defined passing score
- complete a practical task in a sandbox with tests passing
- diagnose a deliberately introduced failure and repair it safely
- transfer the skill to a new example rather than repeat memorized text
- cite its approved learning evidence and state uncertainty or limitations

Use spaced repetition and periodic re-assessment. Store per-skill mastery, not a single misleading "mastered all Bootcamp" flag.

## Rights, provenance, and ownership

DreamCo owns the original curriculum materials it creates, subject to applicable law and contributor agreements. Public availability of a video does not automatically grant rights to download, retain transcripts, create derivative works, or train model weights. Keep source identity, license/permission decisions, attribution obligations, and review evidence in internal provenance records. Customer-facing lessons can be DreamCo-branded, but required attribution must not be removed and third-party expression must not be presented as wholly original. When rights are unclear, use metadata and links only, or obtain permission.

## Required automation and tests

Implement and test:
- complete inventory refresh with count/unique-ID reconciliation and change report
- deterministic multi-label category assignment with confidence and manual-review queue
- division route generation from the canonical registry
- transcript/source authorization gate before guide generation
- schema validation for every guide and provenance record
- duplicate detection, stale-source detection, and missing-material reports
- guide completeness and citation/provenance checks
- tokenizer corpus governance and tokenizer regression suite
- mastery assessment ledger with reproducible evidence
- CI summary that reports actual counts by status and never upgrades a status without evidence

## Completion reporting

The dashboard and PR descriptions must report separately:
- inventory discovered / unique / duplicates / missing / stale
- metadata verified / source material available / authorized for study
- guides drafted / quality checked / human reviewed / assessment passed
- category coverage and division-route coverage
- glossary and tokenizer corpus coverage by division
- Buddy skill mastery by assessment, practical lab, and transfer task
- blockers, required human decisions, and next actions

Do not report the system complete merely because code or a queue exists. Do not claim all videos are summarized, all divisions trained, or Buddy ready for production until the underlying evidence exists.
