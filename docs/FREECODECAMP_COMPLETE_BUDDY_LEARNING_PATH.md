# Buddy Bootcamp: complete freeCodeCamp learning path and video study program

## Mission

Study the complete freeCodeCamp learning ecosystem—not only a handful of popular playlists. This includes the current interactive curriculum, versioned legacy curriculum, official YouTube channel, technical publication, language certifications, community/open-source learning and linked partner resources. Refresh the official sources regularly because videos, courses and certification structures change.

## What the current official source says

The freeCodeCamp repository describes seven core full-stack certification tracks (Responsive Web Design, JavaScript, Front End Development Libraries, Python, Relational Databases, Back End Development and APIs, and Certified Full Stack Developer), plus language certifications and Foundational C# with Microsoft. Its contribution documentation describes the v9 curriculum structure as chapters, modules, blocks and challenges, with theory lessons, workshops, labs, review pages and quizzes. The curriculum GraphQL endpoint currently advertises 37 superblocks, 38 chapters, 217 modules, 779 unique blocks and 14,038 challenges. Treat these as a dated source snapshot, not hard-coded invariants.

## The full video coverage requirement

The official YouTube channel is a separate, continuously changing library. The public channel page currently lists roughly 2.3K videos. DreamCo's checked-in catalog is a legacy 1,740-video snapshot and explicitly marks itself incomplete because it has no persisted upstream playlist count. A prior CI artifact reportedly found 1,741 entries, but the refreshed full inventory is not committed. Therefore, do not tell Buddy that all videos are cataloged until the weekly refresh verifies playlist count equals every unique parsed video ID.

Every discovered public video must have a durable queue record, category tags, source URL, title, duration/date when available, and a guide status. Metadata-only rows are not summaries.

## Detailed video summary standard

For every video with a transcript or equivalent source that is explicitly authorized for study, derivative summary creation and evaluation, Buddy must create a detailed independent study guide. Use `config/freecodecamp-detailed-video-study-guide.schema.json` as the required contract. Each guide must include:

1. Executive overview, scope, intended learner and a detailed original explanation.
2. Timestamped chapter-by-chapter notes, including demonstrations and their purpose.
3. Learning objectives and prerequisite skills.
4. Key concepts with plain-language and technical explanations, use cases and limitations.
5. Glossary with definitions and examples.
6. Code patterns, commands, tools, APIs and configuration patterns actually demonstrated.
7. Worked examples with reasoning and verification.
8. At least three original exercises at graduated difficulty, with acceptance criteria and hints.
9. Original projects, test plans and extension ideas.
10. Common mistakes, symptom/cause/fix/prevention guidance and a debugging playbook.
11. At least five knowledge checks with answer explanations and grading rubrics.
12. Applications to the appropriate DreamCo divisions, without inventing mappings.
13. Citations, provenance, source hash, authoring model, human review and quality checks.

Do not fabricate timestamps, instructor claims, code samples or chapter topics from a title or metadata. If a transcript is unavailable or permission is missing, leave the guide pending and provide only the factual metadata and official link.

## Rights and provenance gate

A publicly viewable YouTube video does not itself grant permission to scrape captions, download transcripts, store derivative summaries, evaluate Buddy on the transcript, train model weights or redistribute content. These are separate permissions. The transcript manifest must include source match, transcript SHA-256, evidence reference, study permission, derivative-summary permission and evaluation permission. Model training requires a separate training permission and evidence reference. Unknown rights are blocked. No automatic caption scraping or video/audio download.

The freeCodeCamp repository states that its software is BSD-3-Clause while learning resources in the curriculum directory are copyrighted. Link to the official course and cite it. Write original explanations, examples, tests and projects; do not copy curriculum lesson text wholesale or claim the codebase license covers all learning content.

## Buddy's complete learning sequence

