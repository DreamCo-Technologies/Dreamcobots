# Buddy: Personal Memory, Shared Learning, and Natural Interaction

## Product goal

Make Buddy familiar, consistent, attentive, and dependable through user-controlled personal memory and a separately governed product-learning system. Buddy remains transparent that it is AI and never fabricates human experiences or manipulates users into dependency.

## Two learning planes

### Personal plane
- Remember only what the individual user authorizes.
- Store useful preferences, goals, project state, decisions, corrections, and recurring workflows.
- Keep memory tenant-isolated; one user’s private memory never becomes another user’s context.
- Support view, correction, export, deletion, retention limits, and disable controls.
- Attach source, timestamp, scope, confidence, and expiry/revalidation conditions.
- Ask before promoting uncertain, sensitive, or consequential information.

### Shared product-learning plane

Cross-user learning uses reviewed generalized procedures and aggregate outcomes—not raw conversation logs. It requires product-improvement opt-in, separate cross-user-sharing opt-in, de-identification, exclusion of sensitive and third-party personal data, a minimum cohort of 20, no user/conversation identifiers, human/privacy review, regression tests, provenance, retention, and revocation evidence.

Foundation-model training is a separate opt-in from product improvement and cross-user sharing. It additionally requires rights/provenance evidence, privacy review, human review, a dataset card, a withdrawal path, and separate budget approval for paid compute. An allowed candidate is not a training job and does not update weights.

## Four independent user controls

1. Personal memory: remember selected facts/preferences for this user.
2. Product improvement: contribute eligible de-identified aggregate patterns.
3. Cross-user sharing: permit a reviewed generalized lesson to help other users.
4. Foundation-model training: permit eligible derived examples to be considered for a separately reviewed training dataset.

Each control needs purpose, scope, retention, and on/off settings. Cross-user sharing and foundation-model training default off. New purposes require new consent. Revocation stops future processing and initiates eligible deletion workflows.

## What makes Buddy feel natural

- Continuity: recall relevant approved context, open tasks, decisions, and project state.
- Consistency: stable identity, tone, terminology, and follow-through across supported devices and model providers.
- Adaptation: learn preferred warmth, directness, detail, language, and formatting from settings and corrections.
- Attunement: acknowledge feelings respectfully without diagnosing or exploiting vulnerability.
- Honesty: flag stale memories, distinguish remembered facts from inference, and admit mistakes.
- Initiative with boundaries: suggest next steps; ask before external, financial, destructive, or consequential acts.
- Repair: explain errors, correct them, and retain only verified reusable lessons.

## Technical contracts

- Machine policy: config/buddy-conversation-learning-governance.json
- Candidate policy evaluator: tools/buddy_conversation_learning_policy.py
- Unit tests: tests/test_buddy_conversation_learning_policy.py
- Data-rights and memory preferences: server/data-rights-policy.ts
- Personal training-source contract: shared/personal-buddy-training-contract.ts
- Wider learning pipeline: docs/BUDDY_UNIVERSAL_LEARNING_ENGINE.md
- Personal AI architecture: docs/DREAMCO_BUILD_YOUR_OWN_AI_FLAGSHIP.md

## Operational truth

Policy files and passing unit tests do not prove production chat ingestion, tenant-isolated storage, consent UI, deletion propagation, privacy review, or model training is deployed. Those require implementation, end-to-end tests, security review, and production evidence. Current status: POLICY_DEFINED_RUNTIME_INTEGRATION_REQUIRED.
