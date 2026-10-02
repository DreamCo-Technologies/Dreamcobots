# DreamCo delivery plan and acceptance contract

This plan translates the available notes into release work. It is not a declaration that every conversation has been fully reviewed or that all planned bots operate in production.

## The three connected experiences

| Experience | Primary job | Required behavior | Completion evidence |
| --- | --- | --- | --- |
| Public website | Explain DreamCo and let visitors explore working examples | Linked capabilities, bot portfolios, public source directory, beginner examples, honest setup and readiness, accessible phone navigation | Link crawl, keyboard/mobile browser tests, no secrets, successful Pages deployment |
| Personal dashboard | Help a person manage their work | Saved goals and drafts, recent tasks, owned bot preferences, learning progress, export and deletion, clearly sourced results | Persistence and recovery tests; authenticated account isolation before private server data is enabled |
| Owner command center | Operate and improve the whole system | Repository/change inventory, 49-chat requirement queue, bot identities, integration health, approvals, tests, logs and release controls | Real authorized backend actions, audit trails, denied-access tests, exact-revision deployment checks |

All three use common repository, bot, capability and requirement identifiers. A different screen does not grant authority. The current Pages controls use public metadata and local browser plans; GitHub writes open GitHub's signed-in editor. Private links can be imported into browser-local storage. Private multi-user administration remains a backend implementation requirement.

## Source comparison and chat completion

The public source of truth is `config/conversation-index.json`, displayed at `project-conversations.html`. It records all 49 previously visible conversations, including one unreadable source. It contains 1,241 retrieved user messages summarized as 4,328 candidate segments. Those segments are automatically extracted review candidates, not unique accepted requirements. Source-family matches are not evidence that the matching code implements the original intent.

Raw chats and attachments remain outside the public repository. One conversation is unreadable, four returned blocks were truncated, and four attachment references have no retrieved contents. Complete enumeration of the project is not established. A complete export is required before claiming no detail is missing.

For every conversation:

1. Recover the complete messages and attachments; retain immutable originals and hashes privately.
2. Review each message in context. Split desired outcomes, constraints, corrections and approvals into stable requirement IDs. Resolve contradictions explicitly; preserve older instructions as superseded history.
3. Map each requirement to an existing implementation or an explicit gap. Record original intent, code path, owner, input/output, required connector and acceptance test.
4. Implement the smallest shared capability that satisfies the requirement; do not create a separate copy for every bot.
5. Run meaningful positive, negative and recovery tests. Preserve command, commit, inputs, output hashes and test artifacts.
6. Verify the deployed revision wherever the promise concerns live behavior. Code presence, generated plans and simulated execution cannot satisfy a live requirement.
7. Only when all requirements pass, move the conversation out of the open-work index while retaining its history and completion receipt. No conversations currently qualify. `tools/chat_implementation_audit.py` checks the evidence contract but never archives or deletes a chat automatically.

Every public conversation entry includes old/new/missing labels, candidate source references and a staged plan by feature family. A reviewer must still complete the private semantic comparison.

## Old bots: preserve, reconcile, implement, prove

The canonical registry has 1,051 profiles. Fifty additional growth profiles now have separate catalog entries and shared sandbox task routes. Their original descriptions, capability lists and source files remain preserved. The 262 historical source records include these 50 and the older 200 income-network notes plus 12 systems; these are overlapping provenance counts, not 262 additional live bots.

Create one behavior matrix per source bot: original capability, current handler, missing dependency, expected artifact, success criteria, failure cases, authorization requirements and verified state. Preserve original code and notes; use explicit aliases for renamed bots. A successful task-packet test proves routing and boundaries only. A document bot must produce a valid document, a code bot a buildable tested artifact, and a connector bot a verified sandbox response before capability completion is claimed.

Prioritize shared implementations: source reading, editable drafts, isolated execution, file/artifact validation, retrieval, connector authentication, queues, retries, logs and rollback. Pilot one bounded workflow per capability family before expanding to the fleet. Live payments, publishing and account actions require their configured permission gates.

## Model development: a measured path

The existing beginner router is a word matcher over written replies. The existing character model and learning procedures are small research components. The browser model lab now exercises pinned third-party model weights locally; it is not a newly trained DreamCo foundation model. A successful inference run proves model execution, not answer correctness. The first small-model coding trial showed repetitive output and is not accepted as coding competence.

1. Define held-out task sets across beginner coding, repository editing, reasoning/math, factual retrieval, long context, instruction following, multilingual use, image/audio tasks, tool use and safety. Track accuracy, completion rate, error severity, latency, memory and cost separately.
2. Establish licensed baseline models and pinned versions. Record exact prompts, generation settings and scoring rules. Keep test data out of training and retrieval context where it would invalidate the evaluation.
3. Add repository retrieval with file citations and secure tools. Test that Buddy reads actual files, produces reviewed patches, runs sandbox tests and reports failures accurately.
4. Curate consented, licensed training examples from successful reviewed tasks. Keep secrets, private chat content and third-party material out unless separately authorized for that use. Deduplicate and separate train/validation/test sets.
5. Fine-tune a small open model only after baselines and data rights are established. Record hardware, budget, checkpoints and reproducible evaluation artifacts. Free local compute depends on the owner's hardware; free hosting does not imply unlimited training or inference.
6. Promote versions only when held-out results improve without regressions in safety, privacy, reliability or latency. Retain rollback checkpoints and publish a model card.
7. Compare with frontier systems on the same named benchmarks and report uncertainty. Broad superiority or 'mastered all Hugging Face' is not an acceptance criterion that can be honestly certified from a catalog scan.

Official references: https://huggingface.co/docs/transformers.js/en/index and https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct . The local lab pins library and model revision and can export unscored test records.

## Connected repositories and new data

Six accessible public repositories have source-tree snapshots in the public directory. The other three accessible repositories remain private; their links can be imported locally without uploading names or contents. Each public repository can load its current GitHub tree, showing new files without pretending they are deployed applications. File links lead to source, signed-in editing and test/deployment runs. Public site links are shown only for the verified Pages repository.

ChatGPT plugins, CodeRabbit connections and Grok access in another application do not automatically become authenticated services inside Buddy. Configure each integration's actual runtime, permissions, credential storage and contract tests before showing it as operational. CodeRabbit connection scopes are documented at https://docs.coderabbit.ai/connections . No paid service is automatically enabled by this plan.

## Release order

1. Reconcile the newer main branch and preserve all original bot data.
2. Pass focused tests for new directories, conversation privacy, supplemental routing, source preservation and browser controls.
3. Regenerate canonical catalogs and indexes and verify no artifact drift.
4. Pass the repository's merge checks, review the exact remote tree, and use the single Pages publisher. Both documentation and the website must be present in its artifact.
5. Verify live navigation, source links, model loading, exports and mobile controls. Retain a release receipt tied to the deployed commit.
6. Continue the per-chat and per-capability backlog through the same evidence gates. Do not mark the entire product production-ready just because the static site deploys.

## Work that still needs external input or evidence

- Complete Dreamco conversation export and attachment contents.
- Verified runtime hosting and real authentication for private multi-user owner controls.
- Provider configurations and sandbox authorization for integrations whose code exists only as an adapter or plan.
- Held-out benchmark results, licensed training data and sufficient compute before model competition claims.
- Full capability-by-capability old-bot output testing and live deployment receipts.