1. Computer science foundations: command line, Git, problem solving, algorithms, data structures, debugging and testing.
2. Responsive Web Design v9: semantic HTML, forms, CSS, accessibility, responsive layouts, Flexbox and Grid.
3. JavaScript v9: language fundamentals, functions, arrays/objects, DOM, algorithms, data structures and testing.
4. Front End Development Libraries v9: React, components, state, routing, UI architecture and testing.
5. Python v9: syntax, control flow, data structures, functions, OOP and testing.
6. Relational Databases v9: relational design, SQL, constraints, joins, transactions and integrity.
7. Back End Development and APIs v9: HTTP, REST, server logic, validation, authentication concepts, database integration and API testing.
8. Full Stack Developer v9 capstone: integrate, secure, deploy, observe and maintain a complete application.
9. Specialist electives: data science, ML/deep learning, generative AI, agents/MCP, cybersecurity, Linux/networking, cloud/DevOps, C/C++/systems, Java/JVM, mobile, games, math/statistics, design/UX and career/interview preparation.
10. Teach-back and transfer: Buddy must explain, build, debug, review and solve unseen tasks—not merely repeat notes.

Parallel language tracks: A2/B1 English for Developers, A1 Professional Spanish, A1 Professional Chinese and Foundational C# with Microsoft. Preserve current and legacy course versions separately.

## Daily and weekly operation

The existing DreamCo target remains five original lesson packages per each of the 55 domain divisions per day (275 planned slots). This is a production target, not a claim that 275 completed lessons exist. Each package should combine a source-aligned concept, original explanation, practical exercise, tests, and evidence.

Every week, test Buddy on every transcript for which weekly evaluation permission is recorded. Capture Buddy model/version, test suite, run ID, timestamp, rights evidence reference, result hash, score and failures. A pass requires valid evidence; the audit must not pretend to execute Buddy. Add spaced repetition and retest failed concepts.

## Graduation rubric

A video guide is complete only after source/provenance validation, detailed summary review and practical checks. A capability is mastered only after repeated target benchmark passes, an independent unseen holdout, regression checks and no unresolved safety/rights failure. Internal DreamCo mastery is not an official freeCodeCamp certification.

## Operational commands

```bash
python tools/sync_freecodecamp_catalog.py
python tools/sync_freecodecamp_catalog.py --check
python tools/build_freecodecamp_division_queues.py --check
python tools/build_freecodecamp_transcript_intake.py --out-dir artifacts/freecodecamp-transcripts
python tools/build_freecodecamp_study_guides.py --out-dir artifacts/freecodecamp-study-guides
python -m unittest discover -s tests -p 'test_freecodecamp_study_guides.py' -v
```

The guide pipeline produces one queue row per catalog video. It will not invent summaries for videos with missing transcripts or missing derivative-summary permission.

## Division-wide course scheduler integration

The eight-track registry now exposes the existing Tolkien, tokenizer, CPU-first LLM, O*NET, Hugging Face task-family, Hugging Face Learn course, freeCodeCamp curriculum and freeCodeCamp video paths through `buddy.learning.course_track_registry`. Every video ID in the checked-in catalog is available in the shared queue for each of the 55 canonical divisions and 65 MasterBot lanes. The legacy snapshot currently contains 1,740 metadata records; the count is derived from the catalog and changes when the verified refresh PR is merged.

**Important completeness boundary:** the checked-in 1,740-video catalog explicitly reports `inventory.complete=false` and `inventory_status=partial`. It is not the complete freeCodeCamp channel archive. The 14,038 challenge / 217 module / 779 unique block curriculum figures are a dated source snapshot, not proof that every current challenge's text, tests, answer keys or prerequisites have been ingested. A verified upstream playlist count and a versioned official curriculum ID inventory are required before marking full coverage complete. The new scheduled refresh workflow enumerates the uploads playlist with pinned yt-dlp, checks count/unique-ID equality and opens a review PR; it never pushes directly to main.

Every queued video remains metadata-only until item-level source rights and transcript/equivalent content are reviewed. The scheduler does not download transcripts, mark lessons studied, or award mastery from a title or description.

## Certification and curriculum-primitive coverage

The course scheduler now includes all seven core current certifications and all five additional official certifications in the roadmap, including the language and C# specialist paths. It also exposes all seven curriculum primitives: theory lessons, workshops, labs, review pages, quizzes, required projects and exams. Legacy curricula are preserved in a separate versioned inventory task and are never silently substituted for current v9 requirements. The scheduler retains the ten learning phases and all 22 video subject tracks, plus every video ID in the current catalog.
