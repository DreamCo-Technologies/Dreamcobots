# Buddy Universal Learning and Mastery Loop

## Mission

Buddy should continuously improve from every eligible source it is authorized to study: permitted conversations and corrections, approved personal memory, user-selected files, repositories, issues, pull requests, CI results, connected apps, databases, APIs, public and licensed research, model cards, audio/video/image-derived material, task outcomes, benchmark results, and verified human feedback.

"Everything" means everything within the user's granted scope, legal rights, connector permissions, and the purpose-specific consent they selected. It does not mean unrestricted access to private accounts, other users' conversations, paywalled material, or third-party data.

## Five separate learning planes

1. **Personal memory:** selected facts and preferences for one user, isolated from every other tenant.
2. **Procedural knowledge:** verified reusable procedures from public, licensed, or owner-authorized sources, with provenance.
3. **Product improvement:** de-identified aggregate patterns under a separate opt-in.
4. **Cross-user lessons:** reviewed generalized procedures under a separate opt-in; no raw transcripts or private memory.
5. **Foundation-model training:** a distinct opt-in and dataset pipeline with rights evidence, privacy review, human review, dataset card, withdrawal path, and separately approved compute.

Reading, indexing, studying, answering from, or evaluating a source does not imply permission to train model weights on it.

## Universal learning cycle

Discover → authenticate owner → verify source scope and rights → classify sensitivity → check purpose-specific consent → minimize and transform → attach provenance/content hash → deduplicate/version → run the learning-policy gate → sandbox-test the candidate lesson → evaluate against regression benchmarks → obtain required human review → promote to the correct learning plane → record lineage and withdrawal path.

Every promoted lesson carries source ID, source version, owner/scope, timestamp, permitted purpose, rights evidence, content hash, transformation record, confidence, evaluation evidence, and expiration/revalidation rule.

## Learn from failures as well as successes

Capture safe, minimized error signatures, failed task classes, tool errors, benchmark regressions, root-cause hypotheses, fix commits, and regression tests. Never preserve secrets, credentials, raw private transcripts, or unneeded personal data as failure examples. A lesson is reusable only after it passes its relevant tests.

## Model weights versus knowledge

Most daily learning should improve retrieval, procedures, tool selection, routing, and evaluation—not mutate model weights. Weight training is a separate reproducible job with pinned base model, dataset manifest and split hashes, rights review, training configuration, compute budget, before/after benchmarks, private holdout, safety regression, and independent promotion approval. No automatic production weight changes.

## Daily and event-driven operation

Run bounded scheduled and event-driven learning cycles. Prioritize high-impact benchmark gaps, dependency-unblocked fixes, verified user corrections, repeated failure patterns, and stale knowledge. Use per-division and per-MasterBot queues, resource quotas, deduplication, bounded retries, and audit artifacts. A scheduled GitHub workflow is best-effort automation, not guaranteed 24/7 GPU training.

## User controls

Users can inspect, correct, export, and delete personal memory; revoke source access; set retention; and separately opt in or out of product improvement, cross-user sharing, and foundation-model training. Revocation blocks future ingestion and starts eligible deletion workflows. Do not promise retroactive removal from already released models where it cannot be guaranteed.

## Current engineering status

The governance policy now describes the full learning coverage and required pipeline. The policy tests validate those requirements. This is not proof that all connectors, persistent stores, ingestion workers, review queues, training clusters, or model-weight updates are deployed. Those components need implementation and runtime evidence before Buddy can be described as learning continuously in production.
